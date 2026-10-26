---
id: "55a14cc4-a8f7-564e-b68a-bd3c5bd396ff"
name: "回调参数透传至 errback"
description: "通过 cb_kwargs 向回调传递上下文参数，并在 errback 中经 Failure.request.cb_kwargs 取回，用于失败时仍能基于原始上下文处理。"
version: "0.1.0"
tags:
  - "scrapy"
  - "errback"
  - "cb_kwargs"
  - "上下文传递"
  - "请求调度"
triggers:
  - "失败后仍需基于原始请求上下文产出数据或做后续处理"
  - "需要在 errback 中访问 callback 的参数"
examples:
  - input: "发起请求时传入 cb_kwargs=dict(main_url=response.url)，并设置 errback"
    output: "errback 中通过 failure.request.cb_kwargs[\"main_url\"] 取回 main_url 并产出结果"
    notes: "callback 与 errback 共享同一上下文参数"
---

# 回调参数透传至 errback

通过 cb_kwargs 向回调传递上下文参数，并在 errback 中经 Failure.request.cb_kwargs 取回，用于失败时仍能基于原始上下文处理。

## Prompt

当请求失败后仍需基于原始回调参数继续处理时，使用本技能：在发起 scrapy.Request 时通过 cb_kwargs 传入所需上下文参数，并在 errback 中通过 failure.request.cb_kwargs 取回这些参数，据此产出数据或做后续处理。

## Objective

在失败回调中访问原始回调参数以继续处理
## Applicable Signals

- 失败后仍需基于原始请求上下文产出数据或做后续处理

## Contraindications

- 失败处理不需要原始回调参数时

## Intervention Moves

- 在 scrapy.Request 中通过 cb_kwargs 传入上下文参数
- 在 errback 中通过 failure.request.cb_kwargs 取回参数
- 基于取回的参数产出结果或做后续处理

## Workflow Steps

- 确定失败后仍需使用的上下文参数
- 在发起请求时通过 cb_kwargs 传入这些参数
- 在 errback 中通过 failure.request.cb_kwargs 取回参数
- 基于取回的参数产出结果或继续处理

## Constraints

- cb_kwargs 中的参数需与 callback 签名匹配
- errback 中通过 failure.request.cb_kwargs 访问参数

## Cautions

- 仅在失败处理确实需要原始上下文时才使用，避免无谓透传

## Output Contract

- errback 中通过 failure.request.cb_kwargs 取回参数并产出结果

## Example Therapist Responses

### Example 1

- Client/Input: 发起请求时传入 cb_kwargs=dict(main_url=response.url)，并设置 errback
- Therapist/Output: errback 中通过 failure.request.cb_kwargs["main_url"] 取回 main_url 并产出结果
- Notes: callback 与 errback 共享同一上下文参数

## Triggers

- 失败后仍需基于原始请求上下文产出数据或做后续处理
- 需要在 errback 中访问 callback 的参数

## Examples

### Example 1

Input:

  发起请求时传入 cb_kwargs=dict(main_url=response.url)，并设置 errback

Output:

  errback 中通过 failure.request.cb_kwargs["main_url"] 取回 main_url 并产出结果

Notes:

  callback 与 errback 共享同一上下文参数
