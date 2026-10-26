# 自定义请求指纹器 子技能地图

## 子技能列表

- [请求错误回调处理（errback）](通用技能领域/Family技能/未分类技能/微技能/请求错误回调处理（errback）/SKILL.md) ｜ 微技能
  - 适用：为 Scrapy 请求配置 errback，并按失败类型（HttpError、DNSLookupError、TimeoutError/TCPTimedOutError）分支记录与处理异常。适用于需要区分不同下载失败并做针对性处理的爬虫。
  - 线索：需要区分 HTTP 错误、DNS 错误、超时等不同失败类型, 希望在请求失败时记录日志或产出诊断数据, scrapy, errback, 错误处理
