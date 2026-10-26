---
id: "8efb2db6-37e9-5869-8b32-ec06a4206585"
name: "FormRequest 表单提交构造"
description: "使用 FormRequest 构造带 formdata 的 POST 请求，并绑定 callback 处理响应，用于向表单 action 端点提交结构化字段数据。"
version: "0.1.0"
tags:
  - "scrapy"
  - "FormRequest"
  - "POST"
  - "表单提交"
  - "请求构造"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "需要向表单 action 端点提交字段数据"
  - "需要以 POST 方式发送结构化表单"
examples:
  - input: "需要向表单 action 端点提交 name 与 age 字段"
    output: "return [FormRequest(url=\"http://www.example.com/post/action\", formdata={\"name\": \"John Doe\", \"age\": \"27\"}, callback=self.after_post)]"
    notes: "以列表形式返回带 formdata 与 callback 的 FormRequest"
---

# FormRequest 表单提交构造

使用 FormRequest 构造带 formdata 的 POST 请求，并绑定 callback 处理响应，用于向表单 action 端点提交结构化字段数据。

## Prompt

当需要向表单 action 端点以 POST 方式提交结构化字段时，构造 FormRequest 对象：设置 url 为目标表单端点，formdata 为字段字典，callback 为处理响应的回调方法，并以列表形式返回该请求对象。

## Objective

构造并发送携带表单数据的 POST 请求
## Applicable Signals

- 目标端点接受表单编码提交
- 需要以 POST 方式发送结构化字段
- 需要为提交后的响应绑定回调处理

## Contraindications

- 目标端点不接受表单编码
- 仅需 GET 抓取静态页面

## Intervention Moves

- 指定表单 action 端点为 url
- 以字典形式提供 formdata 字段
- 绑定 callback 处理响应
- 以列表形式返回请求对象

## Workflow Steps

- 确认目标表单 action 端点及需提交的字段
- 构造 FormRequest，设置 url、formdata 与 callback
- 以列表形式返回该 FormRequest 对象

## Constraints

- formdata 应为字段名到值的映射
- callback 应指向可处理该响应的回调方法

## Cautions

- 若端点不接受表单编码，应改用其他请求类型
- 仅需 GET 抓取静态页面时不应使用本技能

## Output Contract

- 返回一个带 formdata 与 callback 的 FormRequest 对象列表

## Example Therapist Responses

### Example 1

- Client/Input: 需要向表单 action 端点提交 name 与 age 字段
- Therapist/Output: return [FormRequest(url="http://www.example.com/post/action", formdata={"name": "John Doe", "age": "27"}, callback=self.after_post)]
- Notes: 以列表形式返回带 formdata 与 callback 的 FormRequest

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要向表单 action 端点提交字段数据
- 需要以 POST 方式发送结构化表单

## Examples

### Example 1

Input:

  需要向表单 action 端点提交 name 与 age 字段

Output:

  return [FormRequest(url="http://www.example.com/post/action", formdata={"name": "John Doe", "age": "27"}, callback=self.after_post)]

Notes:

  以列表形式返回带 formdata 与 callback 的 FormRequest
