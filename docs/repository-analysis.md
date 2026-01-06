# OpenHands 仓库分析

## 项目概述

OpenHands 是一个基于 AI 驱动的软件开发平台，旨在通过智能代理（Agent）系统帮助开发者更高效地完成软件开发任务。该项目是社区驱动的开源项目,专注于将人工智能能力应用于实际的软件开发工作流中。

## 核心定位

OpenHands 提供了一个可组合的 AI 代理框架，能够自主执行复杂的软件开发任务，包括但不限于代码编写、bug 修复、代码审查、仓库分析等。项目的核心理念是"Code Less, Make More"（少写代码，多创造价值）。

## 产品形态

OpenHands 提供多种产品形态以满足不同用户群体的需求：

### SDK（软件代理 SDK）
- 可组合的 Python 库，包含所有代理技术
- 作为整个系统的引擎，为其他产品形态提供底层支持
- 支持在代码中定义代理，可本地运行或扩展到云端的数千个代理
- 适合需要深度定制和集成的开发者

### CLI（命令行界面）
- 最简单的使用方式，体验类似 Claude Code 或 Codex
- 支持 Claude、GPT 或任何其他大语言模型（LLM）
- 适合命令行工作流的开发者

### Local GUI（本地图形界面）
- 在笔记本电脑上运行代理的图形界面
- 包含 REST API 和单页 React 应用程序
- 使用体验类似 Devin 或 Jules
- 适合喜欢图形界面的本地开发者

### Cloud（云服务）
- 在托管基础设施上运行的 GUI 部署版本
- 提供 $10 免费额度，通过 GitHub 账户登录
- 包含源代码可用的功能和集成：
  - Slack、Jira 和 Linear 的集成
  - 多用户支持
  - 基于角色的访问控制（RBAC）和权限管理
  - 协作功能（如对话共享）

### Enterprise（企业版）
- 面向大型企业的自托管云服务解决方案
- 通过 Kubernetes 在企业自己的 VPC 中部署
- 可与 CLI 和 SDK 配合使用
- 源代码可用但需要商业许可证（超过 30 天试用期）
- 提供扩展支持和研究团队访问权限

## 技术架构

### 后端架构

OpenHands 采用事件驱动的多代理架构，核心组件包括：

#### 核心类

| 组件 | 职责 | 说明 |
|------|------|------|
| **LLM** | 大语言模型交互代理 | 通过 LiteLLM 支持任何底层完成模型，处理所有与 LLM 的交互 |
| **Agent** | 智能代理 | 分析当前状态并生成向目标推进的动作 |
| **AgentController** | 代理控制器 | 初始化代理、管理状态、驱动主循环推动代理逐步执行 |
| **State** | 状态管理 | 表示代理任务的当前状态，包括当前步骤、事件历史、长期计划等 |
| **EventStream** | 事件流 | 中央事件枢纽，任何组件都可以发布或监听事件 |
| **Event** | 事件 | 动作（Action）或观察（Observation）的抽象 |
| **Runtime** | 运行时环境 | 执行动作并返回观察结果 |
| **Sandbox** | 沙箱 | 运行时的一部分，负责在隔离环境（如 Docker）中执行命令 |
| **Server** | 服务器 | 通过 HTTP 协议管理 OpenHands 会话，驱动前端 |
| **Session** | 会话 | 持有单个 EventStream、AgentController 和 Runtime，代表单个任务 |
| **ConversationManager** | 对话管理器 | 维护活动会话列表，确保请求路由到正确的会话 |

#### 控制流程

OpenHands 的核心执行循环：

```
循环执行：
  1. Agent 根据当前 State 生成 Prompt
  2. LLM 基于 Prompt 生成响应
  3. Agent 解析响应为 Action
  4. Runtime 执行 Action 并返回 Observation
  5. State 根据 Action 和 Observation 更新
```

#### 事件驱动通信

EventStream 是所有通信的骨干：
- Agent 向 AgentController 发送 Actions
- AgentController 将 State 传递给 Agent
- AgentController 将 Actions 发布到 EventStream
- Runtime 从 EventStream 接收 Actions
- Runtime 将 Observations 发布到 EventStream
- AgentController 从 EventStream 接收 Observations
- Frontend 通过 EventStream 发送 Actions

### 代理系统（AgentHub）

OpenHands 实现了多代理协作系统，支持不同类型的代理：

#### 可用代理类型

| 代理类型 | 功能说明 |
|---------|---------|
| **CodeActAgent** | 主要代理，负责代码操作和任务执行 |
| **BrowsingAgent** | 专门处理网页浏览和信息检索任务 |
| **VisualBrowsingAgent** | 处理需要视觉理解的浏览任务 |
| **LocAgent** | 位置相关的代理 |
| **ReadOnlyAgent** | 只读操作的代理，用于安全的信息查询 |
| **DummyAgent** | 用于测试的虚拟代理 |

#### 代理能力

代理可以执行的动作类型：

| 动作类型 | 说明 |
|---------|------|
| **CmdRunAction** | 在沙箱终端中运行命令 |
| **IPythonRunCellAction** | 在 Jupyter notebook 中交互执行 Python 代码 |
| **FileReadAction** | 读取文件内容 |
| **FileWriteAction** | 写入文件内容 |
| **BrowseURLAction** | 获取 URL 内容 |
| **AddTaskAction** | 添加子任务到计划 |
| **ModifyTaskAction** | 修改子任务状态 |
| **AgentFinishAction** | 停止控制循环，允许用户输入新任务 |
| **AgentRejectAction** | 拒绝并停止任务 |
| **MessageAction** | 发送消息 |

#### 多代理协作机制

OpenHands 支持代理委派（Agent Delegation）：
- 代理可以将任务委派给其他代理
- 支持多层委派（DELEGATE_LEVEL）
- 维护全局迭代计数和局部迭代计数
- 任务（Task）可以包含多个子任务（Subtask）
- 每个子任务由一个代理执行

### Sub-Agent（子代理）功能详解

#### 核心概念

**任务（Task）与子任务（Subtask）的关系**
- **任务（Task）**：OpenHands 系统与用户之间的端到端对话，可能包含用户的一次或多次输入，从初始任务语句开始，以代理发起的 `AgentFinishAction`、用户停止或错误结束
- **子任务（Subtask）**：代理与用户或另一个代理之间的端到端对话。如果任务由单个代理执行，则它本身也是一个子任务。否则，一个任务由多个子任务组成，每个子任务由一个代理执行

#### 委派架构

##### 主代理与子代理的关系

| 关系维度 | 说明 |
|---------|------|
| **层级结构** | 主代理（Parent Agent）可以创建子代理（Delegate Agent）来处理特定子任务 |
| **委派级别** | 通过 `delegate_level` 标识，主代理为 0，第一层子代理为 1，可递归委派 |
| **迭代计数** | 全局迭代（ITERATION）在所有代理间共享，局部迭代（LOCAL_ITERATION）针对每个子任务 |
| **状态共享** | 子代理与主代理共享 EventStream、全局指标（Metrics）、迭代标志和预算标志 |
| **独立性** | 每个子代理有独立的 State 对象，维护自己的历史和局部指标 |

##### 委派流程

**步骤一：发起委派**
- 主代理生成 `AgentDelegateAction`，指定要委派的代理名称和输入参数
- AgentController 接收到委派动作后调用 `start_delegate()` 方法

**步骤二：创建子代理**
- 根据指定的代理类型实例化相应的 Agent 类
- 创建新的 State 对象，继承主代理的迭代和预算标志
- 实例化新的 AgentController，设置 `is_delegate=True`
- 子代理的 `delegate_level` 为父代理 + 1

**步骤三：执行子任务**
- 子代理通过共享的 EventStream 接收任务消息
- 子代理独立执行其步骤，生成 Actions 和接收 Observations
- 全局迭代计数持续累加，局部迭代计数针对子代理从 0 开始

**步骤四：结束委派**
- 子代理完成任务后发送 `AgentFinishAction` 或 `AgentRejectAction`
- AgentController 调用 `end_delegate()` 方法
- 收集子代理的输出和局部指标
- 生成 `AgentDelegateObservation` 包含子代理的执行结果
- 将观察发送到 EventStream，主代理恢复执行

#### 委派动作与观察

##### AgentDelegateAction

委派动作的数据结构：

| 属性 | 类型 | 说明 |
|------|------|------|
| **agent** | string | 要委派的代理名称（如 "BrowsingAgent"、"VerifierAgent"） |
| **inputs** | dict | 传递给子代理的输入参数 |
| **thought** | string | 主代理对委派的思考说明 |
| **action** | string | 动作类型，固定为 ActionType.DELEGATE |

消息示例："I'm asking BrowsingAgent for help with this task."

##### AgentDelegateObservation

委派观察的数据结构：

| 属性 | 类型 | 说明 |
|------|------|------|
| **outputs** | dict | 子代理返回的输出结果 |
| **content** | string | 执行结果的文本描述 |
| **tool_call_metadata** | object | 关联的工具调用元数据 |

观察内容格式：
- 成功："Delegated agent finished with result: {AgentName} finishes task with {outputs}"
- 错误："Delegated agent finished with result: {AgentName} encountered an error during execution."

#### 典型委派场景示例

**场景：CodeActAgent 委派给 BrowsingAgent 查询 GitHub Stars**

```
-- 任务开始（子任务 0 开始）--

DELEGATE_LEVEL 0, ITERATION 0, LOCAL_ITERATION 0
CodeActAgent: 我应该请求 BrowsingAgent 帮助
动作: AgentDelegateAction(agent="BrowsingAgent", inputs={"task": "查找 OpenHands 仓库的 GitHub Stars 数量"})

-- 委派开始（子任务 1 开始）--

DELEGATE_LEVEL 1, ITERATION 1, LOCAL_ITERATION 0
BrowsingAgent: 让我在 GitHub 上查找答案
动作: BrowseURLAction(url="https://github.com/OpenHands/OpenHands")

DELEGATE_LEVEL 1, ITERATION 2, LOCAL_ITERATION 1
BrowsingAgent: 我找到了答案，让我传达结果并完成
动作: AgentFinishAction(outputs={"stars": "15000"})

-- 委派结束（子任务 1 结束）--

观察: AgentDelegateObservation(outputs={"stars": "15000"}, content="BrowsingAgent finishes task with stars: 15000")

DELEGATE_LEVEL 0, ITERATION 3, LOCAL_ITERATION 1
CodeActAgent: 我从 BrowsingAgent 获得了答案，让我传达结果并完成
动作: AgentFinishAction(outputs={"answer": "OpenHands 有 15000 个 Stars"})

-- 任务结束（子任务 0 结束）--
```

#### 指标和资源管理

##### 指标共享策略

| 指标类型 | 共享方式 | 说明 |
|---------|---------|------|
| **全局指标** | 完全共享 | 主代理和所有子代理共享同一个 Metrics 对象，累计所有代理的资源消耗 |
| **局部指标** | 独立计算 | 每个子代理维护自己的局部指标，用于评估单个子任务的性能 |
| **父代理快照** | 继承 | 子代理启动时保存父代理的指标快照，用于计算子任务的增量消耗 |

##### 迭代和预算控制

| 控制项 | 实现方式 |
|--------|----------|
| **迭代限制** | 通过共享的 `iteration_flag` 控制，所有代理累计迭代次数不超过最大值 |
| **预算限制** | 通过共享的 `budget_flag` 控制，所有代理累计成本不超过任务预算 |
| **增量分配** | 子代理创建时继承父代理的增量配置（iteration_delta、budget_delta） |
| **同步机制** | 每次步骤前同步预算标志与实际指标，确保实时控制 |

#### 子代理生命周期管理

##### 创建阶段

1. **代理实例化**：根据 `AgentDelegateAction.agent` 获取代理类并实例化
2. **配置继承**：使用 `agent_configs` 中的配置或继承主代理配置
3. **LLM 共享**：子代理使用主代理的 LLM 注册表，共享模型连接
4. **状态初始化**：创建新 State，设置委派级别、继承标志、保存父代理快照
5. **控制器创建**：创建 AgentController，标记为委派模式

##### 执行阶段

1. **任务接收**：通过 EventStream 接收 MessageAction 包含任务描述
2. **状态切换**：子代理状态切换到 RUNNING
3. **独立步骤**：子代理执行 `step()` 方法，生成动作
4. **事件通信**：通过共享 EventStream 发布动作和接收观察
5. **迭代累加**：全局迭代和局部迭代同时递增

##### 结束阶段

1. **完成信号**：子代理发送 `AgentFinishAction` 或 `AgentRejectAction`
2. **指标收集**：计算子代理的局部指标
3. **输出提取**：从子代理的 State 中提取 outputs
4. **观察生成**：创建 `AgentDelegateObservation` 包含结果
5. **控制器关闭**：关闭子代理的 AgentController
6. **主代理恢复**：将委派设置为 None，主代理恢复执行

#### Microagent（微代理）系统

Microagent 是一种特殊的知识和任务模块，可以被主代理动态加载和调用：

##### Microagent 类型

| 类型 | 名称 | 触发方式 | 用途 |
|------|------|---------|------|
| **KNOWLEDGE** | 知识微代理 | 关键词触发 | 提供语言最佳实践、框架指南、通用模式、工具使用知识 |
| **REPO_KNOWLEDGE** | 仓库微代理 | 自动加载 | 提供特定仓库的指南、团队实践、项目工作流、自定义文档 |
| **TASK** | 任务微代理 | 命令触发 `/{name}` | 需要用户输入的专门任务，提示用户提供必要参数 |

##### Microagent 结构

| 组件 | 说明 |
|------|------|
| **名称（name）** | 微代理的唯一标识符 |
| **内容（content）** | Markdown 格式的指令和知识内容 |
| **元数据（metadata）** | 包含触发器、输入定义、MCP 工具配置等 |
| **触发器（triggers）** | 激活微代理的关键词列表（KNOWLEDGE 类型） |
| **输入（inputs）** | 需要用户提供的参数定义（TASK 类型） |

##### Microagent 加载机制

**仓库级 Microagent**
- 从 `.openhands/microagents/` 目录加载
- 支持 `.cursorrules` 文件（Cursor IDE 兼容）
- 支持 `AGENTS.md` / `agents.md` 文件
- 支持遗留的 `.openhands_instructions` 文件

**知识库 Microagent**
- 通过关键词匹配自动触发
- 可以包含多个触发词，匹配任一触发词即激活
- 内容被注入到代理的上下文中

**任务 Microagent**
- 通过特殊格式 `/{microagent_name}` 触发
- 可以包含变量占位符 `${variable_name}`
- 自动提示用户提供缺失的输入参数

##### 微代理与主代理的交互

| 交互方式 | 实现机制 |
|---------|----------|
| **知识注入** | 通过 `RecallObservation` 将微代理内容添加到代理上下文 |
| **变量替换** | 任务微代理的变量被用户输入替换后注入 |
| **MCP 工具** | 微代理可以配置 MCP（Model Context Protocol）工具供代理使用 |

##### Microagent 与 Sub-Agent 的区别

| 维度 | Microagent | Sub-Agent |
|------|------------|----------|
| **本质** | 静态知识和指令模块 | 独立的代理实例 |
| **生命周期** | 被动加载，无执行循环 | 完整的执行生命周期 |
| **交互方式** | 内容注入到主代理上下文 | 通过 EventStream 独立通信 |
| **状态管理** | 无状态 | 有独立的 State 对象 |
| **执行能力** | 无法执行动作 | 可以执行完整的 Actions |
| **适用场景** | 提供指导性知识和规则 | 执行复杂的子任务 |

#### 委派的高级特性

##### 递归委派

子代理可以进一步委派任务给其他代理：
- 委派级别递增（delegate_level + 1）
- 全局迭代和预算继续共享
- 形成代理调用链或调用树

##### 安全性传递

子代理继承主代理的安全配置：
- **确认模式**：子代理操作可能需要用户确认
- **安全分析器**：共享安全风险分析器实例
- **无头模式**：继承无头模式配置

##### 配置灵活性

每个代理类型可以有独立的配置：
- 通过 `agent_configs` 字典为不同代理类型指定配置
- 未配置的代理继承主代理配置
- 支持为子代理使用不同的 LLM 模型

#### Sub-Agent 的应用场景

##### 专业能力分工

| 场景 | 主代理 | 子代理 | 目的 |
|------|--------|--------|------|
| **网页研究** | CodeActAgent | BrowsingAgent | 主代理专注代码，子代理专注浏览 |
| **视觉任务** | CodeActAgent | VisualBrowsingAgent | 处理需要视觉理解的网页交互 |
| **仓库研究** | DelegatorAgent | RepoStudyAgent | 深入分析代码仓库结构和内容 |
| **任务验证** | DelegatorAgent | VerifierAgent | 验证任务完成质量 |

##### 任务分解

复杂任务可以分解为多个子任务：
1. 主代理分析整体任务
2. 将子任务委派给专门的子代理
3. 收集所有子代理的结果
4. 主代理整合结果并完成任务

##### 隔离执行

某些风险操作可以在子代理中隔离执行：
- 独立的失败处理
- 局部的错误恢复
- 不影响主任务的实验性操作

#### 委派的技术优势

1. **模块化**：不同能力封装在不同代理中，便于维护和扩展
2. **复用性**：子代理可以被多个主代理重复调用
3. **专业化**：每个代理专注特定领域，提高任务完成质量
4. **可追溯性**：委派级别和局部指标便于调试和性能分析
5. **资源控制**：全局指标确保整体资源消耗在可控范围
6. **并发潜力**：架构支持未来实现并行子代理执行

### 前端架构

#### 技术栈

| 技术 | 用途 |
|------|------|
| **Remix SPA Mode** | React + Vite + React Router 的集成框架 |
| **TypeScript** | 类型安全的开发 |
| **Redux** | 全局状态管理 |
| **TanStack Query** | 异步状态和服务器状态管理 |
| **Tailwind CSS** | 样式框架 |
| **i18next** | 国际化支持 |
| **React Testing Library** | 组件测试 |
| **Vitest** | 单元测试框架 |
| **Mock Service Worker** | API 模拟 |

#### 核心功能

- 通过 WebSocket 实现实时更新
- 多语言国际化支持
- 使用 Remix 的路由数据加载
- GitHub OAuth 用户认证（在 SaaS 模式下）

### 运行时环境

OpenHands 支持多种运行时环境：

| 运行时类型 | 说明 |
|-----------|------|
| **Docker** | 默认的本地沙箱环境 |
| **E2B Sandbox** | 第三方云沙箱 |
| **Modal** | 可选的第三方运行时 |
| **Runloop** | 可选的第三方运行时 |
| **Daytona** | 可选的第三方运行时 |

### 企业功能

企业版在开源版本基础上扩展了以下功能：

#### 认证机制

| 方面 | 开源版 | 企业版 |
|------|--------|--------|
| **认证方法** | 用户通过 UI 添加个人访问令牌（PAT） | 用户通过 UI 进行 OAuth，GitHub 应用提供短期访问令牌和刷新令牌 |
| **令牌存储** | PAT 存储在 Settings 中 | 令牌存储在 GithubTokenManager（后端文件存储） |
| **认证状态** | 检查 Settings 中是否存在令牌 | OAuth 期间发放带有 github_user_id 的签名 Cookie |

#### 集成服务

- GitHub/GitLab/Bitbucket 集成
- Jira 和 Jira DC 集成
- Linear 项目管理集成
- Slack 通知集成
- Stripe 支付服务集成

#### 其他企业特性

- 多用户支持和用户管理
- 基于角色的访问控制（RBAC）
- 对话共享和协作功能
- 实验管理器用于 A/B 测试
- 遥测和监控系统
- 维护任务处理器

## 评估与测试

### 基准测试支持

OpenHands 支持超过 30 种基准测试，用于评估代理性能：

#### 主要基准测试

| 基准测试 | 领域 |
|---------|------|
| **SWE-bench** | 软件工程任务，包括真实的 GitHub 问题修复 |
| **Multi SWE-bench** | 多仓库软件工程任务 |
| **Visual SWE-bench** | 需要视觉理解的软件工程任务 |
| **SWE Perf** | 软件工程性能测试 |
| **WebArena** | 网页交互任务 |
| **VisualWebArena** | 视觉网页交互任务 |
| **MiniWoB** | 简化的网页操作基准 |
| **GAIA** | 通用 AI 助手基准 |
| **AgentBench** | 通用代理能力测试 |
| **Commit0** | 代码提交任务 |
| **ML-Bench** | 机器学习任务 |
| **BioCoder** | 生物信息学代码任务 |
| **BIRD** | 数据库查询任务 |
| **GPQA** | 通用问题回答 |
| **Gorilla** | API 调用任务 |
| **TAU-bench** | 任务理解基准 |
| **TestGenEval** | 测试生成评估 |
| **HumanEvalFix** | 代码修复任务 |
| **DiscoveryBench** | 发现性任务 |
| **NoCode Bench** | 无代码平台任务 |
| **Logic Reasoning** | 逻辑推理任务 |

#### 评估基础设施

- 使用 SWE-bench 作为主要评估基准
- 支持准确性、效率和代码复杂度的三维评估
- 集成多种评估工具和数据集
- 支持流式评估和批量评估

### 测试框架

#### 测试类型

| 测试类型 | 位置 | 说明 |
|---------|------|------|
| **单元测试** | `tests/unit/` | 组件级别的单元测试 |
| **运行时测试** | `tests/runtime/` | 运行时环境和沙箱测试 |
| **端到端测试** | `tests/e2e/` | 完整流程的集成测试 |
| **前端测试** | `frontend/__tests__/` | React 组件和 UI 测试 |

#### 前端测试策略

- 使用 Vitest 作为测试运行器
- React Testing Library 进行组件渲染测试
- Mock Service Worker（MSW）进行 API 模拟
- 强调可访问性测试
- 支持国际化测试
- 覆盖率报告和持续集成

## 集成能力

### 版本控制平台

- **GitHub**：完整集成，包括问题、PR、代码审查
- **GitLab**：支持 GitLab 仓库和工作流
- **Bitbucket**：支持 Bitbucket 仓库
- **Azure DevOps**：通过技能文档支持

### 项目管理工具

- **Jira**：任务跟踪和问题管理
- **Jira DC**：Jira 数据中心版本
- **Linear**：现代项目管理工具

### 通信平台

- **Slack**：通知和协作

### 云服务

- **Google Cloud AI Platform**：AI 模型集成
- **Anthropic Vertex**：Claude 模型集成
- **AWS（Boto3）**：AWS 服务集成
- **Kubernetes**：容器编排和部署

## 技能系统

OpenHands 提供预定义的技能文档（Skills），用于指导代理执行特定任务：

| 技能 | 用途 |
|------|------|
| **add_agent** | 添加新代理 |
| **agent-builder** | 构建自定义代理 |
| **code-review** | 代码审查 |
| **fix_test** | 修复测试 |
| **update_test** | 更新测试 |
| **github** | GitHub 操作 |
| **gitlab** | GitLab 操作 |
| **bitbucket** | Bitbucket 操作 |
| **docker** | Docker 操作 |
| **kubernetes** | Kubernetes 操作 |
| **security** | 安全相关任务 |
| **onboarding** | 新项目入门 |

## 存储和数据管理

### 存储抽象层

OpenHands 提供了灵活的存储抽象，支持多种存储后端：
- 本地文件系统存储
- 内存存储
- 云存储集成

### 数据库支持

企业版使用 SQLAlchemy 和 Alembic 进行数据库管理：
- 支持 PostgreSQL（通过 pg8000 和 asyncpg）
- 数据库迁移版本控制
- 异步数据库操作

## 安全特性

### 沙箱隔离
- 所有代码执行在隔离的容器中
- 支持多种沙箱提供商
- 限制文件系统和网络访问

### 认证与授权
- 企业版支持 OAuth 2.0
- JWT 令牌认证
- 基于角色的访问控制（RBAC）

### 安全审计
- 操作日志记录
- 安全事件监控
- 企业版支持审计跟踪

## 扩展性

### 插件系统
- 支持 JupyterLab 插件
- 运行时插件扩展
- MCP（Model Context Protocol）支持

### 自定义开发
- 可添加自定义代理
- 可实现自定义运行时
- 可扩展动作和观察类型
- 支持自定义 LLM 提供商（通过 LiteLLM）

## 性能特性

### 并发和异步
- 使用 FastAPI 和 Uvicorn 提供高性能 HTTP 服务
- 异步事件处理
- WebSocket 支持实时通信

### 监控和遥测
- OpenTelemetry 集成
- 自定义指标收集
- 企业版提供 SaaS 监控监听器

### 资源管理
- 速率限制
- 流量控制
- 内存分析支持

## 许可证

### 开源部分（MIT 许可证）
- 核心 `openhands` 代码
- `agent-server` Docker 镜像
- CLI 工具
- 评估基础设施

### 企业部分（Polyform Free Trial License）
- `enterprise/` 目录内容
- 免费试用期 30 天/年
- 超过试用期需购买商业许可证

## 社区和生态

### 文档和资源
- 完整的在线文档
- 技术论文支持
- 多语言 README（德语、西班牙语、法语、日语、韩语、葡萄牙语、俄语、中文）

### 开发者社区
- Slack 社区频道
- GitHub 讨论区
- 开放的贡献流程
- 详细的贡献指南

### 相关项目
- Chrome 扩展
- Theory-of-Mind 模块
- 专门的评估基础设施仓库
- 软件代理 SDK 独立仓库

## 性能指标

根据项目说明，OpenHands 在 SWE-bench 基准测试中获得了 **77.6 分**的成绩，这表明其在真实软件工程任务上具有较高的能力。

## 技术依赖

### 核心依赖

| 依赖 | 版本要求 | 用途 |
|------|---------|------|
| **Python** | 3.12-3.13 | 后端运行时 |
| **LiteLLM** | >=1.74.3 | LLM 统一接口 |
| **OpenAI** | 2.8.0 | OpenAI API 客户端 |
| **FastAPI** | Latest | Web 框架 |
| **Docker** | Latest | 容器化 |
| **Playwright** | ^1.55.0 | 浏览器自动化 |
| **PyGithub** | ^2.5.0 | GitHub API |
| **Redis** | 5.2-7.0 | 缓存和消息队列 |
| **Node.js** | 20.x+ | 前端运行时 |

### 可选依赖

- Modal、Runloop、Daytona、E2B：第三方运行时
- Google Cloud AI Platform：Google AI 模型
- Anthropic：Claude 模型
- 各种评估基准数据集

## 部署模式

### 本地开发
- 使用 Docker Compose 快速启动
- 支持前后端分离开发
- Mock Service Worker 用于前端独立开发

### 云部署
- 官方云服务：app.all-hands.dev
- 支持 Kubernetes 部署
- 企业自托管方案

### CI/CD
- GitHub Actions 持续集成
- 自动化测试和代码检查
- Pre-commit hooks

## 配置管理

### 配置文件
- `config.template.toml`：配置模板
- 环境变量支持
- 运行时动态配置

### 代码规范
- Ruff 代码格式化和检查
- MyPy 类型检查
- Pre-commit 自动化检查
- ESLint（前端）
- Prettier（前端）

## 数据流

OpenHands 的典型数据流：

```
用户输入
  → 前端 UI
  → Server/Session
  → EventStream
  → AgentController
  → Agent
  → LLM
  → Action
  → Runtime/Sandbox
  → Observation
  → EventStream
  → AgentController
  → State 更新
  → 前端 UI
  → 用户查看结果
```

## 适用场景

### 代码开发
- 自动化代码生成
- Bug 修复
- 代码重构
- 测试编写

### 代码审查
- 自动化代码审查
- PR 评论处理
- 代码质量分析

### 仓库管理
- 仓库研究和分析
- 文档生成
- 依赖更新

### 问题解决
- GitHub Issues 自动解决
- CI/CD 构建修复
- 性能优化

### 研究和学习
- 代码库理解
- 技术文档生成
- 新手入门指导

## 技术优势

### 多模型支持
通过 LiteLLM，支持所有主流 LLM 提供商，用户可以自由选择最适合的模型。

### 模块化架构
清晰的组件分离和事件驱动设计，易于扩展和维护。

### 多代理协作
支持复杂任务的分解和多代理协同完成。

### 丰富的评估
超过 30 种基准测试确保代理能力的持续改进。

### 灵活部署
支持从本地 CLI 到企业级云部署的多种使用方式。

### 社区驱动
活跃的开源社区和清晰的贡献流程促进持续发展。
