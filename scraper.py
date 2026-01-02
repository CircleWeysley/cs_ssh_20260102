import os
# 核心爬虫逻辑
import re
import time
import json
import random
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils import request_with_retry, ensure_dir, save_to_file, sanitize_filename, parse_cookies_string
from config import QIDIAN_HOME, OUTPUT_DIR, VIP_COOKIES, PROXY, TIMEOUT

# Selenium 导入（可选）
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.edge.options import Options
    from selenium.webdriver.edge.service import Service
    from webdriver_manager.microsoft import EdgeChromiumDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("[警告] Selenium 未安装，某些动态加载的页面可能无法正确爬取")
    print("[提示] 运行 pip install selenium webdriver-manager 来启用完整功能")

class QidianScraper:
    def __init__(self, book_id, cookies_str=None, use_selenium=True):
        """
        初始化爬虫
        :param book_id: 书籍 ID
        :param cookies_str: VIP cookies 字符串（可选，用于爬取 VIP 章节）
        :param use_selenium: 是否使用 Selenium 处理动态加载
        """
        self.book_id = book_id
        self.book_url = f"{QIDIAN_HOME}/book/{book_id}"
        self.cookies = parse_cookies_string(cookies_str or VIP_COOKIES)
        self.chapters = []
        self.book_info = {}
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.driver = None
        
    def get_book_info(self):
        """获取书籍基本信息（书名、作者等）"""
        response = request_with_retry(self.book_url, cookies=self.cookies)
        if not response:
            print(f"[错误] 无法访问书籍页面: {self.book_url}")
            return False
        
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取书名
            book_name = soup.select_one('h1#bookName, h1.book-name')
            if book_name:
                self.book_info['name'] = book_name.get_text(strip=True)
            
            # 提取作者
            author = soup.select_one('span.author, a.writer-name')
            if author:
                author_text = author.get_text(strip=True)
                # 清理 "作者:" 前缀
                if author_text.startswith('作者:'):
                    author_text = author_text[3:]
                self.book_info['author'] = author_text
            
            # 提取简介
            intro = soup.select_one('.book-intro, .intro')
            if intro:
                self.book_info['intro'] = intro.get_text(strip=True)
            
            print(f"[信息] 书名: {self.book_info.get('name', '未知')}")
            print(f"[信息] 作者: {self.book_info.get('author', '未知')}")
            return True
        except Exception as e:
            print(f"[错误] 获取书籍信息失败: {str(e)}")
            return False
    
    def _init_selenium(self):
        """初始化 Selenium WebDriver"""
        if not SELENIUM_AVAILABLE:
            return False
        
        try:
            # Edge 选项 - 最小化参数，只保留必要的反检测
            edge_options = Options()
            
            # 基础稳定性
            edge_options.add_argument('--no-sandbox')
            edge_options.add_argument('--disable-dev-shm-usage')
            edge_options.add_argument('--ignore-certificate-errors')
            
            # 最小反检测参数组合
            edge_options.add_argument('--disable-blink-features=AutomationControlled')
            edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            edge_options.add_experimental_option('useAutomationExtension', False)
            
            # User-Agent
            edge_options.add_argument(f'--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0')
            
            # 配置代理
            if PROXY:
                edge_options.add_argument(f'--proxy-server={PROXY}')

            # 优先使用本地msedgedriver.exe
            local_driver = r"D:\\tools\\scrapyQiDian\\Qidian\\msedgedriver.exe"
            if os.path.exists(local_driver):
                print(f"[信息] 使用本地 EdgeDriver: {local_driver}")
                service = Service(executable_path=local_driver)
                self.driver = webdriver.Edge(service=service, options=edge_options)
            else:
                # 尝试自动下载，失败则直接使用系统中的 Edge
                try:
                    print("[加载] 尝试自动下载 EdgeDriver...")
                    service = Service(EdgeChromiumDriverManager().install())
                    self.driver = webdriver.Edge(service=service, options=edge_options)
                except Exception as download_error:
                    print(f"[警告] 自动下载失败，尝试使用系统 Edge: {str(download_error)}")
                    self.driver = webdriver.Edge(options=edge_options)

            # 增加 page load timeout
            try:
                self.driver.set_page_load_timeout(TIMEOUT)
            except Exception:
                pass

            print("[信息] Edge WebDriver 已初始化")
            print("[提示] 如果出现滑块验证，请手动完成。爬虫会在您拖动滑块后自动继续")
            return True
        except Exception as e:
            print(f"[警告] Selenium 初始化失败: {str(e)}")
            print("[建议] 请确保系统中已安装 Microsoft Edge 浏览器，并有可用的 msedgedriver.exe")
            self.driver = None
            return False
    
    def _get_chapters_via_selenium(self):
        """使用 Selenium 获取章节列表（支持动态加载）"""
        if not self.driver:
            return False
        
        try:
            print("[加载] 用 Selenium 加载页面 (先打开主页设置 cookies)...")
            # 先打开主页设置 domain cookies，再打开书籍页，避免刷新导致 renderer 超时
            try:
                self.driver.get(QIDIAN_HOME)
            except Exception:
                pass

            # 添加 cookies 到域
            for key, value in self.cookies.items():
                try:
                    self.driver.add_cookie({'name': key, 'value': value, 'path': '/', 'domain': '.qidian.com'})
                except Exception:
                    try:
                        self.driver.add_cookie({'name': key, 'value': value})
                    except Exception:
                        pass

            # 然后打开书籍页面
            try:
                self.driver.get(self.book_url)
            except Exception:
                pass
            
            # 等待章节列表出现（尝试多个可能的选择器）
            print("[加载] 等待章节列表加载...")
            try:
                # 方案 1：等待包含章节列表的容器（时间更久以应对慢速页面）
                WebDriverWait(self.driver, max(30, TIMEOUT)).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li a[href*="/chapter/"]'))
                )
                print("[成功] 章节列表已加载")
            except Exception:
                print("[警告] 章节列表等待超时，尝试解析现有内容...")
            
            # 验证通过后，等待人类级别的时间再继续（5-15秒）
            # 这是为了避免被检测为机器人"操作过快"
            wait_time = random.uniform(5, 15)
            print(f"[等待] 人类行为模拟: 等待 {wait_time:.1f} 秒...")
            time.sleep(wait_time)
            
            # 获取页面源码前再等待（2-5秒）
            print("[加载] 正在获取页面内容...")
            time.sleep(random.uniform(2, 5))
            
            # 获取页面源码
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # 解析前再等待（1-3秒）
            time.sleep(random.uniform(1, 3))
            
            # 尝试多种选择器找章节链接
            selectors = [
                'li a[href*="/chapter/"]',
                'a[href*="/chapter/"]',
                '.volume-item a',
                '.chapter-item a'
            ]
            
            chapter_items = []
            for selector in selectors:
                chapter_items = soup.select(selector)
                if chapter_items:
                    print(f"[提示] 用选择器 '{selector}' 找到 {len(chapter_items)} 个章节")
                    break
            
            if not chapter_items:
                print("[警告] 未找到任何章节链接")
                return False
            
            # 解析章节
            for link in chapter_items:
                chapter_url = link.get('href', '')
                
                # 确保是完整的章节 URL
                if chapter_url:
                    # 移除可能已经存在的域名前缀（避免重复）
                    if chapter_url.startswith('http'):
                        pass  # 已经是完整 URL
                    elif chapter_url.startswith('//'):
                        chapter_url = 'https:' + chapter_url
                    elif chapter_url.startswith('/'):
                        chapter_url = QIDIAN_HOME + chapter_url
                    else:
                        chapter_url = QIDIAN_HOME + '/' + chapter_url
                    
                    # 从 URL 中提取 book_id 和 chapter_id
                    # 格式: /chapter/{book_id}/{chapter_id}/
                    match = re.search(r'/chapter/(\d+)/(\d+)/?', chapter_url)
                    if match:
                        chapter_id = match.group(2)
                        chapter_name = link.get_text(strip=True)
                        
                        if not chapter_name:
                            chapter_name = f"第 {len(self.chapters) + 1} 章"
                        
                        # 判断是否是 VIP 章节
                        parent = link.find_parent()
                        is_vip = False
                        if parent:
                            classes = parent.get('class', [])
                            is_vip = any('vip' in cls.lower() or 'lock' in cls.lower() for cls in classes)
                        
                        self.chapters.append({
                            'name': chapter_name,
                            'url': chapter_url,
                            'is_vip': is_vip
                        })
                        
                        # 每解析 5 个章节就稍微延迟一下，模拟真实阅读行为
                        if len(self.chapters) % 5 == 0:
                            time.sleep(random.uniform(0.5, 1.5))
            
            if self.chapters:
                print(f"[成功] Selenium 获取 {len(self.chapters)} 个章节")
                return True
            else:
                print("[警告] 解析失败，未找到任何有效的章节")
                return False
        
        except Exception as e:
            print(f"[错误] Selenium 爬取失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _get_chapters_via_api(self):
        """尝试通过 API 获取章节列表"""
        try:
            # 尝试从 www.qidian.com 的 API 获取
            api_urls = [
                f"https://www.qidian.com/ajax/book/ajaxGetChapterList?bookId={self.book_id}",
                f"https://www.qidian.com/chapter/chapterAjaxList?bookId={self.book_id}&pageIndex=0&pageSize=999",
            ]
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': self.book_url,
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            for api_url in api_urls:
                try:
                    response = request_with_retry(api_url, headers=headers, cookies=self.cookies)
                    if not response:
                        continue
                    
                    data = json.loads(response.text)
                    chapters = []
                    
                    # 尝试多种JSON结构
                    if isinstance(data, dict):
                        chapter_list = data.get('data', {}).get('list') or data.get('list') or data.get('chapters') or data.get('chapterList') or []
                        
                        if isinstance(chapter_list, list):
                            for item in chapter_list:
                                if isinstance(item, dict):
                                    chapter_name = item.get('chapterName') or item.get('name') or item.get('title', '').strip()
                                    chapter_id = item.get('chapterId') or item.get('id')
                                    is_vip = item.get('isVip', 0) == 1 or item.get('saleStatus', 0) == 1
                                    
                                    if chapter_name and chapter_id:
                                        chapter_url = f"{QIDIAN_HOME}/chapter/{chapter_id}/"
                                        chapters.append({
                                            'name': chapter_name,
                                            'url': chapter_url,
                                            'is_vip': is_vip
                                        })
                    
                    if chapters:
                        self.chapters = chapters
                        print(f"[成功] API 获取 {len(self.chapters)} 个章节")
                        return True
                        
                except (json.JSONDecodeError, KeyError, TypeError):
                    continue
            
            return False
                
        except Exception as e:
            print(f"[提示] API 获取失败: {str(e)}")
            return False

    def get_chapter_list(self):
        """获取章节列表（优先 Selenium，然后 API，最后静态爬虫）"""
        # 方案 1：首先尝试 Selenium（推荐，支持动态加载）
        if self.use_selenium and SELENIUM_AVAILABLE:
            if not self.driver:
                self._init_selenium()
            
            if self.driver:
                success = self._get_chapters_via_selenium()
                if success:
                    return True
                print("[降级] Selenium 失败，尝试其他方案...")
        
        # 方案 2：尝试 API（仅备用）
        if self._get_chapters_via_api():
            return True
        
        # 方案 3：静态 BeautifulSoup + HTML解析
        chapter_list_url = f"{self.book_url}/catalog"
        response = request_with_retry(chapter_list_url, cookies=self.cookies)
        
        if not response:
            print(f"[错误] 无法获取章节列表")
            return False
        
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 方法 1：直接查找 a 标签
            chapter_items = soup.select('li.e-item a, li a.j_chapterlist, li[class*="chapter"] a')
            
            # 方法 2：在 script 标签中寻找 JSON 数据
            if not chapter_items:
                script_tags = soup.find_all('script')
                for script in script_tags:
                    if script.string:
                        script_text = script.string
                        # 查找 JSON 数据
                        if 'chapterlist' in script_text.lower() or 'chapters' in script_text.lower():
                            # 尝试提取 JSON 部分
                            import re as regex
                            json_match = regex.search(r'(\{.*?chapterlist.*?\}|\[.*?\])', script_text, regex.DOTALL)
                            if json_match:
                                try:
                                    data = json.loads(json_match.group(1))
                                    if isinstance(data, dict):
                                        chapters = data.get('chapterlist', []) or data.get('chapters', [])
                                        if chapters:
                                            for ch in chapters:
                                                if isinstance(ch, dict):
                                                    chapter_name = ch.get('chapterName') or ch.get('name') or ch.get('title', '')
                                                    chapter_id = ch.get('chapterId') or ch.get('id')
                                                    is_vip = ch.get('isVip', 0) == 1 or ch.get('saleStatus', 0) == 1
                                                    
                                                    if chapter_name and chapter_id:
                                                        chapter_url = f"{QIDIAN_HOME}/chapter/{chapter_id}/"
                                                        self.chapters.append({
                                                            'name': chapter_name,
                                                            'url': chapter_url,
                                                            'is_vip': is_vip
                                                        })
                                    elif isinstance(data, list):
                                        for ch in data:
                                            if isinstance(ch, dict):
                                                chapter_name = ch.get('chapterName') or ch.get('name') or ch.get('title', '')
                                                chapter_id = ch.get('chapterId') or ch.get('id')
                                                is_vip = ch.get('isVip', 0) == 1 or ch.get('saleStatus', 0) == 1
                                                
                                                if chapter_name and chapter_id:
                                                    chapter_url = f"{QIDIAN_HOME}/chapter/{chapter_id}/"
                                                    self.chapters.append({
                                                        'name': chapter_name,
                                                        'url': chapter_url,
                                                        'is_vip': is_vip
                                                    })
                                    
                                    if self.chapters:
                                        print(f"[成功] 从 JavaScript 数据获取 {len(self.chapters)} 个章节")
                                        return True
                                except (json.JSONDecodeError, ValueError):
                                    pass
            
            # 方法 3：处理传统 HTML 链接
            if not self.chapters and chapter_items:
                for link in chapter_items:
                    chapter_name = link.get_text(strip=True)
                    chapter_url = link.get('href', '')
                    
                    if chapter_url and not chapter_url.startswith('http'):
                        chapter_url = QIDIAN_HOME + chapter_url
                    
                    # 判断是否是 VIP 章节
                    parent_li = link.find_parent('li')
                    is_vip = False
                    if parent_li:
                        is_vip = 'vip' in parent_li.get('class', []) or 'lock' in link.get('class', [])
                    
                    if chapter_url and chapter_name:
                        self.chapters.append({
                            'name': chapter_name,
                            'url': chapter_url,
                            'is_vip': is_vip
                        })
            
            if self.chapters:
                print(f"[成功] HTML 解析获取 {len(self.chapters)} 个章节")
                return True
            
            # 方案 3：最后尝试 Selenium
            if self.use_selenium and SELENIUM_AVAILABLE:
                if not self.driver:
                    self._init_selenium()
                
                if self.driver:
                    print("[提示] 切换到 Selenium 处理动态内容...")
                    success = self._get_chapters_via_selenium()
                    if success:
                        return True
            
            print("[警告] 未找到任何章节")
            return False
            
        except Exception as e:
            print(f"[错误] 解析章节列表失败: {str(e)}")
            return False
    
    def get_chapter_content(self, chapter):
        """获取单个章节内容"""
        response = request_with_retry(chapter['url'], cookies=self.cookies)
        if not response:
            return None
        
        try:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取章节内容（多种选择器以适应不同页面）
            content_divs = soup.select('#chapterContent, .chapter-content, .read-content, .j_chapterContent')
            if not content_divs:
                # 备用选择器
                content_div = soup.select_one('[id*="chapterContent"], [class*="content"]')
                if content_div:
                    content_divs = [content_div]
            
            if content_divs:
                content = content_divs[0].get_text('\n', strip=True)
                # 清理非正常文字
                content = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', content)
                return content
            
            return None
        except Exception as e:
            print(f"[错误] 解析章节内容失败: {str(e)}")
            return None
    
    def scrape(self, start_chapter=1, end_chapter=None, skip_vip=False, max_workers=6):
        """
        爬取小说（使用多线程并发爬取章节）
        :param start_chapter: 开始章节编号（1-based）
        :param end_chapter: 结束章节编号，None 表示全部
        :param skip_vip: 是否跳过 VIP 章节
        :param max_workers: 线程池大小（推荐 5-8，太多容易被检测）
        """
        if not self.get_book_info():
            return False
        
        if not self.get_chapter_list():
            # 如果静态爬虫失败但有 Selenium，提示用户
            if not self.use_selenium or not SELENIUM_AVAILABLE:
                print("\n[提示] 这本书可能需要 Selenium 支持以处理动态加载的章节列表")
                print("[解决办法] 运行以下命令安装依赖:")
                print("  pip install selenium webdriver-manager")
                print("然后再次运行爬虫")
            return False
        
        # 确定爬取范围
        total = len(self.chapters)
        end = min(end_chapter or total, total)
        start = max(1, start_chapter)
        
        if start > total:
            print(f"[错误] 起始章节超出范围 (最多 {total} 章)")
            return False
        
        print(f"\n[开始] 爬取第 {start} - {end} 章（共 {total} 章）")
        print(f"[信息] 使用 {max_workers} 个线程并发爬取")
        
        # 创建输出目录
        book_name = sanitize_filename(self.book_info.get('name', f'book_{self.book_id}'))
        output_path = f"{OUTPUT_DIR}/{book_name}"
        ensure_dir(output_path)
        
        # 准备待爬取的章节列表（跳过 VIP 章节）
        chapters_to_fetch = []
        for i in range(start-1, end):
            chapter = self.chapters[i]
            chapter_num = i + 1
            
            if skip_vip and chapter['is_vip']:
                print(f"[跳过] 第 {chapter_num} 章: {chapter['name']} (VIP)")
                continue
            
            chapters_to_fetch.append((chapter_num, chapter))
        
        # 使用线程池并发爬取
        contents_dict = {}
        failed_chapters = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_chapter = {
                executor.submit(self._fetch_chapter_safe, idx, chapter): (idx, chapter)
                for idx, chapter in chapters_to_fetch
            }
            
            # 按完成顺序处理结果
            completed = 0
            for future in as_completed(future_to_chapter):
                chapter_num, chapter = future_to_chapter[future]
                try:
                    content = future.result()
                    if content:
                        contents_dict[chapter_num] = f"\n\n# {chapter['name']}\n\n{content}"
                        print(f"[✓] 第 {chapter_num} 章: {chapter['name']}")
                    else:
                        failed_chapters.append(chapter_num)
                        print(f"[✗] 第 {chapter_num} 章: {chapter['name']} (内容为空)")
                        if chapter['is_vip']:
                            print(f"    这是 VIP 章节，需要有效的 VIP cookies")
                except Exception as e:
                    failed_chapters.append(chapter_num)
                    print(f"[✗] 第 {chapter_num} 章: {chapter['name']} (错误: {str(e)})")
                
                completed += 1
                if completed % 10 == 0:
                    print(f"[进度] {completed}/{len(chapters_to_fetch)} 章完成")
        
        # 按章节顺序拼接内容
        contents = []
        for i in range(start, end + 1):
            if i in contents_dict:
                contents.append(contents_dict[i])
        
        # 保存为文本文件
        if contents:
            full_content = f"# {book_name}\n\n作者: {self.book_info.get('author', '未知')}\n\n" + ''.join(contents)
            output_file = f"{output_path}/{book_name}.txt"
            save_to_file(output_file, full_content)
            print(f"\n[完成] 已保存到: {output_file}")
            if failed_chapters:
                print(f"[警告] {len(failed_chapters)} 章爬取失败: {failed_chapters[:10]}...")
            return True
        else:
            print("\n[失败] 未获取到任何内容")
            return False
    
    def _fetch_chapter_safe(self, chapter_num, chapter):
        """线程安全的章节爬取包装"""
        # 随机延迟，模拟真实用户
        time.sleep(random.uniform(0.5, 2))
        return self.get_chapter_content(chapter)
    
    def __del__(self):
        """清理 Selenium WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
