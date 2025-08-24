#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
報告生成模組
============

生成 AIO 潛力分析的綜合報告，
支持多種格式輸出和圖表生成。
"""

import os
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import json

from .logger import LoggingMixin


class ReportGenerator(LoggingMixin):
    """報告生成器"""
    
    def __init__(self, config: Dict[str, Any], logger=None):
        """
        初始化報告生成器
        
        Args:
            config: 配置字典
            logger: 日誌記錄器
        """
        self.config = config
        if logger:
            self._logger = logger
        
        # 輸出配置
        self.output_config = config.get('output', {})
        self.output_dir = Path(self.output_config.get('directory', 'output'))
        self.output_format = self.output_config.get('format', 'csv')
        self.include_charts = self.output_config.get('include_charts', True)
        self.timestamp_format = self.output_config.get('timestamp_format', '%Y%m%d_%H%M%S')
        
        # 確保輸出目錄存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"報告生成器已初始化 - 輸出目錄: {self.output_dir}")
    
    def _generate_filename(self, base_name: str, extension: str = None) -> str:
        """
        生成帶時間戳的文件名
        
        Args:
            base_name: 基礎文件名
            extension: 文件擴展名
            
        Returns:
            完整的文件名
        """
        timestamp = datetime.now().strftime(self.timestamp_format)
        
        if extension:
            return f"{base_name}_{timestamp}.{extension}"
        else:
            return f"{base_name}_{timestamp}"
    
    async def generate_detailed_report(self,
                                     analysis_data: pd.DataFrame,
                                     gsc_data: pd.DataFrame,
                                     output_dir: str = None) -> str:
        """
        生成詳細的 AIO 分析報告
        
        Args:
            analysis_data: 分析結果數據
            gsc_data: GSC 原始數據
            output_dir: 輸出目錄（可選）
            
        Returns:
            主報告文件路徑
        """
        if output_dir:
            self.output_dir = Path(output_dir)
            self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("開始生成詳細報告...")
        
        # 數據預處理
        processed_data = self._preprocess_data(analysis_data, gsc_data)
        
        # 生成主報告
        main_report_path = await self._generate_main_report(processed_data)
        
        # 生成摘要報告
        summary_path = await self._generate_summary_report(processed_data)
        
        # 生成統計報告
        stats_path = await self._generate_statistics_report(processed_data)
        
        # 如果啟用，生成圖表
        if self.include_charts:
            await self._generate_charts(processed_data)
        
        # 生成元數據文件
        await self._generate_metadata(processed_data, main_report_path)
        
        self.logger.info(f"報告生成完成 - 主報告: {main_report_path}")
        
        return str(main_report_path)
    
    def _preprocess_data(self, analysis_data: pd.DataFrame, gsc_data: pd.DataFrame) -> Dict[str, Any]:
        """
        預處理數據以供報告生成
        
        Args:
            analysis_data: 分析結果數據
            gsc_data: GSC 原始數據
            
        Returns:
            處理後的數據字典
        """
        processed = {
            'analysis_data': analysis_data.copy() if not analysis_data.empty else pd.DataFrame(),
            'gsc_data': gsc_data.copy() if not gsc_data.empty else pd.DataFrame(),
            'timestamp': datetime.now(),
            'summary_stats': {}
        }
        
        # 計算摘要統計
        if not analysis_data.empty:
            total_keywords = len(analysis_data)
            aio_keywords = analysis_data['triggers_aio'].sum() if 'triggers_aio' in analysis_data.columns else 0
            aio_percentage = (aio_keywords / total_keywords * 100) if total_keywords > 0 else 0
            
            # 搜尋量統計
            search_volume_stats = {}
            if 'search_volume' in analysis_data.columns:
                search_volume_stats = {
                    'total_volume': analysis_data['search_volume'].sum(),
                    'avg_volume': analysis_data['search_volume'].mean(),
                    'median_volume': analysis_data['search_volume'].median(),
                    'max_volume': analysis_data['search_volume'].max()
                }
            
            # 競爭程度分布
            competition_distribution = {}
            if 'competition_level' in analysis_data.columns:
                competition_distribution = analysis_data['competition_level'].value_counts().to_dict()
            
            processed['summary_stats'] = {
                'total_keywords': total_keywords,
                'aio_keywords': aio_keywords,
                'aio_percentage': round(aio_percentage, 2),
                'search_volume_stats': search_volume_stats,
                'competition_distribution': competition_distribution
            }
        
        # GSC 數據統計
        if not gsc_data.empty:
            gsc_stats = {
                'total_queries': len(gsc_data),
                'total_clicks': gsc_data['clicks'].sum() if 'clicks' in gsc_data.columns else 0,
                'total_impressions': gsc_data['impressions'].sum() if 'impressions' in gsc_data.columns else 0,
                'avg_ctr': gsc_data['ctr'].mean() if 'ctr' in gsc_data.columns else 0,
                'avg_position': gsc_data['position'].mean() if 'position' in gsc_data.columns else 0
            }
            processed['gsc_stats'] = gsc_stats
        
        return processed
    
    async def _generate_main_report(self, data: Dict[str, Any]) -> Path:
        """生成主要分析報告"""
        filename = self._generate_filename('aio_analysis_report', 'csv')
        file_path = self.output_dir / filename
        
        analysis_df = data['analysis_data']
        
        if not analysis_df.empty:
            # 重新命名欄位為中文
            column_mapping = {
                'keyword_idea': '目標關鍵字',
                'search_volume': '每月搜尋量',
                'competition_level': '競爭程度',
                'triggers_aio': '觸發AIO',
                'competition_index': '競爭指數',
                'low_top_of_page_bid_usd': '最低出價(USD)',
                'high_top_of_page_bid_usd': '最高出價(USD)'
            }
            
            report_df = analysis_df.rename(columns=column_mapping)
            
            # 轉換布林值為 Y/N
            if '觸發AIO' in report_df.columns:
                report_df['觸發AIO'] = report_df['觸發AIO'].apply(lambda x: 'Y' if x else 'N')
            
            # 排序：優先顯示觸發 AIO 的關鍵字，然後按搜尋量排序
            if '每月搜尋量' in report_df.columns and '觸發AIO' in report_df.columns:
                report_df = report_df.sort_values(['觸發AIO', '每月搜尋量'], ascending=[False, False])
            
            # 保存為 CSV
            report_df.to_csv(file_path, index=False, encoding='utf-8-sig')
            
            # 如果配置為 Excel 格式，也生成 Excel 文件
            if self.output_format.lower() == 'excel':
                excel_filename = self._generate_filename('aio_analysis_report', 'xlsx')
                excel_path = self.output_dir / excel_filename
                
                with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                    report_df.to_excel(writer, sheet_name='AIO分析報告', index=False)
                    
                    # 添加摘要工作表
                    summary_df = pd.DataFrame([data['summary_stats']])
                    summary_df.to_excel(writer, sheet_name='分析摘要', index=False)
                
                self.logger.info(f"Excel 報告已生成: {excel_path}")
        
        else:
            # 如果沒有數據，創建空報告
            empty_df = pd.DataFrame(columns=['目標關鍵字', '每月搜尋量', '競爭程度', '觸發AIO'])
            empty_df.to_csv(file_path, index=False, encoding='utf-8-sig')
        
        self.logger.info(f"主報告已生成: {file_path}")
        return file_path
    
    async def _generate_summary_report(self, data: Dict[str, Any]) -> Path:
        """生成摘要報告"""
        filename = self._generate_filename('aio_summary', 'json')
        file_path = self.output_dir / filename
        
        summary = {
            'report_metadata': {
                'generated_at': data['timestamp'].isoformat(),
                'report_type': 'AIO 潛力分析摘要',
                'version': '1.0.0'
            },
            'analysis_summary': data['summary_stats'],
            'gsc_summary': data.get('gsc_stats', {}),
            'top_keywords': self._get_top_keywords(data['analysis_data']),
            'recommendations': self._generate_recommendations(data)
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"摘要報告已生成: {file_path}")
        return file_path
    
    def _get_top_keywords(self, analysis_df: pd.DataFrame, top_n: int = 10) -> Dict[str, List]:
        """獲取重要關鍵字列表"""
        if analysis_df.empty:
            return {}
        
        top_keywords = {}
        
        # 觸發 AIO 的高搜尋量關鍵字
        if 'triggers_aio' in analysis_df.columns and 'search_volume' in analysis_df.columns:
            aio_keywords = analysis_df[analysis_df['triggers_aio'] == True]
            if not aio_keywords.empty:
                top_aio = aio_keywords.nlargest(top_n, 'search_volume')
                top_keywords['high_volume_aio'] = top_aio[['keyword_idea', 'search_volume']].to_dict('records')
        
        # 高搜尋量但未觸發 AIO 的關鍵字（機會關鍵字）
        if 'triggers_aio' in analysis_df.columns and 'search_volume' in analysis_df.columns:
            non_aio_keywords = analysis_df[analysis_df['triggers_aio'] == False]
            if not non_aio_keywords.empty:
                top_opportunities = non_aio_keywords.nlargest(top_n, 'search_volume')
                top_keywords['opportunity_keywords'] = top_opportunities[['keyword_idea', 'search_volume']].to_dict('records')
        
        return top_keywords
    
    def _generate_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """生成分析建議"""
        recommendations = []
        stats = data['summary_stats']
        
        if not stats:
            return ["無足夠數據生成建議"]
        
        aio_percentage = stats.get('aio_percentage', 0)
        total_keywords = stats.get('total_keywords', 0)
        
        # 基於 AIO 觸發率的建議
        if aio_percentage > 50:
            recommendations.append(f"✅ AIO 觸發率較高 ({aio_percentage}%)，表示您的關鍵字策略與 AI Overview 趨勢一致")
        elif aio_percentage > 20:
            recommendations.append(f"⚠️ AIO 觸發率中等 ({aio_percentage}%)，建議優化內容以提高 AI Overview 曝光機會")
        else:
            recommendations.append(f"🔴 AIO 觸發率較低 ({aio_percentage}%)，建議重新評估關鍵字策略並關注問答型內容")
        
        # 基於關鍵字數量的建議
        if total_keywords < 50:
            recommendations.append("📈 建議擴展更多相關關鍵字以獲得更全面的 AIO 潛力分析")
        
        # 基於搜尋量的建議
        search_volume_stats = stats.get('search_volume_stats', {})
        if search_volume_stats:
            avg_volume = search_volume_stats.get('avg_volume', 0)
            if avg_volume > 1000:
                recommendations.append("🎯 平均搜尋量較高，這些關鍵字具有良好的流量潛力")
            elif avg_volume < 100:
                recommendations.append("💡 平均搜尋量較低，考慮加入更多高搜尋量的長尾關鍵字")
        
        # 競爭程度建議
        competition_dist = stats.get('competition_distribution', {})
        if competition_dist:
            high_competition = competition_dist.get('HIGH', 0)
            total_comp = sum(competition_dist.values())
            if high_competition / total_comp > 0.5:
                recommendations.append("⚔️ 高競爭關鍵字較多，建議尋找競爭程度較低的替代關鍵字")
        
        return recommendations
    
    async def _generate_statistics_report(self, data: Dict[str, Any]) -> Path:
        """生成統計分析報告"""
        filename = self._generate_filename('aio_statistics', 'txt')
        file_path = self.output_dir / filename
        
        stats = data['summary_stats']
        gsc_stats = data.get('gsc_stats', {})
        
        report_content = f"""
AIO 潛力分析統計報告
==================
生成時間: {data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}

關鍵字分析統計
--------------
總關鍵字數量: {stats.get('total_keywords', 0):,}
觸發 AIO 關鍵字: {stats.get('aio_keywords', 0):,}
AIO 觸發率: {stats.get('aio_percentage', 0):.2f}%

搜尋量統計
----------
總搜尋量: {stats.get('search_volume_stats', {}).get('total_volume', 0):,}
平均搜尋量: {stats.get('search_volume_stats', {}).get('avg_volume', 0):,.0f}
中位數搜尋量: {stats.get('search_volume_stats', {}).get('median_volume', 0):,.0f}
最高搜尋量: {stats.get('search_volume_stats', {}).get('max_volume', 0):,}

競爭程度分布
------------
"""
        
        competition_dist = stats.get('competition_distribution', {})
        for level, count in competition_dist.items():
            percentage = (count / stats.get('total_keywords', 1)) * 100
            report_content += f"{level}: {count:,} ({percentage:.1f}%)\n"
        
        if gsc_stats:
            report_content += f"""
GSC 數據統計
------------
總查詢數: {gsc_stats.get('total_queries', 0):,}
總點擊數: {gsc_stats.get('total_clicks', 0):,}
總曝光數: {gsc_stats.get('total_impressions', 0):,}
平均 CTR: {gsc_stats.get('avg_ctr', 0):.3f}
平均排名: {gsc_stats.get('avg_position', 0):.1f}
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.logger.info(f"統計報告已生成: {file_path}")
        return file_path
    
    async def _generate_charts(self, data: Dict[str, Any]):
        """生成圖表（需要 matplotlib）"""
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')  # 使用非互動式後端
            
            plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei']
            plt.rcParams['axes.unicode_minus'] = False
            
            analysis_df = data['analysis_data']
            if analysis_df.empty:
                return
            
            # AIO 觸發率餅圖
            if 'triggers_aio' in analysis_df.columns:
                await self._create_aio_pie_chart(analysis_df)
            
            # 搜尋量分布直方圖
            if 'search_volume' in analysis_df.columns:
                await self._create_search_volume_histogram(analysis_df)
            
            # 競爭程度分布柱狀圖
            if 'competition_level' in analysis_df.columns:
                await self._create_competition_bar_chart(analysis_df)
            
        except ImportError:
            self.logger.warning("matplotlib 未安裝，跳過圖表生成")
        except Exception as e:
            self.logger.error(f"生成圖表時發生錯誤: {e}")
    
    async def _create_aio_pie_chart(self, df: pd.DataFrame):
        """創建 AIO 觸發率餅圖"""
        import matplotlib.pyplot as plt
        
        aio_counts = df['triggers_aio'].value_counts()
        labels = ['觸發 AIO', '未觸發 AIO']
        
        plt.figure(figsize=(8, 6))
        plt.pie(aio_counts.values, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.title('AIO 觸發率分布')
        
        filename = self._generate_filename('aio_distribution', 'png')
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"AIO 分布圖已生成: {filename}")
    
    async def _create_search_volume_histogram(self, df: pd.DataFrame):
        """創建搜尋量分布直方圖"""
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(10, 6))
        plt.hist(df['search_volume'], bins=20, edgecolor='black', alpha=0.7)
        plt.xlabel('搜尋量')
        plt.ylabel('關鍵字數量')
        plt.title('搜尋量分布')
        plt.grid(True, alpha=0.3)
        
        filename = self._generate_filename('search_volume_distribution', 'png')
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"搜尋量分布圖已生成: {filename}")
    
    async def _create_competition_bar_chart(self, df: pd.DataFrame):
        """創建競爭程度分布柱狀圖"""
        import matplotlib.pyplot as plt
        
        competition_counts = df['competition_level'].value_counts()
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(competition_counts.index, competition_counts.values)
        plt.xlabel('競爭程度')
        plt.ylabel('關鍵字數量')
        plt.title('競爭程度分布')
        
        # 在柱狀圖上顯示數值
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom')
        
        filename = self._generate_filename('competition_distribution', 'png')
        plt.savefig(self.output_dir / filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.logger.info(f"競爭程度分布圖已生成: {filename}")
    
    async def _generate_metadata(self, data: Dict[str, Any], main_report_path: Path):
        """生成報告元數據"""
        metadata = {
            'report_info': {
                'generated_at': data['timestamp'].isoformat(),
                'main_report': str(main_report_path),
                'output_directory': str(self.output_dir),
                'format': self.output_format
            },
            'data_summary': data['summary_stats'],
            'file_list': [f.name for f in self.output_dir.iterdir() if f.is_file()]
        }
        
        filename = self._generate_filename('report_metadata', 'json')
        metadata_path = self.output_dir / filename
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.info(f"報告元數據已生成: {metadata_path}")
    
    def cleanup_old_reports(self, keep_days: int = 30):
        """清理舊報告文件"""
        if not self.output_dir.exists():
            return
        
        cutoff_time = datetime.now().timestamp() - (keep_days * 24 * 3600)
        
        removed_count = 0
        for file_path in self.output_dir.iterdir():
            if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                try:
                    file_path.unlink()
                    removed_count += 1
                except Exception as e:
                    self.logger.warning(f"無法刪除舊文件 {file_path}: {e}")
        
        if removed_count > 0:
            self.logger.info(f"已清理 {removed_count} 個超過 {keep_days} 天的舊報告文件")
