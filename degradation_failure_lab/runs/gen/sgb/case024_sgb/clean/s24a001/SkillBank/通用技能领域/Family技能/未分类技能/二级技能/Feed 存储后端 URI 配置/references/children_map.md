# Feed 存储后端 URI 配置 子技能地图

## 子技能列表

- [Feed URI 动态参数注入](通用技能领域/Family技能/未分类技能/微技能/Feed URI 动态参数注入/SKILL.md) ｜ 微技能
  - 适用：通过定义 uri_params 函数并配置 FEED_URI_PARAMS，将爬虫运行时属性（如 spider.name）动态注入到 feed 导出 URI 中，实现按爬虫或运行上下文区分的动态导出文件名。适用于多个爬虫共用同一导出命令但需区分输出文件，或需要在导出文件名中包含运行时属性的场景。
  - 线索：需要在导出文件名中包含爬虫名称或其他运行时属性, 多个爬虫共用同一导出命令但需区分输出文件, scrapy, feed_export, uri_parameterization
- [Feed URI 参数生成器](通用技能领域/Family技能/未分类技能/微技能/Feed URI 参数生成器/SKILL.md) ｜ 微技能
  - 适用：实现一个可调用函数，接收默认参数字典与 spider，返回新的参数字典，用于生成 feed 存储 URI 的动态参数（如 batch_id、batch_time、time）。适用于需要按批次或时间动态构造 feed 文件路径、配置 FEED_URI_PARAMS 的场景。
  - 线索：需要按批次或时间动态构造 feed 文件路径, 配置 FEED_URI_PARAMS 时, scrapy, feed_export, uri_param_generation
- [Feed 压缩导出配置](通用技能领域/Family技能/未分类技能/微技能/Feed 压缩导出配置/SKILL.md) ｜ 微技能
  - 适用：为 Scrapy feed 导出选择并配置压缩方式（gzip、lzma、bz2），通过 feed_options 传入对应压缩参数，以减小导出文件体积或满足传输要求。
  - 线索：需要压缩导出文件, 需指定 gzip/lzma/bz2 压缩参数, scrapy, feed_export, compression
- [Scrapy 标准输出 Feed 导出](通用技能领域/Family技能/未分类技能/微技能/Scrapy 标准输出 Feed 导出/SKILL.md) ｜ 微技能
  - 适用：将抓取到的 item 通过 stdout 存储后端直接写入 Scrapy 进程的标准输出，无需任何外部库。适用于需要即时查看导出结果或通过管道交给下游进程、且不需要持久化文件的场景。
  - 线索：需要即时查看导出结果而不落盘, 导出结果需通过管道交给下游进程, scrapy, feed_export, stdout
- [批量 Feed 输出文件命名占位符配置](通用技能领域/Family技能/未分类技能/微技能/批量 Feed 输出文件命名占位符配置/SKILL.md) ｜ 微技能
  - 适用：在 Scrapy feed 导出会生成多个输出文件时，通过在 feed URI 中使用 batch_time 或 batch_id 占位符区分不同输出文件名，并可用 printf 风格格式化控制编号位数。
  - 线索：需要一次导出生成多个文件, 输出文件名需要按批次区分或排序, scrapy, feed_export, uri_placeholder
