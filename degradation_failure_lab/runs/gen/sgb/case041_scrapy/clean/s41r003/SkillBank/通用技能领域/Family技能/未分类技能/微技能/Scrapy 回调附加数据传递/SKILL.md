---
id: "501dbb09-bc4f-50e2-8eeb-0f83cbff1968"
name: "Scrapy 回调附加数据传递"
description: "通过 Request 的 cb_kwargs 向回调函数传递额外上下文数据（如 main_url、foo），使回调能访问请求构造阶段产生的数据。适用于回调需要复用请求阶段上下文信息的场景。"
version: "0.1.0"
tags:
  - "scrapy"
  - "request"
  - "callback"
  - "cb_kwargs"
  - "上下文传递"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "回调需要访问请求阶段产生的额外数据"
  - "需要在多个回调之间传递上下文信息"
examples:
  - input: "构造请求时传入 cb_kwargs={'main_url': main_url, 'foo': foo}"
    output: "def parse_page2(self, response, main_url, foo): yield dict(main_url=main_url, other_url=response.url, foo=foo)"
    notes: "回调参数名与 cb_kwargs 键一一对应"
---

# Scrapy 回调附加数据传递

通过 Request 的 cb_kwargs 向回调函数传递额外上下文数据（如 main_url、foo），使回调能访问请求构造阶段产生的数据。适用于回调需要复用请求阶段上下文信息的场景。

## Prompt

在构造 Request 时，将回调所需的额外上下文数据放入 cb_kwargs 字典；回调函数签名中声明对应参数，Scrapy 会在调用回调时把 cb_kwargs 中的键值作为关键字参数传入。确保回调参数名与 cb_kwargs 键名一致，并在回调中正确使用这些数据。

## Objective

在请求与回调之间传递额外上下文数据
## Applicable Signals

- 回调函数需要接收请求构造阶段已知的额外数据
- 需要在回调中复用请求阶段的上下文变量

## Contraindications

- 回调无需额外上下文数据
- 数据可通过 response 本身直接获取

## Intervention Moves

- 在 Request 中设置 cb_kwargs 字典携带额外数据
- 在回调函数签名中声明与 cb_kwargs 键对应的参数
- 在回调中使用传入的附加数据构造输出

## Workflow Steps

- 确定回调所需的额外上下文数据
- 构造 Request 时将数据放入 cb_kwargs
- 在回调函数签名中声明对应参数
- 在回调中读取并使用这些参数

## Constraints

- cb_kwargs 的键必须与回调函数参数名一致

## Cautions

- 参数名不匹配会导致回调调用失败

## Output Contract

- 回调函数接收到 cb_kwargs 中的附加数据并正确使用

## Example Therapist Responses

### Example 1

- Client/Input: 构造请求时传入 cb_kwargs={'main_url': main_url, 'foo': foo}
- Therapist/Output: def parse_page2(self, response, main_url, foo): yield dict(main_url=main_url, other_url=response.url, foo=foo)
- Notes: 回调参数名与 cb_kwargs 键一一对应

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 回调需要访问请求阶段产生的额外数据
- 需要在多个回调之间传递上下文信息

## Examples

### Example 1

Input:

  构造请求时传入 cb_kwargs={'main_url': main_url, 'foo': foo}

Output:

  def parse_page2(self, response, main_url, foo): yield dict(main_url=main_url, other_url=response.url, foo=foo)

Notes:

  回调参数名与 cb_kwargs 键一一对应
