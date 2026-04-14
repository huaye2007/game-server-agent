#!/usr/bin/env python3
"""游戏服务器开发AI Agent - 支持多模型提供商"""
import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.document import Document

from config import load_config, save_config, PROVIDERS
from agent import GameServerAgent
from i18n import t, set_lang, get_lang

console = Console()
history = InMemoryHistory()


class CommandCompleter(Completer):
    """命令自动补全，支持命令名和子参数补全"""

    def __init__(self, cfg: dict):
        self.cfg = cfg
        # 基础命令列表（无参数或参数不可枚举的）
        self.commands = [
            "/set_project", "/set_proto", "/set_excel",
            "/set_provider", "/set_key", "/set_model",
            "/set_api_base", "/set_lang",
            "/providers", "/clear", "/config", "/help", "/quit",
        ]
        # 子参数补全映射
        self.sub_completions = {
            "/set_provider": lambda: list(PROVIDERS.keys()),
            "/set_lang": lambda: ["zh", "en"],
            "/set_model": lambda: PROVIDERS.get(
                self.cfg.get("provider", "deepseek"), {}
            ).get("models", []),
        }

    def get_completions(self, document: Document, complete_event):
        text = document.text_before_cursor
        # 只在 / 开头时触发补全
        if not text.startswith("/"):
            return

        parts = text.split(maxsplit=1)
        cmd = parts[0].lower()

        if len(parts) == 1 and not text.endswith(" "):
            # 补全命令名本身
            for c in self.commands:
                if c.startswith(cmd):
                    yield Completion(c, start_position=-len(cmd))
        elif len(parts) >= 1 and (text.endswith(" ") or len(parts) == 2):
            # 补全子参数
            sub_text = parts[1].lower() if len(parts) == 2 else ""
            getter = self.sub_completions.get(cmd)
            if getter:
                for option in getter():
                    if option.lower().startswith(sub_text):
                        yield Completion(option, start_position=-len(sub_text))


def show_banner():
    console.print(Panel.fit(
        f"[bold cyan]{t('banner_title')}[/bold cyan]\n"
        f"{t('banner_desc')}\n"
        f"[dim]{t('banner_sub')}[/dim]",
        border_style="cyan",
    ))


def show_help():
    table = Table(title=t("help_title"), show_header=True)
    table.add_column(t("help_col_cmd"), style="cyan", width=28)
    table.add_column(t("help_col_desc"), style="white")
    path_label = "<路径>" if get_lang() == "zh" else "<path>"
    table.add_row(f"/set_project {path_label}", t("cmd_set_project"))
    table.add_row(f"/set_proto {path_label}", t("cmd_set_proto"))
    table.add_row(f"/set_excel {path_label}", t("cmd_set_excel"))
    table.add_row("/set_provider <name>", t("cmd_set_provider"))
    table.add_row("/set_key <API Key>", t("cmd_set_key"))
    model_label = "<模型名>" if get_lang() == "zh" else "<model>"
    table.add_row(f"/set_model {model_label}", t("cmd_set_model"))
    table.add_row("/set_api_base <URL>", t("cmd_set_api_base"))
    table.add_row("/set_lang <zh/en>", t("cmd_set_lang"))
    table.add_row("/providers", t("cmd_providers"))
    table.add_row("/clear", t("cmd_clear"))
    table.add_row("/config", t("cmd_config"))
    table.add_row("/help", t("cmd_help"))
    table.add_row("/quit", t("cmd_quit"))
    input_label = "直接输入文字" if get_lang() == "zh" else "Type freely"
    table.add_row(f"[dim]{input_label}[/dim]", t("cmd_free_input"))
    console.print(table)


def show_providers(current_provider: str):
    """显示支持的提供商列表"""
    table = Table(title=t("providers_title"), show_header=True)
    table.add_column(t("providers_col_name"), style="cyan", width=12)
    table.add_column(t("providers_col_api"), style="white", width=48)
    table.add_column(t("providers_col_models"), style="dim")
    for name, info in PROVIDERS.items():
        if name == "custom":
            continue
        marker = " ✓" if name == current_provider else ""
        models_str = ", ".join(info["models"][:4])
        if len(info["models"]) > 4:
            models_str += ", ..."
        table.add_row(
            f"{name}{marker}",
            info["api_base"],
            models_str,
        )
    table.add_row("custom", "(自定义 / custom URL)", "—")
    console.print(table)


def _handle_set_path(cfg, key: str, arg: str, label_key: str, agent_ref: list):
    """通用的路径设置处理"""
    short_key = key.replace("_path", "")
    if not arg:
        console.print(f"[yellow]{t('set_path_usage', key=short_key)}[/yellow]")
        return
    p = Path(arg).resolve()
    if p.exists():
        cfg[key] = str(p)
        save_config(cfg)
        agent_ref[0] = None
        console.print(f"[green]{t('path_set_ok', label=t(label_key), path=p)}[/green]")
    else:
        console.print(f"[red]{t('path_not_exist', path=arg)}[/red]")


def main():
    cfg = load_config()
    set_lang(cfg.get("lang", "zh"))

    show_banner()
    agent_ref = [None]
    completer = CommandCompleter(cfg)
    session = PromptSession(
        history=history,
        completer=completer,
        complete_while_typing=False,  # 按 Tab 触发，不会打字时弹出干扰
    )

    def get_agent() -> GameServerAgent | None:
        if not cfg.get("api_key"):
            provider = cfg.get("provider", "deepseek")
            console.print(f"[yellow]{t('provider_need_key', provider=provider)}[/yellow]")
            return None
        if not cfg.get("project_path"):
            console.print(f"[yellow]{t('project_not_set')}[/yellow]")
            return None
        if not Path(cfg["project_path"]).exists():
            console.print(f"[red]{t('project_not_exist', path=cfg['project_path'])}[/red]")
            return None
        if agent_ref[0] is None:
            agent_ref[0] = GameServerAgent(
                api_key=cfg["api_key"],
                provider=cfg.get("provider", "deepseek"),
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
            user_input = session.prompt("🎮 > ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print(f"\n[cyan]{t('goodbye')}[/cyan]")
            break

        if not user_input:
            continue

        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1].strip() if len(parts) > 1 else ""

            if cmd in ("/quit", "/exit"):
                console.print(f"[cyan]{t('goodbye')}[/cyan]")
                break
            elif cmd == "/help":
                show_help()
            elif cmd == "/set_project":
                _handle_set_path(cfg, "project_path", arg, "label_project", agent_ref)
            elif cmd == "/set_proto":
                _handle_set_path(cfg, "proto_path", arg, "label_proto", agent_ref)
            elif cmd == "/set_excel":
                _handle_set_path(cfg, "excel_path", arg, "label_excel", agent_ref)
            elif cmd == "/set_provider":
                if not arg:
                    console.print(f"[yellow]{t('provider_set_usage')}[/yellow]")
                elif arg.lower() in PROVIDERS:
                    pname = arg.lower()
                    pinfo = PROVIDERS[pname]
                    cfg["provider"] = pname
                    if pname != "custom":
                        cfg["api_base"] = pinfo["api_base"]
                        cfg["model"] = pinfo["default_model"]
                    save_config(cfg)
                    agent_ref[0] = None
                    console.print(f"[green]{t('provider_set_ok', provider=pname, api_base=cfg['api_base'], model=cfg['model'])}[/green]")
                    if pname == "claude":
                        console.print(t("claude_hint"))
                else:
                    console.print(f"[yellow]{t('provider_invalid', provider=arg)}[/yellow]")
            elif cmd == "/set_key":
                if not arg:
                    console.print(f"[yellow]{t('set_key_usage')}[/yellow]")
                else:
                    cfg["api_key"] = arg
                    save_config(cfg)
                    agent_ref[0] = None
                    console.print(f"[green]{t('key_set_ok')}[/green]")
            elif cmd == "/set_model":
                if not arg:
                    console.print(f"[yellow]{t('current_model', model=cfg['model'])}[/yellow]")
                else:
                    cfg["model"] = arg
                    save_config(cfg)
                    agent_ref[0] = None
                    console.print(f"[green]{t('model_set_ok', model=arg)}[/green]")
            elif cmd == "/set_api_base":
                if not arg:
                    console.print(f"[yellow]{t('api_base_usage')}[/yellow]")
                else:
                    cfg["api_base"] = arg.rstrip("/")
                    cfg["provider"] = "custom"
                    save_config(cfg)
                    agent_ref[0] = None
                    console.print(f"[green]{t('api_base_set_ok', url=cfg['api_base'])}[/green]")
            elif cmd == "/set_lang":
                if set_lang(arg):
                    cfg["lang"] = arg
                    save_config(cfg)
                    agent_ref[0] = None
                    console.print(f"[green]{t('lang_set_ok')}[/green]")
                else:
                    console.print(f"[yellow]{t('lang_invalid', lang=arg)}[/yellow]")
            elif cmd == "/providers":
                show_providers(cfg.get("provider", "deepseek"))
            elif cmd == "/clear":
                if agent_ref[0]:
                    agent_ref[0].clear()
                console.print(f"[green]{t('history_cleared')}[/green]")
            elif cmd == "/config":
                d = {k: v for k, v in cfg.items() if k != "api_key"}
                d["api_key"] = "***" if cfg.get("api_key") else t("api_key_display")
                console.print(json.dumps(d, indent=2, ensure_ascii=False))
            else:
                console.print(f"[yellow]{t('unknown_cmd', cmd=cmd)}[/yellow]")
        else:
            a = get_agent()
            if a:
                a.chat(user_input, max_turns=cfg.get("max_turns", 40))


if __name__ == "__main__":
    main()
