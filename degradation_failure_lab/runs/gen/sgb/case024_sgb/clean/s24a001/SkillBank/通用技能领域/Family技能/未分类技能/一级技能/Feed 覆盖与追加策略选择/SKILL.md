---
id: "c5cbbf46-9076-57d7-9a2c-80ba8d600fee"
name: "Feed 覆盖与追加策略选择"
description: "根据目标存储后端（本地文件系统、FTP、S3、GCS、标准输出）确定 feed 的 overwrite 取值，并判断该后端是否支持追加写入。用于配置 feed 写入模式时。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed"
  - "overwrite"
  - "storage"
  - "configuration"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "需要决定 feed 文件是否覆盖或追加"
  - "目标存储后端可能不支持追加操作"
  - "配置 feed 的 overwrite 参数"
examples:
  - input: "使用 S3 作为 feed 存储，希望追加写入"
    output: "S3 默认 overwrite=True（覆盖），且不支持追加；如需保留历史数据请改用其他后端或分批文件。"
    notes: "S3 不支持追加"
  - input: "使用本地文件系统，未指定 overwrite"
    output: "本地文件系统默认 overwrite=False，即追加写入。"
    notes: "本地文件系统默认追加"
---

# Feed 覆盖与追加策略选择

根据目标存储后端（本地文件系统、FTP、S3、GCS、标准输出）确定 feed 的 overwrite 取值，并判断该后端是否支持追加写入。用于配置 feed 写入模式时。

## Prompt

针对给定的存储后端，确定 feed 定义中 overwrite 的取值，并说明该后端是否支持追加。

步骤：
1. 确认目标存储后端类型（本地文件系统、FTP、S3、GCS、标准输出）。
2. 若用户未显式指定 overwrite，按后端默认值处理：本地文件系统为 False（追加），FTP 为 True（覆盖），S3 为 True（覆盖），GCS 为 True（覆盖），标准输出为 False（不支持覆盖）。
3. 若用户要求追加（overwrite=False），检查后端是否支持追加：S3、GCS、标准输出不支持追加；FTP 部分服务器可能不支持 APPE 命令，需提示风险。
4. 输出 overwrite 取值及追加可行性说明。

## Objective

为给定存储后端选择正确的 overwrite/append 行为
## Applicable Signals

- 用户询问 feed 文件是否会被覆盖或追加
- 用户指定了 S3、GCS 或标准输出并希望追加写入
- 用户使用 FTP 并需要追加写入

## Contraindications

- 仅需选择序列化格式
- 需要配置 item 过滤或后处理插件

## Intervention Moves

- 识别存储后端类型
- 按后端默认值确定 overwrite
- 检查追加可行性并提示不支持的后端

## Workflow Steps

- 确认目标存储后端类型
- 若未显式指定 overwrite，套用后端默认值
- 若要求追加，检查后端是否支持追加
- 输出 overwrite 取值及追加可行性说明

## Constraints

- overwrite 默认值依赖存储后端，不可统一假设
- S3、GCS、标准输出不支持追加
- FTP 追加依赖服务器是否支持 APPE 命令

## Cautions

- FTP 服务器可能不支持 APPE 命令，追加可能失败
- 标准输出不支持覆盖，overwrite 固定为 False

## Output Contract

- 针对所选存储后端的 overwrite 取值及追加可行性说明

## Example Therapist Responses

### Example 1

- Client/Input: 使用 S3 作为 feed 存储，希望追加写入
- Therapist/Output: S3 默认 overwrite=True（覆盖），且不支持追加；如需保留历史数据请改用其他后端或分批文件。
- Notes: S3 不支持追加

### Example 2

- Client/Input: 使用本地文件系统，未指定 overwrite
- Therapist/Output: 本地文件系统默认 overwrite=False，即追加写入。
- Notes: 本地文件系统默认追加

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要决定 feed 文件是否覆盖或追加
- 目标存储后端可能不支持追加操作
- 配置 feed 的 overwrite 参数

## Examples

### Example 1

Input:

  使用 S3 作为 feed 存储，希望追加写入

Output:

  S3 默认 overwrite=True（覆盖），且不支持追加；如需保留历史数据请改用其他后端或分批文件。

Notes:

  S3 不支持追加

### Example 2

Input:

  使用本地文件系统，未指定 overwrite

Output:

  本地文件系统默认 overwrite=False，即追加写入。

Notes:

  本地文件系统默认追加
