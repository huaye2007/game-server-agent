"""AI Agent - 支持 tool calling 的 agentic loop"""
import json
import time
from openai import OpenAI
from rich.console import Console
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

TOOL_LABELS = {
    "list_dir": "📂 浏览项目目录",
    "read_file": "📄 读取文件",
    "search_files": "🔍 搜索文件",
    "grep_search": "🔎 搜索代码内容",
    "write_file": "✏️  写入文件",
    "list_proto_dir": "📂 浏览协议目录",
    "read_proto_file": "📄 读取协议文件",
    "list_excel_dir": "📂 浏览配置表目录",
    "read_excel_meta": "📊 读取配置表结构",
    "write_excel": "📊 写入配置表",
    "memory_read": "🧠 读取记忆",
    "memory_append": "🧠 写入记忆",
}

SYSTEM_PROMPT = """你是一个资深游戏服务器开发专家。你可以通过工具浏览和搜索项目代码、协议文件和配置表。

## 工作流程（严格按顺序执行）

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
- 当用户指出你的错误或纠正你时，用 memory_append 把教训写入记忆
- 写入格式：简短明确的规则，用 - 开头
- 每次开始新任务前，记忆内容已自动加载，务必遵守其中的所有规则
"""


class GameServerAgent:
    def __init__(self, api_key: str, api_base: str, model: str,
                 project_path: str, ignore_dirs: list,
                 proto_path: str = "", excel_path: str = ""):
        self.client = OpenAI(api_key=api_key, base_url=api_base)
        self.model = model
        self.project_path = project_path
        self.ignore_dirs = ignore_dirs
        self.proto_path = proto_path
        self.excel_path = excel_path
        self.messages = self._build_system_messages()

    def _build_system_messages(self) -> list:
        """构建 system 消息，自动注入记忆文件内容和目录配置"""
        memory = load_memory(self.project_path)
        system_content = SYSTEM_PROMPT

        # 注入目录配置信息
        dir_info = "\n\n## 当前目录配置\n"
        dir_info += f"- 项目代码目录: {self.project_path}\n"
        dir_info += f"- 协议文件目录: {self.proto_path or '(未设置)'}\n"
        dir_info += f"- 配置表目录: {self.excel_path or '(未设置)'}\n"
        system_content += dir_info

        if memory:
            system_content += f"\n## 项目记忆（AGENT.md）\n{memory}"
            console.print(f"[dim]已加载项目记忆 ({len(memory)} 字符)[/dim]")

        return [{"role": "system", "content": system_content}]

    def chat(self, user_input: str, max_turns: int = 40):
        """agentic loop：发送消息，自动处理工具调用，直到AI给出最终回复"""
        self.messages.append({"role": "user", "content": user_input})
        start_time = time.time()

        for turn in range(max_turns):
            # 显示思考中的 spinner
            with console.status(
                f"[cyan]🤔 AI 思考中... (轮次 {turn + 1}/{max_turns})[/cyan]",
                spinner="dots",
            ):
                try:
                    resp = self.client.chat.completions.create(
                        model=self.model,
                        messages=self._trimmed_messages(),
                        tools=TOOL_DEFINITIONS,
                        tool_choice="auto",
                        temperature=0.3,
                        max_tokens=8192,
                        stream=False,
                    )
                except Exception as e:
                    console.print(f"\n[bold red]❌ API调用失败: {e}[/bold red]")
                    return

            choice = resp.choices[0]
            msg = choice.message

            # 有工具调用
            if msg.tool_calls:
                self.messages.append(msg.model_dump())
                # 如果 AI 同时返回了文本，先显示出来
                if msg.content:
                    console.print(f"[green]{msg.content}[/green]")

                for i, tc in enumerate(msg.tool_calls):
                    label = TOOL_LABELS.get(tc.function.name, f"🔧 {tc.function.name}")
                    try:
                        args_preview = json.loads(tc.function.arguments)
                        # 取第一个参数值作为简要描述
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
                        result = self._execute_tool(tc)

                    # 显示工具执行结果摘要
                    result_lines = result.split("\n")
                    if result.startswith(("文件已写入", "Excel已写入", "已写入记忆")):
                        console.print(f"  [green]✅ {result}[/green]")
                    elif result.startswith(("工具执行失败", "写入失败", "读取失败",
                                            "参数解析失败", "未知工具")):
                        console.print(f"  [bold red]❌ {result}[/bold red]")
                    else:
                        console.print(f"  [dim]✅ {label} 完成 ({len(result_lines)} 行)[/dim]")

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result,
                    })
                continue

            # 无工具调用，是最终回复
            text = msg.content or ""
            self.messages.append({"role": "assistant", "content": text})
            elapsed = time.time() - start_time
            console.print(f"\n[green]{text}[/green]")
            console.print(f"\n[dim]⏱ 共 {turn + 1} 轮，耗时 {elapsed:.1f}s[/dim]")
            return

        elapsed = time.time() - start_time
        console.print(f"[yellow]⚠️ 达到最大轮次限制 ({max_turns} 轮，耗时 {elapsed:.1f}s)[/yellow]")

    def _execute_tool(self, tool_call) -> str:
        """执行工具调用"""
        name = tool_call.function.name
        try:
            args = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            return "参数解析失败"

        handler = TOOL_HANDLERS.get(name)
        if not handler:
            return f"未知工具: {name}"

        # 注入路径参数
        args["project_path"] = self.project_path
        args["proto_path"] = self.proto_path
        args["excel_path"] = self.excel_path

        if "ignore_dirs" not in args:
            args["ignore_dirs"] = self.ignore_dirs

        # 处理 write_file 的 base_dir 映射
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
            return f"工具执行失败: {e}"

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
            size = len(content) // 3
            if total + size > 100000:
                break
            keep.insert(0, msg)
            total += size
        return system + keep

    def clear(self):
        """清空对话历史，重新加载记忆"""
        self.messages = self._build_system_messages()
