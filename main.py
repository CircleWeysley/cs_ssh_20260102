#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
起点中文网爬虫 - 简洁版（支持动态加载）
支持按书名/ID爬取全部章节（含VIP）
支持 Selenium 处理动态加载的页面
"""

import sys
import argparse
from search import get_book_id
from scraper import QidianScraper
from utils import ensure_dir
from config import OUTPUT_DIR

def main():
    parser = argparse.ArgumentParser(
        description='起点中文网爬虫 - 支持书名/ID查询和全章节爬取（含 Selenium 动态加载支持）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例：
  python main.py "我是至尊"              # 按书名搜索并爬取
  python main.py 1004608              # 按书ID直接爬取
  python main.py -i 1004608 -s 1 -e 50  # 爬取第1-50章
  python main.py -i 1004608 --skip-vip   # 跳过VIP章节
  python main.py -i 1887208 --use-selenium  # 使用 Selenium 处理动态加载
  
VIP章节说明：
  若要爬取VIP章节，需在 config.py 中设置 VIP_COOKIES 或通过环境变量 QD_COOKIES 传入
  获取cookies：登录起点网站 → F12开发者工具 → Network → 复制Cookie

动态加载页面说明：
  某些书籍的章节列表是通过 JavaScript 动态加载的，可使用以下方法处理：
  1. 自动检测：程序会自动尝试使用 Selenium（如已安装）
  2. 手动启用：python main.py -i 1887208 --use-selenium
  3. 安装 Selenium：pip install selenium webdriver-manager
        """
    )
    
    parser.add_argument('book', nargs='?', help='书名或书ID')
    parser.add_argument('-i', '--id', dest='book_id', help='直接指定书ID（优先级高于book参数）')
    parser.add_argument('-s', '--start', type=int, default=1, help='开始章节（默认1）')
    parser.add_argument('-e', '--end', type=int, help='结束章节（默认全部）')
    parser.add_argument('--skip-vip', action='store_true', help='跳过VIP章节')
    parser.add_argument('--cookies', help='VIP cookies 字符串（可选，覆盖config配置）')
    parser.add_argument('--use-selenium', action='store_true', help='使用 Selenium 处理动态加载页面')
    
    args = parser.parse_args()
    
    # 确定书ID
    if args.book_id:
        book_id = args.book_id
    elif args.book:
        book_id = get_book_id(args.book)
    else:
        parser.print_help()
        return
    
    if not book_id:
        print("[错误] 无法获取书籍ID，请检查输入")
        return
    
    # 确保输出目录存在
    ensure_dir(OUTPUT_DIR)
    
    # 创建爬虫并开始爬取
    scraper = QidianScraper(book_id, cookies_str=args.cookies, use_selenium=args.use_selenium)
    scraper.scrape(
        start_chapter=args.start,
        end_chapter=args.end,
        skip_vip=args.skip_vip
    )

if __name__ == '__main__':
    main()
