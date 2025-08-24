#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日誌處理模組
============

提供統一的日誌記錄功能，支持彩色輸出和文件記錄。
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Dict, Any
import colorlog


def setup_logger(config: Dict[str, Any]) -> logging.Logger:
    """
    設置日誌記錄器
    
    Args:
        config: 日誌配置字典
        
    Returns:
        配置好的日誌記錄器
    """
    # 獲取配置參數
    log_level = config.get('level', 'INFO').upper()
    log_format = config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file = config.get('file', 'logs/aio_analyzer.log')
    max_bytes = config.get('max_bytes', 10485760)  # 10MB
    backup_count = config.get('backup_count', 5)
    
    # 創建日誌目錄
    log_file_path = Path(log_file)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 創建日誌記錄器
    logger = logging.getLogger('aio_analyzer')
    logger.setLevel(getattr(logging, log_level))
    
    # 清除現有的處理器
    logger.handlers.clear()
    
    # 創建彩色控制台處理器
    console_handler = colorlog.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level))
    
    # 彩色日誌格式
    color_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s%(reset)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(color_formatter)
    logger.addHandler(console_handler)
    
    # 創建文件處理器（輪轉日誌）
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(getattr(logging, log_level))
    
    # 文件日誌格式（不包含顏色）
    file_formatter = logging.Formatter(
        log_format,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # 防止日誌重複
    logger.propagate = False
    
    logger.info(f"日誌系統初始化完成 - 級別: {log_level}, 文件: {log_file}")
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    獲取日誌記錄器
    
    Args:
        name: 日誌記錄器名稱
        
    Returns:
        日誌記錄器
    """
    if name:
        return logging.getLogger(f'aio_analyzer.{name}')
    return logging.getLogger('aio_analyzer')


class LoggingMixin:
    """日誌記錄混入類別"""
    
    @property
    def logger(self) -> logging.Logger:
        """獲取類別專用的日誌記錄器"""
        return get_logger(self.__class__.__name__)


# 創建模組級別的日誌記錄器
module_logger = get_logger(__name__)
