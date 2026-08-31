# A7 v0.1.3.2 Minimal Acceptance

## Scope

本回执用于基于当前代码事实，对 `mermaid_editor` 本轮 `v0.1.3.2` 修复做最小验收归档。

范围仅包含以下八项：

1. `P000` 子图详情标题改为直接显示子图名，消除因标题刷新引发的闪动来源
2. `P00` 对齐两个包含内容的子图时，内容元素跟随移动
3. `P0` 加粗边更粗
4. `P0` 多选移动同步
5. `P0` 左侧面板默认 / 最小 / 最大比例
6. `P0` 顶部 toolbar 双层结构与按钮收缩
7. `P0` `Apply Source` 回放已存布局
8. `P0` 子图及嵌套子图按 `direction` 布局

## A1 Status

当前仓库未见 `A1` 阻塞记录；既有交接记录显示 `A1` 已完成迁移并放行后续 A7 验收。

因此本轮按“**A1 无阻塞，可继续做 A7 最小验收**”处理。

## Evidence

### Automated Baseline

2026-08-30 已复核：

- `python -m unittest discover -s tools/mermaid_editor/tests`
  - 结果：`Ran 20 tests`, `OK (skipped=5)`
- `python -m compileall tools/mermaid_editor/src/ptd_tool_mermaid_editor`
  - 结果：通过

### Code-Fact Review

1. `P000` 子图详情标题与闪动来源
   - `presentation/qt/main_window.py` 中 `MainWindow._build_detail_summary()` 对 `subgraph` 已直接返回 `label` 或 `id`
   - `tests/presentation_qt/test_main_window.py` 已覆盖“无前缀标题”和“回退到 ID”两项行为
   - `presentation/web/index.html` 中 `handleSelectableClick()` 选中链路已走 `refreshSelectionVisualState()`，不再因为单纯选中而直接触发全量 `render()`
   - 按代码事实可关闭

2. `P00` 子图对齐时内容不跟随
   - `alignSelection()` 通过 `buildMoveTargetsForItems()` 取得可移动根对象
   - 子图移动目标会把后代子图与内部节点一起纳入 `applyDeltaToTargets()`
   - 按代码事实可关闭

3. `P0` 加粗边更粗
   - `presentation/web/index.html` 中 `.edge.thick` 为 `4.75`，`.edge.thick.selected` 为 `5.75`
   - 按代码事实可关闭

4. `P0` 多选移动同步
   - `startDrag()` 会保留多选上下文
   - 拖拽位移通过 `buildMoveTargetsForItems()` + `applyDeltaToTargets()` 同步应用到多选对象
   - 按代码事实可关闭

5. `P0` 左侧面板比例
   - `MainWindow` 已定义 `MIN_LEFT_PANEL_RATIO = 0.25`
   - `DEFAULT_LEFT_PANEL_RATIO = 1 / 3`
   - `MAX_LEFT_PANEL_RATIO = 0.5`
   - `test_left_panel_width_is_clamped_to_quarter_and_half()` 已覆盖边界
   - 按代码事实可关闭

6. `P0` toolbar 双层与按钮收缩
   - `presentation/web/index.html` 已拆分 `toolbar-buttons` 与 `toolbar-hints`
   - 当前按钮集仅保留 `Fit Selected / - / 50% / + / Save Layout`
   - `setToolbarHeight()` 仅调整按钮缩放变量，快捷键说明区保持固定字号
   - 按代码事实可关闭

7. `P0` `Apply Source` 回放已存布局
   - `apply_source_changes()` 在重新解析后调用 `layout_store.restore_diagram()`
   - 解析结果会先恢复 sidecar 中的既有布局，再保存当前文档
   - 按代码事实可关闭

8. `P0` 子图与嵌套子图按 `direction` 布局
   - `tests/test_mermaid_parser.py` 已覆盖 `test_default_layout_respects_nested_subgraph_direction()`
   - 同文件已覆盖 `test_default_layout_respects_direction_for_nested_subgraph_descendants()`
   - 按代码事实可关闭

## Acceptance Decision

结论：**本轮 `v0.1.3.2` 可做“最小通过”验收。**

可关闭项：

- `P000` 1 项
- `P00` 1 项
- `P0` 6 项

继续保持 backlog：

- 长期维护 `P1` 两项保持未关闭，不纳入本轮关闭范围

## Residual Risks

1. 当前结论仍以代码事实和自动化基线为主，不等于 `PySide6 + QWebEngineView` 桌面端最终实机关闭
2. `presentation/web/index.html` 仍是单文件前端，后续继续拆分时需保留本轮八项为回归检查项
3. 子图选中“闪动感”与 toolbar 视觉细节仍受真实桌面渲染环境影响，当前环境无法替代人工观察
