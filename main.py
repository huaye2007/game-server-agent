#!/usr/bin/env python3
"""游戏服务器开发AI Agent - 像 Claude Code 一样直接探索项目代码"""
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from prompt_toolkit import prompt as pt_prompt
from prompt_toolkit.history import InMemoryHistory

from config import load_config, save_config
from agent import GameServerAgent

console = Console()
history = InMemoryHistory()


def show_banner():
    console.print(Panel.fit(
        "[bold cyan]🎮 游戏服务器开发 AI Agent[/bold cyan]\n"
        "AI 自主探索项目代码，实时参考生成业务代码\n"
        "[dim]支持协议文件(.proto)、配置表(Excel)、数据库表、业务代码生成[/dim]",
        border_style="cyan",
    ))


def show_help():
    table = Table(title="可用命令", show_header=True)
    table.add_column("命令", style="cyan", width=24)
    table.add_column("说明", style="white")
    table.add_row("/set_project <路径>", "设置项目代码目录")
    table.add_row("/set_proto <路径>", "设置协议文件(.proto)目录")
    table.add_row("/set_excel <路径>", "设置配置表(Excel)目录")
    table.add_row("/set_key <API Key>", "设置 DeepSeek API Key")
    table.add_row("/set_model <模型名>", "设置模型（默认 deepseek-chat）")
    table.add_row("/clear", "清空对话历史")
    table.add_row("/config", "查看当前配置")
    table.add_row("/help", "显示帮助")
    table.add_row("/quit", "退出")
    table.add_row("[dim]直接输入文字[/dim]", "提需求，AI自动探索并生成代码")
    console.print(table)


def _handle_set_path(cfg, key: str, arg: str, label: str, agent_ref: list):
    """通用的路径设置处理"""
    if not arg:
        console.print(f"[yellow]用法: /set_{key.replace('_path','')} <路径>[/yellow]")
        return
    p = Path(arg).resolve()
    if p.exists():
        cfg[key] = str(p)
        save_config(cfg)
        agent_ref[0] = None  # 重建 agent
        console.print(f"[green]{label}已设置: {p}[/green]")
    else:
        console.print(f"[red]目录不存在: {arg}[/red]")


def main():
    show_banner()
    cfg = load_config()
    agent_ref = [None]  # 用列表包装以便在闭包中修改

    def get_agent() -> GameServerAgent | None:
        if not cfg.get("api_key"):
            console.print("[yellow]请先设置 API Key: /set_key <your_key>[/yellow]")
            return None
        if not cfg.get("project_path"):
            console.print("[yellow]请先设置项目目录: /set_project <路径>[/yellow]")
            return None
        if not Path(cfg["project_path"]).exists():
            console.print(f"[red]项目目录不存在: {cfg['project_path']}[/red]")
            return None
        if agent_ref[0] is None:
            agent_ref[0] = GameServerAgent(
                api_key=cfg["api_key"],
                api_base=cfg["api_base"],
                model=cfg["model"],
                project_path=cfg["project_path"],
                ignore_dirs=cfg["ignore_dirs"],
                proto_path=cfg.get("proto_path", ""),
                excel_path=cfg.get("excel_path", ""),
            )
        return agent_ref[0]

    show_help()
    console.print()

    while True:
        try:
            user_input = pt_prompt("🎮 > ", history=history).strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[cyan]再见！[/cyan]")
            break

        if not user_input:
            continue

        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1].strip() if len(parts) > 1 else ""

            if cmd in ("/quit", "/exit"):
                console.print("[cyan]再见！[/cyan]")
                break
            elif cmd == "/help":
                show_help()
            elif cmd == "/set_project":
                _handle_set_path(cfg, "project_path", arg, "项目目录", agent_ref)
            elif cmd == "/set_proto":
                _handle_set_path(cfg, "proto_path", arg, "协议文件目录", agent_ref)
            elif cmd == "/set_excel":
                _handle_set_path(cfg, "excel_path", arg, "配置表目录", agent_ref)
            elif cmd == "/set_key":
                if not arg:
                    console.print("[yellow]用法: /set_key <API Key>[/yellow]")
                else:
                    cfg["api_key"] = arg
                    save_config(cfg)
                    agent_ref[0] = None
                    console.print("[green]API Key 已设置[/green]")
            elif cmd == "/set_model":
                if not arg:
                    console.print(f"[yellow]当前模型: {cfg['model']}[/yellow]")
                else:
                    cfg["model"] = arg
                    save_config(cfg)
                    agent_ref[0] = None
                    console.print(f"[green]模型已设置: {arg}[/green]")
            elif cmd == "/clear":
                if agent_ref[0]:
                    agent_ref[0].clear()
                console.print("[green]对话历史已清空[/green]")
            elif cmd == "/config":
                d = {k: v for k, v in cfg.items() if k != "api_key"}
                d["api_key"] = "***" if cfg.get("api_key") else "(未设置)"
                console.print(json.dumps(d, indent=2, ensure_ascii=False))
            else:
                console.print(f"[yellow]未知命令: {cmd}，输入 /help 查看帮助[/yellow]")
        else:
            a = get_agent()
            if a:
                a.chat(user_input, max_turns=cfg.get("max_turns", 40))


if __name__ == "__main__":
    main()
