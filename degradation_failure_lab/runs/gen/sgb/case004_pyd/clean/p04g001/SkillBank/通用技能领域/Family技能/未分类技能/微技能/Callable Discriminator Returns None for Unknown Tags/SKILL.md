---
id: "a43912b0-2bb6-56a5-a243-b84dcdacbcc6"
name: "Callable Discriminator Returns None for Unknown Tags"
description: "When writing a callable Discriminator for a Pydantic union, explicitly return None for input types not covered by known branches so that a union_tag_not_found error is raised, and ensure the caller handles that error."
version: "0.1.0"
tags:
  - "pydantic"
  - "union"
  - "discriminator"
  - "error-handling"
  - "未分类技能"
  - "profile:pydantic::未分类技能"
triggers:
  - "判别函数遇到未覆盖的输入类型"
  - "需要明确未知判别值的失败行为"
examples:
  - input: "判别函数仅处理 int 与 dict/BaseModel，其他类型未覆盖"
    output: "在 else 分支返回 None，触发 union_tag_not_found 错误"
    notes: "显式处理未知类型分支"
---

# Callable Discriminator Returns None for Unknown Tags

When writing a callable Discriminator for a Pydantic union, explicitly return None for input types not covered by known branches so that a union_tag_not_found error is raised, and ensure the caller handles that error.

## Prompt

When writing a callable discriminator for a Pydantic union, cover all known input types and return their corresponding tags. For any input type not covered, explicitly return None in an else branch rather than raising another exception or returning an arbitrary default tag. Expect that returning None raises a union_tag_not_found error, and ensure the calling code anticipates and handles that error.

## Objective

Return None from a callable discriminator for unknown input types and expect a union_tag_not_found error
## Applicable Signals

- 判别函数遇到未覆盖的输入类型
- 需要明确未知判别值的失败行为

## Contraindications

- 判别逻辑已保证覆盖所有输入类型时

## Intervention Moves

- 在判别函数末尾添加返回 None 的分支
- 确认已知类型分支返回对应标签
- 调用方捕获 union_tag_not_found 错误

## Workflow Steps

- 检查判别函数是否覆盖所有已知输入类型并返回对应标签
- 为未覆盖的输入类型添加显式返回 None 的分支
- 在调用方预期并捕获 union_tag_not_found 错误

## Constraints

- 判别函数在无法确定标签时必须返回 None，而非抛出其他异常或返回任意默认标签

## Cautions

- 返回 None 会触发 union_tag_not_found 错误，需确保调用方已处理该错误

## Output Contract

- 判别函数在未知分支返回 None，调用方捕获 union_tag_not_found 错误

## Example Therapist Responses

### Example 1

- Client/Input: 判别函数仅处理 int 与 dict/BaseModel，其他类型未覆盖
- Therapist/Output: 在 else 分支返回 None，触发 union_tag_not_found 错误
- Notes: 显式处理未知类型分支

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 判别函数遇到未覆盖的输入类型
- 需要明确未知判别值的失败行为

## Examples

### Example 1

Input:

  判别函数仅处理 int 与 dict/BaseModel，其他类型未覆盖

Output:

  在 else 分支返回 None，触发 union_tag_not_found 错误

Notes:

  显式处理未知类型分支
