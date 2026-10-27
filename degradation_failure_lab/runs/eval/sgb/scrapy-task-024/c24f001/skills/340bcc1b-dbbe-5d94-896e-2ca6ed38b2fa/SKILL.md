---
id: "340bcc1b-dbbe-5d94-896e-2ca6ed38b2fa"
name: "Scrapy GCS Feed 导出配置"
description: "配置 Scrapy feed 导出到 Google Cloud Storage：使用 gs:// URI 方案，并依赖 google-cloud-storage 库完成认证与写入。当需要把抓取结果写入 GCS 存储桶时使用。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed_export"
  - "gcs"
  - "storage_backend"
  - "gs_uri"
triggers:
  - "需要将 feed 导出到 Google Cloud Storage"
  - "目标导出 URI 以 gs:// 开头"
  - "需要为 Scrapy feed 配置 GCS 存储后端"
examples:
  - input: "需要将 feed 导出到名为 mybucket 的 GCS 存储桶的 path/to 目录下，文件名为 export.csv"
    output: "gs://mybucket/path/to/export.csv"
    notes: "需安装 google-cloud-storage 库并按 Google Cloud 文档配置认证"
---

# Scrapy GCS Feed 导出配置

配置 Scrapy feed 导出到 Google Cloud Storage：使用 gs:// URI 方案，并依赖 google-cloud-storage 库完成认证与写入。当需要把抓取结果写入 GCS 存储桶时使用。

## Prompt

当需要将 Scrapy feed 导出到 Google Cloud Storage 时，按以下步骤执行：
1. 确认目标存储后端为 GCS，导出 URI 使用 gs:// 方案。
2. 按 gs://<bucket>/<path>/<filename> 形式构造导出 URI（例如 gs://mybucket/path/to/export.csv）。
3. 确认已安装并可用 google-cloud-storage 库；若缺失，先安装该依赖。
4. 按 Google Cloud 认证文档配置认证凭据，确保进程具备写入目标存储桶的权限。
5. 将 URI 配置到 feed 导出设置中，并验证导出结果写入目标存储桶。
仅处理 GCS 存储后端配置，不涉及序列化格式选择或其他存储后端。

## Objective

让抓取结果正确写入 GCS 存储桶
## Applicable Signals

- 目标存储为 Google Cloud Storage
- 导出 URI 使用 gs:// 方案
- 需要 google-cloud-storage 库支持

## Contraindications

- 目标存储为本地文件系统、FTP 或 S3
- 未安装 google-cloud-storage 库
- 无法配置 Google Cloud 认证凭据

## Intervention Moves

- 确认使用 gs:// URI 方案
- 构造 gs://<bucket>/<path>/<filename> 形式的导出 URI
- 确认安装 google-cloud-storage 库
- 按 Google Cloud 认证文档配置认证凭据

## Workflow Steps

- 确认目标存储后端为 GCS
- 使用 gs:// 方案构造导出 URI
- 确认 google-cloud-storage 库已安装
- 配置 Google Cloud 认证
- 将 URI 配置到 feed 导出设置并验证写入

## Constraints

- 导出 URI 必须使用 gs:// 方案
- 必须依赖 google-cloud-storage 库
- 认证需遵循 Google Cloud 认证文档

## Cautions

- 认证凭据缺失或权限不足会导致写入失败
- 未安装 google-cloud-storage 库时无法使用 GCS 存储后端

## Output Contract

- 可用的 gs:// 导出 URI 配置及依赖说明（含 google-cloud-storage 库与认证要求）

## Example Therapist Responses

### Example 1

- Client/Input: 需要将 feed 导出到名为 mybucket 的 GCS 存储桶的 path/to 目录下，文件名为 export.csv
- Therapist/Output: gs://mybucket/path/to/export.csv
- Notes: 需安装 google-cloud-storage 库并按 Google Cloud 文档配置认证

## Triggers

- 需要将 feed 导出到 Google Cloud Storage
- 目标导出 URI 以 gs:// 开头
- 需要为 Scrapy feed 配置 GCS 存储后端

## Examples

### Example 1

Input:

  需要将 feed 导出到名为 mybucket 的 GCS 存储桶的 path/to 目录下，文件名为 export.csv

Output:

  gs://mybucket/path/to/export.csv

Notes:

  需安装 google-cloud-storage 库并按 Google Cloud 文档配置认证
