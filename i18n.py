"""国际化支持 / Internationalization support"""

# 当前语言 / Current language
_current_lang = "zh"

TEXTS = {
    # === Banner ===
    "banner_title": {
        "zh": "🎮 游戏服务器开发 AI Agent",
        "en": "🎮 Game Server Dev AI Agent",
    },
    "banner_desc": {
        "zh": "AI 自主探索项目代码，实时参考生成业务代码",
        "en": "AI explores your project code and generates business logic",
    },
    "banner_sub": {
        "zh": "支持协议文件(.proto)、配置表(Excel)、数据库表、业务代码生成",
        "en": "Supports .proto files, Excel configs, DB tables, and code generation",
    },

    # === Help table ===
    "help_title": {
        "zh": "可用命令",
        "en": "Available Commands",
    },
    "help_col_cmd": {"zh": "命令", "en": "Command"},
    "help_col_desc": {"zh": "说明", "en": "Description"},
    "cmd_set_project": {"zh": "设置项目代码目录", "en": "Set project code directory"},
    "cmd_set_proto": {"zh": "设置协议文件(.proto)目录", "en": "Set .proto file directory"},
    "cmd_set_excel": {"zh": "设置配置表(Excel)目录", "en": "Set Excel config directory"},
    "cmd_set_key": {"zh": "设置 API Key", "en": "Set API Key"},
    "cmd_set_provider": {"zh": "切换模型提供商", "en": "Switch model provider"},
    "cmd_set_model": {"zh": "设置模型名称", "en": "Set model name"},
    "cmd_set_api_base": {"zh": "自定义 API 地址", "en": "Set custom API base URL"},
    "cmd_set_lang": {"zh": "切换语言 (zh/en)", "en": "Switch language (zh/en)"},
    "cmd_providers": {"zh": "查看支持的提供商列表", "en": "List supported providers"},
    "cmd_clear": {"zh": "清空对话历史", "en": "Clear conversation history"},
    "cmd_config": {"zh": "查看当前配置", "en": "Show current config"},
    "cmd_help": {"zh": "显示帮助", "en": "Show help"},
    "cmd_quit": {"zh": "退出", "en": "Quit"},
    "cmd_free_input": {"zh": "提需求，AI自动探索并生成代码", "en": "Describe your needs, AI explores and generates code"},

    # === Messages ===
    "goodbye": {"zh": "再见！", "en": "Goodbye!"},
    "unknown_cmd": {"zh": "未知命令: {cmd}，输入 /help 查看帮助", "en": "Unknown command: {cmd}, type /help for help"},
    "set_path_usage": {"zh": "用法: /set_{key} <路径>", "en": "Usage: /set_{key} <path>"},
    "path_set_ok": {"zh": "{label}已设置: {path}", "en": "{label} set to: {path}"},
    "path_not_exist": {"zh": "目录不存在: {path}", "en": "Directory not found: {path}"},
    "set_key_usage": {"zh": "用法: /set_key <API Key>", "en": "Usage: /set_key <API Key>"},
    "key_set_ok": {"zh": "API Key 已设置", "en": "API Key set"},
    "current_model": {"zh": "当前模型: {model}", "en": "Current model: {model}"},
    "model_set_ok": {"zh": "模型已设置: {model}", "en": "Model set to: {model}"},
    "history_cleared": {"zh": "对话历史已清空", "en": "Conversation history cleared"},
    "api_key_not_set": {"zh": "请先设置 API Key: /set_key <your_key>", "en": "Please set API Key first: /set_key <your_key>"},
    "project_not_set": {"zh": "请先设置项目目录: /set_project <路径>", "en": "Please set project directory first: /set_project <path>"},
    "project_not_exist": {"zh": "项目目录不存在: {path}", "en": "Project directory not found: {path}"},
    "api_key_display": {"zh": "(未设置)", "en": "(not set)"},
    "lang_set_ok": {"zh": "语言已切换为: 中文", "en": "Language switched to: English"},
    "lang_invalid": {"zh": "不支持的语言: {lang}，可选: zh, en", "en": "Unsupported language: {lang}, options: zh, en"},
    "provider_set_ok": {
        "zh": "已切换到 {provider}，API: {api_base}，模型: {model}",
        "en": "Switched to {provider}, API: {api_base}, model: {model}",
    },
    "provider_invalid": {
        "zh": "未知提供商: {provider}，输入 /providers 查看支持列表",
        "en": "Unknown provider: {provider}, type /providers to see supported list",
    },
    "provider_set_usage": {
        "zh": "用法: /set_provider <提供商名>，输入 /providers 查看列表",
        "en": "Usage: /set_provider <name>, type /providers to see list",
    },
    "provider_need_key": {
        "zh": "请设置 {provider} 的 API Key: /set_key <your_key>",
        "en": "Please set {provider} API Key: /set_key <your_key>",
    },
    "providers_title": {"zh": "支持的模型提供商", "en": "Supported Providers"},
    "providers_col_name": {"zh": "名称", "en": "Name"},
    "providers_col_api": {"zh": "API 地址", "en": "API Base"},
    "providers_col_models": {"zh": "可用模型", "en": "Available Models"},
    "providers_col_current": {"zh": "当前", "en": "Current"},
    "api_base_set_ok": {"zh": "API 地址已设置: {url}", "en": "API base URL set to: {url}"},
    "api_base_usage": {"zh": "用法: /set_api_base <URL>", "en": "Usage: /set_api_base <URL>"},
    "current_provider": {"zh": "当前提供商: {provider}", "en": "Current provider: {provider}"},
    "claude_hint": {
        "zh": "[dim]提示: Claude 使用 Anthropic 原生 API，需安装 anthropic 包: pip install anthropic[/dim]",
        "en": "[dim]Hint: Claude uses Anthropic native API, install: pip install anthropic[/dim]",
    },

    # === Labels for /set_* ===
    "label_project": {"zh": "项目目录", "en": "Project directory"},
    "label_proto": {"zh": "协议文件目录", "en": "Proto directory"},
    "label_excel": {"zh": "配置表目录", "en": "Excel config directory"},

    # === Agent messages ===
    "thinking": {"zh": "🤔 AI 思考中... (轮次 {turn}/{max})", "en": "🤔 AI thinking... (turn {turn}/{max})"},
    "api_error": {"zh": "❌ API调用失败: {err}", "en": "❌ API call failed: {err}"},
    "tool_done": {"zh": "✅ {label} 完成 ({lines} 行)", "en": "✅ {label} done ({lines} lines)"},
    "elapsed": {"zh": "⏱ 共 {turns} 轮，耗时 {time:.1f}s", "en": "⏱ {turns} turns, {time:.1f}s elapsed"},
    "max_turns_reached": {
        "zh": "⚠️ 达到最大轮次限制 ({max} 轮，耗时 {time:.1f}s)",
        "en": "⚠️ Max turns reached ({max} turns, {time:.1f}s elapsed)",
    },
    "memory_loaded": {"zh": "已加载项目记忆 ({size} 字符)", "en": "Project memory loaded ({size} chars)"},
    "parse_error": {"zh": "参数解析失败", "en": "Failed to parse arguments"},
    "unknown_tool": {"zh": "未知工具: {name}", "en": "Unknown tool: {name}"},
    "tool_exec_error": {"zh": "工具执行失败: {err}", "en": "Tool execution failed: {err}"},

    # === Tool labels ===
    "tool_list_dir": {"zh": "📂 浏览项目目录", "en": "📂 Browse project directory"},
    "tool_read_file": {"zh": "📄 读取文件", "en": "📄 Read file"},
    "tool_search_files": {"zh": "🔍 搜索文件", "en": "🔍 Search files"},
    "tool_grep_search": {"zh": "🔎 搜索代码内容", "en": "🔎 Search code content"},
    "tool_write_file": {"zh": "✏️  写入文件", "en": "✏️  Write file"},
    "tool_list_proto_dir": {"zh": "📂 浏览协议目录", "en": "📂 Browse proto directory"},
    "tool_read_proto_file": {"zh": "📄 读取协议文件", "en": "📄 Read proto file"},
    "tool_list_excel_dir": {"zh": "📂 浏览配置表目录", "en": "📂 Browse Excel directory"},
    "tool_read_excel_meta": {"zh": "📊 读取配置表结构", "en": "📊 Read Excel metadata"},
    "tool_write_excel": {"zh": "📊 写入配置表", "en": "📊 Write Excel"},
    "tool_memory_read": {"zh": "🧠 读取记忆", "en": "🧠 Read memory"},
    "tool_memory_append": {"zh": "🧠 写入记忆", "en": "🧠 Write memory"},

    # === Tools.py messages ===
    "dir_not_exist": {"zh": "目录不存在: {path}", "en": "Directory not found: {path}"},
    "empty_dir": {"zh": "空目录", "en": "Empty directory"},
    "file_not_exist": {"zh": "文件不存在: {path}", "en": "File not found: {path}"},
    "not_a_file": {"zh": "不是文件: {path}", "en": "Not a file: {path}"},
    "lines_omitted": {"zh": "... [省略 {count} 行] ...", "en": "... [{count} lines omitted] ..."},
    "read_error": {"zh": "读取失败: {err}", "en": "Read failed: {err}"},
    "no_match_files": {"zh": "未找到匹配文件", "en": "No matching files found"},
    "results_truncated": {"zh": "... 结果过多，已截断", "en": "... too many results, truncated"},
    "no_match_content": {"zh": "未找到匹配内容", "en": "No matching content found"},
    "file_written": {"zh": "文件已写入: {path}", "en": "File written: {path}"},
    "write_error": {"zh": "写入失败: {err}", "en": "Write failed: {err}"},
    "proto_not_set": {"zh": "协议文件目录未设置，请使用 /set_proto <路径> 设置", "en": "Proto directory not set, use /set_proto <path>"},
    "proto_dir_not_exist": {"zh": "协议目录不存在: {path}", "en": "Proto directory not found: {path}"},
    "proto_not_set_short": {"zh": "协议文件目录未设置", "en": "Proto directory not set"},
    "excel_not_set": {"zh": "配置表目录未设置，请使用 /set_excel <路径> 设置", "en": "Excel directory not set, use /set_excel <path>"},
    "excel_dir_not_exist": {"zh": "配置表目录不存在: {path}", "en": "Excel directory not found: {path}"},
    "excel_not_set_short": {"zh": "配置表目录未设置", "en": "Excel directory not set"},
    "need_openpyxl": {"zh": "需要安装 openpyxl: pip install openpyxl", "en": "openpyxl required: pip install openpyxl"},
    "excel_written": {"zh": "Excel已写入: {path}", "en": "Excel written: {path}"},
    "memory_not_exist": {"zh": "记忆文件不存在，尚无持久记忆。", "en": "Memory file not found, no persistent memory yet."},
    "memory_written": {"zh": "已写入记忆文件", "en": "Memory file updated"},
}


def set_lang(lang: str) -> bool:
    """设置当前语言 / Set current language"""
    global _current_lang
    if lang in ("zh", "en"):
        _current_lang = lang
        return True
    return False


def get_lang() -> str:
    return _current_lang


def t(key: str, **kwargs) -> str:
    """获取翻译文本 / Get translated text"""
    entry = TEXTS.get(key)
    if not entry:
        return key
    text = entry.get(_current_lang, entry.get("zh", key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text
