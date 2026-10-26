# 编写自定义 Spider 中间件钩子方法 子技能地图

## 子技能列表

- [process_spider_input 返回值契约](通用技能领域/Family技能/未分类技能/微技能/process_spider_input 返回值契约/SKILL.md) ｜ 微技能
  - 适用：确保自定义 Spider 中间件的 process_spider_input 钩子符合 Scrapy 框架契约：对每个进入 Spider 的响应调用，必须返回 None 或抛出异常；返回 None 时处理链继续执行后续中间件直至交给 Spider。用于实现该钩子时校验返回值行为。
  - 线索：实现 process_spider_input 方法, 审查 Spider 中间件钩子返回值, 响应进入 Spider 前需要放行或中断, scrapy, spider-middleware
