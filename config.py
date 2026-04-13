"""配置管理"""
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".game-server-agent"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "api_key": "",
    "api_base": "https://api.deepseek.com",
    "model": "deepseek-chat",
    "project_path": "",
    "proto_path": "",
    "excel_path": "",
    "ignore_dirs": [
        "node_modules", ".git", "__pycache__", "target",
        "build", "dist", ".idea", ".vscode", "vendor", "bin",
    ],
    "max_turns": 40,
}


def load_config() -> dict:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    return dict(DEFAULT_CONFIG)


def save_config(cfg: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
