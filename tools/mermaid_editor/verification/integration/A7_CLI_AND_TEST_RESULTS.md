# A7 CLI And Test Results

## Scope

本记录用于说明在“实现迁移进新目录”之后，当前可自动化验证的结果。

## Verified

### 1. Unit Test Suite

执行命令：

```powershell
python -m unittest discover -s tools/mermaid_editor/tests
```

结果：

- `20` tests passed
- `5` tests skipped

说明：

- 跳过项为依赖 `PySide6` 的 Qt / 导出相关链路测试
- 当前 Python 环境未安装 `PySide6`，因此跳过属于预期行为

### 1.1 Compile Check

执行命令：

```powershell
python -m compileall tools/mermaid_editor/src/ptd_tool_mermaid_editor
```

结果：

- `compileall` 通过
- 当前 `src/ptd_tool_mermaid_editor/` 全目录未发现语法层错误

### 2. Preview CLI

执行命令：

```powershell
python tools/mermaid_editor/run.py preview --project-root tools/mermaid_editor --markdown-file samples/sample_workflow.md
```

结果：

- 返回 `schema_version = 1.0`
- 返回 `status = ok`
- 能正确统计 `2` 个 Mermaid 图

## Verified Regression Fix

在框架迁移过程中，曾出现以下回归：

- `preview` 子命令在导入阶段过早触发 Qt 模块加载
- 在无 `PySide6` 环境中会直接失败

当前状态：

- 已将桌面窗口导入改为惰性加载
- `preview` 和 `action` 不再因为桌面依赖在模块导入期崩溃

## Not Verified In Current Environment

以下内容当前未完成实机验证：

1. `launch` 桌面启动链路
2. `QWebEngineView` 内嵌页面交互
3. `export_png` / `export_svg` 在具备 `PySide6` 环境下的完整导出体验
4. 触控板缩放 / 平移真实设备体验
5. `v0.1.3` 三项 `P000` 交互问题的桌面端最终实机关闭

## Current Conclusion

在当前环境中可以确认：

- 新目录中的真实实现已经接管核心解析、持久化、导出与 Qt Presentation 代码
- 兼容壳没有破坏现有 CLI 与测试链路
- `presentation/qt/main_window.py` 当前页面入口已指向 `presentation/web/index.html`
- 下一阶段可以在此基础上继续做协议收口和 Web 模块拆分

## v0.1.3.1 Acceptance Baseline

本节仅记录本轮 `v0.1.3.1` 验收准备阶段已确认的自动化证据，不额外假设未执行的桌面结果。

已确认命令：

```powershell
python -m unittest discover -s tools/mermaid_editor/tests
python -m compileall tools/mermaid_editor/src/ptd_tool_mermaid_editor
```

结果：

- 单元测试通过：`20` tests，`5` skipped
- `compileall` 通过

当前未纳入本节结论的内容：

- `PySide6 + QWebEngineView` 桌面实机交互表现
- 子图选中是否彻底消除闪烁
- 高 DPI / 触控板下的交互体验

## v0.1.3.2 Acceptance Baseline

本节记录 2026-08-30 为 `v0.1.3.2` 最小验收回执复核的自动化基线。

已确认命令：

```powershell
python -m unittest discover -s tools/mermaid_editor/tests
python -m compileall tools/mermaid_editor/src/ptd_tool_mermaid_editor
```

结果：

- 单元测试通过：`Ran 20 tests in 0.154s`, `OK (skipped=5)`
- `compileall` 通过

本节仅作为代码事实验收基线，不额外推导以下未执行结果：

- `PySide6 + QWebEngineView` 实机视觉体验
- 触控板 / 高 DPI 环境下的交互稳定性
- 本轮 UI 细节调整的最终视觉确认

## v0.2.0 Acceptance Baseline

本节记录 2026-08-30 为 `v0.2.0` 第一轮开发验收归档复用的自动化基线。

已确认命令：

```powershell
python -m unittest discover -s tools/mermaid_editor/tests
python -m compileall tools/mermaid_editor/src/ptd_tool_mermaid_editor
```

结果：

- 单元测试通过：`Ran 20 tests in 0.016s`, `OK (skipped=5)`
- `compileall` 通过

说明：

- 当前基线用于支撑 `v0.2.0` 文档归档中的“代码事实 + 自动化基线”结论
- 本节不将上述结果外推为桌面端视觉实机验收

## v2.0 / M4 Acceptance Baseline

本节记录 2026-08-31 为 `v2.0 / M4` 验收归档复跑的自动化基线。

已确认命令：

```powershell
python -m unittest discover -s tools/mermaid_editor/tests
python -m compileall tools/mermaid_editor/src/ptd_tool_mermaid_editor
```

结果：

- 单元测试通过：`Ran 37 tests in 0.040s`, `OK (skipped=10)`
- `compileall` 通过

说明：

- 新增覆盖主要来自 `redo`、`edge anchor`、`runtime protocol` 的契约与集成测试
- 跳过项仍主要受当前环境缺少 `PySide6` 影响
- 本节用于支撑 `v2.0 / M4` 的“代码事实 + 自动化基线”结论，不将其外推为桌面端完整交互验收
