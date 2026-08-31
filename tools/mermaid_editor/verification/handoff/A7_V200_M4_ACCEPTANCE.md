# A7 v2.0 / M4 Acceptance

## Scope

本回执用于基于当前代码事实，对 `mermaid_editor` `v2.0 / M4` 做最小验收归档。

本轮范围包含：

1. `redo` 与快捷键闭环
2. 边端点侧向编辑（连接点子编辑）
3. `Web -> Qt` 运行时协议边界收口

## A1 Status

`A1` 已出具架构审查意见，当前结论为：

- 功能链路已基本落地
- 真实入口迁移正确
- 但目录边界与分层目标仍未完全收口

因此本轮按“**A1 未完全放行，但不阻塞 A7 记录代码事实与自动化基线**”处理。

## Automated Baseline

已确认命令：

```powershell
python -m unittest discover -s tools/mermaid_editor/tests
python -m compileall tools/mermaid_editor/src/ptd_tool_mermaid_editor
```

结果：

- 单元测试通过：`Ran 37 tests in 0.040s`, `OK (skipped=10)`
- `compileall` 通过

说明：

- 新增测试主要覆盖 `redo`、`edge anchor` 与 `runtime protocol`
- 跳过项仍主要受当前环境缺少 `PySide6` 影响
- 当前自动化基线用于支撑“代码事实 + 非 GUI 契约”层面的最小验收，不替代桌面端实机交互验收

## Code-Fact Review

### 1. Redo / Shortcut Loop

- 真实入口 `presentation/web/index.html` 已新增 `redoDiagramChange()`
- 已接入 `Ctrl+Y` 与 `Ctrl+Shift+Z`
- 历史提交与拖拽提交统一通过 `pushUndoSnapshot()` / `pushRedoSnapshot()` 维护
- `loadDiagram()` 会重置 `undoStack / redoStack`

按当前代码事实，可认定：

`Ctrl+Z only` 的历史能力已提升为完整的 `undo / redo` 基本闭环。

### 2. Edge Anchor Handle Editing

- `EdgeModel` 已新增 `source_anchor_side` / `target_anchor_side`
- 真实入口已提供边端点侧向手柄与详情面板编辑入口
- Mermaid 解析/序列化已支持 `%% ptd-edge-anchors: source=..., target=...` 注释元数据
- SVG / PNG 导出已共用这条边端点侧向数据链

按当前代码事实，可认定：

边端点侧向编辑已形成 `Web 编辑 -> diagram.save -> Qt 接收 -> Mermaid 注释回写 -> 再解析恢复` 的闭环。

### 3. Runtime Protocol Boundary

- `RuntimeMessage` 已具备 `to_json()` / `from_json()` / `from_dict()` 能力
- `protocols/qt_web.py` 已统一 `message_type` 常量与 Web -> Qt 包络构造器
- `presentation/web/index.html` 已优先通过 `bridge.postMessage(JSON.stringify(RuntimeMessage))` 上报 `pageReady / status / save / selection`
- `EditorBridge` 已统一校验并路由到既有 Qt 信号
- legacy `pageReady()` / `setStatus()` / `saveDiagram()` / `selectionChanged()` 仍保留为兼容回退

按当前代码事实，可认定：

`Web -> Qt` 上行边界已完成统一 dispatcher 收口。

## Acceptance Decision

结论：**Conditional PASS**

本轮可以做 `A7` 最小验收归档，但归档口径必须限定为：

1. `redo / 快捷键闭环` 已按代码事实落地
2. `edge anchor handle editing` 数据链已闭环
3. `Web -> Qt` 已统一为 `RuntimeMessage dispatcher`，但仍保留 legacy fallback

## Residual Risks

1. 当前 `schema_version` / `request_id` 仍未形成严格拒收策略，协议边界仍属于过渡态
2. `Qt -> Web` 下行仍保留 `runJavaScript()` 具名调用，尚未统一进入协议层
3. `redo` 与边端点手柄的自动化主要是静态契约与非 GUI 集成验证，不等于真实桌面交互验证
4. `PySide6 + QWebEngineView` 实机点选、快捷键分发、路径视觉效果仍需按手工清单补验

## Manual Follow-up

后续具备桌面环境的执行方，应至少补验：

- `Ctrl+Y` / `Ctrl+Shift+Z` 在桌面壳内可稳定触发
- 边端点手柄真实点击后路径和源码注释同步更新
- 保存并重开后 `ptd-edge-anchors` 元数据可恢复
- 页面初始化、状态栏提示、选中同步、保存链路在桌面端保持正常
