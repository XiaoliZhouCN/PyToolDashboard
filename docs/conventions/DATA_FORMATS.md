# Data Format Convention

## 1. 适用范围

本规范约束仓库内用于配置、交付、预览和工具通信的数据文件格式，重点覆盖 JSON、CSV 以及相关 schema 文件。

## 2. 通用规则

- 编码统一为 `UTF-8`
- 文本文件统一使用 `LF`
- 时间统一使用 ISO 8601，例如 `2026-08-27T10:30:00Z`
- 布尔值统一使用 `true` / `false`
- 文件路径优先使用相对路径；确需绝对路径时必须注明其基准语义
- 所有结构化数据都应带 `schema_version`

## 3. JSON 规范

JSON 用于以下场景：

- 工具清单
- request / response
- 预览描述
- 层级配置
- 元数据或结构型结果

要求：

- key 使用 `snake_case`
- 顶层推荐结构：

```json
{
  "schema_version": "1.0",
  "record_type": "preview.table",
  "created_at": "2026-08-27T10:30:00Z",
  "metadata": {},
  "data": []
}
```

- JSON 文件中不内嵌大块二进制内容
- 复杂记录不要把一整段 JSON 再塞成字符串字段
- 如有 schema，命名为 `*.schema.json`

## 4. CSV 规范

CSV 仅用于“强表格型、列语义稳定”的数据交换。

要求：

- 第一行必须为表头
- 列名使用 `snake_case`
- 一列只表达一个语义
- 空值默认使用空字符串；如要区分 `null`，必须配套 schema 说明
- 时间列使用 ISO 8601
- 布尔列使用 `true` / `false`

不建议：

- 在单元格里塞 JSON 字符串
- 在未配 schema 的情况下依赖隐式类型推断
- 用 CSV 承载层级结构或高度可变字段

## 5. CSV 配套 schema 规范

凡是给 dashboard 或跨 tool 传递的重要 CSV，建议配套同名 schema 文件：

```text
result.csv
result.schema.json
```

示例：

```json
{
  "schema_version": "1.0",
  "columns": [
    { "name": "file_path", "type": "string", "required": true },
    { "name": "duration_ms", "type": "integer", "required": false },
    { "name": "created_at", "type": "datetime", "required": true }
  ]
}
```

## 6. dashboard 与 tool 交付建议

- 结构复杂：优先 JSON
- 表格预览：CSV + schema
- 大文件结果：主文件 + metadata JSON
- 二进制产物：单独文件 + sidecar metadata JSON

## 7. 禁止事项

- 无版本号的长期协议文件
- 混用编码
- 同一字段在不同文件中使用不同命名
- 通过文件扩展名表达业务状态，例如 `xxx.final.final2.json`
