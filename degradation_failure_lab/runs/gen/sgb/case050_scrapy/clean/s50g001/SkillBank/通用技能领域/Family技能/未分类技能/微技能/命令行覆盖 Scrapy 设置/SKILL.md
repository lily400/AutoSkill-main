---
id: "7268634b-7e29-5a4c-a57f-f797cfd28742"
name: "命令行覆盖 Scrapy 设置"
description: "使用 -s/--set 命令行选项在运行时显式覆盖一个或多个 Scrapy 设置，优先级最高；适用于需要临时覆盖设置而不修改项目文件、或调试时快速切换设置值的场景。"
version: "0.1.0"
tags:
  - "scrapy"
  - "settings"
  - "命令行覆盖"
  - "配置管理"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "需要临时覆盖某设置而不修改项目文件"
  - "调试时快速切换设置值"
  - "需要在命令行运行时显式指定设置项"
examples:
  - input: "需要临时覆盖某设置而不修改项目文件"
    output: "使用 -s（或 --set）命令行选项指定该设置项，运行时以最高优先级生效"
---

# 命令行覆盖 Scrapy 设置

使用 -s/--set 命令行选项在运行时显式覆盖一个或多个 Scrapy 设置，优先级最高；适用于需要临时覆盖设置而不修改项目文件、或调试时快速切换设置值的场景。

## Prompt

当需要在运行时临时覆盖 Scrapy 设置时，使用 -s（或 --set）命令行选项显式指定要覆盖的设置项及其值。命令行设置的优先级最高，会覆盖蜘蛛设置、项目设置、附加组件设置、命令默认设置和全局默认设置。若需要持久化配置变更，应改用项目设置而非命令行覆盖。

## Objective

在命令行运行时临时覆盖指定设置项
## Applicable Signals

- 需要临时覆盖某设置而不修改项目文件
- 调试时快速切换设置值

## Contraindications

- 需要持久化配置变更时应改用项目设置

## Intervention Moves

- 使用 -s 或 --set 命令行选项指定要覆盖的设置项
- 确认命令行设置优先级最高，覆盖其他所有来源

## Workflow Steps

- 确定需要临时覆盖的设置项及其值
- 在命令行中使用 -s（或 --set）选项指定该设置项
- 运行命令，确认命令行设置以最高优先级生效

## Constraints

- 命令行设置优先级最高，会覆盖蜘蛛设置、项目设置、附加组件设置、命令默认设置和全局默认设置
- 仅用于临时覆盖，不用于持久化配置

## Cautions

- 若需要持久化配置变更，应改用项目设置而非命令行覆盖

## Output Contract

- 命令行执行时指定设置项以覆盖值生效

## Example Therapist Responses

### Example 1

- Client/Input: 需要临时覆盖某设置而不修改项目文件
- Therapist/Output: 使用 -s（或 --set）命令行选项指定该设置项，运行时以最高优先级生效

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要临时覆盖某设置而不修改项目文件
- 调试时快速切换设置值
- 需要在命令行运行时显式指定设置项

## Examples

### Example 1

Input:

  需要临时覆盖某设置而不修改项目文件

Output:

  使用 -s（或 --set）命令行选项指定该设置项，运行时以最高优先级生效
