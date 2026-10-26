---
id: "84be0366-caaf-5091-b9c2-99289be1395a"
name: "请求指纹格式约束校验"
description: "在把请求指纹交给依赖指纹的内置组件（如 FilesystemCacheStorage）之前，校验指纹满足该组件要求的格式限制（至少 1 字节长），避免缓存或去重组件报错。"
version: "0.1.0"
tags:
  - "scrapy"
  - "request-fingerprint"
  - "constraint-check"
  - "httpcache"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "自定义指纹器接入 HTTP 缓存等组件前"
  - "指纹可能为空或过短时"
---

# 请求指纹格式约束校验

在把请求指纹交给依赖指纹的内置组件（如 FilesystemCacheStorage）之前，校验指纹满足该组件要求的格式限制（至少 1 字节长），避免缓存或去重组件报错。

## Prompt

在将请求指纹交给依赖指纹的内置组件（如 HTTP 缓存存储）之前，先确认指纹满足该组件要求的格式限制。当前已知限制：指纹长度至少为 1 字节。若指纹为空或过短，应先修正指纹生成逻辑再继续，不要直接交给下游组件。

## Objective

确保生成的请求指纹满足内置组件格式限制
## Applicable Signals

- 准备启用或已启用依赖请求指纹的内置组件
- 自定义 RequestFingerprinter 返回的指纹可能为空或过短

## Contraindications

- 不使用任何依赖指纹的内置组件时

## Intervention Moves

- 识别下游组件对指纹格式的附加限制
- 校验指纹长度是否满足至少 1 字节的要求
- 不满足时阻止指纹进入下游组件并修正生成逻辑

## Workflow Steps

- 确认当前流程中哪些内置组件会使用请求指纹（如 FilesystemCacheStorage）
- 查阅该组件对指纹格式的附加限制
- 对生成的指纹执行格式校验，至少检查长度是否不少于 1 字节
- 校验通过后再交给下游组件；未通过则修正指纹生成逻辑并重新校验

## Constraints

- 指纹必须满足使用它的组件所施加的格式限制
- 内置 FilesystemCacheStorage 要求指纹至少 1 字节长

## Cautions

- 不同组件可能施加额外限制，需按实际使用的组件逐一确认
- 本规则只做约束校验，不负责指纹生成算法实现

## Output Contract

- 通过格式校验的指纹（至少 1 字节），可安全交给依赖指纹的下游组件使用

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 自定义指纹器接入 HTTP 缓存等组件前
- 指纹可能为空或过短时
