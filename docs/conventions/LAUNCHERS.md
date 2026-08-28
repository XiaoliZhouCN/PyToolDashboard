# Launcher Convention

## 1. 目标

本规范定义仓库根目录 `launchers/` 下的启动包装脚本约定，用于保证 PyToolDashboard 在与其他项目共同出现在同一 workspace 时，运行目录始终正确。

## 2. 基本原则

- `launchers/` 放置 `sh` / `bat` 启动脚本
- 这些脚本的职责是“设置上下文并调用 Python 入口”
- 运行时工作目录必须是**主体项目目录**，而不是 `PyToolDashboard/` 仓库根目录
- 脚本可以知道工具仓库的位置，但不能把该位置当作业务运行目录

## 3. 目录与命名

建议结构：

```text
launchers/
├── README.md
└── templates/
    ├── dashboard.bat.example
    └── dashboard.sh.example
```

命名规则：

- dashboard 启动脚本：`dashboard.<ext>`
- tool 独立启动脚本：`tool_<tool_id>.<ext>`
- 若脚本只作为模板，使用 `.example` 后缀

## 4. 工作目录规则

统一要求：

1. launcher 必须接收主体项目根目录，或在无参数时默认使用**当前工作目录**作为主体项目根目录
2. 在调用 Python 前，先切换到主体项目根目录
3. Python 入口应同时接收明确的 `--project-root` 参数，避免只依赖当前工作目录
4. 所有相对路径解析、缓存落点和临时产物应基于 `project_root`

不允许：

- 默认以 `PyToolDashboard/` 根目录作为 `cwd`
- 在脚本中硬编码用户机器的绝对项目路径
- 依赖 IDE 当前打开位置碰巧正确

## 5. 脚本内容规范

每个 launcher 至少应完成以下动作：

1. 在脚本头部写明参数注释
2. 支持无参数直接运行
3. 校验主体项目目录是否存在
4. 解析 PyToolDashboard 仓库路径
5. 切换到主体项目目录
6. 调用目标 Python 入口
7. 显式传递 `--project-root`
8. 保留原始退出码

脚本头部参数注释至少要说明：

- 脚本用途
- 参数列表
- 无参数时的默认行为
- 可选环境变量，例如 `PYTHON_EXE`

推荐附加能力：

- 输出简洁诊断信息
- 对 Python 解释器路径提供可覆盖变量
- 对 dashboard 和 tool 的入口命令做集中封装

## 6. 哪些模块允许独立脚本运行

默认策略：

- **dashboard 必须始终提供独立 launcher**
- **tool 是否允许独立 launcher，由其 `tool.json` 能力声明决定**

建议分类：

### 6.1 可独立运行的 tool

满足以下任一特征时可提供独立 launcher：

- 本身就是明确的单用途桌面工具
- 无需 dashboard 上下文即可完整运行
- 输入输出边界稳定、参数少且清晰

### 6.2 必须经由 dashboard 唤起的 tool

满足以下特征时，建议只允许通过 dashboard 调用：

- 强依赖 dashboard 的选择上下文、预览上下文或任务编排
- 只是某个大工具的子功能，不具备独立产品边界
- 需要统一任务队列、日志面板或状态管理

## 7. 创建新 launcher 的规则

新增 launcher 时必须同步完成：

1. 在 `launchers/` 新增对应脚本或模板
2. 在相关模块 `README.md` 中说明启动方式
3. 若对应 tool 可独立运行，在 `tool.json` 中声明
4. 保证 `bat` 与 `sh` 版本的参数语义一致
5. 避免在脚本中复制业务逻辑，脚本只做入口包装

## 8. 推荐接口风格

推荐命令风格：

```text
dashboard.bat [project_root]
dashboard.sh [project_root]
tool_mermaid_editor.bat [project_root] [extra_args...]
```

默认行为：

- 若 `project_root` 省略，则使用启动脚本时的当前工作目录
- 若 tool 还需要额外参数，建议显式传入 `.` 作为 `project_root`，例如：
  - `tool_mermaid_editor.bat . preview`

## 9. 与 scripts/ 的边界

- `launchers/`：给用户或工作流直接执行
- `scripts/`：给仓库维护、开发、校验、生成流程使用

不要把格式化、初始化、校验脚本放到 `launchers/` 中。
