# A7 v0.2.0 Round 1 Acceptance

## Scope

本回执用于基于当前代码事实，对 `mermaid_editor` `v0.2.0` 第一轮开发已明确落地项做验收归档。

本轮范围仅包含以下 1 项：

1. 加粗边时，箭头头部不跟着变粗，只加粗线条

## A1 Status

当前仓库未见 `A1` 阻塞记录；既有交接记录也未显示本轮存在新的框架阻塞。

因此本轮按“**A1 无阻塞，可继续做 A7 验收归档**”处理。

## Evidence

### Automated Baseline

2026-08-30 已复核：

- `python -m unittest discover -s tools/mermaid_editor/tests`
  - 结果：`Ran 20 tests`, `OK (skipped=5)`
- `python -m compileall tools/mermaid_editor/src/ptd_tool_mermaid_editor`
  - 结果：通过

### Code-Fact Review

1. 加粗边只加粗线条，不放大箭头头部
   - `src/ptd_tool_mermaid_editor/presentation/web/index.html` 中 `.edge` 基类固定使用 `marker-end: url(#arrowhead)`
   - 同文件中 `.edge.thick` 与 `.edge.thick.selected` 仅分别提升 `stroke-width` 到 `4.75` 与 `5.75`
   - 同文件 `<marker id="arrowhead">` 仍定义为固定 `markerWidth="8"`、`markerHeight="8"`、`refX="7"`、`refY="4"`
   - 该 marker 使用 `markerUnits="userSpaceOnUse"`，说明箭头头部尺寸由 marker 自身固定尺寸控制，不随边的 `stroke-width` 一起放大
   - 按当前代码事实，可认定“只加粗线条、箭头头部保持固定尺寸”已落地

## Acceptance Decision

结论：**本轮 `v0.2.0` 第一轮开发可做“最小通过”验收。**

本轮可关闭项：

- `P0` 1 项：加粗边仅线条变粗，箭头头部不随之变粗

继续保持 backlog：

- `P1` 连接点子编辑
- `P1` `assets\\2167_orbital` 风格迁移

## Residual Risks

1. 当前结论以代码事实和自动化基线为主，尚未执行 `PySide6 + QWebEngineView` 桌面端实机视觉复验
2. 本轮没有独立的前端视觉自动化测试专门断言 SVG marker 的最终渲染效果，后续仍需人工确认不同缩放比下的显示一致性
