---
id: "688b17b0-4bcf-5eb2-879a-50609da68fe0"
name: "Pydantic 模型级 before/after 校验器实现"
description: "使用 model_validator 在 before/after 阶段对整体模型输入执行校验，处理原始输入类型并支持提前终止校验，适用于跨字段或模型级约束。"
version: "0.1.0"
tags:
  - "pydantic"
  - "model_validator"
  - "模型级校验"
  - "before"
  - "after"
  - "未分类技能"
  - "profile:pydantic::未分类技能"
triggers:
  - "需要跨字段或整体模型约束校验"
  - "需要在 Pydantic 处理前后介入校验"
examples:
  - input: "需要在模型级禁止输入中出现 card_number 字段"
    output: "@model_validator(mode='before')\n@classmethod\ndef check_card_number_not_present(cls, data: Any) -> Any:\n    if isinstance(data, dict):\n        if 'card_number' in data:\n            raise ValueError(\"'card_number' should not be included\")\n    return data"
    notes: "before 校验器将 data 标注为 Any，并先判断是否为字典再访问键"
---

# Pydantic 模型级 before/after 校验器实现

使用 model_validator 在 before/after 阶段对整体模型输入执行校验，处理原始输入类型并支持提前终止校验，适用于跨字段或模型级约束。

## Prompt

实现模型级校验器时，先判断校验时机：需要在 Pydantic 及其他校验器处理输入之前介入、或需访问原始输入时使用 mode='before'；需要在字段校验完成后对已解析模型做跨字段约束时使用 mode='after'。before 校验器的 data 参数类型标注为 Any，因为原始输入可能是字典，也可能在启用 from_attributes 时是任意类实例，需先判断类型再访问键。校验失败时抛出 ValueError 以终止校验。

## Objective

实现模型级 before/after 校验并正确处理原始输入
## Applicable Signals

- 约束涉及多个字段或整个模型
- 需要在字段校验之前检查原始输入中是否包含禁止字段
- 需要在字段校验之后对已解析模型做整体校验

## Contraindications

- 仅涉及单字段校验
- 无需访问原始输入数据

## Intervention Moves

- 选择 mode='before' 或 mode='after' 以匹配校验时机
- before 校验器将 data 标注为 Any 并先判断是否为 dict 再访问键
- 校验失败时抛出 ValueError 终止校验
- 校验通过时返回 data 以继续后续处理

## Workflow Steps

- 确定约束是模型级还是字段级，模型级才使用 model_validator
- 根据是否需要访问原始输入选择 mode='before'，否则选择 mode='after'
- before 校验器将 data 参数标注为 Any，并先判断类型（如 isinstance(data, dict)）再访问键
- 在检测到违规时抛出 ValueError 并给出明确信息
- 校验通过时返回 data

## Constraints

- before 校验器接收的原始输入不一定是字典，需先判断类型
- 校验失败应通过抛出 ValueError 终止校验

## Cautions

- 启用 from_attributes 时 before 校验器可能收到任意类实例而非字典
- 不要假设原始输入总是字典

## Output Contract

- 可运行的 model_validator 实现，含 before/after 模式与类型处理

## Example Therapist Responses

### Example 1

- Client/Input: 需要在模型级禁止输入中出现 card_number 字段
- Therapist/Output: @model_validator(mode='before')
@classmethod
def check_card_number_not_present(cls, data: Any) -> Any:
    if isinstance(data, dict):
        if 'card_number' in data:
            raise ValueError("'card_number' should not be included")
    return data
- Notes: before 校验器将 data 标注为 Any，并先判断是否为字典再访问键

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要跨字段或整体模型约束校验
- 需要在 Pydantic 处理前后介入校验

## Examples

### Example 1

Input:

  需要在模型级禁止输入中出现 card_number 字段

Output:

  @model_validator(mode='before')
  @classmethod
  def check_card_number_not_present(cls, data: Any) -> Any:
      if isinstance(data, dict):
          if 'card_number' in data:
              raise ValueError("'card_number' should not be included")
      return data

Notes:

  before 校验器将 data 标注为 Any，并先判断是否为字典再访问键
