---
id: "b7e8d5c2-dfcf-59cd-ba27-6299829dcbf3"
name: "Feed 存储后端选择与依赖校验"
description: "根据目标输出位置为 Scrapy feed 选择内置存储后端（本地文件系统、FTP、S3、GCS、标准输出），并在使用前校验所需外部库是否已安装，给出可用后端与依赖校验结论。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed_export"
  - "storage_backend"
  - "dependency_check"
triggers:
  - "需要把抓取结果导出到本地、FTP、S3、GCS 或标准输出"
  - "不确定某存储后端是否可用"
  - "需要确认存储后端的外部依赖是否满足"
examples:
  - input: "我想把抓取结果导出到 S3，但不确定是否可用。"
    output: "S3 后端需要安装 boto3 库；若未安装则该后端不可用，请先安装 boto3 或改用本地文件系统等可用后端。"
    notes: "依赖校验结论需明确可用性"
  - input: "导出到标准输出需要额外依赖吗？"
    output: "标准输出是内置支持的存储后端，无需额外外部库。"
    notes: "内置后端无需外部依赖"
---

# Feed 存储后端选择与依赖校验

根据目标输出位置为 Scrapy feed 选择内置存储后端（本地文件系统、FTP、S3、GCS、标准输出），并在使用前校验所需外部库是否已安装，给出可用后端与依赖校验结论。

## Prompt

当需要把抓取结果导出到某个存储位置时，先确定目标位置对应的存储后端，再校验该后端所需的外部库是否已安装；若依赖缺失则说明该后端不可用并给出替代方案。

## Objective

为给定输出目标确定可用的存储后端并确认依赖满足
## Applicable Signals

- 用户指定了输出位置（本地路径、FTP、S3、GCS 或标准输出）
- 用户询问某存储后端是否可用或为何不可用

## Contraindications

- 仅需选择序列化格式而非存储位置
- 未安装所需外部库且无法安装

## Intervention Moves

- 将目标输出位置映射到内置存储后端：本地文件系统、FTP、S3、GCS、标准输出
- 识别该后端所需的外部库（如 S3 需要 boto3，GCS 需要 google-cloud-storage）
- 校验所需外部库是否已安装，未安装则判定该后端不可用
- 在依赖缺失时提示安装依赖或改用其它可用后端

## Workflow Steps

- 确认目标输出位置类型
- 从内置后端列表中选择对应存储后端
- 确定该后端所需的外部库
- 校验外部库是否可用
- 输出选定后端及依赖校验结论，必要时给出替代后端

## Constraints

- 仅使用内置支持的存储后端：本地文件系统、FTP、S3、GCS、标准输出
- S3 后端仅在安装 boto3 后可用
- GCS 后端仅在安装 google-cloud-storage 后可用
- 外部库缺失时不得声称该后端可用

## Cautions

- 部分存储后端在缺少所需外部库时不可用，需在配置前确认

## Output Contract

- 给出选定的存储后端及依赖校验结论（可用/不可用及原因），必要时附替代后端建议。

## Example Therapist Responses

### Example 1

- Client/Input: 我想把抓取结果导出到 S3，但不确定是否可用。
- Therapist/Output: S3 后端需要安装 boto3 库；若未安装则该后端不可用，请先安装 boto3 或改用本地文件系统等可用后端。
- Notes: 依赖校验结论需明确可用性

### Example 2

- Client/Input: 导出到标准输出需要额外依赖吗？
- Therapist/Output: 标准输出是内置支持的存储后端，无需额外外部库。
- Notes: 内置后端无需外部依赖

## Triggers

- 需要把抓取结果导出到本地、FTP、S3、GCS 或标准输出
- 不确定某存储后端是否可用
- 需要确认存储后端的外部依赖是否满足

## Examples

### Example 1

Input:

  我想把抓取结果导出到 S3，但不确定是否可用。

Output:

  S3 后端需要安装 boto3 库；若未安装则该后端不可用，请先安装 boto3 或改用本地文件系统等可用后端。

Notes:

  依赖校验结论需明确可用性

### Example 2

Input:

  导出到标准输出需要额外依赖吗？

Output:

  标准输出是内置支持的存储后端，无需额外外部库。

Notes:

  内置后端无需外部依赖
