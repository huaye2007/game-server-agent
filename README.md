# 🎮 游戏服务器开发 AI Agent / Game Server Dev AI Agent

AI 自主探索项目代码，实时参考已有业务模块，生成符合项目规范的代码。
AI explores your project code, references existing modules, and generates code that follows your project conventions.

## 支持的模型 / Supported Models

| 提供商 / Provider | 默认模型 / Default | 其他可用 / Also Available |
|---|---|---|
| DeepSeek | deepseek-chat (V3.2) | deepseek-reasoner |
| OpenAI | gpt-5.4 | gpt-5.4-mini, gpt-5.4-nano, gpt-4.1, o3, o4-mini |
| Claude | claude-opus-4-6 | claude-sonnet-4-6, claude-haiku-4-5 |
| Gemini | gemini-3.1-pro-preview | gemini-3.1-flash-preview, gemini-2.5-pro, gemini-2.5-flash |
| GLM (智谱) | glm-5 | glm-5v-turbo, glm-4-plus, glm-4-flash |
| Kimi (月之暗面) | moonshot-v1-kimi-k2 (K2.5) | moonshot-v1-auto, moonshot-v1-128k |
| MiniMax | MiniMax-M2.7 | MiniMax-M2.7-highspeed, MiniMax-M2.5 |
| Custom | 任意 / Any | 兼容 OpenAI API 的服务 / Any OpenAI-compatible API |

## 安装 / Install

```bash
pip install -r requirements.txt

# 如果使用 Claude / If using Claude:
pip install anthropic
```

## 使用 / Usage

```bash
python main.py
```

```
/set_provider openai          # 切换提供商 / Switch provider
/set_key sk-your-api-key      # 设置 API Key
/set_project /path/to/server  # 设置项目目录
/set_lang en                  # 切换英文 / Switch to English
/providers                    # 查看所有提供商 / List all providers

# 自定义 API 地址 / Custom API endpoint:
/set_api_base https://your-proxy.com/v1
/set_model your-model-name
```

## 命令 / Commands

| 命令 / Command | 说明 / Description |
|---|---|
| `/set_provider <name>` | 切换提供商 / Switch provider |
| `/set_key <key>` | 设置 API Key |
| `/set_model <model>` | 设置模型 / Set model |
| `/set_api_base <url>` | 自定义 API 地址 / Custom API URL |
| `/set_project <path>` | 设置项目目录 / Set project directory |
| `/set_proto <path>` | 设置协议文件目录 / Set .proto directory |
| `/set_excel <path>` | 设置配置表目录 / Set Excel config directory |
| `/set_lang <zh\|en>` | 切换语言 / Switch language |
| `/providers` | 查看提供商列表 / List providers |
| `/config` | 查看配置 / Show config |
| `/clear` | 清空对话 / Clear conversation |
| `/quit` | 退出 / Quit |
