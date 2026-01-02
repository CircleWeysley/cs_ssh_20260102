# 配置文件
import os

# 请求配置
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Referer': 'https://www.qidian.com/',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
}

# VIP 章节访问所需的 cookies（需要自己手动添加）
# 方法：登录起点网站后，F12 开发者工具 → Network → 复制 Cookie 字符串
# 粘贴格式：直接粘贴整个 Cookie 值（多行自动合并）
VIP_COOKIES = os.getenv('QD_COOKIES', (
    'x-waf-captcha-referer=; '
    'newstatisticUUID=1767328786_1925956967; '
    '_csrfToken=aTQWQGbVhXlN52mfORIMqieO47FB1i7Yuqx4pkid; '
    'traffic_utm_referer=; '
    'Hm_lvt_f00f67093ce2f38f215010b699629083=1767328787; '
    'Hm_lpvt_f00f67093ce2f38f215010b699629083=1767328787; '
    'HMACCOUNT=9CADC138BE70FB7A; '
    'fu=1959872071; '
    'e1=%7B%22l6%22%3A%22%22%2C%22l7%22%3A%22%22%2C%22l1%22%3A3%2C%22l3%22%3A%22%22%2C%22pid%22%3A%22qd_p_qidian%22%2C%22eid%22%3A%22qd_A1001%22%7D; '
    'e2=%7B%22l6%22%3A%22%22%2C%22l7%22%3A%22%22%2C%22pid%22%3A%22qd_p_qidian%22%2C%22eid%22%3A%22qd_A1008%22%2C%22l1%22%3A3%7D; '
    'w_tsfp=ltvuV0MF2utBvS0Q763qlkOpHzAjdjA4h0wpEaR0f5thQLErU5mD1oV4tsP0NHTf5sxnvd7DsZoyJTLYCJI3dwMcR8iVcNsWjA6YkdMtjttCCUNkFpLZUVQXIOkhujQQenhCNxS00jA8eIUd379yilkMsyN1zap3TO14fstJ019E6KDQmI5uDW3HlFWQRzaLbjcMcuqPr6g18L5a5TfU4gmof1ghVr4Q2EzG0SEdCHt25BfoIu1bME74JceuSqA='
))

# 代理配置（可选）
# 若需要走 Clash 等代理，设置为 "http://127.0.0.1:7890" 或 "socks5://127.0.0.1:7891"
PROXY = os.getenv('QD_PROXY', '')

# 保存配置
OUTPUT_DIR = "./novels"  # 小说保存目录
TIMEOUT = 60  # 请求超时（秒）
RETRY_TIMES = 3  # 重试次数
RETRY_DELAY = 2  # 重试间隔（秒）

# API 及页面配置
QIDIAN_HOME = "https://www.qidian.com"
SEARCH_API = "https://search.qidian.com/api/SearchKey/GetSearchKeywordList"
CHAPTER_API_PATTERN = "https://api.qidian.com/api/Novel/chapter"  # 用于获取目录

# 代理字典（供 requests 使用）
PROXIES = {}
if PROXY:
    PROXIES = {
        'http': PROXY,
        'https': PROXY
    }
