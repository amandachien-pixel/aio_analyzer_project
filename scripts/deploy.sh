#!/bin/bash
# AIO 分析器部署腳本
# ====================
# 用於快速部署 AIO 分析器到不同環境

set -e

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函數定義
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 檢查必要工具
check_requirements() {
    print_info "檢查系統需求..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安裝，請先安裝 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose 未安裝，請先安裝 Docker Compose"
        exit 1
    fi
    
    print_success "系統需求檢查通過"
}

# 檢查環境配置
check_environment() {
    print_info "檢查環境配置..."
    
    ENV_FILE=""
    case $1 in
        "dev"|"development")
            ENV_FILE="backend/env.example"
            ;;
        "prod"|"production")
            ENV_FILE=".env.prod"
            ;;
        *)
            print_error "無效的環境類型: $1"
            print_info "有效選項: dev, development, prod, production"
            exit 1
            ;;
    esac
    
    if [ ! -f "$ENV_FILE" ]; then
        print_warning "環境配置文件 $ENV_FILE 不存在"
        print_info "請根據 backend/env.example 創建環境配置文件"
        return 1
    fi
    
    print_success "環境配置檢查通過"
    return 0
}

# 構建 Docker 映像
build_images() {
    print_info "構建 Docker 映像..."
    
    case $1 in
        "dev"|"development")
            docker-compose build
            ;;
        "prod"|"production")
            docker-compose -f docker-compose.prod.yml build
            ;;
    esac
    
    print_success "Docker 映像構建完成"
}

# 部署開發環境
deploy_development() {
    print_info "部署開發環境..."
    
    # 停止現有服務
    docker-compose down
    
    # 啟動數據庫和 Redis
    docker-compose up -d db redis
    
    # 等待數據庫就緒
    print_info "等待數據庫啟動..."
    sleep 10
    
    # 執行數據庫遷移
    docker-compose run --rm web sh -c "
        cd /app/backend && 
        python manage.py migrate &&
        python manage.py collectstatic --noinput
    "
    
    # 創建超級用戶（如果不存在）
    print_info "檢查超級用戶..."
    docker-compose run --rm web sh -c "
        cd /app/backend && 
        python manage.py shell -c \"
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Super user created: admin/admin123')
else:
    print('Super user already exists')
\"
    "
    
    # 啟動所有服務
    docker-compose up -d
    
    print_success "開發環境部署完成"
    print_info "應用地址: http://localhost:8000"
    print_info "管理後台: http://localhost:8000/admin"
    print_info "API 文檔: http://localhost:8000/api/docs"
    print_info "Flower 監控: http://localhost:5555"
}

# 部署生產環境
deploy_production() {
    print_info "部署生產環境..."
    
    # 檢查生產環境配置
    if [ ! -f ".env.prod" ]; then
        print_error "生產環境配置文件 .env.prod 不存在"
        exit 1
    fi
    
    # 停止現有服務
    docker-compose -f docker-compose.prod.yml down
    
    # 啟動數據庫和 Redis
    docker-compose -f docker-compose.prod.yml up -d db redis
    
    # 等待數據庫就緒
    print_info "等待數據庫啟動..."
    sleep 15
    
    # 執行數據庫遷移
    docker-compose -f docker-compose.prod.yml run --rm web sh -c "
        cd /app/backend && 
        python manage.py migrate &&
        python manage.py collectstatic --noinput
    "
    
    # 啟動所有服務
    docker-compose -f docker-compose.prod.yml up -d
    
    print_success "生產環境部署完成"
    print_info "應用地址: https://your-domain.com"
    print_info "監控地址: http://your-domain.com:3000 (Grafana)"
}

# 查看服務狀態
check_status() {
    print_info "檢查服務狀態..."
    
    case $1 in
        "dev"|"development")
            docker-compose ps
            ;;
        "prod"|"production")
            docker-compose -f docker-compose.prod.yml ps
            ;;
    esac
}

# 查看日誌
show_logs() {
    case $1 in
        "dev"|"development")
            docker-compose logs -f
            ;;
        "prod"|"production")
            docker-compose -f docker-compose.prod.yml logs -f
            ;;
    esac
}

# 停止服務
stop_services() {
    print_info "停止服務..."
    
    case $1 in
        "dev"|"development")
            docker-compose down
            ;;
        "prod"|"production")
            docker-compose -f docker-compose.prod.yml down
            ;;
    esac
    
    print_success "服務已停止"
}

# 清理資源
cleanup() {
    print_warning "這將刪除所有容器、映像和數據卷！"
    read -p "確定要繼續嗎？ (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose down -v --rmi all
        docker system prune -a -f
        print_success "清理完成"
    else
        print_info "操作已取消"
    fi
}

# 備份數據
backup_data() {
    print_info "備份數據..."
    
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # 備份數據庫
    docker-compose exec db pg_dump -U postgres aio_analyzer > "$BACKUP_DIR/database.sql"
    
    # 備份媒體文件
    docker cp $(docker-compose ps -q web):/app/media "$BACKUP_DIR/"
    
    print_success "數據備份完成: $BACKUP_DIR"
}

# 恢復數據
restore_data() {
    if [ -z "$2" ]; then
        print_error "請指定備份目錄"
        exit 1
    fi
    
    BACKUP_DIR="$2"
    
    if [ ! -d "$BACKUP_DIR" ]; then
        print_error "備份目錄不存在: $BACKUP_DIR"
        exit 1
    fi
    
    print_info "恢復數據從: $BACKUP_DIR"
    
    # 恢復數據庫
    if [ -f "$BACKUP_DIR/database.sql" ]; then
        docker-compose exec -T db psql -U postgres -d aio_analyzer < "$BACKUP_DIR/database.sql"
        print_success "數據庫恢復完成"
    fi
    
    # 恢復媒體文件
    if [ -d "$BACKUP_DIR/media" ]; then
        docker cp "$BACKUP_DIR/media" $(docker-compose ps -q web):/app/
        print_success "媒體文件恢復完成"
    fi
}

# 顯示幫助信息
show_help() {
    echo "AIO 分析器部署腳本"
    echo ""
    echo "用法: $0 <命令> [環境] [參數]"
    echo ""
    echo "命令:"
    echo "  deploy <env>     部署到指定環境 (dev/prod)"
    echo "  status <env>     查看服務狀態"
    echo "  logs <env>       查看服務日誌"
    echo "  stop <env>       停止服務"
    echo "  backup           備份數據"
    echo "  restore <dir>    恢復數據"
    echo "  cleanup          清理所有資源"
    echo "  help             顯示此幫助信息"
    echo ""
    echo "環境:"
    echo "  dev, development   開發環境"
    echo "  prod, production   生產環境"
    echo ""
    echo "範例:"
    echo "  $0 deploy dev      部署開發環境"
    echo "  $0 deploy prod     部署生產環境"
    echo "  $0 status dev      查看開發環境狀態"
    echo "  $0 logs prod       查看生產環境日誌"
    echo "  $0 backup          備份數據"
}

# 主程序
main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 1
    fi
    
    case $1 in
        "deploy")
            if [ -z "$2" ]; then
                print_error "請指定環境類型"
                show_help
                exit 1
            fi
            
            check_requirements
            check_environment "$2"
            build_images "$2"
            
            case $2 in
                "dev"|"development")
                    deploy_development
                    ;;
                "prod"|"production")
                    deploy_production
                    ;;
            esac
            ;;
        "status")
            check_status "$2"
            ;;
        "logs")
            show_logs "$2"
            ;;
        "stop")
            stop_services "$2"
            ;;
        "backup")
            backup_data
            ;;
        "restore")
            restore_data "$@"
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 執行主程序
main "$@"
