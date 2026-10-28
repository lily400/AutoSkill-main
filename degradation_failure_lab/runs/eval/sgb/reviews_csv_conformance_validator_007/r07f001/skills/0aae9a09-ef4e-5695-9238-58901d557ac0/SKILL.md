---
id: "0aae9a09-ef4e-5695-9238-58901d557ac0"
name: "产品目录JSON校验"
description: "对下游代理返回的产品目录JSON执行结构化校验，检查格式、数组结构、SKU数量、必填字段、重复ID、枚举值与文本非空，并在无效时向编排器报告。用于收到代理返回的产品目录JSON、需要确认SKU数量与字段完整性时。"
version: "0.1.0"
tags:
  - "数据校验"
  - "结构化校验"
  - "交付前验证"
  - "产品目录"
triggers:
  - "收到代理返回的产品目录JSON"
  - "需要确认SKU数量与字段完整性"
  - "交付前需要验证产品目录数据"
examples:
  - input: "代理返回的产品目录JSON"
    output: "校验通过确认"
    notes: "全部7项校验均通过"
  - input: "含重复sku_id的产品目录JSON"
    output: "向编排器报告：存在重复sku_id"
    notes: "校验失败时报告具体原因"
---

# 产品目录JSON校验

对下游代理返回的产品目录JSON执行结构化校验，检查格式、数组结构、SKU数量、必填字段、重复ID、枚举值与文本非空，并在无效时向编排器报告。用于收到代理返回的产品目录JSON、需要确认SKU数量与字段完整性时。

## Prompt

收到产品目录JSON后，按校验清单逐项检查：1) 是否为可解析的合法JSON；2) 是否为数组结构而非单个对象；3) 是否恰好包含50个SKU对象；4) 每个SKU是否具备全部必填字段；5) 是否存在重复的sku_id；6) 所有category值是否属于合法枚举（tops、bottoms、outerwear）；7) 所有silhouette_description是否为有意义的非空文本。全部通过则返回校验通过确认；任一不通过则向编排器报告具体无效原因。

## Objective

确保产品目录数据满足下游使用前的结构与内容完整性要求
## Applicable Signals

- 收到代理返回的产品目录JSON
- 需要确认SKU数量与字段完整性

## Contraindications

- 输入不是JSON产品目录
- 仅需语义匹配或情感分类时

## Intervention Moves

- 解析并验证JSON格式合法性
- 确认顶层为数组结构
- 核对SKU对象数量是否为50
- 检查每个SKU的必填字段完整性
- 检测sku_id重复
- 校验category枚举值合法性
- 确认silhouette_description为非空有意义文本

## Workflow Steps

- 验证JSON可解析
- 确认数组结构（非单对象）
- 确认恰好50个SKU对象
- 检查每个SKU具备全部必填字段
- 检查无重复sku_id
- 校验category值属于tops/bottoms/outerwear
- 确认silhouette_description非空且有意义
- 全部通过则返回通过确认，否则向编排器报告无效原因

## Constraints

- 必须逐项执行全部7项校验
- category仅允许tops、bottoms、outerwear
- SKU数量必须恰好为50
- sku_id不得重复

## Cautions

- 任一校验失败即视为无效，需向编排器报告具体原因
- silhouette_description为空或null视为无效

## Output Contract

- 校验通过确认，或向编排器返回的无效原因报告

## Example Therapist Responses

### Example 1

- Client/Input: 代理返回的产品目录JSON
- Therapist/Output: 校验通过确认
- Notes: 全部7项校验均通过

### Example 2

- Client/Input: 含重复sku_id的产品目录JSON
- Therapist/Output: 向编排器报告：存在重复sku_id
- Notes: 校验失败时报告具体原因

## Triggers

- 收到代理返回的产品目录JSON
- 需要确认SKU数量与字段完整性
- 交付前需要验证产品目录数据

## Examples

### Example 1

Input:

  代理返回的产品目录JSON

Output:

  校验通过确认

Notes:

  全部7项校验均通过

### Example 2

Input:

  含重复sku_id的产品目录JSON

Output:

  向编排器报告：存在重复sku_id

Notes:

  校验失败时报告具体原因
