# Mermaid Editor Architecture Design

## 1. Tool Goal

`mermaid_editor` 的目标是提供一个面向本地 Markdown 知识库的 Mermaid 图编辑器。

当前核心问题定义：

1. 从 Markdown 文件中提取 Mermaid 代码块
2. 将 Mermaid 图渲染为可交互的可视化画布
3. 支持节点和子图的手工布局，而不是只依赖 Mermaid 自动布局
4. 支持基础结构编辑，并将结果回写到 Markdown 与 sidecar 布局文件

当前明确关注的第一阶段能力：

- 读取 Mermaid 源码并渲染
- 拖拽布局节点和子图
- 增删节点和子图
- 编辑节点 ID、节点显示文本、子图 ID、子图标题
- 支持边的基础交互编辑，包括拖拽式创建和属性面板修改

当前非目标：

- 多人协作编辑
- 云端同步或远程服务依赖
- 完整覆盖所有 Mermaid 图类型
- 复杂权限系统、账号系统或在线发布能力

## 2. Product Positioning

该工具的产品定位是：

- 本地优先的个人知识库工具
- 单用户桌面编辑器
- 更接近轻量 IDE / 图编辑器，而不是在线白板

这意味着设计优先级是：

- 本地文件访问自然
- 打开和保存流程直接
- 支持离线运行
- 保持 Python 作为主控语言

## 3. Architecture Options

### Option A: Frontend / Backend Web App

优点：

- 交互式图编辑的前端技术成熟
- 浏览器是天然运行时，跨平台交付方便
- 后续如要做协作、云同步和分享，扩展路径更顺

缺点：

- 对本地文件工作流并不天然友好
- 如果采用“Python 后端 + 浏览器前端”，核心交互逻辑仍主要在 JavaScript
- 为了获得桌面级体验，通常还需要额外桌面打包层

适用前提：

- 产品目标偏在线协作
- 浏览器访问优先于本地桌面体验

### Option B: Native Desktop Window Program

优点：

- 更符合本地 Markdown 编辑和文件系统操作
- 更适合后续扩展为真正的编辑器工具
- Python 可以直接负责应用编排、解析、持久化和插件边界

缺点：

- 如果完全使用原生控件绘制交互画布，开发成本较高
- 若未来转向协作型产品，迁移成本会更高

适用前提：

- 本地优先
- 单用户
- 手工布局是核心能力

### Chosen Tradeoff

最终选择不是“纯原生 UI”，也不是“纯 Web 应用”，而是混合式桌面架构：

- 桌面壳使用 `PySide6`
- 交互式画布使用 `QWebEngineView` 内嵌 HTML / CSS / JavaScript

这样既保留桌面端的本地文件能力，也保留 Web 技术对图编辑交互的高生产力。

## 4. Final Decision

`mermaid_editor` 的最终架构决策是：

**使用 `PySide6` 构建桌面应用外壳，在 `QWebEngineView` 中嵌入 Web 编辑画布。**

核心技术栈：

- 桌面层：`PySide6`
- 交互画布：HTML / CSS / JavaScript / SVG
- Python 业务层：Markdown 解析、Mermaid 解析、布局持久化、运行入口

选择理由：

1. 更符合本地 Markdown 编辑工具的产品边界
2. 更适合手工布局、结构编辑和本地保存
3. 保持 Python 作为主语言和主控层
4. 为未来扩展 preview、dashboard 接入、导出和历史功能留出空间

## 5. Module Layout

当前真实目录结构对齐如下：

```text
tools/mermaid_editor/
├── architecture_design/
├── samples/
├── src/
│   └── ptd_tool_mermaid_editor/
│       ├── actions/
│       ├── app/
│       ├── domain/
│       ├── infra/
│       ├── preview/
│       └── schemas/
├── tests/
├── pyproject.toml
├── run.py
└── tool.json
```

各层职责如下：

### `actions/`

- 面向 dashboard 或脚本调度的标准 action
- 当前提供 `export_svg`、`export_png`

约束：

- 可以依赖 `domain/` 和 `infra/`
- 返回值应符合标准 action response 结构

### `app/`

- CLI 入口
- `MainWindow`
- Qt 与 Web 画布之间的桥接
- 资源页面加载

约束：

- 可以依赖 `domain/`、`infra/`、`preview/`
- 不承载核心 Mermaid 业务规则

### `domain/`

- 图模型
- 图结构编辑规则
- Mermaid 解析与序列化
- 默认布局分配

约束：

- 不直接依赖 Qt UI
- 不承担文件系统 I/O

### `infra/`

- Markdown 文件读取
- sidecar 布局 JSON 读写

约束：

- 承担外部 I/O
- 不直接操作桌面 UI

### `preview/`

- 面向 dashboard 的摘要预览构建

### `schemas/`

- tool 输入输出 schema

### Dependency Boundaries

允许依赖方向：

```text
app -> domain
app -> infra
app -> preview
preview -> infra
preview -> domain
infra -> domain
```

不允许：

- `domain/` 依赖 Qt 或 Web UI
- tool 直接依赖 dashboard 内部实现

## 6. Data And Persistence

### Inputs

主要输入：

1. Markdown 文件
2. 与 Markdown 相邻的布局 sidecar 文件：`<markdown_file>.layout.json`

Markdown 中的 Mermaid 代码块仍然是结构真源。

### Outputs

主要输出：

1. 回写后的原始 Markdown 文件
2. 保存布局元数据的 sidecar JSON
3. preview 命令输出的标准 JSON 响应
4. action 命令输出的导出 artifact，如 SVG / PNG

### Persistence Strategy

持久化策略如下：

- Mermaid 结构文本保留在 Markdown 中
- 手工布局保存在 sidecar JSON 中

这样做的原因是：

- Mermaid 原文保持可读、可编辑
- 手工布局信息不会因为 Mermaid 重新解析而丢失

### Data Format Rules

- JSON 使用 `UTF-8`
- key 使用 `snake_case`
- sidecar 顶层带 `schema_version`

当前 sidecar 只保存布局坐标与子图尺寸，没有引入复杂迁移逻辑。

## 7. Runtime And Integration

### CLI Entrypoints

当前提供两个主要入口：

- `python run.py launch`
- `python run.py preview`
- `python run.py action`

它们都支持显式传入 `--project-root`。

### Workspace Runtime Rule

必须区分两个根目录：

- tool 源码根目录：`tools/mermaid_editor/`
- 主体项目目录：`project_root`

运行时要求：

- launcher 必须先切换到 `project_root`
- Python 入口必须显式接收 `--project-root`
- 文件对话框与相对路径解析以 `project_root` 为基准

### Dashboard Integration

当前 `tool.json` 已声明：

- `launch`
- `preview`
- `action`
- `launcher_policy = standalone_allowed`

这意味着它既可以被 dashboard 调用，也允许提供独立 launcher。

### Standalone Launcher Decision

`mermaid_editor` 适合独立启动，原因是：

- 它本身就是明确的单用途桌面工具
- 不依赖 dashboard 的上文选择状态才能运行
- 输入边界清楚，主要就是 `project_root` 和可选的 Markdown 文件

因此仓库级 `launchers/` 中维护：

- `tool_mermaid_editor.bat`
- `tool_mermaid_editor.sh`

launcher 负责：

1. 校验 `project_root`
2. 切换 `cwd` 到 `project_root`
3. 显式传入 `--project-root`
4. 将其余参数透传给 tool CLI

### Action Strategy

当前标准 action 包括：

- `export_svg`
- `export_png`

共同输入：

- Markdown 文件
- 可选 `diagram_id`
- 可选输出目录

共同输出：

- 标准 JSON 响应
- artifact 列表

当前导出策略：

- 从本地图模型统一生成导出表达
- `export_svg` 直接写出 SVG
- `export_png` 使用 `QPainter` 直接从图模型光栅化成 PNG

它的目标是先提供一个稳定、可自动化调用的导出能力，为 dashboard 集成和批处理场景打基础。

## 8. Constraints And Risks

当前明确限制：

- Mermaid 解析器主要覆盖 `flowchart` 子集
- 当前边编辑已支持拖拽式创建和基础样式切换，但箭头方向等更细粒度样式仍未完成
- 当前没有撤销/重做
- 当前 PNG 导出还不是浏览器画布级别的高保真截图

当前已知风险：

- Web 画布的交互复杂度继续上升后，需要更明确的前后端状态同步策略
- 如果后续支持更多 Mermaid 语法，现有解析器需要继续扩展或替换
- 桌面端与嵌入式 Web UI 的边界若不持续收紧，未来容易出现状态耦合

## 9. Milestones Or Evolution Plan

### M1

- open Markdown file
- extract Mermaid blocks
- render current diagram

状态：已完成

### M2

- select node
- drag node position
- save manual layout metadata

状态：已完成

### M3

- add/delete node
- rename node id
- edit node display text
- add/delete subgraph

状态：已完成

### M4

- visual edits -> Mermaid text
- Mermaid text edits -> visual model

状态：较为完整，但仍缺撤销重做和更强的边交互

### M5

- export SVG/PNG
- multi-diagram document support
- outline / diagram navigator

状态：部分完成

## 10. Status Update

当前实现已经从早期原型推进到符合仓库标准骨架的形态。

已落地的关键调整：

1. 根目录补齐 `pyproject.toml`、`tool.json` 和标准 README
2. 源码迁移到 `src/ptd_tool_mermaid_editor/`
3. 以 `app / domain / infra / preview / schemas` 分层组织
4. 用本地 `samples/` 取代过时的外部硬编码示例路径
5. 明确拆分 tool 源码根目录与运行时 `project_root`
6. 增加独立 launcher，允许不经 dashboard 直接启动
7. 增加标准 action，并支持 `export_svg`、`export_png`
8. 增加 domain 层图结构编辑服务，使节点/子图编辑具备一致规则和测试覆盖
9. 增加画布属性面板、右键菜单、拖拽式边创建、画布缩放和平移交互
10. 修复边引用已有子图时被错误解析为顶层节点的问题
11. 在 v0.1.2 中将详情编辑面板移出画布覆盖层，并加入多选、框选、对齐、中心缩放与锚点侧向偏好

当前已经落地的设计决策：

- 桌面壳 + Web 画布的混合架构
- Markdown 为结构真源，sidecar JSON 保存布局
- 允许 dashboard 调用，也允许独立运行

当前仍属于后续演进项的内容：

- 更完整的 preview / action 能力
- 更强的 Mermaid 语法兼容
- 更完整的编辑器能力，如撤销重做、更细的边样式控制、高保真导出和历史管理
