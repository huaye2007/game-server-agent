"""工具定义 - 给AI提供文件搜索、读取和写入能力"""
import os
import re
from pathlib import Path


def list_dir(project_path: str, rel_dir: str = "", max_depth: int = 2,
             ignore_dirs: list = None, **_kwargs) -> str:
    """列出目录结构"""
    root = Path(project_path) / rel_dir
    if not root.exists():
        return f"目录不存在: {rel_dir}"
    ignore = set(ignore_dirs or [])
    lines = []
    _walk_tree(root, Path(project_path), lines, ignore, 0, max_depth)
    if not lines:
        return "空目录"
    return "\n".join(lines[:200])


def _walk_tree(path: Path, root: Path, lines: list, ignore: set,
               depth: int, max_depth: int):
    if depth > max_depth:
        return
    try:
        entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name))
    except PermissionError:
        return
    for entry in entries:
        if entry.name.startswith(".") or entry.name in ignore:
            continue
        rel = entry.relative_to(root)
        prefix = "  " * depth
        if entry.is_dir():
            lines.append(f"{prefix}{rel}/")
            _walk_tree(entry, root, lines, ignore, depth + 1, max_depth)
        else:
            lines.append(f"{prefix}{rel}")


def read_file(project_path: str, rel_path: str, max_lines: int = 500,
              **_kwargs) -> str:
    """读取文件内容"""
    fp = Path(project_path) / rel_path
    if not fp.exists():
        return f"文件不存在: {rel_path}"
    if not fp.is_file():
        return f"不是文件: {rel_path}"
    try:
        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        if len(lines) > max_lines:
            half = max_lines // 2
            head = "".join(lines[:half])
            tail = "".join(lines[-half:])
            return f"{head}\n... [省略 {len(lines) - max_lines} 行] ...\n{tail}"
        return "".join(lines)
    except Exception as e:
        return f"读取失败: {e}"


def search_files(project_path: str, pattern: str,
                 ignore_dirs: list = None, **_kwargs) -> str:
    """按文件名模糊搜索"""
    root = Path(project_path)
    ignore = set(ignore_dirs or [])
    results = []
    pat = pattern.lower()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d not in ignore and not d.startswith(".")]
        for fname in filenames:
            if pat in fname.lower():
                rel = str(Path(dirpath, fname).relative_to(root))
                results.append(rel)
                if len(results) >= 50:
                    return "\n".join(results) + "\n... 结果过多，已截断"
    return "\n".join(results) if results else "未找到匹配文件"


def grep_search(project_path: str, pattern: str, file_ext: str = "",
                ignore_dirs: list = None, max_results: int = 30,
                **_kwargs) -> str:
    """在文件内容中搜索文本"""
    root = Path(project_path)
    ignore = set(ignore_dirs or [])
    results = []
    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error:
        regex = re.compile(re.escape(pattern), re.IGNORECASE)

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d not in ignore and not d.startswith(".")]
        for fname in filenames:
            if file_ext and not fname.endswith(file_ext):
                continue
            fp = Path(dirpath, fname)
            try:
                size = fp.stat().st_size
                if size > 512 * 1024:
                    continue
                with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f, 1):
                        if regex.search(line):
                            rel = str(fp.relative_to(root))
                            results.append(f"{rel}:{i}: {line.rstrip()[:150]}")
                            if len(results) >= max_results:
                                return "\n".join(results) + "\n... 结果过多，已截断"
            except Exception:
                continue
    return "\n".join(results) if results else "未找到匹配内容"


# ============ 写文件工具 ============

def write_file(project_path: str, rel_path: str, content: str,
               base_dir: str = "", **_kwargs) -> str:
    """写入文件内容到指定路径。
    base_dir: 可选的基础目录（proto_path/excel_path），为空则使用 project_path。
    """
    if base_dir:
        fp = Path(base_dir) / rel_path
    else:
        fp = Path(project_path) / rel_path
    try:
        fp.parent.mkdir(parents=True, exist_ok=True)
        with open(fp, "w", encoding="utf-8") as f:
            f.write(content)
        return f"文件已写入: {fp}"
    except Exception as e:
        return f"写入失败: {e}"


# ============ 协议文件目录工具 ============

def list_proto_dir(project_path: str, proto_path: str = "",
                   rel_dir: str = "", max_depth: int = 2,
                   **_kwargs) -> str:
    """列出协议文件(.proto)目录结构"""
    if not proto_path:
        return "协议文件目录未设置，请使用 /set_proto <路径> 设置"
    root = Path(proto_path) / rel_dir
    if not root.exists():
        return f"协议目录不存在: {proto_path}"
    lines = []
    _walk_tree(root, Path(proto_path), lines, set(), 0, max_depth)
    if not lines:
        return "空目录"
    return "\n".join(lines[:200])


def read_proto_file(project_path: str, proto_path: str = "",
                    rel_path: str = "", **_kwargs) -> str:
    """读取协议文件(.proto)内容，用于参考已有协议格式"""
    if not proto_path:
        return "协议文件目录未设置"
    fp = Path(proto_path) / rel_path
    if not fp.exists():
        return f"文件不存在: {rel_path}"
    try:
        return fp.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        return f"读取失败: {e}"


# ============ 配置表目录工具 ============

def list_excel_dir(project_path: str, excel_path: str = "",
                   rel_dir: str = "", max_depth: int = 2,
                   **_kwargs) -> str:
    """列出配置表(Excel)目录结构"""
    if not excel_path:
        return "配置表目录未设置，请使用 /set_excel <路径> 设置"
    root = Path(excel_path) / rel_dir
    if not root.exists():
        return f"配置表目录不存在: {excel_path}"
    lines = []
    _walk_tree(root, Path(excel_path), lines, set(), 0, max_depth)
    if not lines:
        return "空目录"
    return "\n".join(lines[:200])


def read_excel_meta(project_path: str, excel_path: str = "",
                    rel_path: str = "", **_kwargs) -> str:
    """读取Excel配置表的sheet名和表头信息（不读取全部数据），用于参考已有配置表格式"""
    if not excel_path:
        return "配置表目录未设置"
    fp = Path(excel_path) / rel_path
    if not fp.exists():
        return f"文件不存在: {rel_path}"
    try:
        import openpyxl
        wb = openpyxl.load_workbook(fp, read_only=True, data_only=True)
        result = []
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            rows = list(ws.iter_rows(max_row=5, values_only=True))
            result.append(f"## Sheet: {sheet_name}")
            for i, row in enumerate(rows):
                cells = [str(c) if c is not None else "" for c in row]
                result.append(f"  行{i+1}: {' | '.join(cells)}")
        wb.close()
        return "\n".join(result)
    except ImportError:
        return "需要安装 openpyxl: pip install openpyxl"
    except Exception as e:
        return f"读取失败: {e}"


def write_excel(project_path: str, excel_path: str = "",
                rel_path: str = "", sheets: str = "", **_kwargs) -> str:
    """写入Excel配置表。
    sheets: JSON字符串，格式为 [{"name": "Sheet1", "headers": [...], "rows": [[...], ...]}, ...]
    """
    import json as _json
    if not excel_path:
        return "配置表目录未设置"
    fp = Path(excel_path) / rel_path
    try:
        import openpyxl
        sheet_data = _json.loads(sheets)
        wb = openpyxl.Workbook()
        # 删除默认sheet
        wb.remove(wb.active)
        for sd in sheet_data:
            ws = wb.create_sheet(title=sd["name"])
            if sd.get("headers"):
                ws.append(sd["headers"])
            for row in sd.get("rows", []):
                ws.append(row)
        fp.parent.mkdir(parents=True, exist_ok=True)
        wb.save(fp)
        return f"Excel已写入: {fp}"
    except ImportError:
        return "需要安装 openpyxl: pip install openpyxl"
    except Exception as e:
        return f"写入失败: {e}"


# ============ 记忆文件（AGENT.md） ============

MEMORY_FILE = "AGENT.md"


def memory_read(project_path: str, **_kwargs) -> str:
    """读取项目记忆文件 AGENT.md"""
    fp = Path(project_path) / MEMORY_FILE
    if not fp.exists():
        return "记忆文件不存在，尚无持久记忆。"
    try:
        return fp.read_text(encoding="utf-8")
    except Exception as e:
        return f"读取失败: {e}"


def memory_append(project_path: str, content: str, **_kwargs) -> str:
    """向项目记忆文件 AGENT.md 追加内容"""
    fp = Path(project_path) / MEMORY_FILE
    try:
        existing = ""
        if fp.exists():
            existing = fp.read_text(encoding="utf-8")
        with open(fp, "w", encoding="utf-8") as f:
            if existing and not existing.endswith("\n"):
                existing += "\n"
            f.write(existing + content.strip() + "\n")
        return "已写入记忆文件"
    except Exception as e:
        return f"写入失败: {e}"


def load_memory(project_path: str) -> str:
    """启动时加载记忆文件内容（供 agent 初始化用）"""
    fp = Path(project_path) / MEMORY_FILE
    if not fp.exists():
        return ""
    try:
        return fp.read_text(encoding="utf-8")
    except Exception:
        return ""


# ============ 工具定义（OpenAI function calling 格式） ============

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "列出项目目录结构。用于了解项目布局、查找相关目录。",
            "parameters": {
                "type": "object",
                "properties": {
                    "rel_dir": {
                        "type": "string",
                        "description": "相对于项目根目录的子目录路径，空字符串表示根目录"
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "目录展开深度，默认2"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取项目中某个文件的内容。用于查看代码实现细节。",
            "parameters": {
                "type": "object",
                "properties": {
                    "rel_path": {
                        "type": "string",
                        "description": "文件相对于项目根目录的路径"
                    }
                },
                "required": ["rel_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_files",
            "description": "按文件名模糊搜索项目中的文件。用于查找特定类型或名称的文件。",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "文件名搜索关键词（模糊匹配）"
                    }
                },
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "grep_search",
            "description": "在项目文件内容中搜索文本或正则表达式。用于查找特定的类名、方法名、协议定义等。",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "搜索的文本或正则表达式"
                    },
                    "file_ext": {
                        "type": "string",
                        "description": "限定文件扩展名，如 .java .go .lua，空表示不限"
                    }
                },
                "required": ["pattern"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "写入文件到项目目录。用于生成业务代码、协议文件等。用户确认后才调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "rel_path": {
                        "type": "string",
                        "description": "文件相对路径"
                    },
                    "content": {
                        "type": "string",
                        "description": "文件内容"
                    },
                    "base_dir": {
                        "type": "string",
                        "description": "基础目录：'proto' 使用协议目录，'excel' 使用配置表目录，空则使用项目目录"
                    }
                },
                "required": ["rel_path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_proto_dir",
            "description": "列出协议文件(.proto)目录结构，查看已有的协议文件。",
            "parameters": {
                "type": "object",
                "properties": {
                    "rel_dir": {
                        "type": "string",
                        "description": "相对于协议目录的子目录路径，空表示根目录"
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "目录展开深度，默认2"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_proto_file",
            "description": "读取已有的.proto协议文件内容，用于参考协议格式和风格。",
            "parameters": {
                "type": "object",
                "properties": {
                    "rel_path": {
                        "type": "string",
                        "description": "协议文件相对于协议目录的路径"
                    }
                },
                "required": ["rel_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_excel_dir",
            "description": "列出配置表(Excel)目录结构，查看已有的配置表文件。",
            "parameters": {
                "type": "object",
                "properties": {
                    "rel_dir": {
                        "type": "string",
                        "description": "相对于配置表目录的子目录路径，空表示根目录"
                    },
                    "max_depth": {
                        "type": "integer",
                        "description": "目录展开深度，默认2"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_excel_meta",
            "description": "读取Excel配置表的sheet名和前几行数据，用于参考已有配置表的格式和字段设计。",
            "parameters": {
                "type": "object",
                "properties": {
                    "rel_path": {
                        "type": "string",
                        "description": "Excel文件相对于配置表目录的路径"
                    }
                },
                "required": ["rel_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_excel",
            "description": "写入Excel配置表文件。用户确认后才调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "rel_path": {
                        "type": "string",
                        "description": "Excel文件相对于配置表目录的路径"
                    },
                    "sheets": {
                        "type": "string",
                        "description": "JSON字符串，格式: [{\"name\": \"Sheet1\", \"headers\": [\"列1\",\"列2\"], \"rows\": [[\"值1\",\"值2\"]]}]"
                    }
                },
                "required": ["rel_path", "sheets"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "memory_read",
            "description": "读取项目记忆文件 AGENT.md。包含项目约定、踩过的坑、开发规范等持久记忆。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "memory_append",
            "description": "向项目记忆文件 AGENT.md 追加内容。当用户指出问题或纠正错误时，将教训写入记忆。",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "要追加的记忆内容（markdown格式）"
                    }
                },
                "required": ["content"]
            }
        }
    },
]
