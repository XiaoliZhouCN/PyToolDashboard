# A7 v0.1.3.1 Minimal Acceptance

## Scope

本回执用于基于当前代码事实，对 `mermaid_editor` 本轮 `v0.1.3.1` 修复做最小验收归档。

范围仅包含以下四项：

1. `P000` 选中子图时闪烁
2. `P00` 空子图作为子图移动超出父边界时，父图边界不跟随
3. `P0` 竖向边路径更直
4. `P0` 空子图适配大小缩到默认节点尺寸

## A1 Status

`A1` 已回执：**无阻塞，可放行验收**。

且 Qt 主窗口实际页面入口已指向：

- `src/ptd_tool_mermaid_editor/presentation/web/index.html`

因此本轮可继续做 A7 文档层验收归档。

## Evidence

### Automated Baseline

已知并确认通过：

- `python -m unittest discover -s tools/mermaid_editor/tests`
  - 结果：`15 tests, 2 skipped`
- `python -m compileall tools/mermaid_editor/src/ptd_tool_mermaid_editor`
  - 结果：通过

### Code-Fact Review

1. `P000` 子图选中闪烁
   - 当前 `handleSelectableClick()` 在选中子图后仍直接调用 `render()`
   - 现有证据不足以证明闪烁问题已被消除
   - 本项暂不关闭

2. `P00` 父图边界不跟随空子图
   - `calculateSubgraphBounds()` 已将嵌套子图纳入边界计算
   - `normalizeSubgraphLayouts()` 会在布局脏时自内向外扩展父子图边界
   - 按代码事实可关闭

3. `P0` 竖向边路径更直
   - `buildEdgePath()` 已在纵向主导场景切换为纵向控制轴
   - 按代码事实可关闭

4. `P0` 空子图适配大小缩到默认节点尺寸
   - `fitSubgraphToContents()` 在无内容时直接写入 `160x56`
   - 按代码事实可关闭

## Acceptance Draft

结论草案：**本轮 `v0.1.3.1` 可做“部分通过”验收。**

可关闭项：

- `P00` 空子图越界时父图边界跟随
- `P0` 竖向边路径更直
- `P0` 空子图适配大小缩到默认节点尺寸

暂不关闭项：

- `P000` 选中子图时闪烁

## Residual Risks

1. `presentation/web/index.html` 仍为单文件实现，选中即整页 `render()` 的行为仍可能继续引入瞬态闪烁
2. 当前结论未包含 `PySide6 + QWebEngineView` 桌面实机观察结果
3. 高 DPI、触控板与长时间交互场景仍未补验
