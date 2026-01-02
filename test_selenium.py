#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接测试 Selenium 获取章节列表
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
import time

def test_selenium():
    """测试 Selenium Edge WebDriver"""
    
    print("[开始] 测试 Selenium Edge WebDriver...")
    
    try:
        # 配置 Edge 选项
        edge_options = Options()
        edge_options.add_argument('--start-maximized')
        edge_options.add_argument('--disable-blink-features=AutomationControlled')
        edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        edge_options.add_experimental_option('useAutomationExtension', False)
        
        # 不使用无头模式，这样能看到浏览器窗口
        # edge_options.add_argument('--headless')
        
        print("[初始化] 启动 Edge 浏览器...")
        
        # 尝试自动下载，失败则直接使用系统 Edge
        try:
            print("[提示] 尝试自动下载 EdgeDriver...")
            service = Service(EdgeChromiumDriverManager().install())
            driver = webdriver.Edge(service=service, options=edge_options)
        except Exception as e:
            print(f"[警告] 自动下载失败: {str(e)}")
            print("[提示] 尝试直接使用系统 Edge...")
            driver = webdriver.Edge(options=edge_options)
        
        print("[加载] 打开书籍页面...")
        book_url = "https://www.qidian.com/book/1887208/"
        driver.get(book_url)
        
        print("[等待] 等待页面加载...")
        time.sleep(3)  # 等待3秒让页面加载
        
        print("[查询] 查找章节列表...")
        
        # 尝试多个选择器
        selectors = [
            'a[href*="/chapter/"]',
            'li a[href*="/chapter/"]',
            '.chapter-item a',
            '.volume-item a'
        ]
        
        found = False
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"[成功] 用选择器 '{selector}' 找到 {len(elements)} 个元素")
                    found = True
                    
                    # 显示前5个章节
                    print("\n前 5 个章节：")
                    for i, elem in enumerate(elements[:5]):
                        href = elem.get_attribute('href')
                        text = elem.text
                        print(f"  {i+1}. {text} -> {href}")
                    
                    break
            except:
                continue
        
        if not found:
            print("[警告] 未找到任何章节链接")
            print("[调试] 页面源代码前 1000 字符：")
            print(driver.page_source[:1000])
        
        print("\n[提示] 浏览器窗口保持打开，你可以手动检查页面")
        print("[提示] 按 Enter 关闭浏览器...")
        input()
        
        driver.quit()
        print("[完成] 测试结束")
        
    except Exception as e:
        print(f"[错误] {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_selenium()
