# DevCollab - Agent 系统文档

> **版本**: v1.0  
> **日期**: 2026-05-11  
> **作者**: AI应用开发团队  
> **关联文档**: PRD / 系统架构文档 / 功能清单文档

---

## 目录

1. [Agent 系统概述](#1-agent-系统概述)
2. [Agent 基类设计](#2-agent-基类设计)
3. [PM Agent (产品经理)](#3-pm-agent-产品经理)
4. [Architect Agent (架构师)](#4-architect-agent-架构师)
5. [Developer Agent (开发者)](#5-developer-agent-开发者)
6. [Tester Agent (测试工程师)](#6-tester-agent-测试工程师)
7. [Reviewer Agent (代码审查员)](#7-reviewer-agent-代码审查员)
8. [Agent 协作模式](#8-agent-协作模式)
9. [Agent 扩展指南](#9-agent-扩展指南)

---

## 1. Agent 系统概述

### 1.1 设计理念

DevCollab 采用 **Multi-Agent Collaboration** 架构，模拟真实软件开发团队的协作模式：

- **角色专业化**: 每个 Agent 专注于一个领域，职责单一、边界清晰
- **协作式决策**: Agent 之间通过消息传递协作，而非单 Agent 包揽全部
- **可观测性**: 每个 Agent 的决策过程透明可见，便于调试和学习
- **可扩展性**: 新 Agent 可通过继承基类快速接入系统

### 1.2 Agent 角色总览

```
┌─────────────────────────────────────────────────────────────┐
│                     DevCollab Agent 系统                     │
├─────────────┬─────────────┬─────────────────────────────────┤
│   Agent     │    角色      │           核心职责               │
├─────────────┼─────────────┼─────────────────────────────────┤
│ PM Agent    │ 产品经理     │ 需求理解、任务拆解、优先级排序    │
├─────────────┼─────────────┼─────────────────────────────────┤
│ Architect   │ 架构师       │ 技术方案设计、架构决策、技术选型  │
├─────────────┼─────────────┼─────────────────────────────────┤
│ Developer   │ 开发者       │ 代码编写、Bug修复、代码重构      │
├─────────────┼─────────────┼─────────────────────────────────┤
│ Tester      │ 测试工程师   │ 测试用例生成、自动化测试、缺陷报告│
├─────────────┼─────────────┼─────────────────────────────────┤
│ Reviewer    │ 代码审查员   │ 代码审查、质量评估、安全检测     │
└─────────────┴─────────────┴─────────────────────────────────┘
```

### 1.3 Agent 协作流程

```
用户输入需求
    │
    ▼
┌─────────────┐
│  PM Agent   │ ──▶ 输出: 结构化任务列表
│ (需求分析)  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Architect  │ ──▶ 输出: 技术方案文档
│   Agent     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Developer  │ ──▶ 输出: 完整代码
│   Agent     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Tester    │ ──▶ 输出: 测试报告
│   Agent     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Reviewer   │ ──▶ 输出: 审查报告
│   Agent     │
└──────┬──────┘
       │
       ▼
   质量门禁检查
       │
  ┌────┴────┐
  │         │
 Pass     Fail
  │         │
  ▼         ▼
交付用户   返回 Developer 修复
```

---

## 2. Agent 基类设计

### 2.1 BaseAgent 抽象类

所有 Agent 必须继承 `BaseAgent`，实现统一的生命周期接口。

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class AgentStatus(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    OBSERVING = "observing"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class TaskContext:
    """任务上下文"""
    task_id: str
    project_id: str
    user_requirement: str
    task_list: List[Dict[str, Any]]
    current_task: Dict[str, Any]
    artifacts: Dict[str, Any]  # 上游 Agent 的产物
    memory: Dict[str, Any]     # 记忆上下文
    
@dataclass
class Thought:
    """思考结果"""
    content: str
    reasoning: str
    plan: List[str]
    
@dataclass
class Action:
    """行动指令"""
    tool_name: str
    tool_input: Dict[str, Any]
    expected_output: str
    
@dataclass
class Observation:
    """观察结果"""
    tool_output: Any
    success: bool
    error_message: Optional[str]
    
@dataclass
class AgentResult:
    """Agent 执行结果"""
    success: bool
    output: Any
    artifacts: Dict[str, Any]
    logs: List[str]
    token_usage: int
    duration_ms: int

class BaseAgent(ABC):
    """
    Agent 基类
    
    所有 Agent 必须继承此类，实现 think/act/observe 三个核心方法。
    生命周期: on_receive -> think -> act -> observe -> on_complete
    """
    
    # Agent 元信息
    name: str = "BaseAgent"
    role: str = "基础Agent"
    description: str = "Agent基类，不应直接实例化"
    
    # 能力配置
    available_tools: List[str] = []
    max_iterations: int = 10
    
    def __init__(self, llm_client, tool_registry, memory_manager):
        """
        初始化 Agent
        
        Args:
            llm_client: LLM 客户端实例
            tool_registry: 工具注册表
            memory_manager: 记忆管理器
        """
        self.llm = llm_client
        self.tools = tool_registry
        self.memory = memory_manager
        self.status = AgentStatus.IDLE
        self.iteration_count = 0
        
    @abstractmethod
    async def think(self, context: TaskContext) -> Thought:
        """
        思考阶段: 分析输入，制定计划
        
        Args:
            context: 任务上下文
            
        Returns:
            Thought: 思考结果，包含推理过程和行动计划
        """
        pass
    
    @abstractmethod
    async def act(self, thought: Thought) -> Action:
        """
        行动阶段: 根据思考结果执行工具调用
        
        Args:
            thought: 思考结果
            
        Returns:
            Action: 行动指令
        """
        pass
    
    @abstractmethod
    async def observe(self, action: Action, result: Any) -> Observation:
        """
        观察阶段: 评估行动结果
        
        Args:
            action: 执行的行动
            result: 工具执行结果
            
        Returns:
            Observation: 观察结果
        """
        pass
    
    async def on_receive(self, context: TaskContext) -> AgentResult:
        """
        接收任务入口
        
        Args:
            context: 任务上下文
            
        Returns:
            AgentResult: 执行结果
        """
        self.status = AgentStatus.THINKING
        start_time = time.time()
        
        try:
            # 思考
            thought = await self.think(context)
            
            # 行动
            self.status = AgentStatus.ACTING
            action = await self.act(thought)
            tool_result = await self.tools.execute(action.tool_name, action.tool_input)
            
            # 观察
            self.status = AgentStatus.OBSERVING
            observation = await self.observe(action, tool_result)
            
            # 完成
            self.status = AgentStatus.COMPLETED
            return AgentResult(
                success=observation.success,
                output=observation.tool_output,
                artifacts=self._collect_artifacts(),
                logs=self._get_logs(),
                token_usage=self.llm.get_token_usage(),
                duration_ms=int((time.time() - start_time) * 1000)
            )
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            return AgentResult(
                success=False,
                output=None,
                artifacts={},
                logs=self._get_logs() + [str(e)],
                token_usage=self.llm.get_token_usage(),
                duration_ms=int((time.time() - start_time) * 1000)
            )
    
    def _collect_artifacts(self) -> Dict[str, Any]:
        """收集产物"""
        return {}
    
    def _get_logs(self) -> List[str]:
        """获取日志"""
        return []
```

### 2.2 Agent 配置规范

```python
# config/agents.yaml
agents:
  pm_agent:
    name: "PM Agent"
    role: "产品经理"
    model: "gpt-4o"
    temperature: 0.3
    max_tokens: 4000
    tools:
      - requirement_parser
      - task_decomposer
    memory:
      short_term: true
      long_term: true
      
  architect_agent:
    name: "Architect Agent"
    role: "架构师"
    model: "gpt-4o"
    temperature: 0.2
    max_tokens: 8000
    tools:
      - code_search
      - dependency_analyzer
      - architecture_template
    memory:
      short_term: true
      long_term: true
      
  developer_agent:
    name: "Developer Agent"
    role: "开发者"
    model: "gpt-4o"
    temperature: 0.1
    max_tokens: 8000
    tools:
      - code_editor
      - terminal
      - code_search
      - dependency_manager
    memory:
      short_term: true
      long_term: true
      
  tester_agent:
    name: "Tester Agent"
    role: "测试工程师"
    model: "gpt-4o"
    temperature: 0.2
    max_tokens: 6000
    tools:
      - test_framework
      - coverage_tool
      - sandbox_executor
    memory:
      short_term: true
      long_term: false
      
  reviewer_agent:
    name: "Reviewer Agent"
    role: "代码审查员"
    model: "gpt-4o"
    temperature: 0.1
    max_tokens: 6000
    tools:
      - linter
      - security_scanner
      - complexity_analyzer
    memory:
      short_term: true
      long_term: false
```

---

## 3. PM Agent (产品经理)

### 3.1 角色定义

| 属性 | 描述 |
|------|------|
| **名称** | PM Agent |
| **角色** | 产品经理 |
| **职责** | 需求理解、任务拆解、优先级排序、验收标准生成 |
| **输入** | 用户自然语言需求、项目上下文 |
| **输出** | 结构化任务列表（含优先级、依赖关系、验收标准） |

### 3.2 核心能力

```
┌─────────────────────────────────────────────────────────────┐
│                      PM Agent 能力矩阵                        │
├─────────────────┬───────────────────────────────────────────┤
│ 需求解析         │ 从自然语言中提取功能点、约束条件、业务规则   │
├─────────────────┼───────────────────────────────────────────┤
│ 需求澄清         │ 对模糊需求发起多轮对话，明确边界和细节        │
├─────────────────┼───────────────────────────────────────────┤
│ 任务拆解         │ 将需求拆分为可执行的原子任务                 │
├─────────────────┼───────────────────────────────────────────┤
│ 优先级排序       │ 根据依赖关系、重要性、复杂度排序              │
├─────────────────┼───────────────────────────────────────────┤
│ 验收标准生成     │ 为每个任务生成明确的验收标准                 │
├─────────────────┼───────────────────────────────────────────┤
│ 复杂度评估       │ 评估每个任务的开发复杂度和预估工时            │
└─────────────────┴───────────────────────────────────────────┘
```

### 3.3 输出格式

```json
{
  "requirement_analysis": {
    "summary": "需求摘要",
    "functional_requirements": ["功能点1", "功能点2"],
    "non_functional_requirements": ["性能要求", "安全要求"],
    "constraints": ["技术约束", "业务约束"]
  },
  "tasks": [
    {
      "id": "task-001",
      "title": "任务标题",
      "description": "详细描述",
      "priority": 1,
      "dependencies": [],
      "acceptance_criteria": ["验收标准1", "验收标准2"],
      "estimated_complexity": "medium",
      "estimated_hours": 4
    }
  ],
  "total_tasks": 5,
  "total_estimated_hours": 20
}
```

### 3.4 Prompt 模板

```python
# prompts/pm_prompts.py

PM_SYSTEM_PROMPT = """你是资深产品经理，负责将用户需求转化为可执行的开发任务。

## 核心职责
1. 深入理解用户需求，提取关键功能点和约束条件
2. 对模糊需求主动澄清，确保理解准确
3. 将需求拆解为粒度合理的原子任务
4. 评估任务优先级和依赖关系
5. 为每个任务制定明确的验收标准

## 输出规范
- 必须输出 JSON 格式
- 任务粒度：单个任务应在一次 Agent 交互中完成
- 优先级：1(最高) ~ 5(最低)
- 复杂度：low / medium / high

## 示例
输入: "实现用户登录功能，支持邮箱和密码登录，需要记住登录状态"
输出: {
  "tasks": [
    {
      "id": "task-001",
      "title": "设计用户认证数据库表",
      "description": "设计用户表结构，包含id、email、password_hash、created_at等字段",
      "priority": 1,
      "dependencies": [],
      "acceptance_criteria": ["表结构符合第三范式", "包含必要的索引"],
      "estimated_complexity": "low",
      "estimated_hours": 2
    },
    {
      "id": "task-002", 
      "title": "实现用户登录API",
      "description": "实现POST /api/login接口，验证邮箱密码，返回JWT Token",
      "priority": 1,
      "dependencies": ["task-001"],
      "acceptance_criteria": ["正确验证邮箱格式", "密码错误返回401", "成功返回JWT"],
      "estimated_complexity": "medium",
      "estimated_hours": 4
    }
  ]
}
"""

PM_CLARIFICATION_PROMPT = """需求存在以下模糊点，需要用户澄清：

{ambiguous_points}

请用友好的方式向用户提问，帮助明确需求细节。
"""
```

### 3.5 实现代码框架

```python
# agents/pm_agent.py

from .base import BaseAgent, TaskContext, Thought, Action, Observation

class PMAgent(BaseAgent):
    """产品经理 Agent"""
    
    name = "PM Agent"
    role = "产品经理"
    description = "负责需求分析和任务拆解"
    
    available_tools = [
        "requirement_parser",
        "task_decomposer", 
        "priority_evaluator"
    ]
    
    async def think(self, context: TaskContext) -> Thought:
        """分析需求，制定拆解计划"""
        
        # 1. 解析需求
        requirement = context.user_requirement
        
        # 2. 检查是否有历史相似需求
        similar_requirements = await self.memory.search_similar(requirement)
        
        # 3. 构建 Prompt
        messages = [
            {"role": "system", "content": PM_SYSTEM_PROMPT},
            {"role": "user", "content": f"项目上下文: {context.project_context}\n\n用户需求: {requirement}"}
        ]
        
        # 4. 调用 LLM 思考
        response = await self.llm.generate(messages)
        
        return Thought(
            content=response["analysis"],
            reasoning=response["reasoning"],
            plan=["解析需求", "拆解任务", "排序优先级", "生成验收标准"]
        )
    
    async def act(self, thought: Thought) -> Action:
        """执行任务拆解"""
        
        return Action(
            tool_name="task_decomposer",
            tool_input={
                "analysis": thought.content,
                "reasoning": thought.reasoning
            },
            expected_output="结构化任务列表"
        )
    
    async def observe(self, action: Action, result: Any) -> Observation:
        """验证任务拆解质量"""
        
        tasks = result.get("tasks", [])
        
        # 检查任务质量
        quality_checks = [
            len(tasks) > 0,  # 至少有一个任务
            all(t.get("title") for t in tasks),  # 每个任务有标题
            all(t.get("acceptance_criteria") for t in tasks),  # 有验收标准
        ]
        
        success = all(quality_checks)
        
        return Observation(
            tool_output=result,
            success=success,
            error_message=None if success else "任务拆解不完整"
        )
```

---

## 4. Architect Agent (架构师)

### 4.1 角色定义

| 属性 | 描述 |
|------|------|
| **名称** | Architect Agent |
| **角色** | 架构师 |
| **职责** | 技术方案设计、架构决策、技术选型、接口设计 |
| **输入** | 任务列表、项目上下文、现有代码结构 |
| **输出** | 技术方案文档（含架构图、API设计、数据模型） |

### 4.2 核心能力

```
┌─────────────────────────────────────────────────────────────┐
│                   Architect Agent 能力矩阵                    │
├─────────────────┬───────────────────────────────────────────┤
│ 技术方案设计     │ 根据需求设计完整的技术实现方案              │
├─────────────────┼───────────────────────────────────────────┤
│ 架构图生成       │ 生成系统架构图、模块关系图、数据流图         │
├─────────────────┼───────────────────────────────────────────┤
│ API接口设计      │ 设计RESTful API（路径、参数、响应格式）      │
├─────────────────┼───────────────────────────────────────────┤
│ 数据模型设计     │ 设计数据库表结构、字段定义、关系映射          │
├─────────────────┼───────────────────────────────────────────┤
│ 技术选型分析     │ 对比多种技术方案，给出选型建议和理由          │
├─────────────────┼───────────────────────────────────────────┤
│ 现有代码分析     │ 分析项目现有代码结构，给出架构改进建议        │
└─────────────────┴───────────────────────────────────────────┘
```

### 4.3 输出格式

```json
{
  "technical_solution": {
    "overview": "方案概述",
    "architecture": {
      "pattern": "分层架构 / 微服务 / 领域驱动",
      "layers": ["表现层", "业务层", "数据层"],
      "components": [
        {"name": "组件名", "responsibility": "职责", "tech_stack": "技术栈"}
      ]
    },
    "api_design": [
      {
        "path": "/api/users",
        "method": "POST",
        "description": "创建用户",
        "request": {"body": {}},
        "response": {"status": 201, "body": {}}
      }
    ],
    "data_model": [
      {
        "table": "users",
        "fields": [
          {"name": "id", "type": "UUID", "constraints": "PRIMARY KEY"}
        ],
        "indexes": ["email"],
        "relations": [{"table": "orders", "type": "one-to-many"}]
      }
    ],
    "tech_stack": {
      "backend": "FastAPI",
      "database": "PostgreSQL",
      "cache": "Redis",
      "reasoning": "选型理由"
    }
  }
}
```

### 4.4 Prompt 模板

```python
# prompts/architect_prompts.py

ARCHITECT_SYSTEM_PROMPT = """你是资深架构师，负责设计高质量的技术方案。

## 核心职责
1. 根据任务需求设计完整的技术方案
2. 设计清晰的数据模型和API接口
3. 选择合适的技术栈，给出选型理由
4. 考虑系统的可扩展性、性能和安全性

## 设计原则
- SOLID原则：单一职责、开闭原则、里氏替换、接口隔离、依赖倒置
- DRY原则：避免重复代码
- KISS原则：保持简单
- 考虑边界条件和异常处理

## 输出规范
- 必须包含：架构概述、数据模型、API设计、技术选型
- API设计使用OpenAPI 3.0规范
- 数据模型包含字段定义、索引、关系

## 约束条件
{project_constraints}
"""
```

### 4.5 实现代码框架

```python
# agents/architect_agent.py

from .base import BaseAgent

class ArchitectAgent(BaseAgent):
    """架构师 Agent"""
    
    name = "Architect Agent"
    role = "架构师"
    description = "负责技术方案设计和架构决策"
    
    available_tools = [
        "code_search",
        "dependency_analyzer",
        "architecture_template"
    ]
    
    async def think(self, context: TaskContext) -> Thought:
        """分析任务，制定架构设计方案"""
        
        # 1. 获取项目现有代码结构
        existing_code = await self.tools.execute("code_search", {
            "query": "project structure",
            "scope": "global"
        })
        
        # 2. 分析依赖关系
        dependencies = await self.tools.execute("dependency_analyzer", {
            "project_id": context.project_id
        })
        
        # 3. 构建架构设计 Prompt
        messages = [
            {"role": "system", "content": ARCHITECT_SYSTEM_PROMPT},
            {"role": "user", "content": f"""
任务列表: {context.task_list}
现有代码结构: {existing_code}
依赖分析: {dependencies}
技术栈约束: {context.project_tech_stack}
"""}
        ]
        
        response = await self.llm.generate(messages)
        
        return Thought(
            content=response["solution"],
            reasoning=response["reasoning"],
            plan=["分析现有代码", "设计数据模型", "设计API接口", "选择技术栈"]
        )
    
    async def act(self, thought: Thought) -> Action:
        """生成技术方案文档"""
        
        return Action(
            tool_name="architecture_template",
            tool_input={
                "solution": thought.content,
                "format": "markdown"
            },
            expected_output="技术方案文档"
        )
```

---

## 5. Developer Agent (开发者)

### 5.1 角色定义

| 属性 | 描述 |
|------|------|
| **名称** | Developer Agent |
| **角色** | 开发者 |
| **职责** | 代码编写、Bug修复、代码重构、依赖管理 |
| **输入** | 技术方案、任务描述、项目代码上下文 |
| **输出** | 完整代码文件（含注释、类型定义、错误处理） |

### 5.2 核心能力

```
┌─────────────────────────────────────────────────────────────┐
│                   Developer Agent 能力矩阵                    │
├─────────────────┬───────────────────────────────────────────┤
│ 代码生成         │ 根据技术方案生成完整可运行的代码            │
├─────────────────┼───────────────────────────────────────────┤
│ 多语言支持       │ 支持Python、JavaScript/TypeScript、Java、Go │
├─────────────────┼───────────────────────────────────────────┤
│ 代码注释生成     │ 自动生成清晰的代码注释和文档字符串           │
├─────────────────┼───────────────────────────────────────────┤
│ 错误处理编写     │ 生成完善的错误处理和边界条件处理             │
├─────────────────┼───────────────────────────────────────────┤
│ Bug修复         │ 根据错误信息或测试报告自动修复Bug            │
├─────────────────┼───────────────────────────────────────────┤
│ 代码重构         │ 消除重复代码、降低复杂度、提升可读性          │
├─────────────────┼───────────────────────────────────────────┤
│ 依赖管理         │ 自动安装和管理项目依赖                       │
└─────────────────┴───────────────────────────────────────────┘
```

### 5.3 代码输出规范

```python
# 生成的代码必须包含：
# 1. 文件头注释
"""
File: user_service.py
Description: 用户服务层，处理用户相关的业务逻辑
Author: Developer Agent
Created: 2026-05-11
"""

# 2. 类型定义
from typing import Optional, List
from pydantic import BaseModel

class User(BaseModel):
    """用户模型"""
    id: str
    email: str
    name: Optional[str] = None

# 3. 函数/类注释
def create_user(email: str, password: str) -> User:
    """
    创建新用户
    
    Args:
        email: 用户邮箱，必须符合邮箱格式
        password: 用户密码，至少8位包含字母和数字
        
    Returns:
        User: 创建成功的用户对象
        
    Raises:
        ValueError: 邮箱格式无效或密码强度不足
        DuplicateError: 邮箱已存在
    """
    pass

# 4. 错误处理
try:
    user = create_user(email, password)
except ValueError as e:
    logger.error(f"Invalid input: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

### 5.4 Prompt 模板

```python
# prompts/developer_prompts.py

DEVELOPER_SYSTEM_PROMPT = """你是高级全栈工程师，负责编写高质量的生产级代码。

## 编码规范
1. 遵循PEP8（Python）或项目指定的代码规范
2. 所有函数和类必须有文档字符串
3. 包含适当的类型注解
4. 完善的错误处理和边界条件处理
5. 避免硬编码，使用配置或常量

## 输出要求
- 输出完整可运行的代码文件
- 包含必要的导入语句
- 包含单元测试用例（可选）
- 代码风格统一，命名清晰

## 技术栈
{tech_stack}

## 现有代码上下文
{code_context}
"""
```

### 5.5 实现代码框架

```python
# agents/developer_agent.py

from .base import BaseAgent

class DeveloperAgent(BaseAgent):
    """开发者 Agent"""
    
    name = "Developer Agent"
    role = "开发者"
    description = "负责代码编写和Bug修复"
    
    available_tools = [
        "code_editor",
        "terminal",
        "code_search",
        "dependency_manager"
    ]
    
    async def think(self, context: TaskContext) -> Thought:
        """分析任务，制定编码计划"""
        
        # 1. 获取相关代码上下文
        related_code = await self.tools.execute("code_search", {
            "query": context.current_task["description"],
            "scope": "project"
        })
        
        # 2. 分析技术方案
        tech_solution = context.artifacts.get("architect_solution", {})
        
        # 3. 制定编码计划
        messages = [
            {"role": "system", "content": DEVELOPER_SYSTEM_PROMPT},
            {"role": "user", "content": f"""
任务: {context.current_task}
技术方案: {tech_solution}
相关代码: {related_code}
"""}
        ]
        
        response = await self.llm.generate(messages)
        
        return Thought(
            content=response["implementation_plan"],
            reasoning=response["reasoning"],
            plan=["分析需求", "设计接口", "编写代码", "添加注释", "处理错误"]
        )
    
    async def act(self, thought: Thought) -> Action:
        """编写代码"""
        
        # 生成代码
        code = await self.llm.generate_code(thought.content)
        
        # 写入文件
        return Action(
            tool_name="code_editor",
            tool_input={
                "operation": "write",
                "file_path": self._determine_file_path(),
                "content": code
            },
            expected_output="代码文件路径"
        )
    
    async def observe(self, action: Action, result: Any) -> Observation:
        """验证代码质量"""
        
        file_path = result.get("file_path")
        
        # 1. 语法检查
        syntax_check = await self.tools.execute("terminal", {
            "command": f"python -m py_compile {file_path}"
        })
        
        # 2. Lint检查
        lint_check = await self.tools.execute("terminal", {
            "command": f"ruff check {file_path}"
        })
        
        success = syntax_check["success"] and lint_check["success"]
        
        return Observation(
            tool_output={"file_path": file_path},
            success=success,
            error_message=lint_check.get("error") if not success else None
        )
```

---

## 6. Tester Agent (测试工程师)

### 6.1 角色定义

| 属性 | 描述 |
|------|------|
| **名称** | Tester Agent |
| **角色** | 测试工程师 |
| **职责** | 测试用例生成、自动化测试执行、缺陷报告、覆盖率统计 |
| **输入** | 生成的代码、验收标准、技术方案 |
| **输出** | 测试用例代码 + 测试执行报告 |

### 6.2 核心能力

```
┌─────────────────────────────────────────────────────────────┐
│                    Tester Agent 能力矩阵                      │
├─────────────────┬───────────────────────────────────────────┤
│ 单元测试生成     │ 自动生成覆盖核心逻辑的单元测试              │
├─────────────────┼───────────────────────────────────────────┤
│ 集成测试生成     │ 生成模块间集成测试用例                      │
├─────────────────┼───────────────────────────────────────────┤
│ 边界条件测试     │ 生成覆盖边界条件和异常场景的测试             │
├─────────────────┼───────────────────────────────────────────┤
│ 测试执行         │ 在沙箱中自动执行测试并收集结果              │
├─────────────────┼───────────────────────────────────────────┤
│ 覆盖率统计       │ 统计代码覆盖率（行覆盖、分支覆盖）           │
├─────────────────┼───────────────────────────────────────────┤
│ 缺陷报告         │ 对失败的测试生成结构化缺陷报告               │
└─────────────────┴───────────────────────────────────────────┘
```

### 6.3 输出格式

```json
{
  "test_report": {
    "summary": {
      "total_tests": 10,
      "passed": 8,
      "failed": 2,
      "skipped": 0,
      "pass_rate": "80%",
      "duration_seconds": 5.2
    },
    "coverage": {
      "line_coverage": "85%",
      "branch_coverage": "78%",
      "function_coverage": "90%"
    },
    "test_cases": [
      {
        "name": "test_create_user_success",
        "status": "passed",
        "duration_ms": 120,
        "description": "测试成功创建用户"
      },
      {
        "name": "test_create_user_duplicate_email",
        "status": "failed",
        "duration_ms": 85,
        "error": "AssertionError: Expected DuplicateError but got None",
        "description": "测试重复邮箱应抛出异常"
      }
    ],
    "defects": [
      {
        "severity": "high",
        "test_case": "test_create_user_duplicate_email",
        "description": "未正确处理重复邮箱的情况",
        "suggestion": "在创建用户前检查邮箱是否已存在"
      }
    ]
  }
}
```

### 6.4 Prompt 模板

```python
# prompts/tester_prompts.py

TESTER_SYSTEM_PROMPT = """你是资深QA工程师，负责生成全面的测试用例并执行测试。

## 测试原则
1. 覆盖正常路径和异常路径
2. 包含边界条件测试
3. 测试用例独立，不相互依赖
4. 使用描述性的测试函数名

## 测试框架
- Python: pytest
- JavaScript: jest

## 输出要求
- 生成完整的测试文件
- 包含测试数据准备（fixtures）
- 使用参数化测试覆盖多种场景
- 测试报告包含通过率和覆盖率

## 验收标准
{acceptance_criteria}
"""
```

### 6.5 实现代码框架

```python
# agents/tester_agent.py

from .base import BaseAgent

class TesterAgent(BaseAgent):
    """测试工程师 Agent"""
    
    name = "Tester Agent"
    role = "测试工程师"
    description = "负责测试用例生成和执行"
    
    available_tools = [
        "test_framework",
        "coverage_tool",
        "sandbox_executor"
    ]
    
    async def think(self, context: TaskContext) -> Thought:
        """分析代码，制定测试计划"""
        
        # 1. 获取被测代码
        code_under_test = context.artifacts.get("developer_code", {})
        
        # 2. 获取验收标准
        acceptance_criteria = context.current_task.get("acceptance_criteria", [])
        
        # 3. 制定测试策略
        messages = [
            {"role": "system", "content": TESTER_SYSTEM_PROMPT},
            {"role": "user", "content": f"""
被测代码: {code_under_test}
验收标准: {acceptance_criteria}
技术栈: {context.project_tech_stack}
"""}
        ]
        
        response = await self.llm.generate(messages)
        
        return Thought(
            content=response["test_plan"],
            reasoning=response["reasoning"],
            plan=["分析代码", "设计测试用例", "生成测试代码", "执行测试", "生成报告"]
        )
    
    async def act(self, thought: Thought) -> Action:
        """生成并执行测试"""
        
        # 1. 生成测试代码
        test_code = await self.llm.generate_code(thought.content)
        
        # 2. 写入测试文件
        await self.tools.execute("code_editor", {
            "operation": "write",
            "file_path": f"tests/test_{self._get_module_name()}.py",
            "content": test_code
        })
        
        # 3. 执行测试
        return Action(
            tool_name="test_framework",
            tool_input={
                "command": "pytest",
                "args": ["-v", "--cov", "--cov-report=json"]
            },
            expected_output="测试执行结果和覆盖率报告"
        )
    
    async def observe(self, action: Action, result: Any) -> Observation:
        """分析测试结果"""
        
        # 解析测试报告
        test_report = self._parse_test_report(result)
        
        # 判断是否通过质量门禁
        pass_threshold = 70  # 通过率阈值
        coverage_threshold = 70  # 覆盖率阈值
        
        success = (
            test_report["summary"]["pass_rate"] >= pass_threshold and
            test_report["coverage"]["line_coverage"] >= coverage_threshold
        )
        
        return Observation(
            tool_output=test_report,
            success=success,
            error_message=None if success else "测试未通过质量门禁"
        )
```

---

## 7. Reviewer Agent (代码审查员)

### 7.1 角色定义

| 属性 | 描述 |
|------|------|
| **名称** | Reviewer Agent |
| **角色** | 代码审查员 |
| **职责** | 代码质量审查、安全漏洞检测、性能问题检测、最佳实践检查 |
| **输入** | 生成的代码、测试报告、技术方案 |
| **输出** | 审查报告（含问题列表、改进建议、安全评估） |

### 7.2 核心能力

```
┌─────────────────────────────────────────────────────────────┐
│                   Reviewer Agent 能力矩阵                     │
├─────────────────┬───────────────────────────────────────────┤
│ 代码质量审查     │ 检查命名规范、代码重复、圈复杂度等          │
├─────────────────┼───────────────────────────────────────────┤
│ 安全漏洞检测     │ 检测SQL注入、XSS、硬编码密钥等安全问题       │
├─────────────────┼───────────────────────────────────────────┤
│ 性能问题检测     │ 识别潜在性能瓶颈（N+1查询、内存泄漏等）       │
├─────────────────┼───────────────────────────────────────────┤
│ 最佳实践检查     │ 检查是否遵循语言/框架的最佳实践              │
├─────────────────┼───────────────────────────────────────────┤
│ 设计原则检查     │ 检查SOLID原则、DRY原则等设计规范            │
├─────────────────┼───────────────────────────────────────────┤
│ 自动修复建议     │ 对审查出的问题提供修复代码示例               │
└─────────────────┴───────────────────────────────────────────┘
```

### 7.3 审查维度

| 维度 | 检查项 | 严重级别 |
|------|--------|---------|
| **代码风格** | 命名规范、缩进、空行、导入排序 | Warning |
| **代码质量** | 代码重复、函数长度、圈复杂度 | Warning |
| **安全性** | SQL注入、XSS、硬编码密钥、敏感信息泄露 | Critical |
| **性能** | N+1查询、内存泄漏、低效算法 | High |
| **最佳实践** | 异常处理、日志记录、配置管理 | Medium |
| **设计原则** | SOLID、DRY、KISS | Medium |

### 7.4 输出格式

```json
{
  "review_report": {
    "summary": {
      "total_issues": 5,
      "critical": 1,
      "high": 1,
      "medium": 2,
      "low": 1,
      "pass_rate": "85%"
    },
    "issues": [
      {
        "id": "ISSUE-001",
        "severity": "critical",
        "category": "security",
        "file": "user_service.py",
        "line": 45,
        "description": "SQL注入漏洞：用户输入直接拼接到SQL语句",
        "suggestion": "使用参数化查询：cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))",
        "code_example": "# 修复后的代码\nquery = 'SELECT * FROM users WHERE id = %s'\ncursor.execute(query, (user_id,))"
      },
      {
        "id": "ISSUE-002",
        "severity": "high",
        "category": "performance",
        "file": "order_service.py",
        "line": 30,
        "description": "N+1查询问题：循环中查询数据库",
        "suggestion": "使用JOIN或批量查询优化",
        "code_example": "# 修复后的代码\norders = Order.objects.select_related('user').filter(status='pending')"
      }
    ],
    "security_score": "B",
    "quality_score": "A-",
    "recommendations": [
      "建议添加输入验证中间件",
      "建议使用连接池管理数据库连接"
    ]
  }
}
```

### 7.5 Prompt 模板

```python
# prompts/reviewer_prompts.py

REVIEWER_SYSTEM_PROMPT = """你是资深Tech Lead，负责严格的代码审查。

## 审查维度
1. 代码风格：命名规范、缩进、空行、导入排序
2. 代码质量：代码重复、函数长度、圈复杂度
3. 安全性：SQL注入、XSS、硬编码密钥、敏感信息泄露
4. 性能：N+1查询、内存泄漏、低效算法
5. 最佳实践：异常处理、日志记录、配置管理
6. 设计原则：SOLID、DRY、KISS

## 严重级别定义
- Critical: 安全漏洞、可能导致系统崩溃的问题
- High: 性能问题、逻辑错误
- Medium: 代码质量问题、不符合最佳实践
- Low: 代码风格问题、建议性改进

## 输出要求
- 每个问题必须包含：位置、描述、建议、修复示例
- 给出安全评分和质量评分
- 提供整体改进建议
"""
```

### 7.6 实现代码框架

```python
# agents/reviewer_agent.py

from .base import BaseAgent

class ReviewerAgent(BaseAgent):
    """代码审查员 Agent"""
    
    name = "Reviewer Agent"
    role = "代码审查员"
    description = "负责代码审查和质量评估"
    
    available_tools = [
        "linter",
        "security_scanner",
        "complexity_analyzer"
    ]
    
    async def think(self, context: TaskContext) -> Thought:
        """分析代码，制定审查计划"""
        
        # 1. 获取代码和测试报告
        code_to_review = context.artifacts.get("developer_code", {})
        test_report = context.artifacts.get("test_report", {})
        
        # 2. 运行静态分析工具
        lint_result = await self.tools.execute("linter", {
            "files": code_to_review.keys()
        })
        
        security_result = await self.tools.execute("security_scanner", {
            "files": code_to_review.keys()
        })
        
        # 3. 制定审查策略
        messages = [
            {"role": "system", "content": REVIEWER_SYSTEM_PROMPT},
            {"role": "user", "content": f"""
待审查代码: {code_to_review}
Lint结果: {lint_result}
安全扫描结果: {security_result}
测试报告: {test_report}
"""}
        ]
        
        response = await self.llm.generate(messages)
        
        return Thought(
            content=response["review_plan"],
            reasoning=response["reasoning"],
            plan=["静态分析", "安全扫描", "质量评估", "生成报告"]
        )
    
    async def act(self, thought: Thought) -> Action:
        """执行代码审查"""
        
        return Action(
            tool_name="complexity_analyzer",
            tool_input={
                "code": thought.content,
                "metrics": ["cyclomatic_complexity", "cognitive_complexity", "lines_of_code"]
            },
            expected_output="代码复杂度分析报告"
        )
    
    async def observe(self, action: Action, result: Any) -> Observation:
        """评估审查结果"""
        
        # 检查是否有关键问题
        critical_issues = [i for i in result.get("issues", []) if i["severity"] == "critical"]
        
        # 质量门禁：不允许有关键问题
        success = len(critical_issues) == 0
        
        return Observation(
            tool_output=result,
            success=success,
            error_message=f"发现 {len(critical_issues)} 个关键问题" if not success else None
        )
```

---

## 8. Agent 协作模式

### 8.1 顺序流水线模式 (Sequential Pipeline)

```python
# core/orchestrator.py

class SequentialOrchestrator:
    """顺序流水线编排器"""
    
    def __init__(self):
        self.agents = {
            "pm": PMAgent(),
            "architect": ArchitectAgent(),
            "developer": DeveloperAgent(),
            "tester": TesterAgent(),
            "reviewer": ReviewerAgent()
        }
        self.pipeline = ["pm", "architect", "developer", "tester", "reviewer"]
    
    async def execute(self, user_requirement: str) -> Dict[str, Any]:
        """执行顺序流水线"""
        
        context = TaskContext(
            task_id=generate_uuid(),
            user_requirement=user_requirement,
            artifacts={}
        )
        
        results = {}
        
        for agent_name in self.pipeline:
            agent = self.agents[agent_name]
            
            # 执行 Agent
            result = await agent.on_receive(context)
            
            if not result.success:
                raise AgentExecutionError(f"{agent_name} 执行失败: {result.logs}")
            
            # 保存结果到上下文
            results[agent_name] = result
            context.artifacts[f"{agent_name}_output"] = result.output
            
        return results
```

### 8.2 迭代优化模式 (Iterative Loop)

```python
class IterativeOrchestrator:
    """迭代优化编排器"""
    
    def __init__(self, max_iterations: int = 3):
        self.max_iterations = max_iterations
        self.developer = DeveloperAgent()
        self.tester = TesterAgent()
        self.reviewer = ReviewerAgent()
    
    async def execute(self, context: TaskContext) -> Dict[str, Any]:
        """执行迭代优化循环"""
        
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            
            # Developer 编写代码
            dev_result = await self.developer.on_receive(context)
            context.artifacts["developer_code"] = dev_result.output
            
            # Tester 执行测试
            test_result = await self.tester.on_receive(context)
            context.artifacts["test_report"] = test_result.output
            
            # Reviewer 代码审查
            review_result = await self.reviewer.on_receive(context)
            context.artifacts["review_report"] = review_result.output
            
            # 质量门禁检查
            if test_result.success and review_result.success:
                return {
                    "success": True,
                    "iterations": iteration,
                    "final_code": dev_result.output
                }
            
            # 准备下一轮迭代
            context.current_task["feedback"] = {
                "test_failures": test_result.output.get("defects", []),
                "review_issues": review_result.output.get("issues", [])
            }
        
        return {
            "success": False,
            "iterations": iteration,
            "error": "达到最大迭代次数，未能通过质量门禁"
        }
```

### 8.3 GroupChat 协作模式

```python
from langgraph import Graph, StateGraph

class GroupChatOrchestrator:
    """GroupChat 多Agent协作编排器"""
    
    def __init__(self):
        self.agents = {
            "pm": PMAgent(),
            "architect": ArchitectAgent(),
            "developer": DeveloperAgent(),
            "tester": TesterAgent(),
            "reviewer": ReviewerAgent()
        }
    
    def build_graph(self) -> StateGraph:
        """构建协作图"""
        
        graph = StateGraph()
        
        # 添加节点
        for name, agent in self.agents.items():
            graph.add_node(name, agent.on_receive)
        
        # 添加边
        graph.add_edge("pm", "architect")
        graph.add_edge("architect", "developer")
        graph.add_edge("developer", "tester")
        graph.add_edge("tester", "reviewer")
        
        # 迭代循环：reviewer -> developer (条件边)
        graph.add_conditional_edge(
            "reviewer",
            self._should_iterate,
            {True: "developer", False: END}
        )
        
        return graph.compile()
    
    def _should_iterate(self, state: Dict) -> bool:
        """判断是否继续迭代"""
        review_report = state.get("review_report", {})
        test_report = state.get("test_report", {})
        iteration = state.get("iteration", 0)
        
        # 检查是否通过质量门禁
        passed = (
            review_report.get("summary", {}).get("critical", 0) == 0 and
            test_report.get("summary", {}).get("pass_rate", 0) >= 70
        )
        
        return not passed and iteration < 3
```

---

## 9. Agent 扩展指南

### 9.1 创建自定义 Agent

```python
# 1. 继承 BaseAgent
from agents.base import BaseAgent, TaskContext, Thought, Action, Observation

class DevOpsAgent(BaseAgent):
    """DevOps Agent 示例"""
    
    name = "DevOps Agent"
    role = "DevOps工程师"
    description = "负责CI/CD配置和部署自动化"
    
    available_tools = [
        "docker_builder",
        "k8s_deployer",
        "ci_configurator"
    ]
    
    # 2. 实现三个核心方法
    async def think(self, context: TaskContext) -> Thought:
        """分析部署需求"""
        return Thought(
            content="分析完成",
            reasoning="基于项目技术栈选择部署方案",
            plan=["构建镜像", "配置CI/CD", "部署到K8s"]
        )
    
    async def act(self, thought: Thought) -> Action:
        """执行部署"""
        return Action(
            tool_name="docker_builder",
            tool_input={"dockerfile_path": "./Dockerfile"},
            expected_output="镜像构建成功"
        )
    
    async def observe(self, action: Action, result: Any) -> Observation:
        """验证部署结果"""
        return Observation(
            tool_output=result,
            success=result.get("success", False),
            error_message=result.get("error")
        )

# 3. 注册到配置
# config/agents.yaml
agents:
  devops_agent:
    name: "DevOps Agent"
    role: "DevOps工程师"
    model: "gpt-4o"
    temperature: 0.2
    tools:
      - docker_builder
      - k8s_deployer
      - ci_configurator
```

### 9.2 Agent 配置规范

```yaml
# config/agents.yaml 完整配置示例
agents:
  # 内置 Agent
  pm_agent:
    enabled: true
    name: "PM Agent"
    role: "产品经理"
    model: "gpt-4o"
    temperature: 0.3
    max_tokens: 4000
    tools:
      - requirement_parser
      - task_decomposer
    memory:
      short_term: true
      long_term: true
    
  # 自定义 Agent
  my_custom_agent:
    enabled: true
    name: "Custom Agent"
    role: "自定义角色"
    model: "gpt-4o"
    temperature: 0.5
    system_prompt: "path/to/custom_prompt.txt"
    tools:
      - tool_1
      - tool_2
    memory:
      short_term: true
      long_term: false
    # 自定义参数
    custom_params:
      param1: value1
      param2: value2
```

### 9.3 Agent 调试技巧

```python
# 1. 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 2. 单 Agent 测试
async def test_single_agent():
    agent = PMAgent(llm_client, tool_registry, memory_manager)
    
    context = TaskContext(
        task_id="test-001",
        user_requirement="实现用户登录功能"
    )
    
    result = await agent.on_receive(context)
    print(f"Success: {result.success}")
    print(f"Output: {result.output}")
    print(f"Token Usage: {result.token_usage}")

# 3. Prompt 调试
async def debug_prompt():
    messages = [
        {"role": "system", "content": PM_SYSTEM_PROMPT},
        {"role": "user", "content": "测试需求"}
    ]
    
    # 打印完整 Prompt
    print(json.dumps(messages, indent=2, ensure_ascii=False))
    
    # 测试 LLM 响应
    response = await llm_client.generate(messages)
    print(json.dumps(response, indent=2, ensure_ascii=False))
```

---

## 附录

### A. Agent 状态机

```
IDLE ──▶ on_receive() ──▶ THINKING ──▶ think()
                              │
                              ▼
                          ACTING ──▶ act()
                              │
                              ▼
                          OBSERVING ──▶ observe()
                              │
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
               COMPLETED              ERROR
                    │                   │
                    ▼                   ▼
              on_complete()        on_error()
```

### B. 工具注册示例

```python
# tools/registry.py

class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        self._tools = {}
    
    def register(self, name: str, tool_class, allowed_agents: List[str] = None):
        """注册工具"""
        self._tools[name] = {
            "class": tool_class,
            "allowed_agents": allowed_agents or []
        }
    
    async def execute(self, tool_name: str, agent_name: str, **kwargs):
        """执行工具"""
        tool = self._tools.get(tool_name)
        
        if not tool:
            raise ToolNotFoundError(f"工具 {tool_name} 未注册")
        
        if agent_name not in tool["allowed_agents"]:
            raise PermissionError(f"Agent {agent_name} 无权使用工具 {tool_name}")
        
        instance = tool["class"]()
        return await instance.execute(**kwargs)

# 注册工具
registry = ToolRegistry()
registry.register("code_editor", CodeEditorTool, ["developer"])
registry.register("test_framework", TestFrameworkTool, ["tester"])
registry.register("linter", LinterTool, ["reviewer"])
```

### C. 相关文档索引

| 文档 | 说明 |
|------|------|
| [DevCollab-PRD.md](./DevCollab-PRD.md) | 产品需求文档 |
| [DevCollab-系统架构文档.md](./DevCollab-系统架构文档.md) | 系统架构设计 |
| [DevCollab-功能清单文档.md](./DevCollab-功能清单文档.md) | 功能详细清单 |
| [DevCollab-项目里程碑文档.md](./DevCollab-项目里程碑文档.md) | 项目里程碑规划 |
