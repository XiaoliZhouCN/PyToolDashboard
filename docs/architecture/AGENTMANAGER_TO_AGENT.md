# AgentManager To Agent

## 1. 文档目的

本文件由 Agent Manager 提供给后续 Agent，用于说明：

- 不同类型 Agent 在开工前**必须读取**哪些文件
- 哪些规范文件属于**按需读取**
- Agent 应如何控制阅读范围，避免一上来扫描全部规范

多 Agent 的组织方式、职责边界与目录归属规则，则统一由：

- [docs/conventions/AGENT_ORGANIZATION.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/AGENT_ORGANIZATION.md)

定义。

本文件当前先覆盖以下 Agent 类型：

1. 架构维护 Agent
2. 框架建构 Agent
3. 专项开发 Agent
4. 验证文档 Agent
5. 仓库分析 Agent
6. 协议/集成 Agent

后续若出现新类型 Agent，再增补对应章节。

## 2. 总原则

### 2.1 不要默认通读全部规范

除非任务本身就是“全面梳理仓库规范”，否则 Agent 不应一开始读取所有文档。

推荐顺序：

1. 识别自己属于哪类 Agent
2. 读取该类型的“开工前必读”
3. 读取本次任务直接涉及的目标目录或目标文件
4. 只有当任务命中某类具体约束时，再补读对应规范

### 2.2 先读边界，再读细则

优先理解：

- 仓库定位
- 模块边界
- 运行目录约束

之后再看：

- 数据格式
- 文档写法
- 代码风格
- 提交信息规则

### 2.3 只读与任务强相关的 README

如果任务只涉及某个 tool，就优先读该 tool 的 `README.md`；  
如果任务只涉及 dashboard，就优先读 `dashboard/README.md`；  
不要把其他无关模块 README 一起扫完。

## 3. 所有 Agent 的公共最小读取集

以下文件对所有 Agent 都属于推荐最小入口：

1. [docs/architecture/ARCHITECTURE.md](file:///d:/Repositories/PyToolDashboard/docs/architecture/ARCHITECTURE.md)
2. [docs/architecture/AGENTMANAGER_TO_AGENT.md](file:///d:/Repositories/PyToolDashboard/docs/architecture/AGENTMANAGER_TO_AGENT.md)
3. [docs/conventions/AGENT_ORGANIZATION.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/AGENT_ORGANIZATION.md)

说明：

- `ARCHITECTURE.md` 用于理解仓库定位、分层、依赖方向和 workspace 运行目录规则
- 本文件用于决定接下来还要读什么、哪些先不用读
- `AGENT_ORGANIZATION.md` 用于理解自己在多 Agent 协作中的职责边界

## 4. 架构维护 Agent

### 4.1 开工前必读

架构维护 Agent 在维护仓库边界、职责分配和架构规范前，必须读取：

1. [docs/architecture/ARCHITECTURE.md](file:///d:/Repositories/PyToolDashboard/docs/architecture/ARCHITECTURE.md)
2. [docs/conventions/AGENT_ORGANIZATION.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/AGENT_ORGANIZATION.md)
3. [docs/conventions/REPOSITORY_STRUCTURE.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/REPOSITORY_STRUCTURE.md)
4. [docs/conventions/DOCUMENTATION.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/DOCUMENTATION.md)

### 4.2 按需读取

- 若涉及 tool 级架构文档：
  [docs/conventions/ARCHITECTURE_DESIGN.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/ARCHITECTURE_DESIGN.md)
- 若涉及运行目录、launcher 或工具接入约束：
  [docs/conventions/LAUNCHERS.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/LAUNCHERS.md)
  和 [docs/contracts/TOOL_RUNTIME_CONTRACT.md](file:///d:/Repositories/PyToolDashboard/docs/contracts/TOOL_RUNTIME_CONTRACT.md)

### 4.3 附加要求

- 架构维护 Agent 不参与具体功能代码实现
- 架构维护 Agent 主要维护文档边界、职责划分和规则上收

## 5. 框架建构 Agent

### 5.1 开工前必读

框架建构 Agent 在维护仓库骨架、共享运行时和基础模板前，必须读取：

1. [docs/architecture/ARCHITECTURE.md](file:///d:/Repositories/PyToolDashboard/docs/architecture/ARCHITECTURE.md)
2. [docs/conventions/AGENT_ORGANIZATION.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/AGENT_ORGANIZATION.md)
3. [docs/conventions/REPOSITORY_STRUCTURE.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/REPOSITORY_STRUCTURE.md)
4. [docs/conventions/DEPENDENCIES.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/DEPENDENCIES.md)
5. [docs/conventions/LAUNCHERS.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/LAUNCHERS.md)

### 5.2 按需读取

- 涉及协议边界时：
  [docs/contracts/TOOL_RUNTIME_CONTRACT.md](file:///d:/Repositories/PyToolDashboard/docs/contracts/TOOL_RUNTIME_CONTRACT.md)
- 涉及共享数据文件格式时：
  [docs/conventions/DATA_FORMATS.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/DATA_FORMATS.md)
- 涉及公共文档模板时：
  [docs/conventions/DOCUMENTATION.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/DOCUMENTATION.md)

### 5.3 附加要求

- 框架建构 Agent 可以跨模块维护框架层
- 框架建构 Agent 不承担具体功能实现
- 专项开发 Agent 的数量和拆分方式，默认由框架建构 Agent 决定

## 6. 专项开发 Agent

### 6.1 开工前必读

专项开发 Agent 在开始编码前，必须读取：

1. [docs/architecture/ARCHITECTURE.md](file:///d:/Repositories/PyToolDashboard/docs/architecture/ARCHITECTURE.md)
2. [docs/conventions/REPOSITORY_STRUCTURE.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/REPOSITORY_STRUCTURE.md)
3. [docs/conventions/AGENT_ORGANIZATION.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/AGENT_ORGANIZATION.md)
4. 当前目标模块的 `README.md`
5. 若目标涉及运行入口、launcher、跨 workspace 调度，补读 [docs/conventions/LAUNCHERS.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/LAUNCHERS.md)

补充要求：

- 若本次任务包含 **Python 代码开发**，应默认补读 [docs/conventions/CODE_STYLE.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/CODE_STYLE.md)
- 若任务已分配固定目录主责，应只修改自己的职责目录；跨目录需求应先显式升级

### 6.2 按需读取

- 写 Python / Web / C++ 代码风格时：
  [docs/conventions/CODE_STYLE.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/CODE_STYLE.md)
- 新增 JSON / CSV / schema / sidecar 数据文件时：
  [docs/conventions/DATA_FORMATS.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/DATA_FORMATS.md)
- 新增依赖、调整依赖边界时：
  [docs/conventions/DEPENDENCIES.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/DEPENDENCIES.md)
- 编写或修改 `tool.json`、request/response、preview 协议时：
  [docs/contracts/TOOL_RUNTIME_CONTRACT.md](file:///d:/Repositories/PyToolDashboard/docs/contracts/TOOL_RUNTIME_CONTRACT.md)
- 编写 README 或架构文档时：
  [docs/conventions/DOCUMENTATION.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/DOCUMENTATION.md)
- 编写或更新单个 tool 的架构设计文档时：
  [docs/conventions/ARCHITECTURE_DESIGN.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/ARCHITECTURE_DESIGN.md)
- 修改运行脚本、缓存/产物、退出码、日志行为时：
  [docs/conventions/OPERATIONS.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/OPERATIONS.md)
- 被要求生成 commit message 或执行提交时：
  [/.trae/rules/git-commit-message.md](file:///d:/Repositories/PyToolDashboard/.trae/rules/git-commit-message.md)

### 6.3 典型示例

- 只改某个 tool 的 Python 业务逻辑：
  读 `ARCHITECTURE.md` + `REPOSITORY_STRUCTURE.md` + `AGENT_ORGANIZATION.md` + 该 tool README，必要时再读 `CODE_STYLE.md`
- 要给 tool 新增 `result.json` / `result.csv`：
  在上面的基础上，加读 `DATA_FORMATS.md`
- 要让 tool 接入 dashboard：
  在上面的基础上，加读 `TOOL_RUNTIME_CONTRACT.md`
- 要为复杂 tool 新建或维护 `ARCHITECTURE_DESIGN.md`：
  在上面的基础上，加读 `ARCHITECTURE_DESIGN.md`

## 7. 验证文档 Agent

### 7.1 开工前必读

验证文档 Agent 在编写 README、规范文档、架构文档或验证记录前，必须读取：

1. [docs/conventions/DOCUMENTATION.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/DOCUMENTATION.md)
2. [docs/architecture/ARCHITECTURE.md](file:///d:/Repositories/PyToolDashboard/docs/architecture/ARCHITECTURE.md)
3. [docs/conventions/AGENT_ORGANIZATION.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/AGENT_ORGANIZATION.md)
4. 当前目标模块的 README 或相关现有文档

### 7.2 按需读取

- 若文档涉及代码风格说明：
  [docs/conventions/CODE_STYLE.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/CODE_STYLE.md)
- 若文档涉及 JSON / CSV / schema：
  [docs/conventions/DATA_FORMATS.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/DATA_FORMATS.md)
- 若文档涉及启动脚本或运行目录：
  [docs/conventions/LAUNCHERS.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/LAUNCHERS.md)
- 若文档涉及工具接入协议：
  [docs/contracts/TOOL_RUNTIME_CONTRACT.md](file:///d:/Repositories/PyToolDashboard/docs/contracts/TOOL_RUNTIME_CONTRACT.md)
- 若文档是某个 tool 的架构设计记录：
  [docs/conventions/ARCHITECTURE_DESIGN.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/ARCHITECTURE_DESIGN.md)

## 8. 仓库分析 Agent

### 8.1 开工前必读

仓库分析 Agent 在做结构分析、风险分析、边界审视前，必须读取：

1. [docs/architecture/ARCHITECTURE.md](file:///d:/Repositories/PyToolDashboard/docs/architecture/ARCHITECTURE.md)
2. [docs/conventions/REPOSITORY_STRUCTURE.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/REPOSITORY_STRUCTURE.md)
3. [docs/conventions/AGENT_ORGANIZATION.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/AGENT_ORGANIZATION.md)
4. 与本次分析范围对应的目录 README 或入口文件

### 8.2 按需读取

- 分析运行入口、工作目录或脚本封装时：
  [docs/conventions/LAUNCHERS.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/LAUNCHERS.md)
- 分析协议边界、dashboard-tool 通信时：
  [docs/contracts/TOOL_RUNTIME_CONTRACT.md](file:///d:/Repositories/PyToolDashboard/docs/contracts/TOOL_RUNTIME_CONTRACT.md)
- 分析数据组织时：
  [docs/conventions/DATA_FORMATS.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/DATA_FORMATS.md)
- 分析依赖污染时：
  [docs/conventions/DEPENDENCIES.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/DEPENDENCIES.md)

### 8.3 分析 Agent 的目标

仓库分析 Agent 的重点是：

- 识别目录职责是否清晰
- 判断依赖方向是否被破坏
- 判断运行目录假设是否正确
- 判断新文件是否放在了正确位置
- 判断多 Agent 目录归属是否发生重叠

## 9. 协议/集成 Agent

### 9.1 开工前必读

协议/集成 Agent 在处理 dashboard 与 tool 的接入、请求响应、预览、独立 launcher 策略时，必须读取：

1. [docs/architecture/ARCHITECTURE.md](file:///d:/Repositories/PyToolDashboard/docs/architecture/ARCHITECTURE.md)
2. [docs/conventions/AGENT_ORGANIZATION.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/AGENT_ORGANIZATION.md)
3. [docs/contracts/TOOL_RUNTIME_CONTRACT.md](file:///d:/Repositories/PyToolDashboard/docs/contracts/TOOL_RUNTIME_CONTRACT.md)
4. [docs/conventions/LAUNCHERS.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/LAUNCHERS.md)
5. 相关模块 README

### 9.2 按需读取

- 需要定义 JSON / CSV 交付格式时：
  [docs/conventions/DATA_FORMATS.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/DATA_FORMATS.md)
- 需要补充退出码、日志、缓存、运行目录细节时：
  [docs/conventions/OPERATIONS.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/OPERATIONS.md)
- 需要检查目录归属和共享包上收时：
  [docs/conventions/REPOSITORY_STRUCTURE.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/REPOSITORY_STRUCTURE.md)

### 9.3 协议 Agent 的重点

- 保证协议不绑定具体语言实现
- 保证 dashboard 不直接耦合 tool 内部代码
- 保证 `project_root` 与 `cwd` 语义一致
- 保证独立 launcher 与 dashboard 调度策略一致

## 10. 读取决策表

| 场景 | 必须补读的文件 |
| --- | --- |
| 要写 JSON 文件 | `DATA_FORMATS.md` |
| 要写 CSV 文件 | `DATA_FORMATS.md` |
| 要写 `tool.json` | `TOOL_RUNTIME_CONTRACT.md` |
| 要写 `ARCHITECTURE_DESIGN.md` | `ARCHITECTURE_DESIGN.md` |
| 要加 launcher / bat / sh | `LAUNCHERS.md` + `OPERATIONS.md` |
| 要加新依赖 | `DEPENDENCIES.md` |
| 要写 README | `DOCUMENTATION.md` |
| 要提交 commit | `.trae/rules/git-commit-message.md` |
| 要分析目录归属 | `REPOSITORY_STRUCTURE.md` |

## 11. Manager 对 Agent 的执行要求

1. 先按 Agent 类型读最小必要集
2. 不因“可能会用到”就预读全部规范
3. 若任务中途命中新场景，再补读相关文件
4. 若任务涉及多个模块，优先读取本次直接修改的模块文档
5. 输出中应说明自己读取了哪些关键规范，以及为什么需要读它们
6. 若任务受多 Agent 分工约束，应先确认自己的主责目录和不可越界范围

## 12. 当前建议

在本仓库当前阶段：

- **专项开发 Agent** 最常用
- **框架建构 Agent** 负责搭骨架和定拆分
- **架构维护 Agent** 负责规则沉淀和边界维护
- **验证文档 Agent** 负责验证与文档同步
- **协议/集成 Agent** 次之
- **仓库分析 Agent** 主要用于结构审视和重构前分析

如果任务不明确，默认先按**仓库分析 Agent**方式读取最小集合，再转入具体类型。
