# DevCollab 项目

这是 DevCollab 多Agent协作智能软件开发助手系统的项目代码目录。

## 项目结构

本项目采用多服务架构，包含以下主要组件：

### 核心服务
- **backend/**: FastAPI后端服务，包含Agent系统、API接口、业务逻辑
- **frontend/**: Vue 3 + TypeScript前端界面
- **sandbox/**: 代码沙箱服务，负责安全执行用户代码

### 基础设施服务
- **PostgreSQL**: 主数据库，存储项目、任务、用户等数据
- **Redis**: 缓存和消息队列
- **Milvus**: 向量数据库，用于语义搜索和记忆存储
- **监控栈**: Prometheus + Grafana + Loki 用于系统监控和日志收集

## 目录结构详解

```
devcollab/
├── .env.example                    # 环境变量配置模板
├── README.md                       # 项目说明文档
├── docker-compose.yml              # Docker Compose编排文件
├── backend/                        # 后端服务目录
│   ├── app/                        # 应用主目录
│   │   ├── main.py                 # FastAPI应用入口
│   │   ├── agents/                 # Agent实现目录
│   │   │   ├── base.py             # Agent基类
│   │   │   ├── pm_agent.py         # PM Agent实现
│   │   │   ├── architect_agent.py  # 架构师Agent实现
│   │   │   ├── developer_agent.py  # 开发者Agent实现
│   │   │   ├── tester_agent.py     # 测试工程师Agent实现
│   │   │   └── reviewer_agent.py   # 代码审查员Agent实现
│   │   ├── core/                   # 核心模块
│   │   │   ├── orchestrator.py     # 工作流编排器
│   │   │   ├── state_manager.py    # 状态管理器
│   │   │   ├── message_bus.py      # 消息总线
│   │   │   └── quality_gate.py     # 质量门禁
│   │   ├── tools/                  # 工具集
│   │   │   ├── tool_registry.py    # 工具注册表
│   │   │   ├── code_editor.py      # 代码编辑器工具
│   │   │   ├── test_framework.py   # 测试框架工具
│   │   │   └── sandbox_executor.py # 沙箱执行工具
│   │   ├── memory/                 # 记忆模块
│   │   │   ├── memory_manager.py   # 记忆管理器
│   │   │   ├── short_term.py       # 短期记忆
│   │   │   └── long_term.py        # 长期记忆
│   │   ├── api/                    # API路由
│   │   │   ├── __init__.py
│   │   │   ├── projects.py         # 项目API
│   │   │   ├── tasks.py            # 任务API
│   │   │   └── agents.py           # Agent API
│   │   ├── models/                 # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── project.py          # 项目模型
│   │   │   ├── task.py             # 任务模型
│   │   │   └── user.py             # 用户模型
│   │   └── prompts/                # Prompt模板
│   │       ├── pm_prompts.py       # PM Agent提示词
│   │       ├── architect_prompts.py # 架构师提示词
│   │       ├── developer_prompts.py # 开发者提示词
│   │       ├── tester_prompts.py   # 测试工程师提示词
│   │       └── reviewer_prompts.py # 代码审查员提示词
│   ├── requirements.txt            # Python依赖包列表
│   └── tests/                      # 测试目录
├── frontend/                       # 前端服务目录
│   ├── src/                        # 源代码目录
│   │   ├── views/                  # 页面视图
│   │   │   ├── Home.vue            # 首页
│   │   │   ├── Projects.vue        # 项目管理页
│   │   │   ├── Tasks.vue           # 任务管理页
│   │   │   └── AgentConsole.vue    # Agent控制台
│   │   ├── components/             # 通用组件
│   │   │   ├── common/             # 通用组件
│   │   │   ├── layout/             # 布局组件
│   │   │   └── agent/              # Agent相关组件
│   │   ├── stores/                 # Pinia状态管理
│   │   │   ├── index.ts            # 状态管理入口
│   │   │   ├── project.ts          # 项目状态
│   │   │   ├── task.ts             # 任务状态
│   │   │   └── agent.ts            # Agent状态
│   │   ├── api/                    # API封装
│   │   │   ├── index.ts            # API入口
│   │   │   ├── project.ts          # 项目API
│   │   │   ├── task.ts             # 任务API
│   │   │   └── agent.ts            # Agent API
│   │   ├── composables/            # 组合式函数
│   │   │   ├── useWebSocket.ts     # WebSocket封装
│   │   │   ├── useCodeEditor.ts    # 代码编辑器封装
│   │   │   └── useAgentStream.ts   # Agent流式响应封装
│   │   └── types/                  # TypeScript类型定义
│   │       ├── index.ts            # 类型导出
│   │       ├── project.ts          # 项目类型
│   │       ├── task.ts             # 任务类型
│   │       └── agent.ts            # Agent类型
│   └── package.json                # 前端依赖包配置
└── sandbox/                        # 代码沙箱目录
    ├── manager.py                  # 沙箱管理器
    ├── executor.py                 # 代码执行器
    └── requirements.txt            # 沙箱依赖包列表
```

### 主要文件说明

#### 根目录文件
- **`.env.example`**: 环境变量配置模板，包含所有可配置参数
- **`README.md`**: 项目说明文档，包含快速启动、开发指南等信息
- **`docker-compose.yml`**: Docker Compose编排文件，定义所有服务及其依赖关系

#### 后端文件 (`backend/`)
- **`app/main.py`**: FastAPI应用入口，包含应用初始化、中间件、路由注册等
- **`app/agents/`**: 5个核心Agent的实现，每个Agent负责特定职责
- **`app/core/`**: 核心业务逻辑模块，包括工作流编排、状态管理等
- **`app/tools/`**: 工具集，为Agent提供各种能力（代码编辑、测试执行等）
- **`app/memory/`**: 记忆管理模块，支持短期和长期记忆存储
- **`app/api/`**: RESTful API路由定义，提供外部接口
- **`app/models/`**: 数据模型定义，对应数据库表结构
- **`app/prompts/`**: Prompt模板库，包含各Agent的提示词
- **`requirements.txt`**: Python依赖包列表，包含FastAPI、LangGraph、LLM SDK等

#### 前端文件 (`frontend/`)
- **`src/views/`**: 页面视图组件，对应不同功能页面
- **`src/components/`**: 可复用UI组件，按功能分类组织
- **`src/stores/`**: Pinia状态管理，管理应用全局状态
- **`src/api/`**: API客户端封装，提供类型安全的API调用
- **`src/composables/`**: 组合式函数，封装可复用逻辑
- **`src/types/`**: TypeScript类型定义，确保类型安全
- **`package.json`**: 前端依赖包配置，包含Vue 3、TypeScript、UI库等

#### 沙箱文件 (`sandbox/`)
- **`manager.py`**: 沙箱管理器，负责创建和管理隔离的执行环境
- **`executor.py`**: 代码执行器，提供代码执行、测试运行、质量分析等功能
- **`requirements.txt`**: 沙箱依赖包列表，包含Docker SDK、代码分析工具等

### 目录设计原则
1. **模块化设计**: 每个目录职责单一，便于维护和扩展
2. **分层架构**: 清晰的层次结构（表现层、业务层、数据层）
3. **可扩展性**: 支持新增Agent、工具、API等扩展
4. **类型安全**: 前后端均使用TypeScript/Python类型注解
5. **配置驱动**: 所有配置通过环境变量管理，便于部署

## 快速启动

### 使用 Docker Compose（推荐）

```bash
# 1. 复制环境变量模板
cp .env.example .env

# 2. 编辑 .env 文件，填入必要的API密钥
#    - OPENAI_API_KEY
#    - ANTHROPIC_API_KEY  
#    - QWEN_API_KEY

# 3. 启动所有服务
docker-compose up -d

# 4. 查看服务状态
docker-compose ps
```

### 服务访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端界面 | http://localhost:3000 | 主Web界面 |
| 后端API | http://localhost:8000 | REST API接口 |
| API文档 | http://localhost:8000/docs | Swagger UI |
| 数据库 | localhost:5432 | PostgreSQL |
| 缓存 | localhost:6379 | Redis |
| 监控面板 | http://localhost:3001 | Grafana (admin/admin) |
| 沙箱服务 | http://localhost:8080 | 代码执行沙箱 |

## 开发指南

### 后端开发

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行开发服务器
uvicorn app.main:app --reload --port 8000
```

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 运行开发服务器
npm run dev
```

### 沙箱开发

```bash
cd sandbox

# 安装依赖
pip install -r requirements.txt

# 运行测试
python -m pytest tests/
```

## 项目配置

### 环境变量

关键环境变量配置：

```bash
# LLM API密钥
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
QWEN_API_KEY=qwen-...

# 数据库连接
DATABASE_URL=postgresql://devcollab:devcollab@localhost:5432/devcollab
REDIS_URL=redis://localhost:6379/0
MILVUS_HOST=localhost
MILVUS_PORT=19530

# 应用配置
DEBUG=true
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 数据库迁移

```bash
# 进入后端目录
cd backend

# 运行数据库迁移
alembic upgrade head

# 创建新的迁移
alembic revision --autogenerate -m "描述变更"
```

## 测试

### 运行测试套件

```bash
# 后端测试
cd backend
pytest tests/ -v --cov=app --cov-report=html

# 前端测试
cd frontend
npm test

# 沙箱测试
cd sandbox
pytest tests/ -v
```

### 代码质量检查

```bash
# Python代码检查
ruff check .
ruff format --check .

# TypeScript代码检查
cd frontend
npm run lint
npm run type-check
```

## 部署

### 生产环境部署

1. 更新 `.env` 文件中的环境变量为生产值
2. 构建Docker镜像：
   ```bash
   docker-compose build --no-cache
   ```
3. 启动服务：
   ```bash
   docker-compose up -d
   ```
4. 验证服务健康状态：
   ```bash
   docker-compose ps
   curl http://localhost:8000/health
   ```

### 监控和日志

- Grafana仪表板：http://localhost:3001
- Prometheus指标：http://localhost:9090
- Loki日志查询：http://localhost:3100

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查PostgreSQL服务是否运行：`docker-compose ps postgres`
   - 验证连接字符串：`DATABASE_URL`环境变量

2. **Redis连接失败**
   - 检查Redis服务状态：`docker-compose ps redis`
   - 验证Redis配置

3. **LLM API调用失败**
   - 检查API密钥是否正确配置
   - 验证网络连接和API配额

4. **沙箱执行失败**
   - 检查Docker守护进程是否运行
   - 验证沙箱服务日志：`docker-compose logs sandbox`

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f sandbox
```

## 贡献指南

请参考父目录的 [DevCollab-README.md](../DevCollab-README.md) 中的贡献指南。

## 许可证

本项目基于 MIT 许可证开源。详见 [LICENSE](../LICENSE) 文件。