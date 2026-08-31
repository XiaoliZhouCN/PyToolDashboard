# 文档简介
这个文档主要用来存储用户对各版本的使用体验反馈。
这个文档不纳入文档规范中，只是快速与Agent沟通的文档。

# 工作流程
- A0根据体验说明分析拆解任务交付给专项开发Agent
- 专项开发Agent根据任务进行开发
- 专项开发Agent将开发结果交付给A0
- A0验收开发结果后交付A1审核开发符合框架规范
- A1审核通过后交付给A0，A0确认后交付给A7梳理文档。

# 版本迭代简介
- v0.1.3 框架重构版本
- v2.0 对齐 `ARCHITECTURE_DESIGN.md` M4 完成版

# 优先级
- P000: 优先级最高，必须解决的问题，非常紧急
- P00：优先级较高，当前版本结局，比较紧急
- P0：优先级一般，当前版本解决
- P1：优先级最低，后续版本中解决，比较不紧急


# 体验说明
## 长期维护问题
### 界面优化
P1:
- [ ] 以assets\2167_orbital风格作为画面风格参考


### v2.0 / M4
P000:
- [x] 补齐撤销/重做闭环；【A7 验收备注：真实入口 `presentation/web/index.html` 已新增 `redoDiagramChange()`，并接入 `Ctrl+Y / Ctrl+Shift+Z`；历史提交与拖拽提交统一走 `pushUndoSnapshot()` / `pushRedoSnapshot()` 语义，`loadDiagram()` 会重置 `undoStack/redoStack`。当前结论基于代码事实与自动化测试，桌面壳快捷键分发仍建议补实机复验。】
- [x] 增加线的连接点子编辑功能（类似无边记）；【A7 验收备注：边模型已补 `source_anchor_side` / `target_anchor_side`，真实入口已提供边端点侧向手柄与详情面板编辑入口，Mermaid 解析/序列化、SVG/PNG 导出已共用该数据链。当前结论不替代高密度图下的实机视觉微调。】
P00:
- [x] 收紧前后端状态边界；【A7 验收备注：`presentation/web/index.html` 已优先通过 `bridge.postMessage(JSON.stringify(RuntimeMessage))` 上报 `pageReady / status / save / selection`，`EditorBridge` 会统一校验并路由到既有 Qt 信号；`Qt -> Web` 下行仍保留兼容 `runJavaScript()` 调用，但不阻塞当前 M4 完成判定。】


### v0.2.0
P0:
- [x] 加粗的箭头箭头部分不需要加粗，只加粗线条；【A7 验收备注：`presentation/web/index.html` 中 `.edge.thick` 与 `.edge.thick.selected` 仅提升线条 `stroke-width`，箭头仍复用固定 `markerWidth="8"` / `markerHeight="8"` 且 `markerUnits="userSpaceOnUse"` 的 `#arrowhead`；按当前代码事实可认定“只加粗线条、不放大箭头头部”已落地。当前结论不替代 `PySide6 + QWebEngineView` 桌面端实机视觉复验。】


### v0.1.3.2
P000:
- [x] 选中子图时闪动来源于选中子图后子图详情面板为适配子图名刷新导致；详情页title删除“selected subgraph”，直接显示子图名。【A7 最小验收备注：`MainWindow._build_detail_summary()` 对子图已直接返回 `label/id`，不再拼接 `Selected subgraph` 前缀；`handleSelectableClick()` 选中链路也已收敛为 `refreshSelectionVisualState()` 局部刷新。按代码事实可关闭，桌面端视觉闪动仍建议补实机观察。】
P00：
- [x] 选中两个子图（包含节点），自动对齐，内容元素不跟随移动【A7 最小验收备注：`alignSelection()` 已通过 `buildMoveTargetsForItems()` 计算移动根对象，并把子图后代节点/嵌套子图一并纳入位移目标；按代码事实可关闭。】
P0:
- [x] 加粗的边路径更粗；【A7 最小验收备注：`presentation/web/index.html` 中 `.edge.thick` 与 `.edge.thick.selected` 已分别提升到 `4.75` 和 `5.75` 的 `stroke-width`；按代码事实可关闭。】
- [x] 多选元素，移动时，不能同步，只能移动被选中的元素；【A7 最小验收备注：拖拽链路已在 `startDrag()` 中保留多选上下文，并通过 `buildMoveTargetsForItems()` + `applyDeltaToTargets()` 同步位移；按代码事实可关闭。】
- [x] 面板布局优化，左侧面板默认只占画面1/3，最小1/4， 最大1/2，目前默认最小1/2，不合理；【A7 最小验收备注：`MainWindow` 已固定 `DEFAULT_LEFT_PANEL_RATIO = 1/3`、`MIN_LEFT_PANEL_RATIO = 0.25`、`MAX_LEFT_PANEL_RATIO = 0.5`，并有 `test_left_panel_width_is_clamped_to_quarter_and_half()` 回归测试；按代码事实可关闭。】
- [x] 右侧上方tool bar优化：删除add node/edge/subgraph/rename/delete按钮；zoom in/out 按钮改为+/-；tool bar分为上下两部分，上半部分放按钮，下半部分放快捷键简介；上下拉动tool bar时，按钮随tool bar缩放，快捷键简介保持字体大小；【A7 最小验收备注：当前 `presentation/web/index.html` 工具栏只保留 `Fit Selected / - / 50% / + / Save Layout`，并拆为 `toolbar-buttons` 与 `toolbar-hints` 两层；`setToolbarHeight()` 仅缩放按钮区比例，快捷键提示字号保持固定。按代码事实可关闭。】
- [x] apply source按钮功能修改为读取以存储的布局文件，而不是重新计算默认布局；【A7 最小验收备注：`apply_source_changes()` 在重新解析后会调用 `layout_store.restore_diagram()` 恢复已存 sidecar 布局，再回写当前 diagram；按代码事实可关闭。】
- [x] 子图、子图的子图都要按照direction属性进行布局；【A7 最小验收备注：`test_default_layout_respects_nested_subgraph_direction()` 与 `test_default_layout_respects_direction_for_nested_subgraph_descendants()` 已覆盖子图及嵌套子图的 `direction` 默认布局；按代码事实可关闭。】


### v0.1.3.1
P000：
- [x] 选中子图时仍然触发重绘，导致画面闪烁；【A7 验收备注：当前真实运行入口已将子图选中链路从全量 `render()` 收敛为局部选择态刷新，并避免无位移点击在 `pointerup` 时再次触发全量重绘；按代码事实可关闭，桌面端视觉体验仍建议补实机复验。】
P00：
- [x] 子图的子图如果是空子图，移动超过父图边界时，父图的边界不会跟随空子图移动。 【A7 验收备注：`calculateSubgraphBounds()` 与 `normalizeSubgraphLayouts()` 已将嵌套空子图边框纳入父子图边界计算；按当前代码事实可关闭，桌面端拖拽表现仍建议补实机复验。】
P0：
- [x] 画线不支持竖向直线，增加画线时贝塞尔曲线的计算方案；可能因为贝塞尔曲线控制点为水平，目前竖向默认是曲线，横向可以接近直线；【A7 验收备注：`buildEdgePath()` 已针对纵向主导路径切换为纵向控制轴，按代码事实可认定“更直”的修复已落地；视觉细节仍待桌面端观察。】
- [x] 空子图选择适配大小时，缩放到与默认节点大小一致；【A7 验收备注：`fitSubgraphToContents()` 在无内容时已直接回落到 `160x56` 默认节点尺寸，按代码事实可关闭。】

### v0.1.3.0
P000:
- [x] 子图（存在空子图，需要考虑特殊情况）只能选中无法移动；【A7 验收备注：本轮已按修复目标关闭，自动化基线已复跑通过；空子图与普通子图的真实桌面拖拽仍待具备 `PySide6` 环境后做实机复验。】
- [x] 选中子图时画面变动（似乎触发了重绘？）；【A7 验收备注：当前按已修复记录关闭，未在当前环境复现到新的自动化错误；是否彻底消除选中瞬态抖动，仍需桌面端人工观察确认。】
- [x] 移动画布不完全跟随鼠标，有偏移；【A7 验收备注：当前按已修复记录关闭，代码入口与前端页面入口已完成迁移对齐；鼠标连续平移和高 DPI / 触控板场景仍未做实机确认。】


补充说明：
- 2026-08-30 A7 已复跑 `python -m unittest discover -s tools/mermaid_editor/tests`，结果为 `Ran 20 tests, OK (skipped=5)`。
- 2026-08-30 A7 已复跑 `python -m compileall tools/mermaid_editor/src/ptd_tool_mermaid_editor`，结果通过。
- 2026-08-30 A7 已完成 `v0.2.0` 第一轮开发归档：在 `A1` 无阻塞前提下，本轮新增关闭 `P0` 1 项“加粗边仅线条变粗、箭头头部保持固定尺寸”；长期维护 backlog 继续保留“连接点子编辑”“2167_orbital 风格迁移”两项。
- 当前最小验收结论更新为“在 A1 无阻塞前提下，`v0.1.3.2` 列出的 `P000/P00/P0` 八项可按当前代码事实关闭；长期维护 `P1` 两项继续保留 backlog；桌面端实机体验验收未完成”。
- 2026-08-31 A7 已完成 `v2.0 / M4` 归档准备：本轮新增关闭 `P000/P00` 3 项，分别为“重做闭环”“连接点子编辑”“Web -> Qt 运行时协议边界收紧”；长期维护 backlog 现仅保留“2167_orbital 风格迁移”。
- 2026-08-31 自动化基线已更新为 `python -m unittest discover -s tools/mermaid_editor/tests -> Ran 37 tests, OK (skipped=10)`，`python -m compileall tools/mermaid_editor/src/ptd_tool_mermaid_editor` 通过。
- 2026-08-31 A1 已补充 `v2.0 / M4` 框架审查：当前结论为“功能链路已落地，但 `presentation/qt/main_window.py` 越层编排、Web 单文件职责仍重，暂不按‘框架完全合规’放行”。
