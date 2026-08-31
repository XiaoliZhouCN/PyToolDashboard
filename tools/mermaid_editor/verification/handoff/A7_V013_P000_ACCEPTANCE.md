# A7 v0.1.3 P000 Acceptance

## Scope

本记录用于验收 `mermaid_editor` 当前这轮 `v0.1.3` 的三项 `P000` 交互修复，并整理交接边界。

验收目标：

1. 子图（含空子图）不再只能选中而无法移动
2. 选中子图时不再出现明显异常画面变动
3. 画布平移链路与鼠标移动保持一致，不再出现明显偏移

## Evidence

### 1. Automated Verification

2026-08-29 已复跑以下命令：

```powershell
python -m unittest discover -s tools/mermaid_editor/tests
python -m compileall tools/mermaid_editor/src/ptd_tool_mermaid_editor
```

结果：

- 单元测试通过：`15` tests，`2` skipped
- 源码编译检查通过：`compileall` 无错误

说明：

- 当前自动化覆盖主要确认解析、导出兼容链路与包结构未因本轮修复退化
- 跳过项仍为依赖 `PySide6` 的链路，不构成当前环境下的失败

### 2. Runtime Entry Snapshot

当前已确认：

- `presentation/qt/main_window.py` 的 `_load_editor_page()` 指向 `src/ptd_tool_mermaid_editor/presentation/web/index.html`
- 本轮桌面壳实际加载入口已经切到 `presentation/web/index.html`

这说明：

- v0.1.3 当前交互修复对应的前端入口已与新目录结构对齐
- 后续实机复验应以 `presentation/web/index.html` 为唯一页面入口，不再以旧 `app/static/editor.html` 作为验收对象

## Acceptance Decision

结论：**本轮可做“有限通过”验收。**

已满足的验收条件：

1. 用户反馈中的三项 `P000` 已按当前修复目标关闭
2. 自动化基线未发现新的解析或打包层回归
3. Qt 页面入口已确认指向新的 `presentation/web/index.html`

未完成的验收部分：

1. 未在具备 `PySide6 + QWebEngineView` 的桌面环境中复验子图拖拽
2. 未对“选中子图时画面异常变动”进行逐帧人工观察
3. 未在真实鼠标、高 DPI、触控板场景下复验平移跟手性与偏移问题

因此当前结论不是“桌面端最终实机关闭”，而是：

- **自动化与文档验收通过**
- **桌面交互实机验收待补**

## Residual Risks

1. `presentation/web/index.html` 仍是单文件前端，交互、渲染、桥接逻辑尚未彻底拆分，后续修改时仍有回归风险
2. 当前环境未安装可用的 `PySide6` 桌面运行链路，无法直接证明 WebView 内事件坐标与浏览器独立运行时完全一致
3. 触控板、缩放与平移耦合场景缺少真实设备验证，高 DPI 下仍可能存在边界偏差

## Manual Follow-up

后续实机复验至少应覆盖：

1. 空子图、普通子图、嵌套子图分别拖拽一次
2. 单击选中子图后观察画布是否发生跳变、闪动或非预期重排
3. 长距离连续平移画布，确认鼠标与画布位移一致
4. 在高 DPI 或触控板环境下重复第 3 项

对应清单已同步到：

- `tools/mermaid_editor/verification/manual_checks/A7_MANUAL_CHECKLIST.md`

## Handoff

建议下一个接手方：

1. 在具备 `PySide6` 的机器上完成手工复验并回填结果
2. 若仍观察到子图选中抖动或平移偏移，优先沿 `presentation/web/index.html` 的交互链路排查
3. 后续 Web 拆分阶段继续把这三项 `P000` 作为回归检查项保留
