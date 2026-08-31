# Mermaid Editor Runtime Protocols

## Overview

本目录用于收口 `mermaid_editor` 在重构过程中的运行时协议约定。
当前重点不是引入远程协议，而是明确 Qt Shell、Web Canvas、CLI/preview/action 之间的本地消息边界。

当前协议状态分为两层：

1. **标准消息包络**
   由 [`messages.py`](file:///d:/Repositories/PyToolDashboard/tools/mermaid_editor/src/ptd_tool_mermaid_editor/protocols/messages.py) 提供 `RuntimeMessage`
2. **Qt <-> Web Bridge 路由**
   当前 `QWebChannel` 已支持统一 `postMessage()` 入口，并保留旧具名槽函数作为兼容层

## Runtime Message Envelope

当前标准消息模型：

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

字段说明：

- `schema_version`
  协议版本，当前固定为 `1.0`
- `message_type`
  消息类型，必须显式存在
- `source`
  发送方模块标识
- `target`
  接收方模块标识
- `request_id`
  可追踪请求标识；无请求上下文时可为空字符串
- `payload`
  业务负载

## Current Qt-Web Bridge

当前桌面端与 Web 画布之间的桥接已进入“**统一上行消息 + 兼容旧方法**”阶段。

### Web -> Qt

Web 端优先调用 `bridge.postMessage(JSON.stringify(RuntimeMessage))`。
当前已经收口到以下标准消息类型（见 [`qt_web.py`](file:///d:/Repositories/PyToolDashboard/tools/mermaid_editor/src/ptd_tool_mermaid_editor/protocols/qt_web.py)）：

1. `lifecycle.page_ready`
   - 含义：页面初始化完成，请求 Qt 推送当前图
   - payload：`{}`
   - 对应行为：Qt 收到后调用 `push_current_diagram()`

2. `status.update`
   - 含义：Web 侧状态提示同步到 Qt 状态栏
   - payload：`{"message": "..."}`

3. `diagram.save`
   - 含义：Web 侧图模型发生结构变更，请求 Qt 接收最新图数据
   - payload：`state.diagram` 的对象结构

4. `selection.sync`
   - 含义：Web 侧选中状态变化，请求 Qt 刷新详情面板
   - payload：选中对象结构

兼容说明：

- 若 `bridge.postMessage` 不可用，Web 端仍会回退到 `pageReady()` / `setStatus()` / `saveDiagram()` / `selectionChanged()`
- Qt 侧 `EditorBridge` 会将兼容调用转换为同一套 `RuntimeMessage` 再统一分发

### Qt -> Web

Qt 端当前直接执行以下页面函数：

1. `window.loadDiagram(payload)`
   - 含义：加载当前图模型到 Web 画布
   - 调用方：`presentation.qt.main_window.MainWindow.push_current_diagram`

2. `window.applyInspectorPayload(payload)`
   - 含义：将 Qt 详情面板编辑结果应用到 Web 当前图模型
   - 调用方：`presentation.qt.main_window.MainWindow.apply_detail_changes`

## Current Status

当前协议处于**过渡阶段**：

- CLI / preview / action 已具备标准 JSON request/response 语义
- Qt / Web 之间已抽出 `RuntimeMessage` 包络模型
- Web -> Qt 的 `page ready / status / save / selection` 已改为统一 envelope + dispatcher
- Qt -> Web 仍保留 `window.loadDiagram(payload)` 与 `window.applyInspectorPayload(payload)` 两个直接入口

## Migration Guidance

后续若继续收口协议，建议顺序如下：

1. 将 Qt -> Web 的 `loadDiagram` / `applyInspectorPayload` 也抽象成统一 message router
2. 为 `RuntimeMessage` 增加更严格的 schema 校验和 request/response 关联
3. 将 Web 页面内的 dispatcher 从单文件脚本提取到独立模块
4. 为协议消息补浏览器侧回退链路与桌面侧集成测试

## Compatibility Note

当前为了保证现有功能不回退，以下兼容路径仍保留：

- `app.bridge` -> 兼容导出到 `presentation.web.bridge.editor_bridge`
- `app.main_window` -> 兼容导出到 `presentation.qt.main_window`
- `domain.mermaid_parser` -> 兼容导出到 `parsing.mermaid.parser`
- `domain.diagram_editor` -> 兼容导出到 `domain.editor.diagram_editor`
- `infra.markdown_loader` -> 兼容导出到 `parsing.markdown.loader`
- `infra.layout_store` -> 兼容导出到 `infra.repository.layout_repository`
- `actions.svg_export` / `actions.png_export` -> 兼容导出到 `infra.export.*`
