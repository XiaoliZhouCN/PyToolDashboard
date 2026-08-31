# Mermaid Editor Agent Task Dispatch

## 1. 文档目的

本文件用于 `tools/mermaid_editor` 的多 Agent 协作开发。

目标：

1. 统一重构拆解方案，避免不同 Agent 各自理解边界
2. 统一模块职责、依赖方向、目录建构与交付物
3. 统一 Agent 分工、阅读入口、回复规范与交接协议
4. 作为后续 Agent 的主要协作文档，由架构分析 Agent 持续维护

使用规则：

1. 后续 Agent 开工前，先阅读本文件，再读取自己分配板块涉及的目标文件
2. 后续 Agent 的回复、阻塞、变更建议，统一追加到本文件的“Agent Reply Log”
3. 若实现过程中发现边界设计需要调整，先更新本文件，再进入开发

---

## 2. 当前问题摘要

当前 `mermaid_editor` 的总体技术路线没有问题：

- 桌面壳：`PySide6`
- 可视化画布：`QWebEngineView + HTML/CSS/JavaScript`
- Python 负责文件、解析、持久化、导出与调度

当前主要问题不在“技术选型”，而在“模块边界不够硬”：

1. `editor.html` 体量过大，状态、渲染、交互、桥接、工具栏、对话框、快捷键混在单文件中
2. Python Qt 层与 Web 层都持有整份图数据，跨层同步点较多
3. 几何规则在前端渲染层、SVG 导出层、PNG 导出层存在重复实现
4. 前端交互层测试薄弱，不利于调试和持续迭代

因此，本轮工作的目标不是推翻现有架构，而是：

**在保留 Qt + WebView 混合架构的前提下，重构为高可维护、可替换、可调试的分层结构。**

---

## 3. 重构总目标

### 3.1 目标

重构后的工程应满足：

1. 单个板块职责清晰，能独立替换或独立调试
2. 业务数据与界面状态严格分离
3. 交互逻辑不直接改渲染细节或文件内容
4. 文件读写不承担业务审核
5. 解析层只负责“文本 <-> 结构”
6. 渲染层只负责“结构/视图状态 -> UI 输出”
7. Qt 与 Web 之间只走明确协议，不走隐式共享逻辑

### 3.2 非目标

本轮不做：

1. 不改成纯 Web 工程
2. 不改成纯 Qt 原生绘图框架
3. 不引入远程服务或多人协作
4. 不一次性重写全部功能

---

## 4. 板块拆解方案

本工具后续按以下 8 个板块拆解。

### 4.1 App Shell

职责：

- 启动程序
- 装配依赖
- 创建 Qt 窗口与 WebView
- 注册 bridge
- 处理 CLI 入口与运行时上下文

不负责：

- Mermaid 语义解析
- 图结构编辑规则
- DOM/SVG 渲染细节
- 文件内容审核

当前主要归属：

- `app/cli.py`
- `app/main_window.py`
- `app/bridge.py`

### 4.2 Application Coordinator

职责：

- 组织用例流程
- 接收交互层意图，调用领域层与持久化层
- 管理“打开文件 / 应用源码 / 保存 / 导出 / 同步选中对象 / 撤销重做”等流程
- 统一 command 与 action 编排

不负责：

- 直接操作 DOM
- 直接解析 Mermaid 文本细节
- 直接读写底层文件格式

说明：

该层是“编排层”，不是“上帝模块”。它只串流程，不吃掉所有职责。

### 4.3 Parsing Layer

该层继续拆为两部分。

#### A. Markdown Parsing

职责：

- 从 Markdown 中提取 Mermaid block
- 将更新后的 Mermaid 文本回填到 Markdown
- 维护文档与图块之间的位置关系

不负责：

- Mermaid 语义分析
- 节点/边/子图编辑规则

#### B. Mermaid Semantic Parsing

职责：

- Mermaid 文本与图模型之间的双向转换
- Mermaid 语法合法性校验
- 默认布局生成

不负责：

- 文件读写
- 交互事件处理
- Qt / DOM 渲染

### 4.4 Persistence Layer

职责：

- 读写 Markdown 文件
- 读写 sidecar 布局文件
- 读写导出产物路径

不负责：

- 审核 Mermaid 内容是否正确
- 判断图结构是否合法
- 渲染

说明：

Persistence 只负责 I/O，不负责业务判断。

### 4.5 Domain Layer

职责：

- 定义图模型
- 维护结构编辑规则
- 维护节点/边/子图约束
- 维护布局几何规则
- 维护合法引用与归一化逻辑

不负责：

- 文件系统 I/O
- Qt / Web UI
- 用户输入事件

### 4.6 Data Store Layer

该层必须严格拆为两类状态。

#### A. Domain Store

职责：

- 维护可保存的核心图数据
- 维护当前文档、当前 diagram、结构修改后的最新状态

包含：

- nodes
- edges
- subgraphs
- direction
- source
- layout

#### B. View Store

职责：

- 维护不可持久化的界面状态

包含：

- 当前选中
- hover 状态
- 缩放比例
- 画布平移
- 拖拽中状态
- 框选状态
- 对话框开关
- 工具栏高度

规则：

- `View Store` 不得直接写回 Markdown
- `Domain Store` 不得混入“拖拽中临时像素状态”

### 4.7 Interaction Layer

职责：

- 接收鼠标、键盘、右键菜单、拖拽、框选等输入
- 将输入翻译为标准化意图或命令
- 把命令发给 Application Coordinator / Data Store

不负责：

- 文件读写
- Mermaid 文本解析
- 直接维护 SVG 结构细节

### 4.8 Presentation Layer

该层继续拆为两块。

#### A. Web Renderer

职责：

- 根据 Domain Store + View Store 渲染 SVG / HTML
- 不直接修改业务数据

#### B. Qt Presentation

职责：

- 左侧列表、源码面板、详情面板、状态栏、窗口布局
- 不承担 Mermaid 业务规则

---

## 5. 推荐依赖方向

推荐依赖方向如下：

```text
App Shell
  -> Application Coordinator
  -> Qt Presentation
  -> Bridge / Protocol

Application Coordinator
  -> Domain
  -> Parsing Layer
  -> Persistence Layer
  -> Data Store Layer

Interaction Layer
  -> Application Coordinator
  -> Data Store Layer

Presentation Layer
  -> Data Store Layer (read-only)
  -> Bridge / Protocol

Persistence Layer
  -> no UI dependency

Parsing Layer
  -> Domain
  -> no UI dependency

Domain
  -> no Qt / no DOM / no file system dependency
```

禁止：

1. Renderer 直接写文件
2. Interaction 直接改 Markdown
3. Persistence 审核 Mermaid 语义
4. Bridge 承担业务规则
5. Domain 依赖 Qt / Web API

---

## 6. 推荐目录建构

### 6.1 可否支持“严格目录授权”

结论：

**原始推荐目录建构接近可用，但还不能完全支持“每个 Agent 只负责互不重叠目录”的强约束。**

原方案中的主要冲突点有：

1. `tests/` 还是一个共享大目录，不利于严格归属
2. `app/` 与 `presentation/qt/` 的边界容易重叠
3. `presentation/web/scripts/utils/` 是典型的模糊共享目录，容易变成多人混改入口
4. `infra/gateway/` 归属不够明确，容易和 `protocols/`、`repository/` 混淆
5. `preview/`、`schemas/`、`protocols/` 需要由同一类 Agent 统一收口，否则协议与验证会分散

因此，若要满足你的要求：

- A0 只管架构和总文档
- A1 可跨目录搭框架
- A2 ~ A7 必须严格按目录边界开发、彼此不重叠

则推荐对目录建构做进一步收紧。

### 6.2 调整后的目录建构

建议未来目录演进为：

```text
tools/mermaid_editor/
├── to_agent/
│   └── AGENT_TASK_DISPATCH.md
├── architecture_design/
├── samples/
├── verification/
│   ├── handoff/
│   ├── integration/
│   └── manual_checks/
├── src/
│   └── ptd_tool_mermaid_editor/
│       ├── app/
│       │   ├── cli.py
│       │   ├── bootstrap.py
│       │   └── runtime.py
│       ├── application/
│       │   ├── commands/
│       │   ├── coordinator/
│       │   ├── store/
│       │   └── undo/
│       ├── domain/
│       │   ├── graph.py
│       │   ├── editor/
│       │   ├── geometry/
│       │   └── validation/
│       ├── parsing/
│       │   ├── markdown/
│       │   └── mermaid/
│       ├── infra/
│       │   ├── repository/
│       │   ├── export/
│       ├── presentation/
│       │   ├── qt/
│       │   └── web/
│       │       ├── index.html
│       │       ├── styles/
│       │       ├── bridge/
│       │       ├── render/
│       │       └── interaction/
│       │           ├── commands/
│       │           └── state/
│       ├── protocols/
│       ├── preview/
│       └── schemas/
├── tests/
│   ├── parsing_domain/
│   ├── infra_export/
│   ├── presentation_qt/
│   ├── presentation_web_render/
│   ├── application_interaction/
│   └── protocols_integration/
├── README.md
├── pyproject.toml
├── requirements.txt
├── run.py
└── tool.json
```

说明：

1. `editor.html` 后续应逐步拆为 `presentation/web/` 下的静态资源目录
2. 共享几何规则应从 UI 与 export 中抽离到 `domain/geometry/`
3. Qt 与 Web 的消息结构应进入 `protocols/`
4. 不再保留跨 Agent 共用的 `utils/` 目录；辅助代码应就近放入所属目录
5. `tests/` 必须按 Agent 所属板块拆分，避免测试目录成为新的共享修改入口
6. `verification/` 用于存放协议验收、手工检查与交接记录，避免和 `architecture_design/` 混淆

### 6.3 目录所有权规则

为实现严格授权，采用以下规则：

1. A2 ~ A7 只能修改自己被授权的目录
2. 除 A1 外，任何 Agent 不得跨目录重构或移动其他 Agent 目录下的文件
3. 若某个需求同时影响多个目录，必须通过接口、参数、协议或回复日志提出，由对应目录所有者完成
4. `architecture_design/` 与 `to_agent/` 默认由 A0 维护；其他 Agent 只能通过回复日志提出修改建议
5. 根目录文件采用“主责所有者”制度；除 A1 外，其他 Agent 只能修改自己主责的根文件

### 6.4 当前建议的根目录主责归属

| 路径 | 主责 Agent | 说明 |
| --- | --- | --- |
| `to_agent/` | A0 | 多 Agent 分发与交接中心 |
| `architecture_design/` | A0 | 架构与功能状态文档 |
| `verification/` | A7 | 验收记录、手工检查、集成结果 |
| `samples/` | A7 | 用于协议与集成验证的样例数据 |
| `README.md` | A0 | 总体对外说明，由 A0 统一同步 |
| `tool.json` | A7 | 协议与运行时契约主责 |
| `run.py` | A1 | 启动与框架入口主责 |
| `pyproject.toml` | A1 | 框架装配与工程骨架主责 |
| `requirements.txt` | A1 | 工程依赖主责 |

---

## 7. Agent 编制建议

建议采用 **1 个架构维护 Agent + 1 个框架建构 Agent + 5 个专项开发 Agent + 1 个验证文档 Agent** 的编制。

总计建议：**8 个 Agent**

### 7.1 A0 - 架构维护 Agent

职责：

- 维护本文件
- 审核拆解边界
- 处理跨板块依赖冲突
- 决定模块归属与协议版本

规则：

- 不承担具体编码
- 只做架构与任务分发

### 7.2 A1 - 框架建构 Agent

职责：

- 完成目录重构骨架
- 建立新模块空壳
- 建立依赖边界
- 搭建基础协议层、状态层、command 层

交付：

- 新目录结构
- 模块入口
- 迁移计划落地点

目录权限范围：

- 可跨目录修改 `src/ptd_tool_mermaid_editor/` 全部目录，仅限于：
  - 建立目录骨架
  - 建立空模块
  - 搬迁文件
  - 调整依赖入口
  - 修正 import / 装配关系
- 可修改根目录：
  - `run.py`
  - `pyproject.toml`
  - `requirements.txt`
- 不负责长期维护任何业务子目录的具体实现细节

### 7.3 A2 - Parsing & Domain Agent

职责：

- 维护 Markdown 解析与 Mermaid 解析
- 整理图模型与领域规则
- 抽离 geometry / validation 共享规则

交付：

- `parsing/`
- `domain/`
- 相关单元测试

目录权限范围：

- `src/ptd_tool_mermaid_editor/parsing/`
- `src/ptd_tool_mermaid_editor/domain/`
- `tests/parsing_domain/`

禁止修改：

- `infra/`
- `presentation/`
- `protocols/`
- `schemas/`

### 7.4 A3 - Persistence & Export Agent

职责：

- 维护 Markdown / layout sidecar 读写
- 维护 SVG / PNG 导出
- 清理导出层与渲染层的重复几何实现

交付：

- `infra/repository/`
- `infra/export/`
- 导出相关测试

目录权限范围：

- `src/ptd_tool_mermaid_editor/infra/repository/`
- `src/ptd_tool_mermaid_editor/infra/export/`
- `tests/infra_export/`

禁止修改：

- `domain/`
- `parsing/`
- `presentation/`
- `protocols/`

### 7.5 A4 - Qt Presentation Agent

职责：

- 维护 Qt 主窗口
- 维护左侧图列表、源码编辑区、详情面板、状态栏
- 将 Qt UI 从业务编排中解耦

交付：

- `presentation/qt/`
- `tests/presentation_qt/`

目录权限范围：

- `src/ptd_tool_mermaid_editor/presentation/qt/`
- `tests/presentation_qt/`

备注：

- `app/` 不归 A4 长期维护；若 Qt 表现层需要新的装配入口，应通过 A1 调整

### 7.6 A5 - Web Renderer Agent

职责：

- 将当前单文件前端拆为渲染模块
- 保证渲染层只吃 ViewModel，不直接处理业务命令

交付：

- `presentation/web/render/`
- `presentation/web/styles/`
- 渲染层基础结构

目录权限范围：

- `src/ptd_tool_mermaid_editor/presentation/web/index.html`
- `src/ptd_tool_mermaid_editor/presentation/web/render/`
- `src/ptd_tool_mermaid_editor/presentation/web/styles/`
- `tests/presentation_web_render/`

禁止修改：

- `presentation/web/interaction/`
- `presentation/web/bridge/`
- `application/`

### 7.7 A6 - Interaction Agent

职责：

- 拆出拖拽、框选、快捷键、右键菜单、对话框、缩放平移等交互逻辑
- 输出标准 command / intent

交付：

- `application/`
- `presentation/web/interaction/`
- 交互状态管理测试

目录权限范围：

- `src/ptd_tool_mermaid_editor/application/`
- `src/ptd_tool_mermaid_editor/presentation/web/interaction/`
- `src/ptd_tool_mermaid_editor/presentation/web/interaction/commands/`
- `src/ptd_tool_mermaid_editor/presentation/web/interaction/state/`
- `tests/application_interaction/`

禁止修改：

- `presentation/web/render/`
- `presentation/web/bridge/`
- `protocols/`

### 7.8 A7 - Protocol & Verification Agent

职责：

- 设计 Qt <-> Web 消息协议
- 维护协议文档与版本
- 维护前后端集成测试、手工验证清单、迁移验收记录

交付：

- `protocols/`
- 协议说明
- 集成验证文档

目录权限范围：

- `src/ptd_tool_mermaid_editor/protocols/`
- `src/ptd_tool_mermaid_editor/presentation/web/bridge/`
- `src/ptd_tool_mermaid_editor/preview/`
- `src/ptd_tool_mermaid_editor/schemas/`
- `verification/`
- `samples/`
- `tests/protocols_integration/`
- `tool.json`

禁止修改：

- `domain/`
- `parsing/`
- `infra/`
- `presentation/qt/`
- `presentation/web/render/`
- `presentation/web/interaction/`

---

## 8. Agent 开发顺序

推荐顺序如下：

1. `A0 架构维护 Agent`
2. `A1 框架建构 Agent`
3. `A7 Protocol & Verification Agent`
4. `A2 Parsing & Domain Agent`
5. `A3 Persistence & Export Agent`
6. `A4 Qt Presentation Agent`
7. `A5 Web Renderer Agent`
8. `A6 Interaction Agent`

原因：

1. 先定框架和协议，再让专项 Agent 落实现
2. 先稳定领域模型和协议，避免前后端接口反复返工
3. Web 渲染与交互拆分后，交互层才能真正做到只发命令

---

## 9. 交付边界要求

每个 Agent 的交付都必须包含以下内容：

1. 修改了哪些目录和文件
2. 本次新增了哪些模块边界
3. 输入是什么
4. 输出是什么
5. 依赖了哪些已有模块
6. 没有解决的遗留问题
7. 建议下一个 Agent 从哪里接手

禁止只回复“已完成”而不说明交接点。

---

## 10. 信息传递协议

本项目的 Agent 间信息传递，分为三层。

### 10.1 任务层协议

用于描述“谁做什么”。

字段：

- `task_id`
- `agent_id`
- `scope`
- `inputs`
- `outputs`
- `dependencies`
- `blocked_by`
- `status`

状态取值：

- `pending`
- `in_progress`
- `blocked`
- `done`

### 10.2 模块层协议

用于描述板块接口。

每个模块都必须写清楚：

1. 输入 DTO
2. 输出 DTO
3. 同步 / 异步
4. 是否可重入
5. 错误返回方式
6. 是否允许直接调用底层依赖

### 10.3 运行时消息协议

用于 Qt 与 Web、Interaction 与 Coordinator、Coordinator 与 Store 的消息传递。

建议统一消息结构：

```json
{
  "schema_version": "1.0",
  "message_type": "command.apply_patch",
  "source": "web.interaction",
  "target": "application.coordinator",
  "request_id": "req-001",
  "payload": {}
}
```

要求：

1. 所有跨层消息都带 `message_type`
2. 所有可追踪请求都带 `request_id`
3. 协议升级时更新 `schema_version`
4. 不允许使用无类型的裸 JSON 字符串作为长期协议

---

## 11. 开发规范

### 11.1 状态修改规范

1. 所有图结构修改统一经过 command / coordinator
2. Renderer 不允许直接写 `Domain Store`
3. Interaction 不允许直接保存文件
4. 保存动作必须经过 Coordinator -> Parsing -> Persistence

### 11.2 调试规范

1. 每个模块应有独立日志前缀
2. 协议消息需可打印、可定位
3. 交互问题优先沿“输入 -> command -> store -> render”链路排查

### 11.3 文档维护规范

1. 本文件是总分发文档
2. 若后续某板块复杂度显著上升，可单独再开对应子文档
3. 若本文件与实际结构不一致，以本文件修订为优先任务之一

### 11.4 用户反馈分发规则

`FEATURES_AND_USAGE.md` 面向使用者，应保持为纯用户说明文档，不写 Agent 分工信息。

因此后续协作中采用以下规则：

1. 用户只从使用者视角描述问题、体验反馈或想要的功能
2. 由 `A0` 负责理解反馈，并在内部判断模块归属
3. 若问题涉及多个目录或多个板块，由 `A0` 拆为主责 Agent 与协同 Agent
4. Agent 间的模块归属、目录权限和交接边界，只保留在 `to_agent/` 文档体系中

默认分发规则：

1. 解析正确性、结构一致性、Mermaid 语义问题 -> `A2`
2. 保存、sidecar、导出、文件落盘问题 -> `A3`
3. 左侧面板、Qt 布局、窗口行为问题 -> `A4`
4. 画布显示、样式、高亮、工具栏视觉问题 -> `A5`
5. 拖拽、快捷键、多选、框选、撤销、触控板交互问题 -> `A6`
6. 协议、运行契约、preview、schema、验证缺失问题 -> `A7`

---

## 12. 当前建议分工

### 12.1 当前代码快照

截至当前交接时点，`mermaid_editor` 已确认的实现状态如下：

1. 当前工具仍基于 `PySide6 + QWebEngineView + editor.html` 单文件前端
2. `editor.html` 已接入基础 `Ctrl+Z` 撤销
3. 子图拖拽链路已改为更稳的 pointer capture + 全局 pointer 跟踪实现
4. 左侧面板已调整为默认约 `1/3`，并限制最大不超过 `1/2`
5. Mermaid 解析已改为“两阶段解析”：先收集定义，再解析边
6. 已补回归测试覆盖：
   - 边先于定义出现的解析场景
   - 嵌套子图 `direction` 的默认布局场景

当前需要特别注意的实际代码文件：

- `src/ptd_tool_mermaid_editor/app/static/editor.html`
- `src/ptd_tool_mermaid_editor/app/main_window.py`
- `src/ptd_tool_mermaid_editor/domain/mermaid_parser.py`
- `tests/test_mermaid_parser.py`

### 12.2 当前验证状态

已验证：

- `python -m unittest discover -s tools/mermaid_editor/tests` 通过
- 当前测试结果：`15` tests，`2` skipped

未在当前环境完成的验证：

- 因环境缺少 `PySide6`，未完成桌面端实机交互复验
- 因环境限制，触控板手势仅完成静态实现与代码级检查，未完成真实设备体验确认

### 12.3 A1 开工前必读

`A1 框架建构 Agent` 开工前必须优先阅读：

1. `tools/mermaid_editor/to_agent/AGENT_TASK_DISPATCH.md`
2. `tools/mermaid_editor/architecture_design/ARCHITECTURE_DESIGN.md`
3. `tools/mermaid_editor/architecture_design/FEATURES_AND_USAGE.md`
4. `tools/mermaid_editor/README.md`

在进入重构前，应特别确认：

1. 当前任务目标是“拆框架与边界”，不是继续往 `editor.html` 堆新功能
2. 当前文档已将基础撤销记为“已存在但不完整”，不得再按“完全未实现”理解
3. 当前 parser 两阶段解析与对应回归测试已经存在，重构时不得回退
4. `to_agent/` 是后续跨 Agent 交接的正式入口，应继续沿用

当前阶段建议：

1. 先由 `A1 框架建构 Agent` 进行目录与骨架拆分
2. 同时由 `A7 Protocol & Verification Agent` 起草协议与验收清单
3. 在框架稳定前，其他开发 Agent 不要直接继续向原 `editor.html` 大量堆功能

---

## 13. Agent Reply Log

后续 Agent 统一按以下模板在本节追加回复。

### Reply Template

```md
#### [agent_id] <agent_name>

- Time:
- Scope:
- Status: pending | in_progress | blocked | done
- Files:
- Inputs:
- Outputs:
- Dependencies:
- Risks:
- Next handoff:
- Notes:
```

### Replies

#### [A0] architecture_analyst

- Time: initial
- Scope: 建立 `mermaid_editor` 多 Agent 协作总任务分发文档
- Status: done
- Files:
  - `tools/mermaid_editor/to_agent/AGENT_TASK_DISPATCH.md`
- Inputs:
  - 当前 `mermaid_editor` 实现结构
  - 当前架构分析结论
- Outputs:
  - 板块拆解方案
  - Agent 编制建议
  - 信息传递协议与回复模板
- Dependencies:
  - `architecture_design/ARCHITECTURE_DESIGN.md`
  - 当前源码结构
- Risks:
  - 后续若框架建构阶段发现目录归属需要微调，应优先修订本文件
- Next handoff:
  - `A1 框架建构 Agent`
- Notes:
  - 当前建议先拆框架与协议，再进入具体开发板块实现

#### [A0] architecture_analyst

- Time: handoff_audit
- Scope: 交接前审计当前实现状态，并同步 README / architecture / features / dispatch 文档
- Status: done
- Files:
  - `tools/mermaid_editor/README.md`
  - `tools/mermaid_editor/architecture_design/ARCHITECTURE_DESIGN.md`
  - `tools/mermaid_editor/architecture_design/FEATURES_AND_USAGE.md`
  - `tools/mermaid_editor/to_agent/AGENT_TASK_DISPATCH.md`
- Inputs:
  - 当前源码实现
  - 当前测试结果
  - 当前体验反馈状态
- Outputs:
  - 已同步基础撤销、两阶段解析、交接入口与当前验证状态
  - 已补充 A1 开工前必读与当前代码快照
- Dependencies:
  - `src/ptd_tool_mermaid_editor/app/static/editor.html`
  - `src/ptd_tool_mermaid_editor/app/main_window.py`
  - `src/ptd_tool_mermaid_editor/domain/mermaid_parser.py`
  - `tests/test_mermaid_parser.py`
- Risks:
  - 触控板与桌面端实机交互在当前环境中仍未完成最终体验确认
- Next handoff:
  - `A1 框架建构 Agent`
- Notes:
  - 当前交接文档已按最新实现状态同步，可作为后续框架重构入口

#### [A1] framework_builder

- Time: 2026-08-29
- Scope: 按 `6.2 调整后的目录建构` 落地首轮框架骨架，并保持现有 CLI / preview / action / parser 测试链路可用
- Status: done
- Files:
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/app/cli.py`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/app/bootstrap.py`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/app/runtime.py`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/application/`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/domain/editor/`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/domain/geometry/`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/domain/validation/`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/parsing/`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/infra/repository/`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/infra/export/`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/presentation/`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/protocols/`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/presentation/web/index.html`
  - `tools/mermaid_editor/tests/__init__.py`
  - `tools/mermaid_editor/tests/parsing_domain/`
  - `tools/mermaid_editor/tests/infra_export/`
  - `tools/mermaid_editor/tests/presentation_qt/`
  - `tools/mermaid_editor/tests/presentation_web_render/`
  - `tools/mermaid_editor/tests/application_interaction/`
  - `tools/mermaid_editor/tests/protocols_integration/`
  - `tools/mermaid_editor/verification/`
  - `tools/mermaid_editor/pyproject.toml`
- Inputs:
  - 当前 `app / actions / domain / infra / preview / schemas` 结构
  - 现有 CLI / preview / action / desktop shell 运行链路
  - `6.2 调整后的目录建构` 目标目录方案
- Outputs:
  - 已建立新的 `application / parsing / infra/repository / infra/export / presentation / protocols` 骨架
  - 已补 `app/bootstrap.py` 与 `app/runtime.py`，并让 CLI 通过新装配入口启动
  - 已复制 `editor.html` 到 `presentation/web/index.html`
  - 已将导出几何锚点逻辑抽出到 `domain/geometry/anchors.py`
  - 已为新测试目录与 `verification/` 建立首轮可跟踪骨架
  - 现有测试仍通过：`15` tests，`2` skipped
- Dependencies:
  - `src/ptd_tool_mermaid_editor/app/main_window.py`
  - `src/ptd_tool_mermaid_editor/app/static/editor.html`
  - `src/ptd_tool_mermaid_editor/domain/mermaid_parser.py`
  - `src/ptd_tool_mermaid_editor/infra/layout_store.py`
  - `src/ptd_tool_mermaid_editor/infra/markdown_loader.py`
  - `src/ptd_tool_mermaid_editor/actions/svg_export.py`
  - `src/ptd_tool_mermaid_editor/actions/png_export.py`
- Risks:
  - 当前新目录中仍存在部分兼容壳，真实业务实现尚未完全迁移出旧路径
  - `presentation/web/render`、`presentation/web/interaction`、`presentation/web/bridge` 目前仅完成目录落点，尚未拆出原 `editor.html` 内部模块
  - `presentation/qt/main_window.py` 当前仍通过兼容导出复用旧 `app.main_window`
- Next handoff:
  - `A7 Protocol & Verification Agent` 可从 `protocols/`、`presentation/web/bridge/`、`verification/` 开始补协议与验收清单
  - `A2 Parsing & Domain Agent` 可从 `parsing/`、`domain/editor/`、`domain/geometry/` 接手，把兼容壳替换为真实实现
- Notes:
  - 本轮优先目标是“新骨架先落地，旧功能不回退”，因此保留了旧模块路径作为兼容层

#### [A1] framework_builder

- Time: 2026-08-29-migration
- Scope: 将核心实现迁入新目录，使 `presentation / parsing / infra / domain.editor` 成为真实实现落点，同时保留旧路径兼容导出
- Status: done
- Files:
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/presentation/qt/main_window.py`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/presentation/web/bridge/editor_bridge.py`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/parsing/markdown/loader.py`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/parsing/mermaid/parser.py`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/domain/editor/diagram_editor.py`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/infra/repository/layout_repository.py`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/infra/export/svg_exporter.py`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/infra/export/png_exporter.py`
  - 兼容壳：
    - `app/main_window.py`
    - `app/bridge.py`
    - `domain/mermaid_parser.py`
    - `domain/diagram_editor.py`
    - `infra/markdown_loader.py`
    - `infra/layout_store.py`
    - `actions/svg_export.py`
    - `actions/png_export.py`
- Inputs:
  - 已建立的新目录骨架
  - 当前真实实现仍位于旧目录的模块
  - 现有 CLI / preview / action / 测试链路
- Outputs:
  - 新目录已承载 Qt 主窗口、bridge、Markdown 解析、Mermaid 解析、编辑规则、layout repository、SVG/PNG 导出真实实现
  - 旧目录改为兼容导出层
  - `presentation/qt/main_window.py` 已切换为加载 `presentation/web/index.html`
  - `preview` CLI 仍可在无 `PySide6` 环境中运行
- Dependencies:
  - `src/ptd_tool_mermaid_editor/app/bootstrap.py`
  - `src/ptd_tool_mermaid_editor/app/cli.py`
  - `src/ptd_tool_mermaid_editor/preview/service.py`
  - `src/ptd_tool_mermaid_editor/actions/service.py`
- Risks:
  - `presentation/web/index.html` 目前仍是单文件前端，尚未拆为 render / interaction 子模块
  - 兼容壳仍需在后续阶段逐步收缩，否则长期会形成双入口认知负担
- Next handoff:
  - `A5 Web Renderer Agent`
  - `A6 Interaction Agent`
  - `A7 Protocol & Verification Agent`
- Notes:
  - 迁移目标是“实现位置迁入新目录”，不是“重写功能”；本轮未主动改变现有行为

#### [A7] protocol_verification_agent

- Time: 2026-08-29-docs
- Scope: 基于迁移后的真实实现，补齐协议说明、CLI/测试验证记录、手工复验清单与交接说明
- Status: done
- Files:
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/protocols/README.md`
  - `tools/mermaid_editor/verification/integration/A7_CLI_AND_TEST_RESULTS.md`
  - `tools/mermaid_editor/verification/manual_checks/A7_MANUAL_CHECKLIST.md`
  - `tools/mermaid_editor/verification/handoff/A7_MIGRATION_PROTOCOL_HANDOFF.md`
- Inputs:
  - `src/ptd_tool_mermaid_editor/protocols/messages.py`
  - `src/ptd_tool_mermaid_editor/presentation/web/index.html`
  - 当前 CLI 与测试执行结果
- Outputs:
  - 已记录 `RuntimeMessage` 包络模型
  - 已记录当前 Qt <-> Web bridge 的具名方法协议
  - 已记录自动化验证结果与当前未验证项
  - 已建立后续桌面实机复验 checklist
- Dependencies:
  - `docs/contracts/TOOL_RUNTIME_CONTRACT.md`
  - 当前 `tool.json`
  - 当前 Web bridge 实现与页面函数
- Risks:
  - 当前 Web 侧仍未全面切换到统一消息总线，bridge 还是过渡协议
  - 桌面端实机验证仍依赖具备 `PySide6` 的环境
- Next handoff:
  - `A5 Web Renderer Agent` 可继续拆 `presentation/web/render/`
  - `A6 Interaction Agent` 可继续拆 `presentation/web/interaction/`
  - `A7 Protocol & Verification Agent` 后续需继续把具名 bridge 收口为统一消息协议
- Notes:
  - 本轮文档只写入 `protocols/` 与 `verification/`，未越权修改 A0 主责的 README / architecture 文档

#### [A7] protocol_verification_agent

- Time: 2026-08-29-v013-p000-acceptance
- Scope: 对 `v0.1.3` 当前三项 `P000` 交互修复做验收归档，并同步用户反馈勾选、自动化结果与实机边界
- Status: done
- Files:
  - `tools/mermaid_editor/to_agent/user_feedback.md`
  - `tools/mermaid_editor/verification/integration/A7_CLI_AND_TEST_RESULTS.md`
  - `tools/mermaid_editor/verification/manual_checks/A7_MANUAL_CHECKLIST.md`
  - `tools/mermaid_editor/verification/handoff/A7_V013_P000_ACCEPTANCE.md`
- Inputs:
  - 用户给定的当前已知验证结果
  - `presentation/qt/main_window.py`
  - `presentation/web/index.html`
  - 2026-08-29 复跑的 unittest / compileall 结果
- Outputs:
  - 已关闭 `user_feedback.md` 中三项 `v0.1.3 P000` 条目，并补充验收备注
  - 已补充 `compileall` 结果与页面入口对齐说明
  - 已新增 `A7_V013_P000_ACCEPTANCE.md` 作为本轮正式验收记录
  - 已把未完成的桌面端实机复验边界写入手工清单
- Dependencies:
  - `src/ptd_tool_mermaid_editor/presentation/qt/main_window.py`
  - `src/ptd_tool_mermaid_editor/presentation/web/index.html`
  - `tools/mermaid_editor/tests/`
- Risks:
  - 当前验收仍属于“自动化基线 + 文档归档”，不等于桌面端最终实机关闭
  - `PySide6 + QWebEngineView` 环境缺失时，无法直接确认子图选中抖动与平移偏移已在真实设备上彻底消失
- Next handoff:
  - 具备桌面环境的执行方应按 `verification/manual_checks/A7_MANUAL_CHECKLIST.md` 完成实机复验
  - 后续 Web 拆分阶段需保留这三项 `P000` 作为回归检查项
- Notes:
  - 本轮未回退任何既有代码或文档改动，只追加验收与交接记录

#### [A6] interaction_agent

- Time: 2026-08-31-v200-m4-redo
- Scope: 为 `v2.0 / M4` 补齐撤销/重做闭环与快捷键支持
- Status: done
- Files:
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/presentation/web/index.html`
  - `tools/mermaid_editor/tests/application_interaction/test_history_redo_contract.py`
- Inputs:
  - `ARCHITECTURE_DESIGN.md` 中 `M4` 缺口定义
  - 当前 Web 历史栈与快捷键链路
- Outputs:
  - 已新增 `redoDiagramChange()`
  - 已统一 `pushSnapshot / pushUndoSnapshot / pushRedoSnapshot` 历史语义
  - 已接入 `Ctrl+Y / Ctrl+Shift+Z`
  - 已补 `redo` 契约测试
- Dependencies:
  - `src/ptd_tool_mermaid_editor/presentation/web/index.html`
  - `tests/application_interaction/`
- Risks:
  - 当前仍缺 `PySide6 + QWebEngineView` 桌面壳中的真实键盘事件复验
- Next handoff:
  - `A1 framework_builder` 审查目录边界与集成状态
  - `A7 acceptance` 记录最小验收结论
- Notes:
  - 本轮只修改真实入口 `presentation/web/index.html`，旧兼容副本未同步 redo

#### [A5] web_renderer_agent

- Time: 2026-08-31-v200-m4-edge-anchor
- Scope: 为 `v2.0 / M4` 落地边端点侧向编辑与可视化手柄链路
- Status: done
- Files:
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/presentation/web/index.html`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/presentation/qt/main_window.py`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/domain/graph.py`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/domain/geometry/`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/domain/editor/diagram_editor.py`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/parsing/mermaid/parser.py`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/infra/export/svg_exporter.py`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/infra/export/png_exporter.py`
  - `tools/mermaid_editor/tests/test_mermaid_parser.py`
  - `tools/mermaid_editor/tests/presentation_web_render/test_edge_marker_contract.py`
- Inputs:
  - 长期 backlog “连接点子编辑功能”
  - 当前边路径、详情面板、Mermaid round-trip、导出链路
- Outputs:
  - 已新增 `source_anchor_side / target_anchor_side`
  - 已落地边端点侧向手柄和详情面板编辑入口
  - 已补 Mermaid 注释元数据 round-trip
  - 已让 SVG / PNG 导出复用同一边端点侧向数据
- Dependencies:
  - `presentation/web/index.html`
  - `presentation/qt/main_window.py`
  - `parsing/mermaid/parser.py`
  - `infra/export/`
- Risks:
  - 高密度图下手柄遮挡仍需后续 UI 微调
- Next handoff:
  - `A1 framework_builder`
  - `A7 acceptance`
- Notes:
  - 本轮没有另起一套状态，仍以统一图模型为中心

#### [A7] protocol_verification_agent

- Time: 2026-08-31-v200-m4-protocol
- Scope: 为 `v2.0 / M4` 收紧 `Web -> Qt` 运行时协议边界
- Status: done
- Files:
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/protocols/messages.py`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/protocols/qt_web.py`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/protocols/__init__.py`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/protocols/README.md`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/presentation/web/bridge/editor_bridge.py`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/presentation/web/index.html`
  - `tools/mermaid_editor/tests/protocols_integration/test_editor_bridge_runtime_protocol.py`
  - `tools/mermaid_editor/tests/protocols_integration/test_web_runtime_protocol_contract.py`
- Inputs:
  - `RuntimeMessage` 包络模型
  - 当前具名 bridge 调用链
- Outputs:
  - 已新增 `bridge.postMessage(...)` 上行入口
  - 已让旧具名方法在 Qt 侧归一化为同一套 runtime message 分发
  - 已补协议集成测试与文档说明
- Dependencies:
  - `protocols/`
  - `presentation/web/bridge/`
  - `presentation/web/index.html`
- Risks:
  - `Qt -> Web` 下行仍未统一收口
  - `schema_version / request_id` 仍未做强约束
- Next handoff:
  - `A1 framework_builder`
  - `A7 acceptance`
- Notes:
  - 当前协议层属于“上行已统一、下行仍兼容”的过渡态

#### [A1] framework_builder

- Time: 2026-08-31-v200-m4-review
- Scope: 审查 `v2.0 / M4` 当前实现是否满足目录边界与框架约束
- Status: blocked
- Files:
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/presentation/qt/main_window.py`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/presentation/web/index.html`
  - `tools/mermaid_editor/src/ptd_tool_mermaid_editor/application/coordinator/`
  - `tools/mermaid_editor/to_agent/AGENT_TASK_DISPATCH.md`
  - `tools/mermaid_editor/verification/handoff/A1_V200_M4_ARCH_REVIEW.md`
- Inputs:
  - 当前 M4 实现
  - 目录授权与依赖方向要求
- Outputs:
  - 已确认真实运行入口正确
  - 已指出 `presentation/qt/main_window.py` 仍越层承担编排职责
  - 已指出 `redo / edge interaction / runtime dispatcher` 仍集中在 `presentation/web/index.html`
  - 已新增 A1 审查回执
- Dependencies:
  - `presentation/qt/`
  - `presentation/web/`
  - `application/coordinator/`
- Risks:
  - 若不继续收口边界，后续 Agent 目录授权会持续与真实代码分布不一致
- Next handoff:
  - `A0` 评估是否进入后续框架收口轮次
  - `A7 acceptance` 在不夸大结论的前提下做最小归档
- Notes:
  - 本轮结论是“功能完成，但框架边界未完全放行”

#### [A7] acceptance_agent

- Time: 2026-08-31-v200-m4-acceptance
- Scope: 基于当前代码事实、自动化基线与 A1 审查结论，对 `v2.0 / M4` 做最小验收归档
- Status: done
- Files:
  - `tools/mermaid_editor/to_agent/user_feedback.md`
  - `tools/mermaid_editor/verification/integration/A7_CLI_AND_TEST_RESULTS.md`
  - `tools/mermaid_editor/verification/manual_checks/A7_MANUAL_CHECKLIST.md`
  - `tools/mermaid_editor/verification/handoff/A7_V200_M4_ACCEPTANCE.md`
- Inputs:
  - `redo` 实现与契约测试
  - 边端点侧向编辑与 round-trip / 导出链路
  - `RuntimeMessage dispatcher` 与协议测试
  - A1 审查回执
- Outputs:
  - 已将 `v2.0 / M4` 功能项写回反馈台账
  - 已补本轮自动化基线与手工复验项
  - 已新增 `A7_V200_M4_ACCEPTANCE.md`
- Dependencies:
  - `verification/`
  - `to_agent/user_feedback.md`
- Risks:
  - 当前验收为 `Conditional PASS`
  - 不应把当前协议状态表述成“完全闭合的双向边界”
- Next handoff:
  - 具备桌面环境的执行方按 `A7_MANUAL_CHECKLIST.md` 完成实机补验
  - 后续框架收口轮次应优先处理 A1 阻塞项
- Notes:
  - 本轮结论是“代码事实通过，桌面实机与框架边界仍有后续工作”
