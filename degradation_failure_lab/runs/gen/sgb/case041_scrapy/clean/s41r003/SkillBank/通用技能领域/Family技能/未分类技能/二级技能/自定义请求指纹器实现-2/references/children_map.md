# 自定义请求指纹器实现 子技能地图

## 子技能列表

- [Request errback 异常捕获处理](通用技能领域/Family技能/未分类技能/微技能/Request errback 异常捕获处理/SKILL.md) ｜ 微技能
  - 适用：为 Scrapy Request 配置 errback 回调以捕获请求处理过程中的异常，并在 errback 中访问 meta 附加数据进行失败分支处理。适用于需要逐请求容错与失败分支处理的爬取流程。
  - 线索：请求可能失败需要失败分支处理, 需要在异常时读取 meta 附加数据, 需要为单个 Request 定制错误处理逻辑, scrapy, errback
- [Scrapy 请求错误回调处理](通用技能领域/Family技能/未分类技能/微技能/Scrapy 请求错误回调处理/SKILL.md) ｜ 微技能
  - 适用：为 Request 配置 errback 回调，捕获并分类处理请求处理过程中的异常（连接超时、DNS 错误、HTTP 错误等），并记录或转交错误。适用于需要稳健处理下载失败的爬虫。
  - 线索：需要捕获连接超时或 DNS 错误, 需要记录并分类请求处理异常, 请求处理可能抛出异常且需避免爬虫中断, scrapy, errback
- [自定义请求指纹器实现](通用技能领域/Family技能/未分类技能/微技能/自定义请求指纹器实现/SKILL.md) ｜ 微技能
  - 适用：实现一个 RequestFingerprinter 类，通过 fingerprint(request) 方法为 Scrapy 请求生成去重指纹，可优先读取 request.meta 中的预置指纹；适用于需要覆盖默认请求指纹算法或自定义去重/缓存键逻辑的场景。
  - 线索：需要覆盖默认请求指纹算法, 需要基于 request.meta 提供预置指纹, 需要自定义请求去重或缓存键逻辑, scrapy, request
- [请求指纹规范化计算](通用技能领域/Family技能/未分类技能/微技能/请求指纹规范化计算/SKILL.md) ｜ 微技能
  - 适用：在自定义 RequestFingerprinter 的 fingerprint() 方法内复用标准指纹逻辑：对 request.url 做 canonicalize_url 规范化，结合 method 与 body 生成 SHA1 哈希，从而忽略参数顺序、会话 cookie 等随机成分，得到唯一标识请求资源的指纹。
  - 线索：需要在 fingerprint() 方法内复用标准指纹算法, URL 参数顺序不同但指向同一资源, 请求仅因会话 cookie 等随机成分不同而应视为同一资源, scrapy, 请求去重
