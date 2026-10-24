---
id: "090a1758-18b6-52ae-b493-2519ea84762f"
name: "Feed URI 动态参数注入"
description: "通过自定义 uri_params 回调函数向 feed URI 注入运行时变量（如 spider 名称），在 FEED_URI_PARAMS 中注册该函数后于 URI 模板中使用占位符，使导出文件路径按运行上下文动态生成。适用于需要按爬虫或运行上下文区分导出文件路径的场景。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed_export"
  - "uri_parameterization"
  - "export_configuration"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "需要按 spider 名称或其他运行时变量区分导出文件"
  - "导出路径需在运行时动态生成"
  - "feed URI 需要包含运行时上下文占位符"
examples:
  - input: "需要按 spider 名称区分导出文件"
    output: "定义 uri_params 返回 {**params, \"spider_name\": spider.name}，设置 FEED_URI_PARAMS = \"myproject.utils.uri_params\"，使用 -o \"%(spider_name)s.jsonl\""
    notes: "三步：定义函数、注册设置、URI 使用占位符"
---

# Feed URI 动态参数注入

通过自定义 uri_params 回调函数向 feed URI 注入运行时变量（如 spider 名称），在 FEED_URI_PARAMS 中注册该函数后于 URI 模板中使用占位符，使导出文件路径按运行上下文动态生成。适用于需要按爬虫或运行上下文区分导出文件路径的场景。

## Prompt

当需要让 feed 导出路径包含运行时上下文变量时，按以下顺序执行：1) 在项目中定义 uri_params(params, spider) 函数，返回合并了自定义变量的字典；2) 在 settings 中将 FEED_URI_PARAMS 指向该函数的导入路径；3) 在 feed URI 模板中使用 %(变量名)s 占位符。完成后确认导出文件按变量正确命名。

## Objective

让 feed 导出路径动态包含运行时上下文变量
## Applicable Signals

- 导出路径需在运行时动态生成
- 需要按 spider 名称或其他运行时变量区分导出文件

## Contraindications

- 导出路径为固定静态值
- 无法在项目中定义并注册回调函数

## Intervention Moves

- 定义 uri_params(params, spider) 函数并返回合并自定义变量的字典
- 在 settings 中设置 FEED_URI_PARAMS 指向该函数路径
- 在 feed URI 模板中使用 %(变量名)s 占位符

## Workflow Steps

- 在项目模块中定义 uri_params(params, spider) 函数，返回 {**params, "spider_name": spider.name} 形式的字典
- 在 settings 中设置 FEED_URI_PARAMS 为该函数的导入路径字符串
- 在 feed URI 中使用 %(spider_name)s 等占位符，例如通过 -o "%(spider_name)s.jsonl" 指定输出

## Constraints

- uri_params 必须返回包含原始 params 的字典
- FEED_URI_PARAMS 必须指向可导入的函数路径
- URI 模板中的占位符名称必须与函数返回的键一致

## Cautions

- 占位符名称与函数返回键不一致会导致 URI 解析失败
- 函数路径配置错误将导致回调无法加载

## Output Contract

- 已注册的 uri_params 函数与含占位符的 feed URI 模板，导出文件按变量正确命名

## Example Therapist Responses

### Example 1

- Client/Input: 需要按 spider 名称区分导出文件
- Therapist/Output: 定义 uri_params 返回 {**params, "spider_name": spider.name}，设置 FEED_URI_PARAMS = "myproject.utils.uri_params"，使用 -o "%(spider_name)s.jsonl"
- Notes: 三步：定义函数、注册设置、URI 使用占位符

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要按 spider 名称或其他运行时变量区分导出文件
- 导出路径需在运行时动态生成
- feed URI 需要包含运行时上下文占位符

## Examples

### Example 1

Input:

  需要按 spider 名称区分导出文件

Output:

  定义 uri_params 返回 {**params, "spider_name": spider.name}，设置 FEED_URI_PARAMS = "myproject.utils.uri_params"，使用 -o "%(spider_name)s.jsonl"

Notes:

  三步：定义函数、注册设置、URI 使用占位符
