# 快速开始指南

## 最简洁的使用方式

### 方式 1：直接用书ID爬取（推荐 - 最稳定）

```bash
# 爬取全部章节
python main.py -i 1004608

# 爬取第1-50章
python main.py -i 1004608 -s 1 -e 50

# 跳过VIP章节（只要免费部分）
python main.py -i 1004608 --skip-vip
```

**常见书ID参考：**
- 1004608 - 我是至尊
- 1010154 - 剑来
- 1006485 - 一念永恒
- 1003954 - 儒道至圣
- 1013088 - 诡秘之主

### 方式 2：按书名搜索

```bash
# 搜索《我是至尊》
python main.py "我是至尊"

# 会列出搜索结果，选择要爬的那一本
```

**注意**：搜索功能需要网络正常，如果网络有限制可以使用"方式1"。

## 完整使用示例

### 例1：快速爬取一本书

```bash
# 使用书ID，爬取全部章节
python main.py 1004608
```

### 例2：爬取指定章节范围

```bash
# 爬取第1-100章
python main.py -i 1004608 -s 1 -e 100
```

### 例3：爬取免费章节（跳过VIP）

```bash
# 某些书的后面章节是VIP，用这个命令只爬免费部分
python main.py -i 1004608 --skip-vip
```

### 例4：自定义VIP Cookies爬取全部章节

```bash
# 如果你有起点VIP账号，可以爬取VIP章节
python main.py -i 1004608 --cookies "qd_VK=xxx; qd_token=yyy"
```

## 获取书ID的方法

### 方法1：从起点网站URL中提取

在浏览器打开起点网站，找到你要爬的书，URL 格式为：
```
https://www.qidian.com/book/1004608
                                ^^^^^^^^
                                这就是书ID
```

### 方法2：从搜索功能获得

```bash
python main.py "我是至尊"
# 程序会列出搜索结果，显示书ID
```

## 获取VIP Cookies 的方法（爬取VIP章节）

如果你是起点VIP会员，可以按以下步骤获取cookies 来爬取付费章节：

1. **登录起点网站**
   - 在浏览器打开 https://www.qidian.com
   - 登录你的VIP账号

2. **打开开发者工具**
   - 按 `F12` 或 `Ctrl+Shift+I`
   - 切换到 **Network** 标签

3. **刷新页面并查找请求**
   - 按 `Ctrl+R` 或 `F5` 刷新
   - 在 Network 中找任意一个请求（如 HTML 或 JS 文件）

4. **复制 Cookie**
   - 点击那个请求
   - 在右侧找 **Request Headers**
   - 找到 **Cookie** 字段，复制整个内容

5. **使用 Cookie 爬取**

方法A：修改 config.py（永久）
```python
# 打开 qidian_scraper/config.py，找到这一行：
VIP_COOKIES = os.getenv('QD_COOKIES', '')

# 改为：
VIP_COOKIES = "粘贴你的cookie字符串"
```

方法B：使用命令行参数（临时）
```bash
python main.py -i 1004608 --cookies "粘贴你的cookie字符串"
```

## 爬虫输出在哪里

爬取完成后，小说会保存在：
```
./novels/<书名>/<书名>.txt
```

例如：
```
./novels/我是至尊/我是至尊.txt
./novels/剑来/剑来.txt
```

## 常见问题排查

### Q: 显示 "无法连接到服务器"

**A:** 这是网络问题，可能原因：
- 网络连接不稳定
- 需要使用代理/VPN
- 起点网站临时无法访问

**解决办法：**
1. 检查网络连接
2. 尝试用浏览器直接访问 https://www.qidian.com 确认是否可用
3. 如果需要代理，修改 `config.py` 中的 `PROXY` 设置

### Q: 显示 "未找到相关书籍"

**A:** 说明搜索功能无法工作，但你可以直接用书ID：

```bash
# 用书ID代替书名，避免搜索
python main.py 1004608
```

### Q: 爬取速度很慢

**A:** 这是正常的，程序每章之间设置了1-2秒延迟以避免被封IP。如果想加快，可以在 `scraper.py` 中修改延迟时间（但不建议太短，容易被封）。

### Q: VIP章节显示为空或乱码

**A:** 说明 cookies 过期或无效，需要：
1. 重新登录起点网站
2. 重新复制最新的 cookies
3. 按上面的 "获取VIP Cookies" 步骤更新

### Q: 某个章节爬取失败

**A:** 这很正常，可能是：
- 网络超时
- 起点网站的反爬虫机制
- VIP章节需要 cookies

可以重新运行爬虫，会自动重试。

## 进阶选项

```bash
python main.py --help
```

这会显示所有可用的命令行选项。

## 配置文件说明

**config.py** 中的主要配置项：

```python
# VIP cookies（用于爬取付费章节）
VIP_COOKIES = ""

# 代理设置（如需翻墙，改为你的代理地址）
PROXY = ""

# 输出目录
OUTPUT_DIR = "./novels"

# 请求超时时间（秒）
TIMEOUT = 10

# 重试次数
RETRY_TIMES = 3
```

## 下一步

- 修改 `config.py` 配置你的 cookies 和代理
- 运行 `python main.py -i 1004608` 开始爬取
- 在 `./novels` 目录中查看爬取结果

有问题? 查看 README.md 或检查输出的错误信息。
