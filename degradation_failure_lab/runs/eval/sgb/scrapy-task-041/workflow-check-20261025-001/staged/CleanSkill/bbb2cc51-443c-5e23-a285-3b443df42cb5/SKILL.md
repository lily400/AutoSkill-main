---
id: "bbb2cc51-443c-5e23-a285-3b443df42cb5"
name: "请求指纹规范化计算"
description: "在自定义 RequestFingerprinter 的 fingerprint() 方法内复用标准指纹逻辑：对 request.url 做 canonicalize_url 规范化，结合 method 与 body 生成 SHA1 哈希，从而忽略参数顺序、会话 cookie 等随机成分，得到唯一标识请求资源的指纹。"
version: "0.1.0"
tags:
  - "scrapy"
  - "请求去重"
  - "指纹"
  - "URL规范化"
  - "SHA1"
triggers:
  - "需要在 fingerprint() 方法内复用标准指纹算法"
  - "URL 参数顺序不同但指向同一资源"
  - "请求仅因会话 cookie 等随机成分不同而应视为同一资源"
examples:
  - input: "两个 URL：http://www.example.com/query?id=111&cat=222 与 http://www.example.com/query?cat=222&id=111"
    output: "两者经 canonicalize_url 规范化后得到相同指纹"
    notes: "参数顺序不同但指向同一资源"
  - input: "仅会话 cookie 不同的同一页面请求"
    output: "指纹忽略 cookie 随机成分，得到相同指纹"
    notes: "会话 id 等随机成分不应影响指纹"
---

# 请求指纹规范化计算

在自定义 RequestFingerprinter 的 fingerprint() 方法内复用标准指纹逻辑：对 request.url 做 canonicalize_url 规范化，结合 method 与 body 生成 SHA1 哈希，从而忽略参数顺序、会话 cookie 等随机成分，得到唯一标识请求资源的指纹。

## Prompt

当需要在自定义 RequestFingerprinter 的 fingerprint() 方法中复用标准指纹算法时，调用 scrapy.utils.request.fingerprint()（默认参数）。该函数对 request.url 取 canonicalize_url 规范化版本，并结合 request.method 与 request.body 计算 SHA1 哈希，返回 bytes。确保返回值为 bytes 且能唯一标识请求指向的资源；对参数顺序不同但等价的 URL 应得到相同指纹，对仅因会话 cookie 等随机成分不同的请求应忽略这些成分。

## Objective

对单个请求计算规范化指纹哈希
## Applicable Signals

- 自定义指纹器需要复用标准指纹逻辑
- 存在等价但字面不同的 URL（如参数顺序不同）
- 请求含会话 cookie 等应被忽略的随机成分

## Contraindications

- 需要完全自定义非哈希指纹策略时不应使用本微技能

## Intervention Moves

- 在 fingerprint() 中调用 scrapy.utils.request.fingerprint() 并传入 request
- 依赖 canonicalize_url 规范化 request.url
- 结合 request.method 与 request.body 计算 SHA1 哈希
- 返回 bytes 类型的指纹

## Workflow Steps

- 确认当前处于自定义 RequestFingerprinter 的 fingerprint() 实现中
- 调用 scrapy.utils.request.fingerprint()（默认参数）并传入 request
- 确认返回值是唯一标识该请求资源的 bytes 对象
- 验证等价 URL（参数顺序不同）得到相同指纹，含会话 cookie 的请求指纹不受随机成分影响

## Constraints

- fingerprint() 必须返回 bytes 对象
- 指纹应唯一标识请求指向的资源
- 默认实现基于 canonicalize_url 规范化 URL 并结合 method、body 生成 SHA1

## Cautions

- 若需非哈希或完全自定义策略，应自行实现 fingerprint() 而非复用标准函数

## Output Contract

- 基于规范化 URL、method、body 的 SHA1 指纹（bytes），可唯一标识请求资源。

## Example Therapist Responses

### Example 1

- Client/Input: 两个 URL：http://www.example.com/query?id=111&cat=222 与 http://www.example.com/query?cat=222&id=111
- Therapist/Output: 两者经 canonicalize_url 规范化后得到相同指纹
- Notes: 参数顺序不同但指向同一资源

### Example 2

- Client/Input: 仅会话 cookie 不同的同一页面请求
- Therapist/Output: 指纹忽略 cookie 随机成分，得到相同指纹
- Notes: 会话 id 等随机成分不应影响指纹

## Triggers

- 需要在 fingerprint() 方法内复用标准指纹算法
- URL 参数顺序不同但指向同一资源
- 请求仅因会话 cookie 等随机成分不同而应视为同一资源

## Examples

### Example 1

Input:

  两个 URL：http://www.example.com/query?id=111&cat=222 与 http://www.example.com/query?cat=222&id=111

Output:

  两者经 canonicalize_url 规范化后得到相同指纹

Notes:

  参数顺序不同但指向同一资源

### Example 2

Input:

  仅会话 cookie 不同的同一页面请求

Output:

  指纹忽略 cookie 随机成分，得到相同指纹

Notes:

  会话 id 等随机成分不应影响指纹
