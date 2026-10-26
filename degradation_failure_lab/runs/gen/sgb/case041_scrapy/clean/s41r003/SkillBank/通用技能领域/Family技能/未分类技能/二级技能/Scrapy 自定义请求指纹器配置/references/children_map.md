# Scrapy 自定义请求指纹器配置 子技能地图

## 子技能列表

- [回调参数透传至 errback](通用技能领域/Family技能/未分类技能/微技能/回调参数透传至 errback/SKILL.md) ｜ 微技能
  - 适用：通过 cb_kwargs 向回调传递上下文参数，并在 errback 中经 Failure.request.cb_kwargs 取回，用于失败时仍能基于原始上下文处理。
  - 线索：失败后仍需基于原始请求上下文产出数据或做后续处理, 需要在 errback 中访问 callback 的参数, scrapy, errback, cb_kwargs
