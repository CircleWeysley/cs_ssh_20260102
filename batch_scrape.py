#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量爬取脚本 - 一次爬取多本书籍

使用方法：
1. 修改下面的 BOOKS_TO_SCRAPE 列表，添加要爬的书籍信息
2. 运行 python batch_scrape.py

配置示例：
    BOOKS_TO_SCRAPE = [
        {
            'id': '1004608',
            'name': '我是至尊',
            'start': 1,
            'end': 50,
            'skip_vip': False
        },
        {
            'id': '1010154',
            'name': '剑来',
            'start': 1,
            'end': None,  # None 表示全部
            'skip_vip': True
        }
    ]
"""

from scraper import QidianScraper
from utils import ensure_dir
from config import OUTPUT_DIR
import time

# ==================== 配置区 ====================
# 在这里添加你要爬的书籍
BOOKS_TO_SCRAPE = [
    {
        'id': '1004608',
        'name': '我是至尊',
        'start': 1,
        'end': None,  # None = 爬全部
        'skip_vip': False,
        'cookies': None  # 可选，设置特定的 VIP cookies
    },
    # 添加更多书籍，参考上面的格式
    # {
    #     'id': '1010154',
    #     'name': '剑来',
    #     'start': 1,
    #     'end': 100,
    #     'skip_vip': True,
    #     'cookies': None
    # },
]

# ==================== 执行 ====================

def batch_scrape():
    """批量爬取"""
    if not BOOKS_TO_SCRAPE:
        print("[提示] 未配置任何书籍，请修改 BOOKS_TO_SCRAPE 列表")
        return
    
    ensure_dir(OUTPUT_DIR)
    
    total = len(BOOKS_TO_SCRAPE)
    print(f"\n{'='*60}")
    print(f"批量爬取 {total} 本书籍")
    print(f"{'='*60}\n")
    
    for idx, book_config in enumerate(BOOKS_TO_SCRAPE, 1):
        book_id = book_config.get('id')
        book_name = book_config.get('name', f'书籍_{book_id}')
        start = book_config.get('start', 1)
        end = book_config.get('end')
        skip_vip = book_config.get('skip_vip', False)
        cookies = book_config.get('cookies')
        
        print(f"\n[{idx}/{total}] 开始爬取《{book_name}》(ID: {book_id})")
        print(f"    范围: 第 {start} - {end or '全部'} 章")
        print(f"    跳过VIP: {'是' if skip_vip else '否'}")
        print(f"-" * 60)
        
        try:
            scraper = QidianScraper(book_id, cookies_str=cookies)
            success = scraper.scrape(
                start_chapter=start,
                end_chapter=end,
                skip_vip=skip_vip
            )
            
            if success:
                print(f"✓ 《{book_name}》爬取成功")
            else:
                print(f"✗ 《{book_name}》爬取失败")
        
        except Exception as e:
            print(f"✗ 《{book_name}》爬取异常: {str(e)}")
        
        # 书籍之间延迟，避免被封IP
        if idx < total:
            print(f"等待 5 秒后继续下一本...")
            time.sleep(5)
    
    print(f"\n{'='*60}")
    print(f"批量爬取完成")
    print(f"输出目录: {OUTPUT_DIR}")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    batch_scrape()
