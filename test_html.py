#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试直接从HTML提取章节"""

import requests
from config import HEADERS
from bs4 import BeautifulSoup

print('[测试] 直接获取书籍页面 HTML...')
url = 'https://www.qidian.com/book/1887208/'
response = requests.get(url, headers=HEADERS, timeout=10)
print(f'状态码: {response.status_code}')

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 寻找章节链接
    links = soup.find_all('a', href=True)
    chapter_links = [l for l in links if '/chapter/' in l.get('href', '')]
    print(f'找到 {len(chapter_links)} 个章节链接')
    
    # 显示前5个
    if chapter_links:
        print('\n前5个章节：')
        for i, link in enumerate(chapter_links[:5]):
            print(f'  {i+1}. {link.text.strip()[:50]} -> {link.get("href")}')
    else:
        print('\n[警告] 未找到任何章节链接')
        print('\n页面前2000个字符：')
        print(response.text[:2000])
else:
    print(f'[错误] 获取失败，状态码: {response.status_code}')
