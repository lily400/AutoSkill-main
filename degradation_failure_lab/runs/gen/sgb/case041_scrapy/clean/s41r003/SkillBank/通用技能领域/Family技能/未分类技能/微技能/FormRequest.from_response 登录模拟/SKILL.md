---
id: "fd94eb98-3273-588e-bd85-64c78e5d016e"
name: "FormRequest.from_response 登录模拟"
description: "用 FormRequest.from_response() 基于已有响应中的表单自动预填隐藏字段（如会话数据、认证令牌），仅覆盖用户名密码等少数字段以模拟登录提交。适用于登录页含隐藏令牌字段、需要保留预填值只覆盖关键字段的场景。"
version: "0.1.0"
tags:
  - "scrapy"
  - "FormRequest"
  - "from_response"
  - "登录模拟"
  - "会话建立"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
triggers:
  - "登录页含 input type=hidden 的令牌或会话字段"
  - "需要保留预填字段仅覆盖用户名密码"
  - "需要基于已有响应表单模拟用户登录"
examples:
  - input: "登录页响应含隐藏的会话/认证令牌字段，需以用户名密码登录"
    output: "FormRequest.from_response(response, formdata={\"username\": \"...\", \"password\": \"...\"}, callback=self.after_login)"
    notes: "保留隐藏字段，仅覆盖用户名密码"
---

# FormRequest.from_response 登录模拟

用 FormRequest.from_response() 基于已有响应中的表单自动预填隐藏字段（如会话数据、认证令牌），仅覆盖用户名密码等少数字段以模拟登录提交。适用于登录页含隐藏令牌字段、需要保留预填值只覆盖关键字段的场景。

## Prompt

当目标登录页包含预填充表单字段（如 <input type="hidden"> 的会话数据或认证令牌）时，使用 FormRequest.from_response() 从已有响应构造登录请求：保留表单中自动预填的隐藏字段，仅覆盖用户名、密码等少数字段，并指定 callback 处理登录后响应。不要用于无表单或无需认证的页面，也不要用于需要完全手工构造全部字段的场景。

## Objective

基于已有响应表单自动预填并覆盖关键字段完成登录提交
## Applicable Signals

- 登录页含 input type=hidden 的令牌或会话字段
- 需要保留预填字段仅覆盖用户名密码

## Contraindications

- 目标页面无表单或无需认证
- 需要完全手工构造全部字段

## Intervention Moves

- 从已有响应调用 FormRequest.from_response()
- 保留自动预填的隐藏字段
- 仅覆盖用户名、密码等少数字段
- 指定 callback 处理登录后响应

## Workflow Steps

- 确认登录页表单含需保留的隐藏字段（会话数据、认证令牌等）
- 在解析登录页的响应回调中调用 FormRequest.from_response()
- 通过 formdata 仅覆盖用户名、密码等少数字段
- 指定 callback 处理登录后的响应

## Constraints

- 必须基于已有响应表单构造，而非从零构造全部 formdata
- 仅覆盖少数字段，保留其余预填字段

## Cautions

- 若页面无表单或无需认证，不应使用此方法

## Output Contract

- 生成一个继承隐藏字段并覆盖指定字段的登录 FormRequest

## Example Therapist Responses

### Example 1

- Client/Input: 登录页响应含隐藏的会话/认证令牌字段，需以用户名密码登录
- Therapist/Output: FormRequest.from_response(response, formdata={"username": "...", "password": "..."}, callback=self.after_login)
- Notes: 保留隐藏字段，仅覆盖用户名密码

## Files

- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 登录页含 input type=hidden 的令牌或会话字段
- 需要保留预填字段仅覆盖用户名密码
- 需要基于已有响应表单模拟用户登录

## Examples

### Example 1

Input:

  登录页响应含隐藏的会话/认证令牌字段，需以用户名密码登录

Output:

  FormRequest.from_response(response, formdata={"username": "...", "password": "..."}, callback=self.after_login)

Notes:

  保留隐藏字段，仅覆盖用户名密码
