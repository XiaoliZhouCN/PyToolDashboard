# Launchers

本目录用于放置面向工作区项目的启动包装脚本。

职责：

- 校验主体项目目录
- 切换到主体项目目录作为运行时 `cwd`
- 调用 dashboard 或允许独立运行的 tool
- 显式传递 `--project-root`
- 支持无参数直接运行，默认使用当前工作目录作为 `project_root`

边界：

- 这里放的是运行入口，不是仓库开发辅助脚本
- 仓库维护脚本仍放在 `scripts/`
- 是否允许 tool 独立启动，以 `tool.json` 的 `launcher_policy` 为准

模板脚本可参考：

- `templates/dashboard.bat.example`
- `templates/dashboard.sh.example`

当前已维护的独立 launcher：

- `dashboard.bat`
- `dashboard.sh`
- `tool_mermaid_editor.bat`
- `tool_mermaid_editor.sh`

脚本要求：

- 脚本头部必须写清参数注释
- 若省略 `project_root`，脚本应默认使用当前工作目录
