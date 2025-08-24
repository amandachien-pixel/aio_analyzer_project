#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AIO 分析器配置設定
==================

此文件包含 AIO 潛力分析器的所有配置選項。
請根據您的環境和需求修改相應的設置。
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

# 獲取項目根目錄
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / 'config'


class Config:
    """配置管理類別"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置
        
        Args:
            config_file: 自定義配置文件路徑
        """
        self._config = self._load_default_config()
        
        # 如果提供了自定義配置文件，則加載並合併
        if config_file and os.path.exists(config_file):
            self._load_custom_config(config_file)
        
        # 從環境變數覆蓋設置
        self._load_from_environment()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """載入默認配置"""
        return {
            # Google Search Console 設定
            "gsc": {
                "credentials_file": str(CONFIG_DIR / "credentials.json"),
                "token_file": str(CONFIG_DIR / "token.json"),
                "scopes": ['https://www.googleapis.com/auth/webmasters.readonly']
            },
            
            # Google Ads API 設定
            "ads": {
                "yaml_file": str(CONFIG_DIR / "google-ads.yaml"),
                "language_code": "gid/1001",  # 繁體中文
                "geo_target_code": "gid/1013274",  # 台灣
                "keyword_limit": 20  # API 限制
            },
            
            # SERP API 設定
            "serp": {
                "api_key": "YOUR_SERP_API_KEY",
                "endpoint": "https://serpapi.com/search.json",
                "country": "tw",
                "language": "zh-tw",
                "concurrent_requests": 10,  # 並發請求數量
                "rate_limit": 1.0  # 每秒請求率限制
            },
            
            # 分析設定
            "analysis": {
                "site_url": "sc-domain:your-domain.com",
                "customer_id": "123-456-7890",
                "default_days_back": 90,
                "default_regex": r'^(what|how|why|when|where|who|which|什麼|如何|為何|哪裡|誰是)\b',
                "row_limit": 5000
            },
            
            # 輸出設定
            "output": {
                "directory": str(PROJECT_ROOT / "output"),
                "format": "csv",  # csv, excel, json
                "include_charts": True,
                "timestamp_format": "%Y%m%d_%H%M%S"
            },
            
            # 日誌設定
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": str(PROJECT_ROOT / "logs" / "aio_analyzer.log"),
                "max_bytes": 10485760,  # 10MB
                "backup_count": 5
            },
            
            # 效能設定
            "performance": {
                "timeout": 30,  # 請求超時時間（秒）
                "retry_attempts": 3,
                "retry_delay": 1,  # 重試延遲（秒）
                "chunk_size": 100  # 批次處理大小
            }
        }
    
    def _load_custom_config(self, config_file: str):
        """載入自定義配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.endswith('.yaml') or config_file.endswith('.yml'):
                    custom_config = yaml.safe_load(f)
                else:
                    # 假設是 Python 文件
                    import importlib.util
                    spec = importlib.util.spec_from_file_location("config", config_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    custom_config = getattr(module, 'CONFIG', {})
                
                self._merge_config(self._config, custom_config)
                
        except Exception as e:
            print(f"載入自定義配置時發生錯誤: {e}")
    
    def _load_from_environment(self):
        """從環境變數載入配置"""
        env_mappings = {
            'GSC_CREDENTIALS_FILE': ('gsc', 'credentials_file'),
            'GSC_TOKEN_FILE': ('gsc', 'token_file'),
            'GOOGLE_ADS_YAML_FILE': ('ads', 'yaml_file'),
            'SERP_API_KEY': ('serp', 'api_key'),
            'SITE_URL': ('analysis', 'site_url'),
            'CUSTOMER_ID': ('analysis', 'customer_id'),
            'LOG_LEVEL': ('logging', 'level'),
            'OUTPUT_DIR': ('output', 'directory')
        }
        
        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                if section not in self._config:
                    self._config[section] = {}
                self._config[section][key] = value
    
    def _merge_config(self, base: Dict, custom: Dict):
        """遞歸合併配置字典"""
        for key, value in custom.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get(self, section: str, default=None) -> Any:
        """
        獲取配置值
        
        Args:
            section: 配置節點路徑，支持點分隔符（如 'gsc.credentials_file'）
            default: 默認值
            
        Returns:
            配置值
        """
        keys = section.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, section: str, value: Any):
        """
        設置配置值
        
        Args:
            section: 配置節點路徑
            value: 配置值
        """
        keys = section.split('.')
        config = self._config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def validate(self) -> bool:
        """
        驗證配置的有效性
        
        Returns:
            配置是否有效
        """
        required_fields = [
            'gsc.credentials_file',
            'ads.yaml_file',
            'serp.api_key',
            'analysis.site_url',
            'analysis.customer_id'
        ]
        
        for field in required_fields:
            value = self.get(field)
            if not value or value == "YOUR_API_KEY" or value == "your-domain.com":
                print(f"配置項目 {field} 未正確設置")
                return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """返回完整配置字典"""
        return self._config.copy()


# 創建全局配置實例
config = Config()


# 導出常用配置項目
GSC_CONFIG = config.get('gsc', {})
ADS_CONFIG = config.get('ads', {})
SERP_CONFIG = config.get('serp', {})
ANALYSIS_CONFIG = config.get('analysis', {})
OUTPUT_CONFIG = config.get('output', {})
LOGGING_CONFIG = config.get('logging', {})
PERFORMANCE_CONFIG = config.get('performance', {})
