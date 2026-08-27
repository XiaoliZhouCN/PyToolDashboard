# Packages

本目录用于承载 dashboard 与 tools 共享的基础模块，避免跨模块直接耦合。

建议优先拆分为：

- `ptd_contracts`：协议、schema、共享数据模型
- `ptd_runtime`：进程调度、路径、日志、错误封装
- `ptd_storage`：JSON/CSV 读写、schema 校验、迁移

规则：

- `packages/` 不依赖具体 tool
- dashboard 和 tool 都可以依赖 `packages/`
- 一旦某段逻辑被多个模块复用，应优先上收至此
