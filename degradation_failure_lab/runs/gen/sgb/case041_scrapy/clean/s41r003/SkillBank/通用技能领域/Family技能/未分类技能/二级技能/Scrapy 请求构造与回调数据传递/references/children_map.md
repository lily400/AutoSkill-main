# Scrapy 请求构造与回调数据传递 子技能地图

## 子技能列表

- [Scrapy 请求 errback 失败处理](通用技能领域/Family技能/未分类技能/微技能/Scrapy 请求 errback 失败处理/SKILL.md) ｜ 微技能
  - 适用：为 Scrapy 请求设置 errback 回调，在请求处理失败时接收 Failure 对象并执行降级、重试或记录；适用于需要容错处理的抓取请求。
  - 线索：请求可能失败需要容错, 需要在失败时读取请求附加数据, 需要为请求指定失败处理回调, scrapy, errback
- [从 cURL 命令构造 Scrapy Request](通用技能领域/Family技能/未分类技能/微技能/从 cURL 命令构造 Scrapy Request/SKILL.md) ｜ 微技能
  - 适用：使用 Request.from_curl 从 cURL 命令字符串创建 Scrapy Request，自动填充 HTTP 方法、URL、头、cookie 和 body；当已有 cURL 命令（如从浏览器复制）需要转为 Scrapy 请求时使用。
  - 线索：已有 cURL 命令需转为 Scrapy 请求, 需复用从浏览器复制的请求, scrapy, request, curl
- [通过 cb_kwargs 向回调传递附加数据](通用技能领域/Family技能/未分类技能/微技能/通过 cb_kwargs 向回调传递附加数据/SKILL.md) ｜ 微技能
  - 适用：在构造 scrapy.Request 时使用 cb_kwargs 将上下文数据传入后续回调函数，并在回调中读取这些参数，实现跨请求的状态传递。适用于需要在第二个回调中复用第一个回调的上下文数据，或回调函数需要额外参数而非仅 response 的场景。
  - 线索：需要在第二个回调中复用第一个回调的上下文数据, 回调函数需要额外参数而非仅 response, scrapy, request, callback
