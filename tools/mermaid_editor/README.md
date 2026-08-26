# Mermaid Editor

一个基于 Python 的本地 Mermaid 知识库编辑工具，面向个人使用场景。当前版本采用 `PySide6 + QWebEngineView` 的桌面混合架构，支持从 Markdown 中读取 Mermaid 图，并在可视化画布中做基础编辑。

## 当前能力

- 打开本地 Markdown 文件并提取 Mermaid 代码块
- 以 `/d:/Repositories/NexusRenderer/workflow.md` 作为示例加载真实 Mermaid 内容
- 在桌面窗口中切换多个 Mermaid 图
- 手动拖拽节点与子图，保存布局信息
- 手动添加节点、子图
- 修改节点 ID、节点显示文本、子图 ID、子图标题
- 删除节点或子图
- 将结构变化回写为 Mermaid 源码
- 将手动布局保存到独立的 sidecar 文件

## 项目结构

```text
mermaid_editor/
├── app/
│   ├── models/
│   │   └── graph.py
│   ├── services/
│   │   ├── layout_store.py
│   │   ├── markdown_loader.py
│   │   └── mermaid_parser.py
│   ├── static/
│   │   └── editor.html
│   ├── __init__.py
│   ├── bridge.py
│   └── main_window.py
├── architecture_design/
│   └── ARCHITECTURE_DESIGN.md
├── tests/
│   └── test_mermaid_parser.py
├── requirements.txt
├── run.py
└── README.md
```

## 安装依赖

建议使用独立虚拟环境：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 运行方式

```powershell
python run.py
```

启动后会默认尝试打开：

- `D:\Repositories\NexusRenderer\workflow.md`

你也可以通过窗口顶部工具栏中的 `Open Markdown` 打开任意 Markdown 文件。

## 数据保存说明

### Markdown 原文

- Mermaid 结构编辑会回写到原始 Markdown 文件中的对应 Mermaid 代码块。

### 手动布局

- 手动布局保存到与 Markdown 同目录的 sidecar 文件：
  - 例如 `workflow.md.layout.json`

这样可以让 Mermaid 源文本与编辑器布局状态解耦，避免纯 Mermaid 语法无法表达的手工布局信息丢失。

## 使用说明

### 左侧区域

- 上方显示当前文件路径
- 中间是当前 Markdown 中的 Mermaid 图列表
- 下方是当前选中图的 Mermaid 源码编辑区

### 右侧画布

- 拖拽节点或子图可手动调整位置
- 双击节点可修改节点 ID 和显示文本
- 双击子图可修改子图 ID 和标题
- 选中子图后新增节点，会默认挂到该子图下

### 顶部按钮

- `Open Markdown`：打开新的 Markdown 文件
- `Save`：保存 Markdown 和布局
- `Apply Source`：将左侧 Mermaid 源码重新解析并刷新画布
- `Reload Sample`：重新加载 `workflow.md`

### 画布工具栏

- `Add Node`：新增节点
- `Add Subgraph`：新增子图
- `Rename`：重命名当前选中项
- `Delete`：删除当前选中项
- `Save Layout`：立即将画布数据回传到桌面端

## 安全与边界

- 当前版本仅处理本地文件，不引入网络服务
- 未执行任意脚本，不解析不受控 HTML
- 图编辑界面使用浏览器内置 `prompt` 做轻量输入，后续可升级为更完整的表单面板

## 当前限制

- 当前解析器主要覆盖 `flowchart`，对更复杂 Mermaid 语法的支持仍需继续扩展
- 手动新增节点后，边关系仍需通过左侧 Mermaid 源码手动补充
- 子图尺寸采用内容包围盒策略，复杂嵌套场景还可进一步优化
- 当前未实现撤销/重做、自动历史快照、导出 SVG/PNG

## 测试

```powershell
python -m unittest discover -s tests
```

## 后续建议

- 增加边的可视化创建与编辑
- 增加属性面板，替代浏览器 `prompt`
- 增加自动保存与文件变更监听
- 增加 SVG/PNG 导出
- 扩展更多 Mermaid 图类型支持
