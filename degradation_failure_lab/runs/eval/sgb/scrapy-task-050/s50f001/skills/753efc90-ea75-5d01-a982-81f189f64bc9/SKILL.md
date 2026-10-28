---
id: "753efc90-ea75-5d01-a982-81f189f64bc9"
name: "Scrapy 设置分层配置"
description: "按命令行、Spider、项目 settings.py、插件、命令默认、全局默认的优先级顺序放置并覆盖 Scrapy 设置项，用于需要定制爬虫行为时。"
version: "0.1.0"
tags:
  - "scrapy"
  - "settings"
  - "配置管理"
  - "优先级"
triggers:
  - "需要为所有 Spider 设置通用配置"
  - "需要按优先级覆盖某个设置项"
  - "需要决定某个设置项应放在哪一层级"
examples:
  - input: "需要为所有 Spider 设置通用配置"
    output: "在项目 settings.py 中写入该设置项，使其对所有 Spider 生效"
    notes: "项目级设置适用于所有 Spider"
  - input: "需要为某个 Spider 覆盖已有设置"
    output: "在 Spider 的 from_crawler 中调用 settings.set(\"SOME_SETTING\", value, priority=\"spider\")"
    notes: "Spider 级设置优先级高于项目设置"
---

# Scrapy 设置分层配置

按命令行、Spider、项目 settings.py、插件、命令默认、全局默认的优先级顺序放置并覆盖 Scrapy 设置项，用于需要定制爬虫行为时。

## Prompt

当需要为 Scrapy 项目定制行为时，按优先级层级放置设置项：优先在项目 settings.py 中放置适用于所有 Spider 的通用配置；仅在需要按 Spider 覆盖时使用 Spider 级设置（如通过 from_crawler 中的 settings.set 并指定 priority="spider"）；命令行设置用于临时覆盖。确认每个设置项落在正确的层级，并说明其生效优先级。

## Objective

按优先级层级正确放置并覆盖 Scrapy 设置项
## Applicable Signals

- 需要为所有 Spider 设置通用配置
- 需要按优先级覆盖某个设置项

## Contraindications

- 仅需临时调试单个命令参数

## Intervention Moves

- 将适用于所有 Spider 的通用设置放入项目 settings.py
- 需要按 Spider 覆盖时在 Spider 中通过 settings.set 指定 priority="spider"
- 使用命令行设置进行临时覆盖

## Workflow Steps

- 识别需要配置的设置项及其作用范围（全局或单个 Spider）
- 将适用于所有 Spider 的通用设置放入项目 settings.py
- 如需按 Spider 覆盖，在 Spider 的 from_crawler 中调用 settings.set 并指定 priority="spider"
- 如需临时覆盖，使用命令行设置
- 确认各设置项落在正确层级并说明生效优先级

## Constraints

- 通用配置应优先放在项目 settings.py
- Spider 级覆盖需显式指定 priority="spider"

## Cautions

- 避免将仅适用于单个 Spider 的配置放入项目全局设置

## Output Contract

- 一份按正确优先级生效的 settings 配置

## Example Therapist Responses

### Example 1

- Client/Input: 需要为所有 Spider 设置通用配置
- Therapist/Output: 在项目 settings.py 中写入该设置项，使其对所有 Spider 生效
- Notes: 项目级设置适用于所有 Spider

### Example 2

- Client/Input: 需要为某个 Spider 覆盖已有设置
- Therapist/Output: 在 Spider 的 from_crawler 中调用 settings.set("SOME_SETTING", value, priority="spider")
- Notes: Spider 级设置优先级高于项目设置

## Triggers

- 需要为所有 Spider 设置通用配置
- 需要按优先级覆盖某个设置项
- 需要决定某个设置项应放在哪一层级

## Examples

### Example 1

Input:

  需要为所有 Spider 设置通用配置

Output:

  在项目 settings.py 中写入该设置项，使其对所有 Spider 生效

Notes:

  项目级设置适用于所有 Spider

### Example 2

Input:

  需要为某个 Spider 覆盖已有设置

Output:

  在 Spider 的 from_crawler 中调用 settings.set("SOME_SETTING", value, priority="spider")

Notes:

  Spider 级设置优先级高于项目设置
