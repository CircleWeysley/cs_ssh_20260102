#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快速测试脚本"""

from search import search_book_by_name

print("=" * 60)
print("测试搜索功能")
print("=" * 60)

books = search_book_by_name('剑来')
print(f"\n找到 {len(books)} 本书：")
for i, book in enumerate(books[:5], 1):
    print(f"{i}. 《{book['bname']}》- {book['author']}")
    print(f"   介绍: {book['intro']}")

print("\n搜索功能测试完成！")
