# Dependency Convention

## 1. 总原则

- 仓库按 monorepo 组织，但依赖按模块边界管理
- `dashboard/`、每个 `tools/<tool_id>/`、以及共享 `packages/` 都应有清晰依赖边界
- 平台层与具体 tool 的依赖关系必须是单向的

## 2. 依赖分层

### 2.1 仓库级开发依赖

放在仓库根部，用于统一格式化、lint、测试和基础开发工具。

示例：

- `ruff`
- `pytest`
- `coverage`

### 2.2 模块级运行依赖

每个可运行模块自己声明运行时依赖：

- `dashboard/pyproject.toml`
- `tools/<tool_id>/pyproject.toml`

不要把所有工具的运行依赖都堆在仓库根部。

## 3. 共享逻辑收敛规则

若 dashboard 与多个 tool 共享以下内容，应上收至 `packages/`：

- 数据模型
- JSON schema
- 进程调度封装
- 存储读写器
- 通用错误定义

## 4. 依赖禁止事项

- dashboard 直接 import tool 内部模块
- tool A 直接 import tool B 内部模块
- 在 `packages/` 中引用某个具体 tool
- 为图方便复制共享逻辑而不沉淀公共包

## 5. 外部语言与可执行程序

对于 C++ 或其他语言产物：

- 视为外部能力单元
- 通过 CLI、文件协议或标准化 IPC 接入
- 不以“语言一致性”为理由破坏平台层依赖边界

## 6. 版本锁定建议

- 开发依赖应可锁定
- 对协议影响较大的核心依赖要固定主版本
- 对生成产物敏感的依赖升级前要做回归验证
