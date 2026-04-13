# 🎮 游戏服务器开发 AI Agent

AI 自主探索项目代码，实时参考已有业务模块，生成符合项目规范的代码。

## 原理

不做预分析、不总结经验。AI 通过工具自主探索项目代码、协议文件、配置表，找到相似的已有业务模块作为参考，严格模仿生成新代码。

## 工作流程

1. 用户提需求 → AI 生成需求确认清单 → 用户逐项确认
2. 需求确认后 → AI 并发生成 Excel 配置表、.proto 协议文件、数据库表设计 → 展示给用户确认
3. 用户确认设计 → 写入配置表和协议文件
4. AI 探索项目代码 → 生成业务代码 → 展示确认后写入

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```bash
python main.py
```

```
/set_key sk-your-deepseek-api-key
/set_project /path/to/your/game-server
/set_proto /path/to/proto/files
/set_excel /path/to/excel/configs
实现一个邮件系统，支持发送、领取附件、删除邮件
```

## 命令

| 命令 | 说明 |
|------|------|
| `/set_project <路径>` | 设置项目代码目录 |
| `/set_proto <路径>` | 设置协议文件(.proto)目录 |
| `/set_excel <路径>` | 设置配置表(Excel)目录 |
| `/set_key <key>` | 设置 API Key |
| `/set_model <模型>` | 设置模型（默认 deepseek-chat） |
| `/clear` | 清空对话 |
| `/config` | 查看配置 |
| `/quit` | 退出 |
