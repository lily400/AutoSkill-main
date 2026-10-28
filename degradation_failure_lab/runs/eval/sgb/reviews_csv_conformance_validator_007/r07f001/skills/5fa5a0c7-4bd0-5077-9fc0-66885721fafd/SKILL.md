---
id: "5fa5a0c7-4bd0-5077-9fc0-66885721fafd"
name: "产品目录分类映射校验"
description: "依据受约束的类别词表（tops/bottoms/outerwear）及其定义，将产品描述映射到合法类别，并校验目录中 category 字段取值是否合法。用于需要统一产品分类口径或校验目录类别字段时。"
version: "0.1.0"
tags:
  - "产品分类"
  - "受控词表"
  - "类别校验"
  - "目录运营"
triggers:
  - "需要将产品描述归入固定类别集合"
  - "需要校验目录中 category 字段是否合法"
  - "需要统一产品分类口径"
examples:
  - input: "Wind-resistant shell"
    output: "outerwear"
    notes: "shell 属于 outerwear 定义"
  - input: "Lightweight performance hoodie"
    output: "tops"
    notes: "hoodie 属于 tops 定义"
  - input: "category: outer-wear"
    output: "不合法"
    notes: "取值不在 {tops, bottoms, outerwear} 内"
---

# 产品目录分类映射校验

依据受约束的类别词表（tops/bottoms/outerwear）及其定义，将产品描述映射到合法类别，并校验目录中 category 字段取值是否合法。用于需要统一产品分类口径或校验目录类别字段时。

## Prompt

使用本参考词表进行产品分类映射与校验：
1. 仅使用三个允许类别：tops、bottoms、outerwear。
2. 依据定义映射：tops 包含 tees、shirts、hoodies、sweatshirts、jerseys；bottoms 包含 pants、joggers、shorts、leggings、tights；outerwear 包含 jackets、parkas、windbreakers、vests、shells。
3. 对每个产品，根据其描述匹配上述定义，输出一个合法类别；若无法归入任何允许类别，则标记为不合法。
4. 校验目录中每个条目的 category 字段是否属于 {tops, bottoms, outerwear}；不属于则标记为不合法。
5. 不要引入词表之外的类别或自由标签；本资产只提供定义与校验口径，不负责语义相似度判断。

## Objective

提供受约束的产品类别定义与映射口径，用于分类和校验
## Applicable Signals

- 产品描述需要归入固定类别集合
- 目录条目含 category 字段待校验
- 需要统一分类口径

## Contraindications

- 类别体系未定义或允许自由标签
- 需要语义相似度判断而非类别归属

## Intervention Moves

- 按定义将产品描述匹配到 tops/bottoms/outerwear 之一
- 校验 category 字段是否属于允许类别集合
- 对无法归类的产品标记为不合法

## Workflow Steps

- 确认使用受约束类别集合 {tops, bottoms, outerwear}
- 依据类别定义将产品描述映射到单一合法类别
- 校验目录中每个条目的 category 字段合法性
- 对无法归入允许类别的产品标记为不合法

## Constraints

- 仅使用 tops、bottoms、outerwear 三个类别
- 映射须依据给定类别定义
- 不得引入词表之外的类别或自由标签

## Cautions

- 本资产只提供定义与校验口径，不承担语义相似度判断
- 类别定义之外的描述需标记为不合法而非强行归类

## Output Contract

- 每个产品被映射到合法类别或标记为不合法

## Example Therapist Responses

### Example 1

- Client/Input: Wind-resistant shell
- Therapist/Output: outerwear
- Notes: shell 属于 outerwear 定义

### Example 2

- Client/Input: Lightweight performance hoodie
- Therapist/Output: tops
- Notes: hoodie 属于 tops 定义

### Example 3

- Client/Input: category: outer-wear
- Therapist/Output: 不合法
- Notes: 取值不在 {tops, bottoms, outerwear} 内

## Triggers

- 需要将产品描述归入固定类别集合
- 需要校验目录中 category 字段是否合法
- 需要统一产品分类口径

## Examples

### Example 1

Input:

  Wind-resistant shell

Output:

  outerwear

Notes:

  shell 属于 outerwear 定义

### Example 2

Input:

  Lightweight performance hoodie

Output:

  tops

Notes:

  hoodie 属于 tops 定义

### Example 3

Input:

  category: outer-wear

Output:

  不合法

Notes:

  取值不在 {tops, bottoms, outerwear} 内
