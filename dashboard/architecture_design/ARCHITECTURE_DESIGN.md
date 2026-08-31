# Dashboard Architecture Design

## 1. Tool Goal

`dashboard` 的目标是作为 `PyToolDashboard` 的平台宿主，统一承担以下职责：

1. 发现并索引本地可接入的 tool
2. 读取 tool manifest 与能力声明
3. 根据上下文展示摘要预览、入口信息与运行状态
4. 按统一协议启动 tool 窗口或调用 tool action
5. 聚合日志、历史记录与运行结果，作为用户进入工具体系的总入口

当前核心问题定义：

- 仓库中会同时存在多个独立 tool，`dashboard` 需要提供稳定的一致入口
- `dashboard` 必须通过 manifest 与协议调度 tool，而不是直接耦合 tool 内部实现
- 所有运行行为都必须围绕主体项目目录 `project_root`，不能错误绑定到工具仓库根目录

当前非目标：

- 将 `dashboard` 设计成远程服务或在线协作平台
- 在平台层承载具体 tool 的业务规则
- 通过直接 import tool 内部模块来换取“方便”的调用方式
- 在第一阶段就引入重型插件框架、分布式调度或账号体系

## 2. Product Positioning

`dashboard` 的产品定位是：

- 本地优先的桌面宿主程序
- 面向单个 workspace / 项目根目录的工具总览面板
- tool 发现、调度、预览与运行状态的统一入口

这意味着它更接近“本地工具平台壳”，而不是单个具体工具，也不是 Web 服务后台。

设计优先级如下：

1. 正确理解并维护 `project_root` 语义
2. 保持平台层与 tool 层的依赖边界稳定
3. 让新 tool 能以低接入成本接入 `dashboard`
4. 先保证工具发现、预览、调度闭环，再逐步增强体验层能力

## 3. Architecture Options

### Option A: Pure CLI Launcher Collection

做法：

- 不提供统一桌面宿主
- 只通过多个 `bat` / `sh` 脚本直接启动各个 tool

优点：

- 初始实现最轻
- 几乎没有 UI 复杂度
- 对单个 tool 的独立运行支持天然友好

缺点：

- 无法提供统一工具索引、预览、日志聚合与历史记录
- 用户需要记忆每个 tool 的启动方式与参数
- 难以形成平台层能力，也不利于后续统一调度

该方案适合仓库早期验证，但不适合作为长期平台架构。

### Option B: Browser-Based Web Dashboard

做法：

- `dashboard` 主要以 Web 应用形式存在
- Python 负责本地 API 或调度服务
- 浏览器页面作为主交互入口

优点：

- 列表、预览、卡片视图、筛选等 UI 交互开发效率高
- 未来若要做远程访问或共享展示，迁移路径较顺

缺点：

- 本地文件系统、桌面窗口、外部进程启动与权限语义更复杂
- 仍需要额外桌面壳或本地服务编排层
- 当前仓库定位是本地工具平台，不需要先引入服务端形态

该方案适合以后某些复杂视图采用 Web 技术，但不适合作为第一阶段主形态。

### Option C: Native Desktop Host + Local Tool Processes

做法：

- `dashboard` 作为桌面宿主
- 通过 `tool.json` 发现 tool
- 通过 CLI / JSON / stdout JSON 与 tool 交互
- 对复杂视图按需嵌入 Web UI，但平台控制权仍在桌面宿主

优点：

- 最符合仓库当前“本地优先 + 独立 tool + 协议接入”的总架构
- 能自然处理工作目录、外部进程、日志聚合与窗口调度
- 能保持 Python 作为平台主控语言

缺点：

- 宿主层状态管理、日志聚合、调度抽象需要提前设计清楚
- 若后续某些视图采用 Web 技术，需要继续维护桌面壳与前端视图边界

### Chosen Tradeoff

最终选择 `Option C`：

**使用 Python 桌面宿主作为平台入口，通过 manifest 与运行协议接入本地 tool 进程；复杂展示能力按需引入 Web UI，但不改变平台层的主控边界。**

## 4. Final Decision

`dashboard` 的最终架构决策是：

**将 `dashboard` 设计为一个本地桌面平台宿主，围绕 `registry + launcher + preview + views + services` 建立稳定分层，并通过标准运行协议与 tool 解耦。**

核心技术方向：

- 平台主控语言：Python
- 宿主 UI：优先桌面 UI 方案
- tool 接入方式：`tool.json` + 标准 CLI / JSON 请求响应
- 共享契约来源：`packages/` 与 `docs/contracts/`

选择理由：

1. 与仓库现有 `Platform / Tool / Contract` 分层完全一致
2. 能自然满足 `project_root` 作为运行上下文的硬约束
3. 避免 `dashboard` 与具体 tool 内部实现产生直接耦合
4. 为后续接入更多 tool、日志聚合、历史记录和预览机制留出扩展空间

## 5. Module Layout

`dashboard` 当前目录已经预留了 `src/` 与 `tests/`，但实现仍处于骨架待补齐阶段。

目标目录结构如下：

```text
dashboard/
├── architecture_design/
│   └── ARCHITECTURE_DESIGN.md
├── README.md
├── pyproject.toml
├── src/
│   └── ptd_dashboard/
│       ├── app/
│       ├── launcher/
│       ├── preview/
│       ├── registry/
│       ├── services/
│       └── views/
└── tests/
```

各层职责如下：

### `app/`

- 桌面宿主入口
- 启动参数解析
- 应用初始化与主窗口装配

约束：

- 负责应用编排，不承载具体 tool 业务逻辑
- 可以依赖 `registry/`、`launcher/`、`preview/`、`services/`、`views/`

### `registry/`

- 扫描和读取 `tool.json`
- 构建 tool 索引、分类、能力映射
- 为 UI 与调度层提供稳定的 manifest 查询接口

约束：

- 只依赖共享契约、文件系统与 schema 校验能力
- 不直接调用具体 tool 内部模块

### `launcher/`

- 根据 manifest 与用户动作拼装启动请求
- 管理 `launch` / `preview` / `action` 调用
- 负责进程级调度、超时、退出码与结果解析

约束：

- 明确依赖运行协议
- 所有调用都必须显式携带 `project_root`

### `preview/`

- 将 tool 返回的 preview 数据适配为 dashboard 可展示的数据结构
- 负责预览失败降级、空状态和错误态展示所需的中间模型

约束：

- 不定义 tool 私有业务语义
- 面向平台展示层做统一适配

### `views/`

- 工具列表、详情面板、预览面板、日志面板、历史面板等 UI 视图
- 只消费平台层中间模型，不直接拼装底层调用协议

约束：

- 不直接访问文件系统或子进程
- 不在视图层堆积调度逻辑

### `services/`

- 配置读取
- 缓存、日志、历史记录管理
- 运行时状态协调

约束：

- 平台公共服务收敛点
- 如服务内容对多个模块通用，应优先考虑上收至 `packages/`

### Dependency Boundaries

允许依赖方向：

```text
app -> registry
app -> launcher
app -> preview
app -> services
app -> views
views -> preview
views -> services
launcher -> services
registry -> services
preview -> services
dashboard -> packages
```

不允许：

- `dashboard` 直接 import `tools/<tool_id>/` 内部模块
- `views/` 直接调用子进程或解析 manifest 文件
- 在 `packages/` 中反向引用 `dashboard` 实现

## 6. Data And Persistence

### Inputs

`dashboard` 的主要输入包括：

1. 仓库中的 tool manifest，例如 `tool.json`
2. tool 返回的 preview 响应
3. tool action / launch 的标准输出、错误信息与退出码
4. 主体项目目录中的配置、缓存与运行上下文

### Outputs

`dashboard` 的主要输出包括：

1. UI 中展示的工具索引与预览结果
2. 调度请求与标准化的运行记录
3. 日志、历史记录、缓存与最近使用状态

### Persistence Strategy

当前已经锁定的原则：

- 配置、缓存、日志和历史都应相对 `project_root` 或显式运行目录组织
- 不把运行时产物默认写到 `PyToolDashboard/` 仓库根目录
- 所有结构化数据优先使用 JSON，并遵守 `schema_version` 与 `snake_case` 规则

当前尚未锁定但建议的方向：

- 将 `dashboard` 自有运行数据统一收拢到主体项目目录下的专属运行时目录
- 区分 `cache`、`logs`、`history`、`artifacts`，避免不同生命周期数据混放

### Data Format Rules

- JSON：`UTF-8`、`LF`、`snake_case`、带 `schema_version`
- 表格预览：必要时使用 `CSV + schema`
- 日志：应支持结构化聚合展示，至少包含时间、级别、来源模块

## 7. Runtime And Integration

### Workspace Runtime Rule

`dashboard` 必须严格区分两个根目录：

- 工具仓库目录：`PyToolDashboard/`
- 主体项目目录：`project_root`

运行时要求：

1. `dashboard` 默认运行上下文是 `project_root`
2. launcher 必须在启动前切换到 `project_root`
3. 应用入口必须显式接收 `--project-root`
4. 所有相对路径解析、缓存落点、日志落点都以 `project_root` 为基准

### Dashboard Launcher Decision

根据仓库规范，`dashboard` 必须始终提供独立 launcher。

目标脚本：

- `launchers/dashboard.bat`
- `launchers/dashboard.sh`

当前状态：

- 仓库中已有 `launchers/templates/dashboard.bat.example`
- 仓库中已有 `launchers/templates/dashboard.sh.example`
- 正式 launcher 已补齐，后续只需要随着入口参数演进持续维护

### Tool Integration Strategy

`dashboard` 与 tool 的集成遵循以下原则：

1. 通过 `tool.json` 做静态发现
2. 通过标准请求结构发起 `launch`、`preview`、`action`
3. 通过标准响应结构接收状态、payload、artifacts、errors
4. 通过退出码区分参数错误、输入错误、业务失败和内部异常

这意味着：

- `dashboard` 只理解“契约”和“能力声明”
- `dashboard` 不理解 tool 内部模块实现细节
- 若多个 tool 需要共享 schema、运行时封装或错误模型，应上收至 `packages/`

### Preview Strategy

预览策略分为三层：

1. `registry` 判断 tool 是否声明 preview 能力
2. `launcher` 负责请求 preview 数据
3. `preview` 层将原始响应转换为平台统一的展示模型

这样做的目的是让 tool 保持领域自由度，同时让 `dashboard` 获得一致 UI。

## 8. Constraints And Risks

当前明确约束：

- 平台层不能直接依赖具体 tool 内部实现
- 运行目录不能默认落在仓库根目录
- launcher 与应用入口都必须显式传递 `project_root`
- 文档、代码与协议要同步维护，不能让 README、架构文档与真实目录长期漂移

当前已知风险：

- 如果过早把 UI、调度、日志和缓存写在同一层，后续会快速失去可维护性
- 如果 preview 数据缺少统一中间模型，视图层很容易和具体 tool 响应耦合
- 如果没有尽早锁定配置、日志、历史的目录与 schema，后续迁移成本会升高
- 如果正式 launcher 与 dashboard 主入口迟迟不落地，`project_root` 语义容易在实现阶段被弱化

## 9. Milestones Or Evolution Plan

### M1: Skeleton

- 补齐 `pyproject.toml`
- 建立 `src/ptd_dashboard/` 包结构
- 提供应用入口与 `--project-root` 参数解析

状态：未开始

### M2: Registry

- 实现 `tool.json` 扫描与加载
- 建立 tool 索引与能力映射
- 提供基础列表数据模型

状态：未开始

### M3: Launcher And Preview

- 实现标准进程调度
- 支持 `launch` / `preview` / `action`
- 建立 preview 适配层与基础错误处理

状态：未开始

### M4: Host UI

- 实现工具列表页
- 实现工具详情区与预览区
- 增加日志 / 运行状态 / 历史记录面板

状态：未开始

### M5: Runtime Services And Tests

- 锁定配置、缓存、日志、历史目录
- 增加 registry 测试、契约测试、dashboard-tool 集成测试
- 补齐正式 launcher 与 README 联动更新

状态：未开始

## 10. Status Update

当前 `dashboard` 处于“架构约束已明确、实现骨架待补齐”的阶段。

当前已具备的基础：

1. 仓库级架构、依赖方向和运行目录规则已经明确
2. `dashboard/README.md` 已定义产品职责
3. `dashboard/src/` 与 `dashboard/tests/` 目录已预留
4. `launchers/templates/` 中已经有 dashboard 启动模板示例
5. `launchers/dashboard.bat` 与 `launchers/dashboard.sh` 已可作为正式入口脚本使用
6. tool 运行协议与 manifest 基础契约已经在 `docs/contracts/` 中落下
7. 第一版 `launcher/` 已能调用 tool 的 `preview` 与 `action` entrypoint
8. 第一版 `preview/` 已能将 tool preview 响应适配为 dashboard 使用的中间模型

当前已经锁定的设计决策：

- `dashboard` 是平台宿主，不是具体业务 tool
- 平台与 tool 通过 manifest 与运行协议解耦
- 所有运行时上下文围绕 `project_root`
- 后续实现按 `app / registry / launcher / preview / views / services` 分层
- tool entrypoint 可以在 `project_root` 作为 `cwd` 的前提下运行，必要时由 launcher 层补齐相对脚本路径和 `PYTHONPATH`

当前仍属于后续实现项的内容：

- 更完整的 manifest 校验、工具索引与分类能力
- 更丰富的 preview 适配、日志聚合、历史记录与宿主 UI
