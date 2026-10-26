---
id: "6ea881fb-07e2-5ee9-8311-f419990e543a"
name: "自定义请求指纹器实现"
description: "实现一个 RequestFingerprinter 类，通过 fingerprint(request) 方法为 Scrapy 请求生成去重指纹，可优先读取 request.meta 中的预置指纹；适用于需要覆盖默认请求指纹算法或自定义去重/缓存键逻辑的场景。"
version: "0.1.0"
tags:
  - "scrapy"
  - "request"
  - "fingerprint"
  - "去重"
  - "缓存键"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "需要覆盖默认请求指纹算法"
  - "需要基于 request.meta 提供预置指纹"
  - "需要自定义请求去重或缓存键逻辑"
examples:
  - input: "需要在 request.meta 中提供预置指纹"
    output: "class RequestFingerprinter:\n    def fingerprint(self, request):\n        if \"fingerprint\" in request.meta:\n            return request.meta[\"fingerprint\"]\n        return fingerprint(request)"
    notes: "优先读取 meta 中的预置指纹，否则回退到默认算法"
---

# 自定义请求指纹器实现

实现一个 RequestFingerprinter 类，通过 fingerprint(request) 方法为 Scrapy 请求生成去重指纹，可优先读取 request.meta 中的预置指纹；适用于需要覆盖默认请求指纹算法或自定义去重/缓存键逻辑的场景。

## Prompt

实现一个 RequestFingerprinter 类，提供 fingerprint(self, request) 方法。若 request.meta 中已存在预置指纹则直接返回该值，否则调用默认 fingerprint(request) 生成指纹。确保生成的指纹满足下游组件（如文件系统缓存存储）对指纹格式的限制。

## Objective

为 Scrapy 请求生成可复用的自定义指纹
## Applicable Signals

- 需要覆盖默认请求指纹算法
- 需要基于 request.meta 提供预置指纹

## Contraindications

- 仅需默认指纹行为时
- 指纹格式不满足下游组件限制时

## Intervention Moves

- 定义 RequestFingerprinter 类并实现 fingerprint(self, request) 方法
- 在方法内优先检查 request.meta 中的预置指纹并返回
- 否则调用默认 fingerprint(request) 生成指纹

## Workflow Steps

- 定义 RequestFingerprinter 类
- 实现 fingerprint(self, request) 方法
- 若 request.meta 中存在预置指纹则返回该值
- 否则调用默认 fingerprint(request) 生成并返回指纹
- 确认指纹满足下游组件（如文件系统缓存存储）的格式限制

## Constraints

- 指纹必须满足使用它的 Scrapy 组件所施加的格式限制
- 文件系统缓存存储要求指纹至少 1 字节长

## Cautions

- 自定义指纹算法变更可能影响去重与缓存命中行为
- 若需复现旧版本指纹算法，应显式实现对应算法

## Output Contract

- 一个可被 REQUEST_FINGERPRINTER_CLASS 使用的 RequestFingerprinter 类

## Example Therapist Responses

### Example 1

- Client/Input: 需要在 request.meta 中提供预置指纹
- Therapist/Output: class RequestFingerprinter:
    def fingerprint(self, request):
        if "fingerprint" in request.meta:
            return request.meta["fingerprint"]
        return fingerprint(request)
- Notes: 优先读取 meta 中的预置指纹，否则回退到默认算法

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要覆盖默认请求指纹算法
- 需要基于 request.meta 提供预置指纹
- 需要自定义请求去重或缓存键逻辑

## Examples

### Example 1

Input:

  需要在 request.meta 中提供预置指纹

Output:

  class RequestFingerprinter:
      def fingerprint(self, request):
          if "fingerprint" in request.meta:
              return request.meta["fingerprint"]
          return fingerprint(request)

Notes:

  优先读取 meta 中的预置指纹，否则回退到默认算法
