---
id: "feef4a0a-e457-54fe-95b0-d28f9ed4ec32"
name: "自定义请求指纹器实现"
description: "实现并配置自定义 RequestFingerprinter，用于按需纳入特定请求头或 URL 片段计算请求指纹，或完全自定义指纹逻辑，从而改变 Scrapy 默认去重指纹行为。适用于需要定制请求去重指纹的场景。"
version: "0.1.0"
tags:
  - "scrapy"
  - "请求去重"
  - "指纹定制"
  - "REQUEST_FINGERPRINTER_CLASS"
  - "WeakKeyDictionary"
  - "指纹计算"
  - "未分类技能"
  - "profile:scrapy::未分类技能"
  - "kind:parent"
triggers:
  - "需要将特定请求头纳入指纹计算"
  - "需要保留 URL 片段参与指纹"
  - "需要完全自定义指纹算法"
  - "默认指纹导致去重不符合预期"
  - "默认指纹无法区分或误合并资源"
  - "需要忽略随机 cookie 或参数顺序差异"
  - "需要改变默认指纹逻辑"
examples:
  - input: "需要将名为 X-ID 的请求头纳入指纹计算"
    output: "定义 RequestFingerprinter 类，其 fingerprint 方法返回 fingerprint(request, include_headers=[\"X-ID\"])，并在 settings 中设置 REQUEST_FINGERPRINTER_CLASS = \"my_project.utils.RequestFingerprinter\""
    notes: "复用 scrapy.utils.request.fingerprint() 即可，无需自行缓存"
  - input: "仅按请求 URL 计算指纹，忽略方法、请求体及规范化"
    output: "从零实现 fingerprint 方法，用 sha1 对 to_bytes(request.url) 求摘要，并用 WeakKeyDictionary 缓存结果"
    notes: "从零实现时必须使用 WeakKeyDictionary 缓存"
---

# 自定义请求指纹器实现

实现并配置自定义 RequestFingerprinter，用于按需纳入特定请求头或 URL 片段计算请求指纹，或完全自定义指纹逻辑，从而改变 Scrapy 默认去重指纹行为。适用于需要定制请求去重指纹的场景。

## Prompt

当默认指纹无法满足去重需求时，按以下步骤实现自定义请求指纹器：
1. 明确定制目标：是纳入特定请求头、保留 URL 片段，还是完全自定义算法。
2. 若仅需纳入特定请求头，优先复用 scrapy.utils.request.fingerprint()，通过 include_headers 参数传入需纳入的请求头列表。
3. 若需保留 URL 片段，将 keep_fragments 设为 True（例如处理无头浏览器请求时）。
4. 若完全自定义指纹逻辑，实现一个带 fingerprint(self, request) 方法的类；若不使用 scrapy.utils.request.fingerprint()，必须用 WeakKeyDictionary 缓存指纹，确保每个请求只计算一次并避免请求对象长期驻留内存。
5. 在 settings 中通过 REQUEST_FINGERPRINTER_CLASS 指向自定义类（如 "my_project.utils.RequestFingerprinter"）。
6. 如需在 spider 回调中按请求覆盖指纹，可让指纹器优先读取 request.meta 中的指纹，缺失时回退到 scrapy.utils.request.fingerprint()。

## Objective

按业务需求定制请求指纹计算逻辑并正确接入 Scrapy 去重流程
## Applicable Signals

- 默认指纹忽略请求头导致不同请求被误判为重复
- 需要 URL 片段参与去重判断
- 业务要求自定义指纹算法
- 默认指纹无法区分或误合并资源
- 需要忽略随机 cookie 或参数顺序差异

## Contraindications

- 默认指纹已满足去重需求
- 仅需调整下载中间件行为
- 仅需默认 URL+method+body 的 SHA1 指纹

## Intervention Moves

- 复用 fingerprint() 并传入 include_headers
- 设置 keep_fragments=True 保留片段
- 从零实现 fingerprint 方法并用 WeakKeyDictionary 缓存
- 通过 REQUEST_FINGERPRINTER_CLASS 注册自定义类
- 在指纹器中读取 request.meta 支持按请求覆盖
- 设置 REQUEST_FINGERPRINTER_CLASS 为自定义指纹器类或导入路径
- 实现 fingerprint(request) 方法返回 bytes 指纹
- 在实现中复用 scrapy.utils.request.fingerprint() 处理常见场景

## Workflow Steps

- 确定指纹定制目标（请求头、片段或完全自定义）
- 选择实现方式：复用 fingerprint() 或从零实现
- 若从零实现，使用 WeakKeyDictionary 缓存指纹
- 在 settings 中配置 REQUEST_FINGERPRINTER_CLASS
- 如需按请求覆盖，实现从 request.meta 读取指纹并回退到默认逻辑
- 确认默认指纹无法满足去重需求（如误合并或无法区分资源）
- 编写实现 fingerprint(request) 方法的指纹器组件，返回唯一标识请求的 bytes
- 如需处理常见场景，在 fingerprint() 中复用 scrapy.utils.request.fingerprint()
- 通过 REQUEST_FINGERPRINTER_CLASS 设置指向自定义指纹器类或其导入路径

## Constraints

- 不使用 scrapy.utils.request.fingerprint() 时必须用 WeakKeyDictionary 缓存指纹
- 缓存需保证每个请求只计算一次指纹
- REQUEST_FINGERPRINTER_CLASS 需指向可导入的类路径
- fingerprint() 必须返回 bytes 对象
- 自定义指纹器须遵循请求指纹限制

## Cautions

- 请求头默认被忽略，需显式通过 include_headers 纳入
- URL 片段默认被忽略，需显式设置 keep_fragments=True
- 缓存若使用普通字典会导致请求对象无法释放内存
- 默认指纹器基于规范化 URL、method 和 body 生成 SHA1，忽略会话 cookie 等随机成分需自定义实现

## Output Contract

- 可用的 RequestFingerprinter 类及 settings 中 REQUEST_FINGERPRINTER_CLASS 配置
- 返回唯一标识请求的 bytes 指纹

## Example Therapist Responses

### Example 1

- Client/Input: 需要将名为 X-ID 的请求头纳入指纹计算
- Therapist/Output: 定义 RequestFingerprinter 类，其 fingerprint 方法返回 fingerprint(request, include_headers=["X-ID"])，并在 settings 中设置 REQUEST_FINGERPRINTER_CLASS = "my_project.utils.RequestFingerprinter"
- Notes: 复用 scrapy.utils.request.fingerprint() 即可，无需自行缓存

### Example 2

- Client/Input: 仅按请求 URL 计算指纹，忽略方法、请求体及规范化
- Therapist/Output: 从零实现 fingerprint 方法，用 sha1 对 to_bytes(request.url) 求摘要，并用 WeakKeyDictionary 缓存结果
- Notes: 从零实现时必须使用 WeakKeyDictionary 缓存

## 子技能目录
- [Request errback 异常捕获处理](通用技能领域/Family技能/未分类技能/微技能/Request errback 异常捕获处理/SKILL.md) ｜ 适用：为 Scrapy Request 配置 errback 回调以捕获请求处理过程中的异常，并在 errback 中访问 meta 附加数据进行失败分支处理。适用于需要逐请求容错与失败分支处理的爬取流程。
- [Scrapy 请求错误回调处理](通用技能领域/Family技能/未分类技能/微技能/Scrapy 请求错误回调处理/SKILL.md) ｜ 适用：为 Request 配置 errback 回调，捕获并分类处理请求处理过程中的异常（连接超时、DNS 错误、HTTP 错误等），并记录或转交错误。适用于需要稳健处理下载失败的爬虫。
- [自定义请求指纹器实现](通用技能领域/Family技能/未分类技能/微技能/自定义请求指纹器实现/SKILL.md) ｜ 适用：实现一个 RequestFingerprinter 类，通过 fingerprint(request) 方法为 Scrapy 请求生成去重指纹，可优先读取 request.meta 中的预置指纹；适用于需要覆盖默认请求指纹算法或自定义去重/缓存键逻辑的场景。
- [请求指纹规范化计算](通用技能领域/Family技能/未分类技能/微技能/请求指纹规范化计算/SKILL.md) ｜ 适用：在自定义 RequestFingerprinter 的 fingerprint() 方法内复用标准指纹逻辑：对 request.url 做 canonicalize_url 规范化，结合 method 与 body 生成 SHA1 哈希，从而忽略参数顺序、会话 cookie 等随机成分，得到唯一标识请求资源的指纹。

## 选用规则（微技能目录）
- 当目标、阶段或方法更接近 `Request errback 异常捕获处理` 时，优先调用它。 线索：请求可能失败需要失败分支处理, 需要在异常时读取 meta 附加数据, 需要为单个 Request 定制错误处理逻辑, scrapy, errback
- 当目标、阶段或方法更接近 `Scrapy 请求错误回调处理` 时，优先调用它。 线索：需要捕获连接超时或 DNS 错误, 需要记录并分类请求处理异常, 请求处理可能抛出异常且需避免爬虫中断, scrapy, errback
- 当目标、阶段或方法更接近 `自定义请求指纹器实现` 时，优先调用它。 线索：需要覆盖默认请求指纹算法, 需要基于 request.meta 提供预置指纹, 需要自定义请求去重或缓存键逻辑, scrapy, request
- 当目标、阶段或方法更接近 `请求指纹规范化计算` 时，优先调用它。 线索：需要在 fingerprint() 方法内复用标准指纹算法, URL 参数顺序不同但指向同一资源, 请求仅因会话 cookie 等随机成分不同而应视为同一资源, scrapy, 请求去重

## Files

- `references/children_manifest.json`
- `references/children_map.md`
- `references/evidence.md`
- `references/evidence_manifest.json`

## Triggers

- 需要将特定请求头纳入指纹计算
- 需要保留 URL 片段参与指纹
- 需要完全自定义指纹算法
- 默认指纹导致去重不符合预期
- 默认指纹无法区分或误合并资源
- 需要忽略随机 cookie 或参数顺序差异
- 需要改变默认指纹逻辑

## Examples

### Example 1

Input:

  需要将名为 X-ID 的请求头纳入指纹计算

Output:

  定义 RequestFingerprinter 类，其 fingerprint 方法返回 fingerprint(request, include_headers=["X-ID"])，并在 settings 中设置 REQUEST_FINGERPRINTER_CLASS = "my_project.utils.RequestFingerprinter"

Notes:

  复用 scrapy.utils.request.fingerprint() 即可，无需自行缓存

### Example 2

Input:

  仅按请求 URL 计算指纹，忽略方法、请求体及规范化

Output:

  从零实现 fingerprint 方法，用 sha1 对 to_bytes(request.url) 求摘要，并用 WeakKeyDictionary 缓存结果

Notes:

  从零实现时必须使用 WeakKeyDictionary 缓存
