---
id: "16d43fc7-a942-5143-bc5e-8799de2381a8"
name: "Feed URI 动态参数注入"
description: "通过定义 uri_params 函数并配置 FEED_URI_PARAMS，将爬虫运行时属性（如 spider.name）动态注入到 feed 导出 URI 中，实现按爬虫或运行上下文区分的动态导出文件名。适用于多个爬虫共用同一导出命令但需区分输出文件，或需要在导出文件名中包含运行时属性的场景。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed_export"
  - "uri_parameterization"
  - "export_configuration"
triggers:
  - "需要在导出文件名中包含爬虫名称或其他运行时属性"
  - "多个爬虫共用同一导出命令但需区分输出文件"
examples:
  - input: "需要在导出文件名中包含爬虫名称"
    output: "定义 uri_params 返回 {**params, \"spider_name\": spider.name}，设置 FEED_URI_PARAMS = \"myproject.utils.uri_params\"，使用 -o \"%(spider_name)s.jsonl\""
    notes: "占位符名称须与函数返回字典键一致"
---

# Feed URI 动态参数注入

通过定义 uri_params 函数并配置 FEED_URI_PARAMS，将爬虫运行时属性（如 spider.name）动态注入到 feed 导出 URI 中，实现按爬虫或运行上下文区分的动态导出文件名。适用于多个爬虫共用同一导出命令但需区分输出文件，或需要在导出文件名中包含运行时属性的场景。

## Prompt

当需要让 feed 导出 URI 引用运行时爬虫属性时执行本微技能：
1. 在项目中定义一个可导入的 uri_params(params, spider) 函数，返回合并了运行时属性的字典，例如 {**params, "spider_name": spider.name}。
2. 在 settings 中将 FEED_URI_PARAMS 指向该函数的导入路径字符串（如 "myproject.utils.uri_params"）。
3. 在导出 URI 中使用 %(spider_name)s 占位符，例如 scrapy crawl <spider_name> -o "%(spider_name)s.jsonl"。
4. 验证导出时占位符被正确替换为实际爬虫属性值。

## Objective

让 feed 导出 URI 能引用运行时爬虫属性，实现动态文件名
## Applicable Signals

- 导出文件名需要随爬虫或运行上下文变化
- 多个爬虫共用同一导出命令但需区分输出文件

## Contraindications

- 导出路径为固定静态值，无需运行时变量
- 无法在项目中定义可导入的 Python 函数

## Intervention Moves

- 定义 uri_params(params, spider) 函数并合并运行时属性
- 在 settings 中设置 FEED_URI_PARAMS 指向该函数导入路径
- 在导出 URI 中使用 %(spider_name)s 占位符

## Workflow Steps

- 在项目中定义可导入的 uri_params(params, spider) 函数，返回 {**params, "spider_name": spider.name} 等合并字典
- 在 settings 中设置 FEED_URI_PARAMS = "<module.path>.uri_params"
- 在导出 URI 中使用 %(spider_name)s 占位符，如 scrapy crawl <spider_name> -o "%(spider_name)s.jsonl"
- 运行导出并确认占位符被替换为实际爬虫属性值

## Constraints

- uri_params 函数必须可被导入，FEED_URI_PARAMS 使用导入路径字符串
- URI 占位符名称须与函数返回字典中的键一致

## Cautions

- 若函数不可导入或路径错误，占位符将无法解析

## Output Contract

- 配置好的 uri_params 函数与 FEED_URI_PARAMS 设置，导出 URI 中 %(spider_name)s 被正确替换为运行时爬虫属性值

## Example Therapist Responses

### Example 1

- Client/Input: 需要在导出文件名中包含爬虫名称
- Therapist/Output: 定义 uri_params 返回 {**params, "spider_name": spider.name}，设置 FEED_URI_PARAMS = "myproject.utils.uri_params"，使用 -o "%(spider_name)s.jsonl"
- Notes: 占位符名称须与函数返回字典键一致

## Triggers

- 需要在导出文件名中包含爬虫名称或其他运行时属性
- 多个爬虫共用同一导出命令但需区分输出文件

## Examples

### Example 1

Input:

  需要在导出文件名中包含爬虫名称

Output:

  定义 uri_params 返回 {**params, "spider_name": spider.name}，设置 FEED_URI_PARAMS = "myproject.utils.uri_params"，使用 -o "%(spider_name)s.jsonl"

Notes:

  占位符名称须与函数返回字典键一致
