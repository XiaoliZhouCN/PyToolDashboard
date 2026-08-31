# A7 Manual Verification Checklist

## Goal

本清单用于后续具备 `PySide6` 桌面环境时，对 `mermaid_editor` 的重构结果进行人工复验。

## Desktop Launch

- [ ] `python run.py launch --project-root .` 可启动主窗口
- [ ] 不指定 `launch` 子命令时，`python run.py --project-root .` 仍可默认启动
- [ ] 主窗口左侧默认占比约 `1/3`
- [ ] 左侧最大拖拽不超过整体宽度 `1/2`

## Document Loading

- [ ] 打开 `samples/sample_workflow.md` 能显示图列表
- [ ] 可在多 Mermaid block 之间切换
- [ ] 左侧源码区与右侧图形视图保持同步

## Web Bridge

- [ ] 页面初始化后，Qt 能推送当前图到 Web
- [ ] Web 状态文本可同步到 Qt 状态栏
- [ ] 选中节点/子图/边时，Qt 详情面板会同步刷新
- [ ] Web 侧结构修改后，Qt 能收到最新图模型

## Editing Flow

- [ ] 节点拖拽可正常更新位置
- [ ] 子图拖拽可带动内部节点与嵌套子图
- [ ] `Ctrl+Z` 可撤销最近结构修改
- [ ] 双击空白画布新增节点可用
- [ ] 右键新增边流程可用
- [ ] 左侧详情面板修改节点/子图/边属性可用

## v0.1.3 P000 Follow-up

- [ ] 空子图可被选中后直接拖动，且拖动后位置正确更新
- [ ] 普通子图可被选中后直接拖动，且其内部节点会一起移动
- [ ] 嵌套子图可单独拖动，不会误触发父子图异常联动
- [ ] 单击选中子图时，画面不会出现跳变、闪动或明显重绘抖动
- [ ] 长距离拖动画布时，画布位移与鼠标轨迹保持一致
- [ ] 高 DPI 或触控板环境下，平移链路无明显偏移

## Persistence

- [ ] `Save` 会回写 Markdown
- [ ] 布局 sidecar 会同步写入 `.layout.json`
- [ ] 重新打开同一文件时，已保存布局能恢复

## Export

- [ ] `action export_svg` 可生成 SVG
- [ ] `action export_png` 可生成 PNG
- [ ] 指定 `diagram_id` 时，只导出目标图

## Known Follow-up Checks

- [ ] 验证 `presentation/web/index.html` 与旧 `app/static/editor.html` 的内容未发生意外漂移
- [ ] 验证未来拆分 `presentation/web/render` / `interaction` 时，未破坏当前 bridge 约定

## v0.1.3.1 Follow-up

- [ ] 单击选中空子图、普通子图、嵌套子图时，画面无可见闪烁或抖动
- [ ] 空子图作为子图拖出父边界后，父子图边界会随拖拽结果扩展
- [ ] 纵向连线在视觉上明显比旧版本更接近直线
- [ ] 空子图执行“适配大小”后，尺寸回落为默认节点大小 `160x56`

## v0.1.3.2 Follow-up

- [ ] 选中子图后，左侧详情标题直接显示子图名或子图 ID，不再出现 `Selected subgraph` 前缀
- [ ] 单击选中子图时，详情刷新不会伴随明显闪动、跳变或整页重绘感
- [ ] 同时选中两个包含内容的子图后执行对齐，内部节点与嵌套子图会随父子图一起移动
- [ ] 多选节点 / 子图后，拖动任一被选对象时，其余被选对象会同步位移
- [ ] 加粗边在普通态和选中态下都明显比普通边更粗
- [ ] 左侧主面板默认约为窗口宽度 `1/3`，向左拖拽最小约 `1/4`，向右拖拽最大约 `1/2`
- [ ] 顶部工具栏仅保留当前按钮集，缩放按钮显示为 `+` / `-`
- [ ] 顶部工具栏分为按钮区与快捷键说明区；拖动底部 resizer 时按钮随高度缩放，快捷键说明字号保持稳定
- [ ] 修改源码后点击 `Apply Source`，已保存的 sidecar 布局会被恢复，而不是重新落回默认布局
- [ ] 子图与子图的子图在默认布局下都遵循各自的 `direction` 属性

## v0.2.0 Follow-up

- [ ] 将边样式切换为 `thick` 后，线条明显变粗，但箭头头部仍保持固定尺寸，不会随线宽一起放大

## v2.0 / M4 Follow-up

- [ ] `Ctrl+Z`、`Ctrl+Y`、`Ctrl+Shift+Z` 在 `PySide6 + QWebEngineView` 桌面壳内均可触发，且拖拽后可正确撤销/重做
- [ ] 重新加载图或执行 `Apply Source` 后，历史栈被正确清空，不会把旧图的 `redo` 记录带入新图
- [ ] 选中边后，起点和终点对应对象会显示连接点侧向手柄，点击后曲线路径会立即更新
- [ ] 通过左侧详情面板修改 `Edge Source Side / Edge Target Side` 后，画布路径、源码注释与保存结果保持一致
- [ ] 保存并重新打开后，`%% ptd-edge-anchors: source=..., target=...` 注释元数据仍能恢复到同一条边
- [ ] 页面初始化、状态栏提示、选中同步、图模型保存这 4 条 `Web -> Qt` 消息在桌面端仍然工作正常
- [ ] 当前 `Web -> Qt` 使用 `RuntimeMessage dispatcher`，但 `Qt -> Web` 仍走兼容 JS 调用；需确认页面刷新、切图与详情应用在实机中无同步异常
