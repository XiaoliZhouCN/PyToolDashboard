# PyToolDashboard Architecture

## 1. 项目定位

PyToolDashboard 是一个本地优先的个人工具仓库，目标是统一承载两类内容：

- `tools/`：独立工具本体。每个 tool 可以单独开发、测试、运行和发布。
- `dashboard/`：工具调度与总览入口。负责发现工具、展示工具、预览结果、拉起工具窗口或调用工具子功能。

该仓库默认以 Python 作为平台层实现语言，同时从第一天起按“可接入 C++/可执行程序”的方式设计协议边界。

## 2. 一级目录职责

```text
PyToolDashboard/
├── dashboard/   # 平台入口、注册表、预览、调度与 UI
├── tools/       # 独立工具集合
├── packages/    # dashboard 与 tools 共享的契约、运行时和基础库
├── docs/        # 架构、规范、协议、设计记录与 agent 协作文档
├── launchers/   # 面向工作区项目的启动脚本包装层
├── scripts/     # 仓库级辅助脚本
├── tests/       # 仓库级集成测试与契约测试
└── examples/    # 示例数据与演示输入输出
```

## 2.1 Agent 协作治理

除运行时代码结构外，仓库还应维护一套稳定的 Agent 协作治理文档，用于定义：

- Agent 类型和职责边界
- Agent to Agent 沟通目录
- 多 Agent 并行开发时的目录归属

推荐入口：

- [docs/architecture/AGENTMANAGER_TO_AGENT.md](file:///d:/Repositories/PyToolDashboard/docs/architecture/AGENTMANAGER_TO_AGENT.md)
- [docs/conventions/AGENT_ORGANIZATION.md](file:///d:/Repositories/PyToolDashboard/docs/conventions/AGENT_ORGANIZATION.md)

## 3. 分层原则

### 3.1 Platform 层

由 `dashboard/` 和 `packages/` 中的平台相关模块构成，职责包括：

- 读取工具清单
- 构建工具索引与分类
- 调度工具启动
- 统一展示预览与运行状态
- 收集日志和运行结果

### 3.2 Tool 层

每个 tool 自己维护业务逻辑、输入输出和局部 UI，不应把内部实现细节暴露给 dashboard。

### 3.3 Contract 层

由 `packages/ptd_contracts` 与 `docs/contracts/` 中的协议文档共同定义。其职责是让不同语言、不同实现方式的工具都能被统一接入。

## 4. 依赖方向

依赖必须保持单向：

```text
docs/                (文档，不参与运行时依赖)
packages/            -> 不依赖 dashboard/ 或具体 tools/
dashboard/           -> 可依赖 packages/
tools/<tool_name>/   -> 可依赖 packages/
dashboard/           -/-> 不直接依赖 tool 内部实现
tool A               -/-> 不直接依赖 tool B 内部实现
```

约束重点：

- dashboard 通过清单和协议调用 tool，不直接 import tool 的业务模块。
- tool 之间如果确有共享逻辑，应先上收至 `packages/`。
- 任何运行时跨语言边界都必须经过文件协议、CLI 参数或标准化 IPC。

## 5. 推荐通信模型

默认采用“桌面宿主 + 本地进程工具”的模型：

1. dashboard 读取 `tool.json`
2. dashboard 根据能力声明决定是：
   - 启动完整工具窗口
   - 请求预览数据
   - 调用某个 action
3. tool 通过 CLI / JSON 文件 / stdout JSON 返回结果
4. dashboard 再将结果转为 UI 展示

## 5.1 Workspace 运行目录规则

本仓库未来会与其他项目共同出现在同一 workspace 中，因此运行时必须区分：

- **工具仓库目录**：`PyToolDashboard/` 所在目录
- **主体项目目录**：当前工作区中被调度、被分析或被服务的目标项目根目录

统一规定：

- dashboard 和 tool 的运行时工作目录默认应为**主体项目目录**
- 不应默认以 `PyToolDashboard/` 作为运行时工作目录
- `launchers/` 中的 `sh` / `bat` 包装脚本必须显式切换到主体项目目录后再调用 Python 入口
- tool 在解析相对路径、生成缓存、读取局部配置时，必须基于主体项目目录或显式传入的 `project_root`

这条规则的目的是让 PyToolDashboard 能稳定服务外部项目，而不是把外部项目错误地绑定到工具仓库根目录。

## 6. 数据边界

- **配置数据**：稳定、可版本化，适合 JSON/TOML/YAML
- **交付数据**：表格型优先 CSV；结构型优先 JSON
- **缓存数据**：不入库、不入 Git，放运行目录
- **示例数据**：放 `examples/`，可用于联调和文档示例

## 7. 后续必须补齐的契约

开发开始前，至少需要稳定以下文件级契约：

1. `tool.json`：工具清单协议
2. request/response JSON schema：调度协议
3. preview schema：预览数据协议
4. 退出码规范：工具成功、业务失败、参数错误、内部异常
5. 日志格式规范：便于 dashboard 聚合显示

## 8. 演进策略

- 短期：Python 主体 + 本地桌面宿主 + 独立 tool
- 中期：在复杂交互 tool 中嵌入 Web UI
- 长期：按需接入 C++ 可执行程序或 Python 扩展模块，但不破坏平台层协议
