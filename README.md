# CogniForge

> **AI时代开发者认知增强引擎** — 让AI工具记住你的每一个决策

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-orange.svg)](https://github.com/lanekingkong/cogniforge)

[English](README_EN.md) | [文档](docs/5W1H_ARCHITECTURE.md)

---

## 痛点：AI工具时代的开发者困境

| 痛点 | 数据 | CogniForge 解法 |
|------|------|-----------------|
| **会话间记忆断裂** | 开发者每周损失 3.2 小时重述上下文 | 记忆宫殿引擎 - 持久化、可检索的决策历史 |
| **Token 消耗爆炸** | 40 文件项目需 47,450 tokens 建立上下文 | 智能上下文压缩 - 节省 60-95% token |
| **多工具知识孤岛** | 88% 开发者因切换工具降低效率 | 跨工具同步桥接 - Claude/Cursor/Copilot 统一上下文 |
| **代码遗忘曲线** | 3 个月后只能回忆 20% 项目关键决策 | 知识图谱引擎 - 零 LLM 调用的代码结构索引 |

## 核心能力

### 1. 记忆宫殿引擎 (Memory Palace)
```
Palace（宫殿）
 ├── Wing（翼：按项目/模块分区）
 │   ├── Hall（走廊：decisions/patterns/knowledge/fixes/context）
 │   │   ├── Room（房间：具体主题）
 │   │   │   ├── Memory（记忆条目）
```
- **自动记忆巩固**：合并重复记忆，减少碎片化
- **语义搜索**：基于 LanceDB 向量存储的关键词和语义搜索
- **访问热度排序**：最常访问的记忆优先展示

### 2. 代码知识图谱引擎 (Knowledge Graph)
- **零 LLM 调用**：纯 AST 解析，不消耗 token
- **自动构建索引**：扫描项目生成函数/类/模块关系图
- **依赖关系追踪**：继承链、调用链一目了然
- **增量更新**：仅重新索引变更文件

### 3. 智能上下文压缩 (Context Compressor)
- **Level 1 - 摘要层**（~200 tokens）：项目概述
- **Level 2 - 结构层**（~500 tokens）：目录树 + 关键接口
- **Level 3 - 细节层**（按需加载）：记忆 + 焦点文件
- **自适应压缩**：超过 token 限制自动裁剪

### 4. 跨工具同步桥接 (Sync Bridge)
| 工具 | 同步路径 | 格式 |
|------|----------|------|
| Claude Code | `.claude/skills/cogniforge/` | Markdown Skill |
| Cursor | `.cursor/rules/` | MDC Rule |
| GitHub Copilot | `.github/copilot-instructions.md` | Markdown 指令 |
| 通用 MCP | `localhost:8765` | JSON-RPC |

## 快速开始

### 安装

```bash
# 从源码安装
git clone https://github.com/lanekingkong/cogniforge.git
cd cogniforge
pip install -e .

# 安装完整依赖
pip install -e ".[dev]"
```

### 30 秒上手

```bash
# 1. 初始化项目
cogniforge init ./my-project

# 2. 记录一条记忆
cogniforge memory remember "使用 FastAPI 作为 Web 框架" --topic "技术选型" --hall decisions

# 3. 查看记忆
cogniforge memory recall "FastAPI"

# 4. 构建代码知识图谱
cogniforge graph build

# 5. 搜索代码
cogniforge graph search "Database"

# 6. 同步到 AI 工具
cogniforge sync all

# 7. 获取压缩上下文
cogniforge index context --level 2
```

## 项目架构

```
cogniforge/
├── src/
│   ├── core/                    # 核心引擎
│   │   ├── memory_engine.py     # 记忆宫殿引擎
│   │   ├── knowledge_graph.py   # 代码知识图谱
│   │   ├── context_compressor.py # 上下文压缩
│   │   └── sync_bridge.py       # 跨工具同步
│   ├── storage/                 # 存储层
│   │   ├── vector_store.py      # LanceDB 向量存储
│   │   ├── graph_store.py       # SQLite 图谱存储
│   │   └── local_db.py          # 本地元数据存储
│   ├── cli/                     # CLI 入口
│   │   └── main.py              # Typer CLI
│   └── adapters/                # 适配器（预留）
├── skills_builtin/              # 内置 AI 技能
│   ├── project_onboarding.yaml  # 项目知识问答
│   ├── change_tracker.yaml      # 变更追踪
│   ├── prompt_enhancer.yaml     # Prompt 增强
│   └── code_review.yaml         # 智能代码审查
├── tests/                       # 测试
│   ├── test_core.py             # 核心引擎测试
│   └── conftest.py              # 测试配置
├── examples/                    # 示例
│   └── usage.py                 # 完整使用示例
└── docs/
    └── 5W1H_ARCHITECTURE.md     # 架构文档
```

## 技术栈

| 层 | 技术 | 用途 |
|---|------|------|
| 向量存储 | LanceDB + Sentence-Transformers | 语义搜索 |
| 图谱存储 | SQLite + NetworkX | 关系查询 |
| 解析层 | Python AST | 零 LLM 代码分析 |
| CLI | Typer + Rich | 终端交互 |
| 同步协议 | MCP (FastMCP) / 文件监听 (Watchdog) | 跨工具通信 |
| 测试 | Pytest | 单元测试 |

## API 使用

```python
from cogniforge.core.memory_engine import jiyigongdian
from cogniforge.core.knowledge_graph import zhishitupu

# 记忆引擎
jiyi = jiyigongdian('./my-project')
jiyi.jilu("选择 Redis 作为缓存方案", "缓存选型", hall_type="decisions")
jiyi.huiqu("Redis")

# 知识图谱
tupu = zhishitupu('./my-project')
tupu.goujian_suoyin()
tupu.chaxun("cache")
```

## 版本规划

- **v0.1.0** (当前): 核心四大引擎 + CLI + 内置技能
- **v0.2.0**: 向量语义搜索增强 + 增量图谱更新
- **v0.3.0**: MCP服务器正式版 + IDE插件
- **v1.0.0**: 跨项目智能推荐 + 团队共享记忆

## 贡献

欢迎提交 Issue 和 PR！请参考 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

MIT License © 2026 lanekingkong

---

> *"程序员的记忆不应局限于一个会话窗口"*
>
> CogniForge 让 AI 工具真正理解你的项目历史，不再从零开始。
