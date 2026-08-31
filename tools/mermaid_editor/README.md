# Mermaid Editor

## Overview

`mermaid_editor` 是一个本地优先的 Mermaid 图编辑工具，面向个人 Markdown 知识库场景。
它采用 `PySide6 + QWebEngineView` 的桌面混合架构：

- Python 负责文件加载、Mermaid 解析、布局持久化和桌面壳
- 内嵌 Web 画布负责节点/子图的交互编辑

## Use Cases

- 打开本地 Markdown 文件并提取 Mermaid 图
- 对节点和子图做手动拖拽布局
- 增删节点、子图并修改标识符和显示文本
- 新增、重命名、删除边
- 将结构变化回写到 Markdown 中的 Mermaid 代码块
- 将手工布局保存到 sidecar JSON 文件

## Structure

```text
mermaid_editor/
├── to_agent/
│   └── AGENT_TASK_DISPATCH.md
├── architecture_design/
│   └── ARCHITECTURE_DESIGN.md
├── samples/
│   └── sample_workflow.md
├── src/
│   └── ptd_tool_mermaid_editor/
│       ├── app/
│       │   ├── static/
│       │   │   └── editor.html
│       │   ├── bridge.py
│       │   ├── cli.py
│       │   └── main_window.py
│       ├── actions/
│       │   ├── service.py
│       │   ├── png_export.py
│       │   └── svg_export.py
│       ├── domain/
│       │   ├── graph.py
│       │   ├── diagram_editor.py
│       │   └── mermaid_parser.py
│       ├── infra/
│       │   ├── layout_store.py
│       │   └── markdown_loader.py
│       ├── preview/
│       │   └── service.py
│       ├── schemas/
│       │   ├── action_request.schema.json
│       │   ├── action_response.schema.json
│       │   ├── launch_request.schema.json
│       │   └── preview_response.schema.json
│       ├── __init__.py
│       └── __main__.py
├── tests/
│   └── test_mermaid_parser.py
├── pyproject.toml
├── requirements.txt
├── run.py
└── tool.json
```

## Entrypoints

开发环境下可直接使用：

```powershell
python run.py
python run.py launch --project-root .
python run.py preview --project-root . --markdown-file samples/sample_workflow.md
python run.py action --project-root . --action-name export_svg --markdown-file samples/sample_workflow.md
python run.py action --project-root . --action-name export_png --markdown-file samples/sample_workflow.md
```

通过仓库级 launcher 运行：

```powershell
..\..\launchers\tool_mermaid_editor.bat . 
..\..\launchers\tool_mermaid_editor.bat . preview --markdown-file samples/sample_workflow.md
..\..\launchers\tool_mermaid_editor.bat . action --action-name export_svg --markdown-file samples/sample_workflow.md
..\..\launchers\tool_mermaid_editor.bat . action --action-name export_png --markdown-file samples/sample_workflow.md
```

安装为包后也可以使用：

```powershell
python -m ptd_tool_mermaid_editor launch --project-root .
```

参数说明：

- `--project-root`：主体项目目录。文件对话框和相对路径解析以此为基准
- `--markdown-file`：启动时自动打开的 Markdown 文件
- launcher 的第一个参数固定为 `project_root`，后续参数直接透传给 tool CLI

## Inputs

主要输入有两类：

1. Markdown 文件  
   其中包含一个或多个 ```` ```mermaid ```` 代码块
2. 布局 sidecar 文件  
   文件名形式为 `<markdown_file>.layout.json`

示例：

- `notes/workflow.md`
- `notes/workflow.md.layout.json`

## Outputs

主要输出有两类：

1. 回写后的原始 Markdown 文件
2. sidecar 布局 JSON

布局文件特征：

- `UTF-8`
- JSON key 使用 `snake_case`
- 顶层带 `schema_version`

## Dashboard Actions

当前已提供的 dashboard 友好入口：

- `launch`：启动完整桌面编辑器
- `preview`：输出 Mermaid 文档摘要 JSON
- `action`：执行标准 action，目前支持 `export_svg`、`export_png`

当前 action 仍是轻量实现，结构编辑主流程仍以桌面交互为主。

## Examples

安装依赖：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

运行桌面编辑器：

```powershell
python run.py launch --project-root .
..\..\launchers\tool_mermaid_editor.bat .
```

生成预览 JSON：

```powershell
python run.py preview --project-root . --markdown-file samples/sample_workflow.md
..\..\launchers\tool_mermaid_editor.bat . preview --markdown-file samples/sample_workflow.md
```

导出 SVG：

```powershell
python run.py action --project-root . --action-name export_svg --markdown-file samples/sample_workflow.md
..\..\launchers\tool_mermaid_editor.bat . action --action-name export_svg --markdown-file samples/sample_workflow.md
```

导出 PNG：

```powershell
python run.py action --project-root . --action-name export_png --markdown-file samples/sample_workflow.md
..\..\launchers\tool_mermaid_editor.bat . action --action-name export_png --markdown-file samples/sample_workflow.md
```

## Limitations

- 当前解析器主要覆盖 `flowchart` 子集
- 当前边编辑已支持基础增删改，但还不是完整的可视化连线交互
- 当前已提供基础 `Ctrl+Z` 撤销，但还没有重做，也还没有系统化历史快照管理
- preview 入口目前只输出摘要，不返回完整图模型
- `export_svg` 和 `export_png` 当前输出的是基于本地图模型的简化导出，而不是浏览器画布的逐像素还原

## Handoff Docs

若后续由新的 AI / Agent 接手开发，建议优先阅读以下文档：

1. [architecture_design/ARCHITECTURE_DESIGN.md](file:///d:/Repositories/PyToolDashboard/tools/mermaid_editor/architecture_design/ARCHITECTURE_DESIGN.md)
2. [architecture_design/FEATURES_AND_USAGE.md](file:///d:/Repositories/PyToolDashboard/tools/mermaid_editor/architecture_design/FEATURES_AND_USAGE.md)
3. [to_agent/AGENT_TASK_DISPATCH.md](file:///d:/Repositories/PyToolDashboard/tools/mermaid_editor/to_agent/AGENT_TASK_DISPATCH.md)

其中：

- `ARCHITECTURE_DESIGN.md` 说明当前实现边界、限制与风险
- `FEATURES_AND_USAGE.md` 说明当前功能状态与体验反馈处理进度
- `AGENT_TASK_DISPATCH.md` 用于多 Agent 协作、任务分发与交接回复
