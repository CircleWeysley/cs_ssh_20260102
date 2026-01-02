# 工具函数
import os
import time
import random
import requests
from config import HEADERS, TIMEOUT, PROXIES, RETRY_TIMES, RETRY_DELAY
import json

def ensure_dir(directory):
    """确保目录存在"""
    os.makedirs(directory, exist_ok=True)

def save_to_file(filename, content):
    """将内容保存到文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

def read_from_file(filename):
    """读取文件内容"""
    if not os.path.exists(filename):
        return None
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def request_with_retry(url, method='GET', cookies=None, **kwargs):
    """带重试和反爬虫机制的 HTTP 请求"""
    headers = kwargs.pop('headers', HEADERS.copy())
    timeout = kwargs.pop('timeout', TIMEOUT)
    proxies = kwargs.pop('proxies', PROXIES)
    
    # 随机化请求头（避免检测为爬虫）
    headers['Accept-Language'] = random.choice(['zh-CN,zh;q=0.9', 'zh-CN,zh;q=0.8,en;q=0.6', 'zh-CN'])
    headers['Accept-Encoding'] = random.choice(['gzip, deflate, br', 'gzip, deflate', 'br, gzip, deflate'])
    
    for attempt in range(RETRY_TIMES):
        try:
            # 添加人类级别的随机延迟，避免被识别为爬虫
            if attempt == 0:
                # 第一次请求：2-5秒延迟
                delay = random.uniform(2, 5)
            else:
                # 重试：3-8秒延迟
                delay = random.uniform(3, 8) + RETRY_DELAY
            
            print(f"[延迟] 等待 {delay:.1f} 秒后请求...")
            time.sleep(delay)
            
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout, 
                                       proxies=proxies, cookies=cookies, **kwargs)
            else:
                response = requests.post(url, headers=headers, timeout=timeout,
                                        proxies=proxies, cookies=cookies, **kwargs)
            
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            if attempt < RETRY_TIMES - 1:
                print(f"[请求失败] {url} - 重试 {attempt+1}/{RETRY_TIMES-1}")
                # 失败后等待更长时间
                time.sleep(random.uniform(5, 10))
            else:
                print(f"[最终失败] {url} - {str(e)}")
                return None
    return None

def parse_cookies_string(cookie_str):
    """将 cookie 字符串解析为字典"""
    if not cookie_str:
        return {}
    cookies = {}
    for item in cookie_str.split(';'):
        item = item.strip()
        if '=' in item:
            key, value = item.split('=', 1)
            cookies[key.strip()] = value.strip()
    return cookies

def sanitize_filename(filename):
    """清理非法文件名字符"""
    invalid_chars = r'<>:"/\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename
