<p align="center">
  <h1 align="center">DevCollab</h1>
  <p align="center">
    <strong>多Agent协作智能软件开发助手系统</strong>
  </p>
  <p align="center">
    模拟真实软件团队协作，从需求分析到代码交付全流程自动化
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Vue-3.4+-green.svg" alt="Vue">
  <img src="https://img.shields.io/badge/FastAPI-0.110+-teal.svg" alt="FastAPI">
  <img src="https://img.shields.io/badge/LangGraph-0.2+-purple.svg" alt="LangGraph">
  <img src="https://img.shields.io/badge/License-MIT-orange.svg" alt="License">
</p>

---

## 项目简介

**DevCollab** 是一个基于多Agent协作架构的智能软件开发助手。它模拟真实软件开发团队中的多个角色，通过Agent间的协作与对话，自动完成从需求分析到代码交付的全流程任务。

只需输入自然语言需求，系统将自动完成：

```
用户需求 → 需求拆解 → 方案设计 → 代码编写 → 测试执行 → 代码审查 → 交付
```

## 核心特性

- **5个专业Agent**：PM、架构师、开发者、测试工程师、代码审查员各司其职
- **端到端自动化**：从自然语言需求到可运行代码+测试+审查报告
- **迭代优化**：代码审查/测试不通过时自动迭代修复（最多3轮）
- **安全沙箱**：代码在Docker容器中隔离执行，确保系统安全
- **流式输出**：代码生成过程实时展示，体验流畅
- **可扩展架构**：Agent和工具均可插拔替换，支持自定义Agent角色

## 系统架构

```
┌─────────────────────────────────────────────────┐
│              Vue 3 + TypeScript Web UI           │
├─────────────────────────────────────────────────┤
│            FastAPI REST API + WebSocket          │
├─────────────────────────────────────────────────┤
│           LangGraph Agent 编排引擎               │
│  ┌──────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ PM   │ │Architect │ │Developer│ │ Tester │ │
│  │Agent │ │  Agent   │ │  Agent  │ │ Agent  │ │
│  └──────┘ └──────────┘ └──────────┘ └────────┘ │
│  ┌──────────┐                                    │
│  │ Reviewer │                                    │
│  │  Agent   │                                    │
│  └──────────┘                                    │
├─────────────────────────────────────────────────┤
│  PostgreSQL │ Redis │ Milvus │ Docker Sandbox    │
└─────────────────────────────────────────────────┘
```

## Agent 角色

| Agent | 角色 | 职责 |
|-------|------|------|
| **PM Agent** | 产品经理 | 需求理解、任务拆解、优先级排序、验收标准生成 |
| **Architect Agent** | 架构师 | 技术方案设计、API接口设计、数据模型设计、技术选型 |
| **Developer Agent** | 开发者 | 代码生成、Bug修复、代码重构、多语言支持 |
| **Tester Agent** | 测试工程师 | 测试用例生成、自动化测试执行、覆盖率统计 |
| **Reviewer Agent** | 代码审查员 | 代码质量审查、安全漏洞检测、性能问题检测 |

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Vite + Pinia |
| 后端 | FastAPI (Python 3.11+) |
| Agent框架 | LangGraph |
| LLM | GPT-4o / Claude 3.5 / Qwen |
| 数据库 | PostgreSQL 16 |
| 缓存/队列 | Redis 7 |
| 向量数据库 | Milvus 2.3 |
| 容器化 | Docker + Docker Compose |
| 代码质量 | Ruff / Pylint |

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- Docker 24+
- Docker Compose 2.20+

### 安装部署

```bash
# 1. 克隆项目
git clone https://github.com/your-org/devcollab.git
cd devcollab

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 LLM API Key 等配置

# 3. 一键启动所有服务
docker-compose up -d

# 4. 查看服务状态
docker-compose ps
```

### 访问服务

| 服务 | 地址 |
|------|------|
| 前端界面 | http://localhost:3000 |
| 后端API | http://localhost:8000 |
| API文档 | http://localhost:8000/docs |

### 本地开发

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 前端
cd frontend
npm install
npm run dev
```

## 项目结构

```
devcollab/
├── docker-compose.yml
├── README.md
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI入口
│   │   ├── agents/                 # Agent实现
│   │   │   ├── base.py             # Agent基类
│   │   │   ├── pm_agent.py
│   │   │   ├── architect_agent.py
│   │   │   ├── developer_agent.py
│   │   │   ├── tester_agent.py
│   │   │   └── reviewer_agent.py
│   │   ├── core/                   # 核心模块
│   │   │   ├── orchestrator.py     # 工作流编排器
│   │   │   ├── state_manager.py
│   │   │   ├── message_bus.py
│   │   │   └── quality_gate.py
│   │   ├── tools/                  # 工具集
│   │   ├── memory/                 # 记忆模块
│   │   ├── api/                    # API路由
│   │   ├── models/                 # 数据模型
│   │   └── prompts/                # Prompt模板
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── views/                  # 页面视图
│   │   ├── components/             # 通用组件
│   │   ├── stores/                 # Pinia状态管理
│   │   ├── api/                    # API封装
│   │   ├── composables/            # 组合式函数
│   │   └── types/                  # TypeScript类型
│   └── package.json
└── sandbox/
    ├── manager.py                  # 沙箱管理器
    └── executor.py
```

## 使用示例

### 基本使用

```
用户: 帮我实现一个用户登录功能，支持邮箱和密码登录

系统自动执行:
  PM Agent      → 拆解为5个子任务（数据库设计、API开发、前端页面等）
  Architect     → 设计技术方案（FastAPI + JWT + PostgreSQL）
  Developer     → 生成完整代码（含类型定义、错误处理、注释）
  Tester        → 生成并执行测试（覆盖率85%）
  Reviewer      → 代码审查通过，安全评分A

交付物: 完整代码 + 测试用例 + 测试报告 + 审查报告
```

### API调用示例

```bash
# 创建项目
curl -X POST http://localhost:8000/api/projects \
  -H "Authorization: Bearer <token>" \
  -d '{"name": "my-project", "tech_stack": "Python/FastAPI"}'

# 提交开发任务
curl -X POST http://localhost:8000/api/projects/{id}/tasks \
  -H "Authorization: Bearer <token>" \
  -d '{"requirement": "实现用户注册功能"}'
```

## 功能概览

| 模块 | 功能 | 状态 |
|------|------|------|
| Agent协作引擎 | 5个专业Agent协作开发 | MVP |
| 工作流管理 | 顺序流水线 + 迭代优化 | MVP |
| 代码沙箱 | Docker隔离执行 + 多语言环境 | MVP |
| 记忆系统 | 短期记忆 + 上下文管理 | MVP |
| 长期记忆 | 跨会话持久化 + 语义检索 | V1.1 |
| 文档生成 | README / API文档 / 架构文档 | V1.1 |
| Git集成 | 自动Commit / PR / 分支管理 | V1.1 |
| 可视化 | Agent状态面板 + 工作流图 | V1.2 |
| 自定义Agent | 用户自定义Agent角色 | V1.2 |
| 插件生态 | 工具/Agent插件体系 | V2.0 |

## 版本规划

| 版本 | 时间 | 目标 |
|------|------|------|
| **MVP** | 第3-6周 | 端到端多Agent协作流程可用 |
| **V1.1** | 第7-10周 | 记忆增强 + Git集成 + 文档生成 |
| **V1.2** | 第11-14周 | 自定义Agent + 可视化 + 性能优化 |
| **V2.0** | 第15-18周 | 插件生态 + 多项目并行 + 开源发布 |

## 项目文档

| 文档 | 说明 |
|------|------|
| [PRD](./DevCollab-PRD.md) | 产品需求文档 |
| [系统架构文档](./DevCollab-系统架构文档.md) | 系统架构设计 |
| [功能清单文档](./DevCollab-功能清单文档.md) | 111项功能详细清单 |
| [项目里程碑文档](./DevCollab-项目里程碑文档.md) | 18周开发里程碑规划 |
| [AGENTS.md](./DevCollab-AGENTS.md) | Agent系统设计与实现指南 |

## 贡献指南

欢迎参与 DevCollab 的开发！请阅读 [贡献指南](./CONTRIBUTING.md) 了解：

1. Fork 本仓库并创建特性分支
2. 遵循项目的代码规范（Ruff + ESLint）
3. 为新功能编写测试用例
4. 提交 Pull Request 并通过 CI 检查

## 开源协议

本项目基于 [MIT](./LICENSE) 协议开源。
