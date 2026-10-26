---
id: "d4fd663d-e1d2-5ea4-8be4-d7c525bc68d3"
name: "Scrapy 请求错误回调处理"
description: "为 Request 配置 errback 回调，捕获并分类处理请求处理过程中的异常（连接超时、DNS 错误、HTTP 错误等），并记录或转交错误。适用于需要稳健处理下载失败的爬虫。"
version: "0.1.0"
tags:
  - "scrapy"
  - "errback"
  - "异常处理"
  - "请求处理"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "需要捕获连接超时或 DNS 错误"
  - "需要记录并分类请求处理异常"
  - "请求处理可能抛出异常且需避免爬虫中断"
examples:
  - input: "请求可能因 DNS 解析失败或连接超时而失败"
    output: "为该 Request 注册 errback，在回调中捕获 DNSLookupError 与 TimeoutError 并记录"
    notes: "errback 接收 Failure 作为第一个参数"
---

# Scrapy 请求错误回调处理

为 Request 配置 errback 回调，捕获并分类处理请求处理过程中的异常（连接超时、DNS 错误、HTTP 错误等），并记录或转交错误。适用于需要稳健处理下载失败的爬虫。

## Prompt

当某个 Request 存在下载失败风险（连接超时、DNS 解析失败、HTTP 错误等）时，为该 Request 注册 errback 回调。errback 接收 Twisted Failure 作为第一个参数，在回调中判断异常类型（如 HttpError、DNSLookupError、TimeoutError、TCPTimedOutError），记录错误并按需分类处理或转交，避免爬虫因单个请求失败而中断。

## Objective

在请求失败时通过 errback 捕获并分类处理异常，避免爬虫中断
## Applicable Signals

- 请求可能因连接超时、DNS 错误或 HTTP 错误失败
- 需要记录并分类请求处理异常

## Contraindications

- 仅需正常响应处理且无失败风险

## Intervention Moves

- 为 Request 指定 errback 回调函数
- 在 errback 中接收 Failure 参数并判断异常类型
- 记录错误并按需分类处理或转交

## Workflow Steps

- 识别存在下载失败风险的 Request
- 为该 Request 注册 errback 回调
- 在 errback 中接收 Failure 作为第一个参数
- 判断异常类型（如 HttpError、DNSLookupError、TimeoutError、TCPTimedOutError）
- 记录错误并按需分类处理或转交

## Constraints

- errback 的第一个参数为 Twisted Failure
- 异常分类需依据具体异常类型判断

## Cautions

- errback 仅处理请求处理过程中的异常，不替代正常响应回调

## Output Contract

- 已注册 errback 的 Request，异常被捕获并记录或转交

## Example Therapist Responses

### Example 1

- Client/Input: 请求可能因 DNS 解析失败或连接超时而失败
- Therapist/Output: 为该 Request 注册 errback，在回调中捕获 DNSLookupError 与 TimeoutError 并记录
- Notes: errback 接收 Failure 作为第一个参数

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要捕获连接超时或 DNS 错误
- 需要记录并分类请求处理异常
- 请求处理可能抛出异常且需避免爬虫中断

## Examples

### Example 1

Input:

  请求可能因 DNS 解析失败或连接超时而失败

Output:

  为该 Request 注册 errback，在回调中捕获 DNSLookupError 与 TimeoutError 并记录

Notes:

  errback 接收 Failure 作为第一个参数
