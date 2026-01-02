# 起点中文网爬虫 - 简洁版

一个轻量级、易操作的起点小说爬虫，支持按书名或书ID爬取全部章节（包括VIP章节）。

## 特点

- **简单易用**：仅依赖 `requests` 和 `beautifulsoup4` 两个库
- **灵活查询**：支持书名搜索和直接书ID查询
- **完整爬取**：可爬取全部章节，包括VIP付费内容
- **容错机制**：带重试、超时控制和代理支持
- **命令行友好**：丰富的命令行选项，支持指定章节范围

## 安装

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 VIP 访问（可选）

如需爬取 VIP 章节，需要添加有效的起点账号 cookies：

**方法一：修改 `config.py`**
```python
# 在 config.py 中找到 VIP_COOKIES 变量，粘贴你的 cookies
VIP_COOKIES = "你的cookie字符串"
```

**方法二：环境变量**
```bash
# Windows PowerShell
$env:QD_COOKIES = "你的cookie字符串"

# Linux/Mac
export QD_COOKIES="你的cookie字符串"
```

**获取 cookies 步骤：**
1. 在浏览器中登录 https://www.qidian.com
2. 按 `F12` 打开开发者工具
3. 切换到 **Network** 标签
4. 刷新页面
5. 找到任意请求（如 HTML），在 **Request Headers** 中复制 **Cookie** 字段内容
6. 粘贴到上述位置

### 3. 配置代理（可选）

如果使用 Clash 等 VPN 代理，可在 `config.py` 设置：

```python
# config.py
PROXY = "http://127.0.0.1:7890"  # 改为你的代理地址
```

或通过环境变量：
```bash
set QD_PROXY=http://127.0.0.1:7890
# 或
export QD_PROXY=http://127.0.0.1:7890
```

## 使用

### 基础用法

**按书名搜索并爬取：**
```bash
python main.py "我是至尊"
```
程序会列出搜索结果，你选择对应的书籍。

**按书ID直接爬取：**
```bash
python main.py 1004608
```
或：
```bash
python main.py -i 1004608
```

### 进阶用法

**爬取指定章节范围（如第1-50章）：**
```bash
python main.py -i 1004608 -s 1 -e 50
```

**跳过VIP章节（只爬取免费部分）：**
```bash
python main.py -i 1004608 --skip-vip
```

**使用自定义 cookies（不修改 config.py）：**
```bash
python main.py -i 1004608 --cookies "qd_VK=xxx; qd_token=yyy"
```

**查看所有选项：**
```bash
python main.py --help
```

## 完整命令示例

```bash
# 搜索《我是至尊》并爬取全部章节
python main.py "我是至尊"

# 使用书ID 1004608，爬取第1-100章
python main.py -i 1004608 -s 1 -e 100

# 爬取全部章节，但跳过VIP（免费章节）
python main.py -i 1004608 --skip-vip

# 使用代理和自定义cookies爬取
set QD_PROXY=http://127.0.0.1:7890
python main.py -i 1004608 --cookies "qd_VK=abc; qd_token=xyz"
```

## 输出文件

爬取完成后，小说内容保存在 `./novels/<书名>/<书名>.txt`：

```
./novels/
└── 我是至尊/
    └── 我是至尊.txt
```

文件为纯文本格式，内容包括：
- 书名、作者
- 各章节标题和内容
- 换行清晰，便于阅读或导入电子书

## 常见问题

### Q: 爬取速度很慢

**A:** 这是正常的，程序在每个章节之间设置了 1-2 秒延迟以避免被封 IP。如需加快，可修改 `scraper.py` 中的延迟时间（但不建议太短）。

### Q: VIP 章节显示为乱码或内容为空

**A:** 说明 cookies 无效或过期，需要：
1. 重新登录起点网站
2. 重新复制最新的 cookies
3. 更新到 `config.py` 或通过 `--cookies` 参数传入

### Q: 无法连接到网站（Connection refused）

**A:** 可能原因：
1. 网络连接问题 — 检查网络或尝试切换 WiFi
2. 被起点网站封 IP — 等待 30 分钟后重试
3. 需要代理 — 配置 `config.py` 中的 `PROXY` 或 `QD_PROXY` 环境变量

### Q: 搜索结果为空

**A:** 可能原因：
1. 书名拼写错误 — 尝试用更简洁的关键词
2. 网络问题 — 检查连接
3. 搜索 API 变化 — 更新代码（联系开发者）

## 文件结构

```
qidian_scraper/
├── main.py          # 主程序入口
├── config.py        # 配置文件（设置 cookies、代理等）
├── scraper.py       # 爬虫核心逻辑
├── search.py        # 书籍搜索功能
├── utils.py         # 工具函数
├── requirements.txt # 依赖
└── README.md        # 本文件
```

## 更新日志

### v1.0
- 初版发布
- 支持书名搜索和书ID查询
- 支持VIP章节爬取
- 支持代理和自定义headers

## 免责声明

本项目仅供学习和研究使用，不得用于商业用途。用户需自行承担使用本工具造成的任何后果。

请尊重网站版权和内容创作者的权益，合理使用爬虫功能。

## License

MIT
