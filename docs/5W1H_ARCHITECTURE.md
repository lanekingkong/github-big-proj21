# CogniForge - 5W1H Architecture Document

## WHAT - 项目定义

**CogniForge** 是一个面向AI时代开发者的认知增强引擎（Cognitive Enhancement Engine for AI-Era Developers）。它融合四大核心能力：

1. **AI记忆系统（Memory Palace Engine）** - 借鉴MemPalace/mem0/GBrain的记忆宫殿架构，实现分层空间记忆
2. **代码知识图谱（Code Knowledge Graph）** - 借鉴codegraph/Understand-Anything，构建代码库的结构化语义索引
3. **智能上下文压缩（Context Compressor）** - 借鉴Headroom，节省60-95%的Token消耗
4. **跨AI工具同步（Cross-Tool Sync Bridge）** - 解决多AI工具间知识孤岛问题

项目定位：本地优先、MIT开源、可插拔架构。

## WHY - 为什么需要 CogniForge

### 核心痛点

| 痛点 | 现状 | 数据支撑 |
|------|------|----------|
| AI会话间记忆断裂 | 每次新对话AI都失忆，需重复交代项目背景 | 开发者每周平均损失3.2小时重述上下文 |
| Token消耗爆炸 | 40文件FastAPI项目需47450 tokens才能建立上下文 | Headroom报告可节省60-95% token |
| 多工具知识孤岛 | 88%开发者因切换工具降低效率 | Cursor/Claude/Copilot间数据零互通 |
| 记忆不可持久化 | 传统RAG仅存分块，不存语义关联 | 向量搜索与关键词搜索本质差异 |
| AI治理缺失 | 无审计追踪, 无记忆版本控制 | 66%企业关注但仅37%有安全审查 |

### 市场时机

- MemPalace上线13天获47K+ stars
- mem0达55K+ stars
- GBrain上线24小时5400 stars
- Claude Code Skills生态月增65K+ stars

记忆层正从可选插件变为Agent架构基础设施。

## WHO - 目标用户

### 核心用户画像

1. **AI辅助开发者** - 使用Claude Code/Cursor/Copilot的工程师
2. **技术团队负责人** - 需要团队知识沉淀和AI治理的Tech Lead
3. **独立开发者/创业者** - 一人团队需要AI辅助全栈开发
4. **开源项目维护者** - 需要让新贡献者快速理解代码库

### 用户故事

- "我昨天和Claude讨论的架构决策，今天Cursor完全不知道" → CogniForge同步
- "每次打开新会话都要重新解释项目结构" → 记忆持久化
- "Token账单每月爆表" → 上下文压缩
- "团队新人看不懂老代码" → 知识图谱可视化

## WHEN - 时间节点

- 项目启动：2026年6月7日
- v0.1 Alpha：核心记忆引擎 + CLI
- v0.5 Beta：知识图谱 + 上下文压缩
- v1.0 Release：完整功能 + 多适配器

## WHERE - 部署架构

### 本地优先（Local-First）

- 数据存储在本地 `~/.cogniforge/`
- 支持SQLite + LanceDB双后端
- 可选团队同步至私有服务器
- 零数据外泄，完全隐私

### 跨工具覆盖

```
CogniForge Core
├── Claude Code Adapter → .claude/skills/cogniforge/
├── Cursor Adapter → .cursor/rules/cogniforge/
├── GitHub Copilot Adapter → .github/copilot-instructions.md
├── Cline/OpenClaw Adapter → MCP Server
└── Generic MCP → 标准MCP协议
```

## HOW - 技术架构

### 核心架构图

```
┌─────────────────────────────────────────────────┐
│                  CogniForge CLI                   │
├─────────────────────────────────────────────────┤
│  Memory Palace │ Knowledge Graph │ Context Comp  │
│     Engine     │     Engine      │    Engine     │
├─────────────────────────────────────────────────┤
│              Sync Bridge (MCP + REST)             │
├─────────────────────────────────────────────────┤
│         Adapters Layer (Claude/Cursor/...)        │
├─────────────────────────────────────────────────┤
│         Storage Layer (LanceDB + SQLite)          │
└─────────────────────────────────────────────────┘
```

### 1. Memory Palace Engine（记忆宫殿引擎）

借鉴MemPalace的空间记忆模型：

```
Palace（宫殿）
 ├── Wing: 项目A（按项目/主题划分）
 │   ├── Hall: 架构决策（记忆类型）
 │   │   ├── Room: 数据库选型（具体主题）
 │   │   │   ├── Memory: 为什么选PostgreSQL而非MySQL
 │   │   │   └── Memory: 连接池配置决策
 │   │   └── Room: API设计
 │   └── Hall: 代码模式
 ├── Wing: 项目B
 └── Wing: 个人知识库
```

关键特性：
- AAAK压缩语言：AI-native缩写系统减少存储成本
- 记忆关联检索：不是向量相似度，而是空间位置导航
- 记忆巩固周期：夜间自动整理碎片化记忆

### 2. Knowledge Graph Engine（知识图谱引擎）

借鉴codegraph + GBrain的零LLM自布线：

- **代码实体提取**：函数/类/模块自动识别
- **依赖关系建模**：调用链、数据流、继承关系
- **增量更新**：Git Hook触发自动更新图谱
- **语义搜索**：自然语言查询代码位置

### 3. Context Compressor（上下文压缩引擎）

借鉴Headroom的分层压缩：

- **Level 1 - 摘要**：项目简介（~200 tokens）
- **Level 2 - 结构**：目录树+关键接口（~500 tokens）
- **Level 3 - 细节**：当前焦点文件（按需加载）
- **动态展开**：AI需要时自动展开更深层级

### 4. Sync Bridge（跨工具同步桥接）

- **MCP Server**：标准MCP协议，兼容所有MCP客户端
- **文件监听**：Watch .claude/ .cursor/ .github/ 目录变化
- **知识导出**：生成各工具格式的配置文件
- **冲突解决**：多工具同时写入时自动合并

### 技术选型

| 组件 | 技术 | 理由 |
|------|------|------|
| 向量存储 | LanceDB | 零依赖、本地嵌入、支持增量索引 |
| 图谱存储 | NetworkX + SQLite | 轻量、Python原生、易于查询 |
| 嵌入模型 | all-MiniLM-L6-v2 | 384维、本地运行、无需GPU |
| CLI框架 | Typer + Rich | 优雅终端UI、自动补全 |
| MCP协议 | FastMCP | Python原生MCP SDK |
| 文件监听 | Watchdog | 跨平台文件系统事件 |

### API设计

```python
# 核心API
cogniforge init          # 初始化项目记忆
cogniforge remember      # 手动记录一条记忆
cogniforge recall        # 搜索/召回记忆
cogniforge graph         # 构建/查询知识图谱
cogniforge compress      # 压缩项目上下文
cogniforge sync          # 同步到各AI工具
cogniforge serve         # 启动MCP Server

# Python SDK
from cogniforge import MemoryPalace, KnowledgeGraph, ContextCompressor

palace = MemoryPalace("./my-project")
palace.remember("架构决策", "选择FastAPI作为Web框架", wing="backend")
results = palace.recall("为什么选择FastAPI")

kg = KnowledgeGraph("./my-project")
kg.build_index()
results = kg.search("处理用户认证的代码在哪里")

compressor = ContextCompressor("./my-project")
context = compressor.get_context(level=2)  # 返回压缩后的上下文
```

### 项目结构

```
CogniForge/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── memory_engine.py      # 记忆宫殿核心
│   │   ├── knowledge_graph.py    # 代码知识图谱
│   │   ├── context_compressor.py  # 上下文压缩
│   │   └── sync_bridge.py        # 跨工具同步
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base_adapter.py       # 适配器基类
│   │   ├── claude_adapter.py     # Claude Code适配
│   │   ├── cursor_adapter.py     # Cursor适配
│   │   └── copilot_adapter.py    # Copilot适配
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── vector_store.py       # LanceDB向量存储
│   │   ├── graph_store.py        # 图谱持久化
│   │   └── local_db.py           # SQLite元数据
│   ├── ui/
│   │   ├── __init__.py
│   │   └── dashboard.py          # 终端仪表盘
│   └── cli/
│       ├── __init__.py
│       └── main.py               # CLI入口
├── skills_builtin/
│   ├── code_review.py            # 代码审查技能
│   ├── onboarding.py             # 新人入门技能
│   └── architecture.py           # 架构决策记录
├── tests/
│   ├── test_memory_engine.py
│   ├── test_knowledge_graph.py
│   ├── test_context_compressor.py
│   └── test_sync_bridge.py
├── examples/
│   ├── basic_usage.py
│   ├── team_sync.py
│   └── advanced_graph.py
├── docs/
│   ├── 5W1H_ARCHITECTURE.md
│   ├── API_REFERENCE.md
│   ├── USER_GUIDE_CN.md
│   └── USER_GUIDE_EN.md
├── README.md
├── README_EN.md
├── setup.py
├── requirements.txt
├── pyproject.toml
├── LICENSE
└── .gitignore
```
