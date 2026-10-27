---
id: "d5862d9c-e48d-5b19-9342-c94d0fbc3157"
name: "Feed 存储后端 URI 配置"
description: "通过 FEEDS 设置使用一个或多个 URI 定义 feed 存储位置，并按 URI scheme 选择本地文件系统、FTP、S3、GCS 或标准输出等存储后端。适用于需要将导出结果写入特定存储位置的场景。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed_export"
  - "storage_backend"
  - "FEEDS"
  - "URI"
triggers:
  - "需要将 feed 写入远程或本地存储"
  - "需要多目标存储输出"
  - "需要按 URI scheme 选择存储后端"
---

# Feed 存储后端 URI 配置

通过 FEEDS 设置使用一个或多个 URI 定义 feed 存储位置，并按 URI scheme 选择本地文件系统、FTP、S3、GCS 或标准输出等存储后端。适用于需要将导出结果写入特定存储位置的场景。

## Prompt

当需要为 feed 导出指定存储位置时，使用 FEEDS 设置配置一个或多个 URI。根据 URI scheme 选择对应存储后端（本地文件系统、FTP、S3、GCS、标准输出）。若需扩展或自定义存储后端，可通过 FEED_STORAGES 相关设置调整。确认每个 URI 的 scheme 与目标后端匹配后再启用导出。

## Objective

为 feed 导出配置正确的存储后端与 URI
## Applicable Signals

- 需要将 feed 写入远程或本地存储
- 需要多目标存储输出
- 需要按 URI scheme 选择存储后端

## Contraindications

- 仅需选择序列化格式而存储位置已确定

## Intervention Moves

- 在 FEEDS 设置中定义一个或多个存储 URI
- 根据 URI scheme 匹配本地文件系统、FTP、S3、GCS 或标准输出后端
- 如需扩展后端，通过 FEED_STORAGES 相关设置配置

## Workflow Steps

- 确定 feed 的目标存储位置（本地、FTP、S3、GCS 或标准输出）
- 在 FEEDS 设置中写入对应的一个或多个 URI
- 确认每个 URI 的 scheme 与目标存储后端匹配
- 如需自定义或扩展后端，调整 FEED_STORAGES 相关设置

## Constraints

- 存储位置必须通过 FEEDS 设置中的 URI 定义
- 存储后端由 URI scheme 决定

## Cautions

- 多目标输出时需确保每个 URI 的 scheme 均正确对应后端

## Output Contract

- 已按 URI scheme 配置好存储后端的 FEEDS 设置

## Triggers

- 需要将 feed 写入远程或本地存储
- 需要多目标存储输出
- 需要按 URI scheme 选择存储后端
