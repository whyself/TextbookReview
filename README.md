# Textbook Review Agent 📚🔍

> 基于 LangGraph 与 TextIn 智能解析的教材申报材料自动化审核系统。

## ✨ 项目简介

**Textbook Review Agent** 是一个专为教材申报审核场景设计的自动化工具。它利用大语言模型（LLM）的推理能力结合 TextIn 的文档解析技术，能够自动读取、理解并核对大量的教材申报材料。

系统可以自动遍历指定目录下的申报文件夹，提取“申报书”、“版权页”、“CIP数据”中的关键信息（如书名、ISBN、版次、时间等），进行交叉比对，并将最终的审核结论及不一致原因自动填入 Excel 表格。

## 🚀 核心功能

*   **多模态文档理解**：支持处理 PDF、Word (.docx)、JPG/PNG 图片等多种格式的申报材料。
*   **智能信息提取**：
    *   **结构化提取**：精准提取申报书中的几十项关键字段。
    *   **非结构化解析**：自动阅读版权页和 CIP 数据截图，捕捉细微的版次和时间信息。
*   **自动逻辑一致性校验**：
    *   核对申报书与版权页的出版时间是否一致。
    *   核对版次、ISBN、主编姓名等关键信息是否匹配。
*   **自动化报表**：审核结果实时写入 Excel，支持断点续传（自动跳过已存在的列）。
*   **鲁棒的 Agent 架构**：基于 **LangGraph** 构建，具备错误重试和自我修正能力。

## 🛠️ 技术栈

*   **LLM Orchestration**: [LangChain](https://www.langchain.com/) / [LangGraph](https://langchain-ai.github.io/langgraph/)
*   **Document Intelligence**: [TextIn API](https://www.textin.com/) (合合信息)
*   **Python Runtime Manager**: [uv](https://github.com/astral-sh/uv)
*   **Data Processing**: Pandas, OpenPyXL

## 🏁 快速开始

### 1. 环境准备

本项目推荐使用 **[uv](https://github.com/astral-sh/uv)** 进行极速环境管理（无需手动安装 Python）。

**安装 uv (Windows PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. 获取代码

```bash
git clone https://github.com/yourusername/TextbookReview.git
cd TextbookReview
```

### 3. 配置 API 密钥

在项目根目录下创建一个 `.env` 文件，并填入以下配置：

```ini
# LLM 模型配置 (支持 OpenAI 格式，推荐使用 Qwen/DeepSeek 等)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
MODEL_NAME=qwen-max

# TextIn 文档解析配置
TEXTIN_APP_ID=xxxxxxxx
TEXTIN_SECRET_CODE=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 4. 准备数据

请将待审核的教材文件夹放入 `data` 目录中。结构如下：

```text
data/
├── 运筹学/
│   ├── 申报书.docx
│   ├── 版权页.pdf
│   └── CIP数据.jpg
├── 另一个教材/
│   └── ...
```

### 5. 运行程序

**方式一：使用 uv (推荐)**
```powershell
uv run main.py
```
*(系统会自动安装 Python 环境和所有依赖包)*

**方式二：Windows 用户一键运行**
直接双击根目录下的 `run.bat` 脚本。

## 📂 项目结构

```text
TextbookReview/
├── data/                    # [忽略] 存放申报材料输入
├── src/
│   ├── agents/
│   │   └── review_agent.py  # Agent 核心编排逻辑 (LangGraph)
│   ├── tools/
│   │   ├── textin_tool.py   # TextIn API 封装 (OCR & Parsing)
│   │   ├── excel_tool.py    # Excel 读写工具
│   │   └── update_task.py   # 状态反馈工具
│   └── utils/               # 通用工具函数
├── main.py                  # 程序入口
├── pyproject.toml           # 项目依赖定义
├── review_results.xlsx      # [自动生成] 审核结果输出
└── run.bat                  # 快捷运行脚本
```

## 📄 License

MIT License
