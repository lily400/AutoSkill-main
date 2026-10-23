---
id: "7c6e4142-008c-527e-97cd-842ef4911d30"
name: "Feed 存储 URI 参数化配置"
description: "使用 %(name)s、%(time)s 等占位符及 spider 参数构造 Feed 存储 URI，实现按 spider 或时间分目录导出到 FTP/S3 等存储。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed-export"
  - "uri-templating"
  - "storage"
triggers:
  - "需要按 spider 或时间分目录存放导出文件"
  - "需要将 Feed 写入 FTP 或 S3 等远程存储"
examples:
  - input: "FTP 存储，按 spider 分目录"
    output: "ftp://user:password@ftp.example.com/scraping/feeds/%(name)s/%(time)s.json"
  - input: "S3 存储，按 spider 分目录"
    output: "s3://mybucket/scraping/feeds/%(name)s/%(time)s.json"
---

# Feed 存储 URI 参数化配置

使用 %(name)s、%(time)s 等占位符及 spider 参数构造 Feed 存储 URI，实现按 spider 或时间分目录导出到 FTP/S3 等存储。

## Prompt

根据目标存储类型（FTP、S3 等）与目录隔离需求，构造带占位符的 Feed 存储 URI 模板。
1. 确定存储协议与基础路径（如 ftp://user:password@host/path 或 s3://bucket/path）。
2. 在路径中插入占位符以实现隔离：按 spider 用 %(name)s，按时间用 %(time)s。
3. 指定导出文件名与格式后缀（如 .json）。
4. 若需使用 spider 参数，记住 spider 参数会成为 spider 属性，因此可作为存储 URI 参数引用。
5. 输出最终 URI 模板字符串，供 FEEDS 配置使用。

## Objective

生成带占位符的 Feed 存储 URI，实现按 spider/时间分目录导出
## Applicable Signals

- 需要按 spider 或时间分目录存放导出文件
- 需要将 Feed 写入 FTP 或 S3 等远程存储

## Contraindications

- 仅需本地单文件导出且无需目录隔离

## Intervention Moves

- 选择存储协议与基础路径
- 插入 %(name)s 实现按 spider 隔离
- 插入 %(time)s 实现按时间隔离
- 追加文件名与格式后缀
- 如需动态值，引用 spider 参数（作为 spider 属性）

## Workflow Steps

- 确定存储协议与基础路径
- 插入 %(name)s 和/或 %(time)s 占位符
- 指定导出文件名与格式后缀
- 如需动态值，引用 spider 参数
- 输出最终 URI 模板

## Constraints

- 占位符需与 spider 属性名一致
- spider 参数会成为 spider 属性，可作为 URI 参数引用

## Cautions

- 远程存储 URI 中可能包含凭据，注意避免泄露

## Output Contract

- 可用的参数化存储 URI 模板（如 ftp://.../%(name)s/%(time)s.json）

## Example Therapist Responses

### Example 1

- Client/Input: FTP 存储，按 spider 分目录
- Therapist/Output: ftp://user:password@ftp.example.com/scraping/feeds/%(name)s/%(time)s.json

### Example 2

- Client/Input: S3 存储，按 spider 分目录
- Therapist/Output: s3://mybucket/scraping/feeds/%(name)s/%(time)s.json

## Triggers

- 需要按 spider 或时间分目录存放导出文件
- 需要将 Feed 写入 FTP 或 S3 等远程存储

## Examples

### Example 1

Input:

  FTP 存储，按 spider 分目录

Output:

  ftp://user:password@ftp.example.com/scraping/feeds/%(name)s/%(time)s.json

### Example 2

Input:

  S3 存储，按 spider 分目录

Output:

  s3://mybucket/scraping/feeds/%(name)s/%(time)s.json
