# 搜索功能：通过书名查找书ID
import json
from utils import request_with_retry
from config import SEARCH_API, QIDIAN_HOME
from bs4 import BeautifulSoup

def search_book_by_name(book_name):
    """
    通过书名搜索，返回候选书籍列表
    尝试多个搜索方案（API → 网页爬虫）
    返回格式：[{"bid": "书ID", "bname": "书名", "author": "作者"}, ...]
    """
    # 方案1：尝试官方搜索 API
    books = _search_via_api(book_name)
    if books:
        return books
    
    # 方案2：降级方案 - 网页搜索爬虫
    print("[降级] 官方API不可用，使用网页搜索爬虫")
    books = _search_via_web(book_name)
    return books

def _search_via_api(book_name):
    """通过官方 API 搜索"""
    params = {
        'query': book_name,
        'size': 10
    }
    
    response = request_with_retry(SEARCH_API, method='GET', params=params)
    if not response:
        return []
    
    try:
        data = response.json()
        # 起点搜索 API 返回的结构
        if 'data' in data and 'book' in data['data']:
            books = []
            for item in data['data']['book']:
                books.append({
                    'bid': item.get('bid', ''),
                    'bname': item.get('bname', ''),
                    'author': item.get('author', ''),
                    'intro': item.get('intro', '')[:100] + '...' if item.get('intro') else ''
                })
            return books
        return []
    except Exception as e:
        print(f"[提示] API 查询失败: {str(e)}")
        return []

def _search_via_web(book_name):
    """通过网页爬虫搜索（降级方案）"""
    search_url = f"{QIDIAN_HOME}/search.aspx"
    params = {'kw': book_name}
    
    response = request_with_retry(search_url, method='GET', params=params)
    if not response:
        return []
    
    try:
        soup = BeautifulSoup(response.text, 'html.parser')
        books = []
        
        # 查找搜索结果中的书籍
        search_items = soup.select('ul.search-result li')
        for item in search_items[:10]:
            link = item.select_one('h3 a')
            author = item.select_one('.author')
            intro = item.select_one('.intro')
            
            if link:
                href = link.get('href', '')
                # 从 URL 提取书ID: /book/1234567
                import re
                match = re.search(r'/book/(\d+)', href)
                if match:
                    bid = match.group(1)
                    bname = link.get_text(strip=True)
                    author_text = author.get_text(strip=True) if author else '未知'
                    intro_text = intro.get_text(strip=True)[:100] if intro else ''
                    
                    books.append({
                        'bid': bid,
                        'bname': bname,
                        'author': author_text,
                        'intro': intro_text
                    })
        
        return books
    except Exception as e:
        print(f"[错误] 网页搜索失败: {str(e)}")
        return []

def prompt_book_selection(books):
    """
    交互式选择书籍
    """
    if not books:
        print("未找到相关书籍")
        return None
    
    print(f"\n找到 {len(books)} 本书：")
    for i, book in enumerate(books, 1):
        print(f"{i}. 《{book['bname']}》- {book['author']}")
        print(f"   介绍: {book['intro']}")
    
    while True:
        try:
            choice = input(f"\n请选择 (1-{len(books)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(books):
                return books[idx]['bid']
            else:
                print(f"请输入 1-{len(books)} 之间的数字")
        except ValueError:
            print("输入无效，请输入数字")

def get_book_id(book_input):
    """
    获取书ID：可以是直接的ID或者书名
    - 如果是纯数字，当作 ID 直接返回
    - 否则作为书名搜索
    """
    if book_input.isdigit():
        print(f"[输入] 使用书ID: {book_input}")
        return book_input
    else:
        print(f"[搜索] 搜索书名: {book_input}")
        books = search_book_by_name(book_input)
        if books:
            bid = prompt_book_selection(books)
            return bid
        else:
            print(f"搜索失败: 未找到《{book_input}》相关书籍")
            return None
