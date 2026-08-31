# A1 v2.0 / M4 Architecture Review

## Scope

本回执用于对 `mermaid_editor` 当前 `v2.0 / M4` 实现做框架合规审查，重点核对：

1. 真实运行入口是否仍以 `presentation/qt/main_window.py` 与 `presentation/web/index.html` 为主
2. `redo`、边端点交互、运行时协议是否落在约定目录
3. 当前实现是否满足 `to_agent/AGENT_TASK_DISPATCH.md` 定义的目录边界与依赖方向

## Review Verdict

结论：**A1 阻塞，不建议按“框架已完全合规”放行。**

说明：

- 本轮 `M4` 的功能链路基本已落地
- 真实入口迁移也仍然正确
- 但当前实现尚未满足既定目录授权和分层目标，因此只能判定为“功能完成，框架边界待继续收口”

## Findings

### 1. Blocking: `presentation/qt/main_window.py` 仍越层承担编排职责

当前 `MainWindow` 仍直接依赖 `domain / parsing / infra / presentation.web.bridge`，并在同一类内完成解析、归一化、sidecar 恢复、源码回写和保存。

这与 `AGENT_TASK_DISPATCH.md` 中建议的：

`App Shell -> Application Coordinator -> Domain / Parsing / Persistence`

目标分层仍不一致。仓库内虽然已经预留 `application/coordinator/`，但尚未真正接入启动主链。

### 2. High: `redo` 与边交互仍停留在 `presentation/web/index.html`

本轮新增的 `redoDiagramChange()`、历史栈语义、边端点手柄、边端点侧向编辑等逻辑，仍集中在真实入口 `presentation/web/index.html`。

这意味着：

- A5 的 Web 主入口仍承载大量交互逻辑
- A6 负责的 `presentation/web/interaction/` 与 `application/` 还未接管这部分真实实现
- 目录授权在当前轮仍是“功能先落地”，而不是“职责已完全收口”

### 3. High: 运行时协议只完成了 `Web -> Qt` 上行收口

当前 `protocols/`、`qt_web.py`、`RuntimeMessage` 与 `EditorBridge.postMessage()` 已经形成统一的上行入口，但：

- Web 端 dispatcher 仍内嵌在 `presentation/web/index.html`
- `Qt -> Web` 下行仍直接调用 `window.loadDiagram(...)` / `window.applyInspectorPayload(...)`

因此，协议层目前应视为“已收口一侧，仍处于过渡态”，尚不适合写成完全闭合的前后端边界。

## Confirmed Non-Issues

以下事项在本轮 A1 审查中成立：

1. 真实桌面启动链仍以 `presentation/qt/main_window.py` 为主
2. 页面真实入口仍是 `presentation/web/index.html`
3. 未发现当前运行主链继续引用 `app/static/editor.html`

## Release Position

从 A1 角度，本轮建议表述为：

- `M4` 功能目标已基本达成
- 但框架边界仍未完全满足既定目录授权模型
- 可继续做 A7 基于代码事实的最小归档，但不应宣称“框架审查已完全通过”

## Follow-up

1. 将 `MainWindow` 的解析、保存、恢复与协调逻辑收口到 `application/coordinator/`
2. 继续把 `redo` 与边交互从 `presentation/web/index.html` 拆到 `presentation/web/interaction/`
3. 为 `Qt -> Web` 下行建立对应协议入口，减少对具名 JS 调用的依赖
