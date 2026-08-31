# A7 Migration Protocol Handoff

## Summary

本次交接聚焦两件事：

1. 记录“真实实现已经迁入新目录”的现状
2. 说明当前协议与验收还处在什么阶段

## Migrated Implementations

当前以下目录已经承载真实实现，而不再只是空壳：

- `presentation/qt/main_window.py`
- `presentation/web/bridge/editor_bridge.py`
- `parsing/markdown/loader.py`
- `parsing/mermaid/parser.py`
- `domain/editor/diagram_editor.py`
- `infra/repository/layout_repository.py`
- `infra/export/svg_exporter.py`
- `infra/export/png_exporter.py`

## Compatibility Layer Still Kept

为了保持现有功能完整，以下旧路径仍保留兼容导出：

- `app/main_window.py`
- `app/bridge.py`
- `domain/mermaid_parser.py`
- `domain/diagram_editor.py`
- `infra/markdown_loader.py`
- `infra/layout_store.py`
- `actions/svg_export.py`
- `actions/png_export.py`

这些兼容层的目标是：

- 不打断现有入口
- 给后续 A2/A5/A6/A7 留出逐步迁移空间
- 避免一次性改动带来桌面交互回退

## Protocol State

当前协议并未完全收口到统一消息总线。

已完成：

- 有标准 `RuntimeMessage` 包络模型
- 有明确 Qt <-> Web bridge 方法列表
- 有 CLI / preview / action 的标准 JSON 响应结构

未完成：

- Web 端尚未统一通过 `RuntimeMessage` dispatcher 发消息
- Qt 端尚未建立独立 message router
- bridge 仍以具名槽函数为主

## Verification State

当前已完成：

- CLI preview 验证
- 单元测试验证

当前未完成：

- 桌面启动实机验证
- WebView 交互实机验证
- 依赖 `PySide6` 的导出链路完整复验

## Recommended Next Owners

### A2 Parsing & Domain Agent

建议继续：

- 去掉 `domain/mermaid_parser.py`、`domain/diagram_editor.py` 的兼容依赖
- 在新目录中进一步清理解析/领域边界

### A5 Web Renderer Agent

建议继续：

- 以 `presentation/web/index.html` 为当前真实入口
- 将其中渲染逻辑拆入 `presentation/web/render/`

### A6 Interaction Agent

建议继续：

- 将 `index.html` 中事件处理、拖拽、框选、快捷键逻辑拆入 `presentation/web/interaction/`

### A7 Protocol & Verification Agent

建议继续：

- 将 bridge 具名槽函数逐步包进统一消息协议
- 增加协议集成测试
- 在具备桌面环境时完成手工验收清单
