# Runtime Skills 功能集成说明

## 实施总结

本文档记录了运行时 Skills 功能的完整实施情况以及待完成的集成工作。

## ✅ 已完成的组件

### 1. 后端基础架构（100% 完成）

#### 1.1 Memory 类扩展
**文件**: `openhands/memory/memory.py`

新增功能：
- `runtime_skills: dict[str, KnowledgeMicroagent | RepoMicroagent]` - 存储运行时Skills
- `skill_sources: dict[str, str]` - 跟踪每个Skill的来源
- `add_runtime_skill(skill)` - 添加运行时Skill
- `update_runtime_skill(name, skill)` - 更新运行时Skill
- `remove_runtime_skill(name)` - 删除运行时Skill
- `get_runtime_skill(name)` - 获取指定的运行时Skill
- `get_all_skills_with_source()` - 获取所有Skills及其来源
- `list_runtime_skills()` - 列出所有运行时Skills

优先级实现：
- 修改了 `_find_microagent_knowledge()` 方法
- 实现四级优先级：runtime > repo > user > global
- 运行时Skills会覆盖同名的其他来源Skills

#### 1.2 Skills 验证器
**文件**: `openhands/microagent/validator.py` (277 行)

验证功能：
- `validate_skill_name()` - 名称验证（2-100字符，仅允许字母数字连字符下划线）
- `validate_content()` - 内容验证（10字节-50KB）
- `validate_skill_type()` - 类型验证（knowledge/task/repo）
- `validate_triggers()` - 触发词验证
- `check_trigger_conflicts()` - 检查触发词冲突
- `validate_skill()` - 综合验证入口

异常处理：
- `SkillValidationError` 自定义异常类，包含错误消息和字段信息

#### 1.3 数据模型
**文件**: `openhands/app_server/app_conversation/app_conversation_models.py`

新增模型（5个）：
- `RuntimeSkillCreateRequest` - 创建Skill请求
- `RuntimeSkillUpdateRequest` - 更新Skill请求
- `RuntimeSkillResponse` - Skill响应
- `RuntimeSkillsListResponse` - Skills列表响应
- `RuntimeSkillPersistRequest` - 持久化请求

### 2. API 端点实现（100% 完成）

#### 2.1 Runtime Skills Router
**文件**: `openhands/app_server/app_conversation/runtime_skills_router.py` (374 行)

实现的端点：
- `POST /{conversation_id}/runtime-skills` - 创建Skill
- `GET /{conversation_id}/runtime-skills` - 列出所有Skills
- `GET /{conversation_id}/runtime-skills/{name}` - 获取指定Skill
- `PUT /{conversation_id}/runtime-skills/{name}` - 更新Skill
- `DELETE /{conversation_id}/runtime-skills/{name}` - 删除Skill
- `POST /{conversation_id}/runtime-skills/{name}/persist` - 持久化Skill

每个端点都包含：
- 完整的参数验证
- 错误处理和日志记录
- 符合RESTful规范的HTTP状态码
- 详细的文档字符串

### 3. 前端 UI 实现（100% 完成）

#### 3.1 SkillEditor 组件
**文件**: `frontend/src/components/features/conversation-panel/skill-editor.tsx` (275 行)

功能特性：
- 名称输入（实时验证）
- 类型选择（knowledge/task/repo）
- 触发词管理（动态添加/删除）
- Markdown内容编辑器
- 持久化选项
- 完整的表单验证
- 错误提示

UI元素：
- 使用React Hooks（useState, useEffect）
- 响应式设计
- 友好的用户体验
- 实时字符计数

#### 3.2 SkillsModal 扩展
**文件**: `frontend/src/components/features/conversation-panel/skills-modal.tsx`

新增功能：
- "Create Skill" 按钮
- 创建/编辑模式切换
- 集成 SkillEditor 组件
- 运行时Skills管理界面
- 确认对话框（删除操作）

状态管理：
- `isCreating` - 创建模式标志
- `editingSkill` - 当前编辑的Skill
- 与API hooks集成

#### 3.3 SkillItem 组件扩展
**文件**: `frontend/src/components/features/conversation-panel/skill-item.tsx`

新增功能：
- 来源标记（runtime/repo/user/global）
- 编辑按钮（仅runtime skills）
- 删除按钮（仅runtime skills）
- 持久化按钮（仅runtime skills）
- 彩色来源标签

视觉设计：
- 蓝色标签表示runtime
- 绿色标签表示repo
- 紫色标签表示user
- 灰色标签表示其他来源

#### 3.4 API 调用钩子
**文件**: `frontend/src/hooks/mutation/use-runtime-skills.ts` (156 行)

实现的Hooks：
- `useCreateRuntimeSkill()` - 创建Skill mutation
- `useUpdateRuntimeSkill()` - 更新Skill mutation
- `useDeleteRuntimeSkill()` - 删除Skill mutation
- `usePersistRuntimeSkill()` - 持久化Skill mutation

功能特性：
- 使用React Query (TanStack Query)
- 自动invalidate相关查询
- 完整的错误处理
- TypeScript类型安全

#### 3.5 类型定义更新
**文件**: 
- `frontend/src/api/conversation-service/v1-conversation-service.types.ts`
- `frontend/src/api/open-hands.types.ts`

类型扩展：
- `Skill.type` 添加 "task" 类型
- `Skill.source` 添加来源字段
- `Microagent.type` 添加 "task" 类型
- `Microagent.source` 添加来源字段

### 4. 单元测试（100% 完成）

#### 4.1 Memory 测试
**文件**: `tests/unit/memory/test_runtime_skills.py` (268 行，13个测试)

测试覆盖：
- 添加、更新、删除runtime skills
- 获取和列出runtime skills
- 优先级机制验证
- 不同类型的skills处理
- 边界条件测试

#### 4.2 验证器测试
**文件**: `tests/unit/microagent/test_validator.py` (289 行，34个测试)

测试覆盖：
- 名称验证（各种有效/无效情况）
- 内容验证（长度限制、编码）
- 类型验证
- 触发词验证
- 冲突检测
- 综合验证场景

## ⚠️ 待完成的集成工作

### 1. Memory 实例访问（关键集成点）

**问题描述**：
Runtime Skills Router 中的所有端点都有 TODO 注释，需要访问 conversation 的 Memory 实例才能真正操作 runtime skills。

**当前状态**：
```python
# 在 runtime_skills_router.py 中
# TODO: Add skill to conversation's Memory
# This requires accessing the agent's memory instance
# For now, return the skill info
# In a complete implementation, we would:
# 1. Get the agent session for this conversation
# 2. Access its memory
# 3. Call memory.add_runtime_skill(skill)
```

**需要解决的问题**：
1. 如何从 `conversation_id` 获取对应的 agent session/runtime
2. 如何访问 agent 的 Memory 实例
3. 如何在不同的应用架构中（Standalone vs Clustered）实现这个访问

**可能的解决方案**：

#### 方案 A：通过 AppConversationService
```python
# 1. 扩展 AppConversationService 接口
class AppConversationService(ABC):
    @abstractmethod
    async def get_agent_memory(self, conversation_id: UUID) -> Memory | None:
        """Get the agent's memory for a conversation."""
        pass

# 2. 在 runtime_skills_router.py 中使用
memory = await app_conversation_service.get_agent_memory(conversation_id)
if memory:
    memory.add_runtime_skill(skill)
```

#### 方案 B：通过 Agent Server API
```python
# 如果 agent 运行在远程服务器上，通过 HTTP API 访问
async def add_runtime_skill_via_api(
    conversation_id: UUID,
    skill: KnowledgeMicroagent | RepoMicroagent
):
    runtime_info = await get_runtime_info(conversation_id)
    url = f"{runtime_info['url']}/api/conversations/{conversation_id}/runtime-skills"
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=skill.to_dict())
        response.raise_for_status()
```

#### 方案 C：通过会话管理器
```python
# 查看 ClusteredConversationManager 或 SaaSNestedConversationManager
# 它们可能有 get_agent_session() 方法

# 在 enterprise/server/saas_nested_conversation_manager.py 中发现：
def get_agent_session(self, sid: str):
    """Get the agent session for a given session ID."""
    # 实现逻辑
```

**推荐方案**：
- 对于 V0 架构：使用方案 C（会话管理器）
- 对于 V1 架构：使用方案 B（Agent Server API）
- 统一接口：使用方案 A（抽象层）

### 2. Skills 持久化实现

**问题描述**：
`persist_runtime_skill` 端点需要实现将运行时Skill写入文件系统的功能。

**需要实现的逻辑**：
```python
async def persist_runtime_skill(
    conversation_id: UUID,
    skill_name: str,
    persist_request: RuntimeSkillPersistRequest,
):
    # 1. 从 Memory 获取 runtime skill
    skill = memory.get_runtime_skill(skill_name)
    
    # 2. 确定保存位置
    if persist_request.location == 'repo':
        path = '.openhands/microagents/'
    elif persist_request.location == 'user':
        path = os.path.expanduser('~/.openhands/microagents/')
    
    # 3. 生成 Markdown 文件（带 YAML frontmatter）
    content = f"""---
name: {skill.name}
type: {skill.type}
triggers:
{yaml.dump(skill.triggers, default_flow_style=False)}
---

{skill.content}
"""
    
    # 4. 写入文件
    file_path = os.path.join(path, f"{skill.name}.md")
    with open(file_path, 'w') as f:
        f.write(content)
    
    # 5. 更新 source（从 runtime 变为 file）
    # 6. 返回文件路径
    return {"message": "Skill persisted", "path": file_path}
```

**需要考虑的问题**：
- 文件命名冲突处理
- 权限检查
- Git 自动提交（可选）
- Workspace 路径获取

### 3. Router 注册

**问题描述**：
Runtime Skills Router 需要在主应用中注册。

**需要修改的文件**：
- `openhands/app_server/app.py` (V0)
- `openhands/app_server/v1/app.py` (V1)

**需要添加的代码**：
```python
# 在 app.py 中
from openhands.app_server.app_conversation.runtime_skills_router import router as runtime_skills_router

# 注册 router
app.include_router(runtime_skills_router)
```

**验证方法**：
```bash
# 启动服务器后检查
curl http://localhost:3000/docs

# 应该能看到 "Runtime Skills" 标签和所有端点
```

### 4. 与现有 Microagents 端点集成

**问题描述**：
现有的 `GET /conversations/{id}/microagents` 端点需要包含 runtime skills。

**需要修改的位置**：
```python
# 在相应的 microagents 端点中
def get_microagents(conversation_id: UUID):
    # 原有逻辑：获取文件系统中的 microagents
    file_skills = load_microagents_from_files()
    
    # 新增逻辑：获取 runtime skills
    memory = get_agent_memory(conversation_id)
    runtime_skills = memory.list_runtime_skills() if memory else []
    
    # 合并并返回（runtime skills 排在前面）
    all_skills = runtime_skills + file_skills
    return {"microagents": all_skills}
```

**V1 Skills 端点**：
```python
# V1ConversationService.getSkills() 也需要类似修改
```

### 5. 前端 API 服务集成

**当前状态**：
前端已经创建了 mutation hooks，但需要确保 API 服务文件包含相应的方法。

**可能需要的修改**：
```typescript
// 在 ConversationService 或 V1ConversationService 中
// 如果需要的话，添加 runtime skills 相关方法
// 但由于我们直接使用 openHands axios 实例，可能不需要修改
```

### 6. 国际化（可选）

**需要添加的翻译键**：
```json
// 在 frontend/src/i18n/translation.json 中
{
  "SKILLS$CREATE_SKILL": {
    "en": "Create Skill",
    "zh-CN": "创建技能"
  },
  "SKILLS$EDIT_SKILL": {
    "en": "Edit Skill",
    "zh-CN": "编辑技能"
  },
  "SKILLS$DELETE_CONFIRM": {
    "en": "Are you sure you want to delete this skill?",
    "zh-CN": "确定要删除此技能吗？"
  },
  "SKILLS$RUNTIME_LABEL": {
    "en": "Runtime",
    "zh-CN": "运行时"
  },
  "SKILLS$PERSIST_SUCCESS": {
    "en": "Skill persisted successfully",
    "zh-CN": "技能已成功保存"
  }
}
```

## 🔧 集成步骤建议

### 阶段 1：Memory 实例访问（最高优先级）
1. 研究现有的会话管理器实现
2. 选择合适的访问方案
3. 在 `runtime_skills_router.py` 中实现 Memory 访问逻辑
4. 编写集成测试验证功能

### 阶段 2：Router 注册和基本功能测试
1. 在主应用中注册 Runtime Skills Router
2. 启动服务器验证端点可访问
3. 使用 curl 或 Postman 测试基本 CRUD 操作
4. 验证前端 UI 与后端的连接

### 阶段 3：Skills 持久化
1. 实现文件写入逻辑
2. 处理路径和权限问题
3. 添加错误处理
4. 测试持久化功能

### 阶段 4：与现有端点集成
1. 修改现有的 microagents 端点
2. 确保 runtime skills 正确显示在列表中
3. 测试优先级机制在实际场景中的表现

### 阶段 5：端到端测试
1. 创建完整的用户流程测试
2. 验证所有功能在不同架构中的表现
3. 性能测试和优化
4. 文档更新

## 📝 测试计划

### 单元测试（已完成）
- ✅ Memory 类功能测试
- ✅ 验证器功能测试

### 集成测试（待完成）
- ⬜ Runtime skills CRUD 端到端测试
- ⬜ 优先级机制集成测试
- ⬜ 持久化功能测试
- ⬜ 并发操作测试

### UI 测试（待完成）
- ⬜ SkillEditor 组件测试
- ⬜ SkillsModal 交互测试
- ⬜ API 错误处理测试
- ⬜ 用户工作流测试

## 📚 参考资料

### 相关文件
- 设计文档：`/data/.task/design.md`
- 实施总结：`.qoder/quests/add-agent-skills-feature-implementation-summary.md`
- Memory 类：`openhands/memory/memory.py`
- 验证器：`openhands/microagent/validator.py`
- API Router：`openhands/app_server/app_conversation/runtime_skills_router.py`
- SkillEditor：`frontend/src/components/features/conversation-panel/skill-editor.tsx`

### 相关 Issue/PR
（待添加）

## 🎯 关键决策点

1. **Memory 访问方式**：需要与团队讨论选择哪种方案
2. **持久化策略**：是否需要 Git 自动提交
3. **架构兼容性**：确保在 V0 和 V1 中都能工作
4. **安全考虑**：Skills 内容的安全验证级别

## 💡 后续优化建议

1. **Skills 版本控制**：实现 Skills 的版本历史
2. **Skills 模板**：提供常用 Skills 的模板库
3. **Skills 分享**：允许用户分享 Skills
4. **Skills 统计**：收集 Skills 使用情况
5. **AI 辅助**：使用 LLM 帮助用户创建 Skills

---

**最后更新**：2024年（根据实际日期更新）
**状态**：等待 Memory 集成
**负责人**：待分配
