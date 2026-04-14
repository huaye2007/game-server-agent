"""配置管理"""
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".game-server-agent"
CONFIG_FILE = CONFIG_DIR / "config.json"

# 预设的模型提供商配置
# 所有提供商都兼容 OpenAI SDK，通过 api_base 区分
PROVIDERS = {
    "deepseek": {
        "api_base": "https://api.deepseek.com",
        "default_model": "deepseek-chat",
        "models": ["deepseek-chat", "deepseek-reasoner"],
    },
    "openai": {
        "api_base": "https://api.openai.com/v1",
        "default_model": "gpt-5.4",
        "models": ["gpt-5.4", "gpt-5.4-mini", "gpt-5.4-nano", "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "o3", "o4-mini"],
    },
    "claude": {
        "api_base": "https://api.anthropic.com/v1",
        "default_model": "claude-opus-4-6",
        "models": ["claude-opus-4-6", "claude-sonnet-4-6", "claude-haiku-4-5"],
        "extra": {"is_anthropic": True},
    },
    "gemini": {
        "api_base": "https://generativelanguage.googleapis.com/v1beta/openai",
        "default_model": "gemini-3.1-pro-preview",
        "models": ["gemini-3.1-pro-preview", "gemini-3.1-flash-preview", "gemini-3.1-flash-lite-preview", "gemini-2.5-pro", "gemini-2.5-flash"],
    },
    "glm": {
        "api_base": "https://open.bigmodel.cn/api/paas/v4",
        "default_model": "glm-5",
        "models": ["glm-5", "glm-5v-turbo", "glm-4-plus", "glm-4-flash"],
    },
    "kimi": {
        "api_base": "https://api.moonshot.ai/v1",
        "default_model": "moonshot-v1-kimi-k2",
        "models": ["moonshot-v1-kimi-k2", "moonshot-v1-auto", "moonshot-v1-128k", "moonshot-v1-32k"],
    },
    "minimax": {
        "api_base": "https://api.minimax.chat/v1",
        "default_model": "MiniMax-M2.7",
        "models": ["MiniMax-M2.7", "MiniMax-M2.7-highspeed", "MiniMax-M2.5", "MiniMax-M2.5-highspeed"],
    },
    "custom": {
        "api_base": "",
        "default_model": "",
        "models": [],
    },
}

DEFAULT_CONFIG = {
    "api_key": "",
    "provider": "deepseek",
    "api_base": "https://api.deepseek.com",
    "model": "deepseek-chat",
    "project_path": "",
    "proto_path": "",
    "excel_path": "",
    "lang": "zh",
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
