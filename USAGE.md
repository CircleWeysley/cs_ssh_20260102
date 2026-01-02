# 起点爬虫项目 - 使用说明

## 📁 项目结构

```
qidian_scraper/
├── main.py              ← 主程序（运行这个）
├── batch_scrape.py      ← 批量爬虫（爬多本书）
├── config.py            ← 配置文件（设置 cookies、代理等）
├── scraper.py           ← 爬虫核心逻辑
├── search.py            ← 搜索功能（书名→书ID）
├── utils.py             ← 工具函数
├── requirements.txt     ← 项目依赖
├── README.md            ← 详细说明（英文风格）
├── QUICKSTART.md        ← 快速开始指南（推荐先看）
└── novels/              ← 爬取结果保存目录（自动创建）
    ├── 我是至尊/
    │   └── 我是至尊.txt
    └── ...
```

## 🚀 快速开始（三步）

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行爬虫

**方式A：用书ID直接爬（推荐）**
```bash
python main.py 1004608
```

**方式B：按书名搜索**
```bash
python main.py "我是至尊"
```

### 3. 在 `novels/` 目录中查看结果

爬取完成后，小说被保存为纯文本文件。

## 💡 常用命令

| 命令 | 说明 |
|------|------|
| `python main.py 1004608` | 用书ID爬全部 |
| `python main.py 1004608 -s 1 -e 50` | 爬第1-50章 |
| `python main.py 1004608 --skip-vip` | 只爬免费章节 |
| `python main.py "我是至尊"` | 按书名搜索 |
| `python batch_scrape.py` | 批量爬多本书 |
| `python main.py --help` | 显示全部选项 |

## 🔑 常见书ID参考

| 书名 | ID |
|------|-----|
| 我是至尊 | 1004608 |
| 剑来 | 1010154 |
| 一念永恒 | 1006485 |
| 儒道至圣 | 1003954 |
| 诡秘之主 | 1013088 |

或从URL中获取：`https://www.qidian.com/book/1004608` → `1004608`

## 📖 详细文档

- **快速指南**：查看 [QUICKSTART.md](QUICKSTART.md)
- **完整说明**：查看 [README.md](README.md)
- **帮助信息**：`python main.py --help`

## ⚙️ 配置说明

编辑 `config.py` 可配置：

```python
# VIP 章节 cookies（爬取付费内容）
VIP_COOKIES = "粘贴你的cookie"

# 代理（如需翻墙）
PROXY = "http://127.0.0.1:7890"

# 其他设置
OUTPUT_DIR = "./novels"      # 输出目录
TIMEOUT = 10                 # 请求超时
RETRY_TIMES = 3              # 重试次数
```

## 🎯 批量爬虫使用

编辑 `batch_scrape.py` 中的 `BOOKS_TO_SCRAPE` 列表，然后运行：

```bash
python batch_scrape.py
```

示例配置：
```python
BOOKS_TO_SCRAPE = [
    {'id': '1004608', 'name': '我是至尊', 'start': 1, 'end': 100},
    {'id': '1010154', 'name': '剑来', 'start': 1, 'end': None},
]
```

## ❓ 常见问题

**Q: 怎样获取书ID？**
- 在起点网站找到书，从URL提取：`www.qidian.com/book/1004608`
- 或运行 `python main.py "书名"` 搜索

**Q: 怎样爬取VIP章节？**
- 登录起点网站 → F12 → Network → 复制 Cookie
- 粘贴到 `config.py` 的 `VIP_COOKIES`

**Q: 网络不稳定怎么办？**
- 检查网络连接
- 修改 `config.py` 的 `PROXY` 配置代理
- 增加 `RETRY_TIMES` 和 `TIMEOUT` 的值

**Q: 爬取很慢？**
- 这是正常的（避免被封IP）
- 可修改 `scraper.py` 中的延迟时间

## 📝 输出格式

爬取的文件为纯文本格式，内容包括：
- 书名、作者
- 各章节标题和内容
- 可直接阅读或导入电子书工具

示例：
```
# 我是至尊

作者: 狐尾的笔

# 第1章 重生

章节内容...

# 第2章 初入

章节内容...
```

## ⚡ 性能提示

- 每本书的爬取时间取决于章节数和网络速度（通常 1-2 分钟/100章）
- 避免频繁爬取同一本书，容易被起点网站临时封IP
- 建议在非高峰时间爬取

## 📌 注意事项

- 本工具仅供学习研究之用
- 请尊重网站版权和内容创作者
- 不得用于商业目的
- 频繁爬取可能被网站封IP，请合理使用

## 🐛 问题反馈

遇到问题：
1. 查看输出的错误信息
2. 检查网络连接和配置
3. 尝试增加重试次数或超时时间
4. 重新运行脚本

---

**祝你使用愉快！** 🎉
