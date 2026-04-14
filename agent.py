"""AI Agent - 支持多模型提供商的 agentic loop"""
import json
import time
from openai import OpenAI
from rich.console import Console
from config import PROVIDERS
from i18n import t, get_lang
from tools import (
    TOOL_DEFINITIONS, list_dir, read_file, search_files, grep_search,
    write_file, list_proto_dir, read_proto_file,
    list_excel_dir, read_excel_meta, write_excel,
    memory_read, memory_append, load_memory,
)

console = Console()

TOOL_HANDLERS = {
    "list_dir": list_dir,
    "read_file": read_file,
    "search_files": search_files,
    "grep_search": grep_search,
    "write_file": write_file,
    "list_proto_dir": list_proto_dir,
    "read_proto_file": read_proto_file,
    "list_excel_dir": list_excel_dir,
    "read_excel_meta": read_excel_meta,
    "write_excel": write_excel,
    "memory_read": memory_read,
    "memory_append": memory_append,
}

TOOL_LABEL_KEYS = {
    "list_dir": "tool_list_dir",
    "read_file": "tool_read_file",
    "search_files": "tool_search_files",
    "grep_search": "tool_grep_search",
    "write_file": "tool_write_file",
    "list_proto_dir": "tool_list_proto_dir",
    "read_proto_file": "tool_read_proto_file",
    "list_excel_dir": "tool_list_excel_dir",
    "read_excel_meta": "tool_read_excel_meta",
    "write_excel": "tool_write_excel",
    "memory_read": "tool_memory_read",
    "memory_append": "tool_memory_append",
}

SYSTEM_PROMPT_ZH = """你是一个资深游戏服务器开发专家。你可以通过工具浏览和搜索项目代码、协议文件和配置表。

## 重要：判断用户意图

收到用户消息后，先判断是否属于"游戏服务器业务开发需求"（如：实现某个游戏功能、新增业务模块、设计协议/配置表/数据库表等）。

- 如果是业务开发需求 → 执行下面的"工作流程"
- 如果不是（如：闲聊、问技术问题、问项目结构、让你读代码解释、代码review、bug排查等）→ 直接正常回答，不要走需求分析流程

## 工作流程（仅用于游戏服务器业务开发需求，严格按顺序执行）

### 第一阶段：需求确认
当用户提出业务需求时：
1. 如果需求描述不够清晰，主动向用户提问，确认细节
2. 生成一份【需求确认清单】，包含：
   - 功能点列表（每个功能点编号）
   - 涉及的数据结构/字段
   - 客户端-服务端交互流程
   - 需要的配置表及字段说明
   - 数据库表设计
3. 让用户逐项确认，有修改意见就调整，直到用户说"确认"或"没问题"

### 第二阶段：生成设计产物（用户确认需求后）
同时生成以下内容并展示给用户：
1. **Excel配置表设计** - 展示表名、sheet结构、字段名、字段类型、示例数据
2. **.proto协议文件** - 展示完整的proto文件内容
3. **数据库表设计** - 展示建表SQL或表结构说明
注意：此阶段只展示内容，不写入文件！等用户确认后再写入。

### 第三阶段：写入设计产物（用户确认设计后）
用户确认设计没问题后，调用工具写入：
- 用 write_excel 写入Excel配置表到配置表目录
- 用 write_file + base_dir="proto" 写入.proto文件到协议目录
- 告知用户文件已写入

### 第四阶段：生成业务代码（设计产物写入后）
1. 先用工具探索项目代码，找到相似的已有业务模块作为参考
2. 严格模仿项目中已有代码的写法生成新业务代码
3. 展示代码内容给用户确认
4. 用户确认后调用 write_file 写入项目目录

## 探索项目代码的方式
- 用 list_dir 了解项目结构
- 用 search_files 和 grep_search 找到与需求相似的已有业务模块
- 用 read_file 读取这些文件，理解项目的实际开发模式
- 用 list_proto_dir 和 read_proto_file 查看已有协议文件作为模板
- 用 list_excel_dir 和 read_excel_meta 查看已有配置表作为模板

## 核心原则
- 永远先看代码再写代码，不要凭空想象
- 严格模仿项目中已有的命名风格、代码结构、调用方式
- 如果项目代码中没有某个模式（如事务、锁、缓存），就不要加
- 使用项目中已有的工具类、基类、方法，不要自己发明
- 新文件的目录结构、包名要与已有代码保持一致
- 生成.proto文件时，必须先读取已有的.proto文件作为模板参考
- 生成Excel配置表时，必须先读取已有的Excel配置表作为格式参考
- 任何文件写入前，必须先展示内容让用户确认

## 记忆机制
- 项目根目录下的 AGENT.md 是你的持久记忆文件
- 记忆只用于存储通用的项目规则和约定，例如：命名规范、代码风格、框架使用约定、踩过的通用坑
- 不要记录具体业务模块的实现细节、某次需求的具体内容、或单个功能的使用方式
- 只有当用户指出你的错误或纠正你，且该教训具有通用性（适用于未来其他任务）时，才用 memory_append 写入记忆
- 写入格式：简短明确的规则，用 - 开头
- 每次开始新任务前，记忆内容已自动加载，务必遵守其中的所有规则

请用中文回复用户。
"""

SYSTEM_PROMPT_EN = """You are a senior game server development expert. You can browse and search project code, protocol files, and config tables via tools.

## Important: Determine User Intent

When you receive a message, first determine whether it is a "game server business development request" (e.g., implement a game feature, add a business module, design protocols/config tables/DB tables).

- If it IS a business development request → follow the "Workflow" below
- If it is NOT (e.g., casual chat, technical questions, asking about project structure, code review, bug investigation, etc.) → just answer normally, do NOT run the requirements analysis workflow

## Workflow (only for game server business development requests, follow strictly in order)

### Phase 1: Requirements Confirmation
When the user describes a feature:
1. If the requirements are unclear, ask clarifying questions
2. Generate a **Requirements Checklist** including:
   - Numbered feature list
   - Data structures / fields involved
   - Client-server interaction flow
   - Config tables and field descriptions
   - Database table design
3. Let the user confirm each item; adjust until they say "confirmed" or "looks good"

### Phase 2: Generate Design Artifacts (after user confirms requirements)
Generate and display all of the following:
1. **Excel config table design** - table name, sheet structure, field names, types, sample data
2. **.proto protocol file** - full proto file content
3. **Database table design** - CREATE TABLE SQL or schema description
Note: Only display content at this stage, do NOT write files! Wait for user confirmation.

### Phase 3: Write Design Artifacts (after user confirms design)
After user confirms the design:
- Use write_excel to write Excel config tables to the config directory
- Use write_file + base_dir="proto" to write .proto files to the proto directory
- Inform the user that files have been written

### Phase 4: Generate Business Code (after design artifacts are written)
1. Explore project code first, find similar existing modules as reference
2. Strictly mimic the existing code style to generate new business code
3. Show code to user for confirmation
4. Write to project directory after user confirms

## How to Explore Project Code
- Use list_dir to understand project structure
- Use search_files and grep_search to find similar existing modules
- Use read_file to read those files and understand the actual development patterns
- Use list_proto_dir and read_proto_file to review existing proto files as templates
- Use list_excel_dir and read_excel_meta to review existing config tables as templates

## Core Principles
- Always read code before writing code, never guess
- Strictly mimic existing naming conventions, code structure, and call patterns
- If the project doesn't use a pattern (transactions, locks, caching), don't add it
- Use existing utility classes, base classes, and methods; don't invent your own
- New files must follow the same directory structure and package naming as existing code
- When generating .proto files, always read existing .proto files as template reference first
- When generating Excel config tables, always read existing tables as format reference first
- Always show content to user for confirmation before writing any file

## Memory Mechanism
- AGENT.md in the project root is your persistent memory file
- Memory is ONLY for storing universal project rules and conventions, such as: naming conventions, code style, framework usage patterns, common pitfalls
- Do NOT record specific business module implementation details, individual feature requirements, or per-module usage notes
- Only use memory_append when the user corrects you AND the lesson is universally applicable to future tasks
- Write format: short, clear rules starting with -
- Memory content is auto-loaded before each new task; always follow all rules in it

Please reply in English.
"""


def _get_system_prompt() -> str:
    return SYSTEM_PROMPT_EN if get_lang() == "en" else SYSTEM_PROMPT_ZH


def _build_anthropic_tools() -> list:
    """将 OpenAI 格式的工具定义转换为 Anthropic 格式"""
    tools = []
    for td in TOOL_DEFINITIONS:
        func = td["function"]
        tools.append({
            "name": func["name"],
            "description": func["description"],
            "input_schema": func["parameters"],
        })
    return tools


class AnthropicAdapter:
    """Anthropic Claude API 适配器，提供与 OpenAI 兼容的调用接口"""

    def __init__(self, api_key: str):
        try:
            import anthropic
        except ImportError:
            raise ImportError("Claude provider requires: pip install anthropic")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.tools = _build_anthropic_tools()

    def chat(self, model: str, messages: list, temperature: float = 0.3,
             max_tokens: int = 8192):
        """调用 Claude API，返回统一格式的结果"""
        # 分离 system 消息
        system_content = ""
        chat_messages = []
        for msg in messages:
            if isinstance(msg, dict) and msg.get("role") == "system":
                system_content = msg["content"]
            else:
                chat_messages.append(msg)

        # 转换消息格式：将 OpenAI tool 消息转为 Anthropic 格式
        anthropic_messages = []
        for msg in chat_messages:
            if not isinstance(msg, dict):
                continue
            role = msg.get("role", "")

            if role == "user":
                anthropic_messages.append({"role": "user", "content": msg["content"]})
            elif role == "assistant":
                # 可能包含 tool_calls
                content_blocks = []
                if msg.get("content"):
                    content_blocks.append({"type": "text", "text": msg["content"]})
                for tc in msg.get("tool_calls", []):
                    fn = tc if isinstance(tc, dict) else tc
                    func = fn.get("function", fn)
                    try:
                        input_data = json.loads(func["arguments"]) if isinstance(func["arguments"], str) else func["arguments"]
                    except (json.JSONDecodeError, KeyError):
                        input_data = {}
                    content_blocks.append({
                        "type": "tool_use",
                        "id": fn.get("id", ""),
                        "name": func["name"],
                        "input": input_data,
                    })
                if content_blocks:
                    anthropic_messages.append({"role": "assistant", "content": content_blocks})
            elif role == "tool":
                # Anthropic 需要 tool_result 在 user 消息中
                tool_result = {
                    "type": "tool_result",
                    "tool_use_id": msg.get("tool_call_id", ""),
                    "content": msg.get("content", ""),
                }
                # 合并连续的 tool results 到同一个 user 消息
                if anthropic_messages and anthropic_messages[-1]["role"] == "user":
                    last = anthropic_messages[-1]
                    if isinstance(last["content"], list):
                        last["content"].append(tool_result)
                    else:
                        anthropic_messages[-1]["content"] = [tool_result]
                else:
                    anthropic_messages.append({"role": "user", "content": [tool_result]})

        resp = self.client.messages.create(
            model=model,
            system=system_content,
            messages=anthropic_messages,
            tools=self.tools,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return self._convert_response(resp)

    @staticmethod
    def _convert_response(resp):
        """将 Anthropic 响应转换为类 OpenAI 格式的字典"""
        text_parts = []
        tool_calls = []
        for block in resp.content:
            if block.type == "text":
                text_parts.append(block.text)
            elif block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "type": "function",
                    "function": {
                        "name": block.name,
                        "arguments": json.dumps(block.input, ensure_ascii=False),
                    },
                })
        return {
            "content": "\n".join(text_parts) if text_parts else None,
            "tool_calls": tool_calls if tool_calls else None,
        }


class GameServerAgent:
    def __init__(self, api_key: str, provider: str, api_base: str, model: str,
                 project_path: str, ignore_dirs: list,
                 proto_path: str = "", excel_path: str = ""):
        self.provider = provider
        self.model = model
        self.project_path = project_path
        self.ignore_dirs = ignore_dirs
        self.proto_path = proto_path
        self.excel_path = excel_path
        self.is_anthropic = PROVIDERS.get(provider, {}).get("extra", {}).get("is_anthropic", False)

        if self.is_anthropic:
            self.anthropic_adapter = AnthropicAdapter(api_key)
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key, base_url=api_base)
            self.anthropic_adapter = None

        self.messages = self._build_system_messages()

    def _build_system_messages(self) -> list:
        """构建 system 消息，自动注入记忆文件内容和目录配置"""
        memory = load_memory(self.project_path)
        system_content = _get_system_prompt()

        dir_info_header = "\n\n## 当前目录配置\n" if get_lang() == "zh" else "\n\n## Current Directory Config\n"
        not_set = "(未设置)" if get_lang() == "zh" else "(not set)"
        if get_lang() == "zh":
            dir_info = dir_info_header
            dir_info += f"- 项目代码目录: {self.project_path}\n"
            dir_info += f"- 协议文件目录: {self.proto_path or not_set}\n"
            dir_info += f"- 配置表目录: {self.excel_path or not_set}\n"
        else:
            dir_info = dir_info_header
            dir_info += f"- Project directory: {self.project_path}\n"
            dir_info += f"- Proto directory: {self.proto_path or not_set}\n"
            dir_info += f"- Excel config directory: {self.excel_path or not_set}\n"
        system_content += dir_info

        if memory:
            mem_header = "\n## 项目记忆（AGENT.md）\n" if get_lang() == "zh" else "\n## Project Memory (AGENT.md)\n"
            system_content += f"{mem_header}{memory}"
            console.print(f"[dim]{t('memory_loaded', size=len(memory))}[/dim]")

        return [{"role": "system", "content": system_content}]

    def _call_llm(self) -> dict | None:
        """统一的 LLM 调用入口，返回 {content, tool_calls} 或 None"""
        if self.is_anthropic:
            return self.anthropic_adapter.chat(
                model=self.model,
                messages=self._trimmed_messages(),
                temperature=0.3,
                max_tokens=8192,
            )
        else:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=self._trimmed_messages(),
                tools=TOOL_DEFINITIONS,
                tool_choice="auto",
                temperature=0.3,
                max_tokens=8192,
                stream=False,
            )
            msg = resp.choices[0].message
            tool_calls = None
            if msg.tool_calls:
                tool_calls = [tc.model_dump() for tc in msg.tool_calls]
            return {
                "content": msg.content,
                "tool_calls": tool_calls,
            }

    def chat(self, user_input: str, max_turns: int = 40):
        """agentic loop：发送消息，自动处理工具调用，直到AI给出最终回复"""
        self.messages.append({"role": "user", "content": user_input})
        start_time = time.time()

        for turn in range(max_turns):
            with console.status(
                f"[cyan]{t('thinking', turn=turn+1, max=max_turns)}[/cyan]",
                spinner="dots",
            ):
                try:
                    result = self._call_llm()
                except Exception as e:
                    console.print(f"\n[bold red]{t('api_error', err=e)}[/bold red]")
                    return

            content = result.get("content")
            tool_calls = result.get("tool_calls")

            if tool_calls:
                # 构建 assistant 消息
                assistant_msg = {"role": "assistant", "content": content or ""}
                assistant_msg["tool_calls"] = tool_calls
                self.messages.append(assistant_msg)

                if content:
                    console.print(f"[green]{content}[/green]")

                for tc in tool_calls:
                    func = tc.get("function", tc)
                    func_name = func["name"]
                    tc_id = tc.get("id", "")

                    label_key = TOOL_LABEL_KEYS.get(func_name)
                    label = t(label_key) if label_key else f"🔧 {func_name}"
                    try:
                        args_preview = json.loads(func["arguments"]) if isinstance(func["arguments"], str) else func["arguments"]
                        brief = ""
                        for v in args_preview.values():
                            if isinstance(v, str) and v:
                                brief = v if len(v) <= 60 else v[:57] + "..."
                                break
                    except Exception:
                        brief = ""

                    desc = f"{label}"
                    if brief:
                        desc += f" → [white]{brief}[/white]"

                    with console.status(f"[cyan]{desc}[/cyan]", spinner="dots"):
                        tool_result = self._execute_tool_from_dict(tc)

                    result_lines = tool_result.split("\n")
                    success_prefixes = ("文件已写入", "Excel已写入", "已写入记忆",
                                        "File written", "Excel written", "Memory file updated")
                    error_prefixes = ("工具执行失败", "写入失败", "读取失败", "参数解析失败", "未知工具",
                                      "Tool execution failed", "Write failed", "Read failed",
                                      "Failed to parse", "Unknown tool")
                    if tool_result.startswith(success_prefixes):
                        console.print(f"  [green]✅ {tool_result}[/green]")
                    elif tool_result.startswith(error_prefixes):
                        console.print(f"  [bold red]❌ {tool_result}[/bold red]")
                    else:
                        console.print(f"  [dim]{t('tool_done', label=label, lines=len(result_lines))}[/dim]")

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tc_id,
                        "content": tool_result,
                    })
                continue

            # 无工具调用，是最终回复
            text = content or ""
            self.messages.append({"role": "assistant", "content": text})
            elapsed = time.time() - start_time
            console.print(f"\n[green]{text}[/green]")
            console.print(f"\n[dim]{t('elapsed', turns=turn+1, time=elapsed)}[/dim]")
            return

        elapsed = time.time() - start_time
        console.print(f"[yellow]{t('max_turns_reached', max=max_turns, time=elapsed)}[/yellow]")

    def _execute_tool_from_dict(self, tool_call_dict: dict) -> str:
        """从字典格式的 tool_call 执行工具"""
        func = tool_call_dict.get("function", tool_call_dict)
        name = func["name"]
        try:
            args = json.loads(func["arguments"]) if isinstance(func["arguments"], str) else func["arguments"]
        except (json.JSONDecodeError, KeyError):
            return t("parse_error")

        handler = TOOL_HANDLERS.get(name)
        if not handler:
            return t("unknown_tool", name=name)

        args["project_path"] = self.project_path
        args["proto_path"] = self.proto_path
        args["excel_path"] = self.excel_path

        if "ignore_dirs" not in args:
            args["ignore_dirs"] = self.ignore_dirs

        if name == "write_file" and args.get("base_dir"):
            bd = args["base_dir"].lower()
            if bd == "proto":
                args["base_dir"] = self.proto_path
            elif bd == "excel":
                args["base_dir"] = self.excel_path
            else:
                args["base_dir"] = ""

        try:
            return handler(**args)
        except Exception as e:
            return t("tool_exec_error", err=e)

    def _trimmed_messages(self) -> list:
        """裁剪消息历史，防止超token"""
        system = [self.messages[0]]
        rest = self.messages[1:]
        total = 0
        keep = []
        for msg in reversed(rest):
            content = ""
            if isinstance(msg, dict):
                content = msg.get("content", "") or ""
                if isinstance(content, list):
                    content = str(content)
            size = len(content) // 3
            if total + size > 100000:
                break
            keep.insert(0, msg)
            total += size
        return system + keep

    def clear(self):
        """清空对话历史，重新加载记忆"""
        self.messages = self._build_system_messages()
