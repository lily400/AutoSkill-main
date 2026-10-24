---
id: "341bd0da-1d52-5a40-87dd-44477cdec422"
name: "Feed 覆盖与追加策略选择"
description: "依据存储后端（本地文件系统、FTP、S3、GCS、标准输出）确定 feed 的 overwrite 取值，并处理后端不支持追加或覆盖的情况，避免数据被意外覆盖或追加失败。用于配置 feed 输出目标时选择覆盖/追加行为。"
version: "0.1.0"
tags:
  - "scrapy"
  - "feed-export"
  - "overwrite"
  - "storage-backend"
  - "configuration"
triggers:
  - "配置 feed 的 overwrite 参数"
  - "目标存储不支持追加（如 S3、GCS、标准输出）"
  - "需要决定 feed 输出是覆盖还是追加已有文件"
examples:
  - input: "feed 目标为 S3，未指定 overwrite"
    output: "overwrite=True（S3 默认覆盖，且不支持追加）"
    notes: "S3 无法追加，只能覆盖"
  - input: "feed 目标为标准输出，未指定 overwrite"
    output: "overwrite=False（标准输出默认追加，不支持覆盖）"
    notes: "标准输出不支持覆盖"
---

# Feed 覆盖与追加策略选择

依据存储后端（本地文件系统、FTP、S3、GCS、标准输出）确定 feed 的 overwrite 取值，并处理后端不支持追加或覆盖的情况，避免数据被意外覆盖或追加失败。用于配置 feed 输出目标时选择覆盖/追加行为。

## Prompt

当需要为某个 feed 输出目标决定 overwrite 行为时：
1. 确认目标存储后端（本地文件系统、FTP、S3、GCS、标准输出）。
2. 若 feed 定义中显式提供了 overwrite，则采用该值；否则按后端默认值：本地文件系统 False（追加）、FTP True（覆盖）、S3 True（覆盖）、GCS True（覆盖）、标准输出 False（追加）。
3. 检查后端限制：S3 与 GCS 不支持追加，标准输出不支持覆盖；FTP 部分服务器可能不支持 APPE 追加命令。
4. 若所需行为与后端能力冲突，调整 overwrite 取值或更换存储后端，并向调用方说明限制。
5. 输出最终 overwrite 取值及对应后端限制说明。

## Objective

为给定存储后端选择正确的 overwrite 行为
## Applicable Signals

- feed 定义中未指定 overwrite 需取默认值
- 目标后端为 S3、GCS 或标准输出等不支持追加/覆盖的存储
- 担心已有输出文件被覆盖或追加失败

## Contraindications

- 仅需选择序列化格式
- 与 overwrite 决策无关的其他 feed 配置项

## Intervention Moves

- 识别目标存储后端
- 按后端取 overwrite 默认值或采用显式配置
- 核对后端对追加/覆盖的支持能力
- 冲突时调整取值或更换后端并说明限制

## Workflow Steps

- 确认目标存储后端类型
- 读取 feed 定义中的 overwrite（若有）
- 否则应用后端默认值：本地文件系统 False、FTP True、S3 True、GCS True、标准输出 False
- 检查后端限制：S3/GCS 不支持追加，标准输出不支持覆盖，部分 FTP 服务器不支持 APPE
- 冲突时调整 overwrite 或更换后端
- 输出 overwrite 取值与后端限制说明

## Constraints

- overwrite 默认值依赖存储后端，不可统一假设
- S3 与 GCS 不支持追加，只能覆盖
- 标准输出不支持覆盖，只能追加
- FTP 追加依赖服务器是否支持 APPE 命令

## Cautions

- 部分 FTP 服务器可能不支持 APPE 追加命令，追加可能失败
- 对不支持追加的后端设置 overwrite=False 会导致写入失败

## Output Contract

- 确定的 overwrite 取值及对应后端限制说明

## Example Therapist Responses

### Example 1

- Client/Input: feed 目标为 S3，未指定 overwrite
- Therapist/Output: overwrite=True（S3 默认覆盖，且不支持追加）
- Notes: S3 无法追加，只能覆盖

### Example 2

- Client/Input: feed 目标为标准输出，未指定 overwrite
- Therapist/Output: overwrite=False（标准输出默认追加，不支持覆盖）
- Notes: 标准输出不支持覆盖

## Triggers

- 配置 feed 的 overwrite 参数
- 目标存储不支持追加（如 S3、GCS、标准输出）
- 需要决定 feed 输出是覆盖还是追加已有文件

## Examples

### Example 1

Input:

  feed 目标为 S3，未指定 overwrite

Output:

  overwrite=True（S3 默认覆盖，且不支持追加）

Notes:

  S3 无法追加，只能覆盖

### Example 2

Input:

  feed 目标为标准输出，未指定 overwrite

Output:

  overwrite=False（标准输出默认追加，不支持覆盖）

Notes:

  标准输出不支持覆盖
