---
id: "43affaf4-7057-57e5-9e23-916199739db6"
name: "WeakKeyDictionary 指纹缓存"
description: "在自行实现请求指纹算法（未使用 scrapy.utils.request.fingerprint()）时，使用 WeakKeyDictionary 缓存指纹，确保每个请求只计算一次，同时避免请求对象因缓存引用而无法释放。"
version: "0.1.0"
tags:
  - "scrapy"
  - "fingerprint"
  - "cache"
  - "WeakKeyDictionary"
  - "memory"
triggers:
  - "自行编写指纹算法而未使用 scrapy.utils.request.fingerprint()"
  - "实现自定义 RequestFingerprinter 的 fingerprint 方法"
examples:
  - input: "自定义 RequestFingerprinter，仅按 URL 计算指纹"
    output: "class RequestFingerprinter:\n    cache = WeakKeyDictionary()\n    def fingerprint(self, request):\n        if request not in self.cache:\n            fp = sha1()\n            fp.update(to_bytes(request.url))\n            self.cache[request] = fp.digest()\n        return self.cache[request]"
    notes: "缓存避免重复计算，弱引用避免内存泄漏"
---

# WeakKeyDictionary 指纹缓存

在自行实现请求指纹算法（未使用 scrapy.utils.request.fingerprint()）时，使用 WeakKeyDictionary 缓存指纹，确保每个请求只计算一次，同时避免请求对象因缓存引用而无法释放。

## Prompt

当你在自定义 RequestFingerprinter 中从零编写指纹逻辑、且未调用 scrapy.utils.request.fingerprint() 时，使用 WeakKeyDictionary 作为指纹缓存：先检查 request 是否已在缓存中，未命中则计算指纹并写入缓存，命中则直接返回缓存值。不要使用普通 dict 缓存，以免请求对象被永久持有。

## Objective

以 WeakKeyDictionary 缓存指纹，兼顾 CPU 与内存效率
## Applicable Signals

- 自定义指纹逻辑未复用内置 fingerprint() 工具函数
- 需要保证每个请求的指纹只计算一次

## Contraindications

- 直接使用内置 fingerprint() 工具函数时无需自行实现缓存

## Intervention Moves

- 声明类级 cache = WeakKeyDictionary()
- 在 fingerprint 方法中先查缓存，未命中再计算并写入
- 命中缓存时直接返回已存指纹

## Workflow Steps

- 确认未使用 scrapy.utils.request.fingerprint()，需要自行实现指纹逻辑
- 在指纹器类中定义 cache = WeakKeyDictionary()
- 在 fingerprint(request) 中判断 request 是否在 cache 中
- 未命中时计算指纹并写入 cache，命中时返回缓存值

## Constraints

- 必须使用 WeakKeyDictionary 而非普通 dict 作为缓存容器
- 缓存键为 request 对象本身

## Cautions

- 使用普通 dict 会导致请求对象无法释放，造成内存泄漏

## Output Contract

- 带 WeakKeyDictionary 缓存的指纹方法，每个请求的指纹仅计算一次且不阻止请求对象被回收

## Example Therapist Responses

### Example 1

- Client/Input: 自定义 RequestFingerprinter，仅按 URL 计算指纹
- Therapist/Output: class RequestFingerprinter:
    cache = WeakKeyDictionary()
    def fingerprint(self, request):
        if request not in self.cache:
            fp = sha1()
            fp.update(to_bytes(request.url))
            self.cache[request] = fp.digest()
        return self.cache[request]
- Notes: 缓存避免重复计算，弱引用避免内存泄漏

## Triggers

- 自行编写指纹算法而未使用 scrapy.utils.request.fingerprint()
- 实现自定义 RequestFingerprinter 的 fingerprint 方法

## Examples

### Example 1

Input:

  自定义 RequestFingerprinter，仅按 URL 计算指纹

Output:

  class RequestFingerprinter:
      cache = WeakKeyDictionary()
      def fingerprint(self, request):
          if request not in self.cache:
              fp = sha1()
              fp.update(to_bytes(request.url))
              self.cache[request] = fp.digest()
          return self.cache[request]

Notes:

  缓存避免重复计算，弱引用避免内存泄漏
