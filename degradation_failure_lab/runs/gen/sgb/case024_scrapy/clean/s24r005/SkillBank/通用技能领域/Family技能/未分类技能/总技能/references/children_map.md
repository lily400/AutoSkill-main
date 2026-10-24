# 未分类技能 子技能地图

- parent: `未分类技能/总技能/SKILL.md`

## 子技能列表

1. [CSV 导出列字段控制](通用技能领域/Family技能/未分类技能/微技能/CSV 导出列字段控制/SKILL.md)
   - 层级：微技能
   - 类型：导出字段控制
   - 适用条件：使用 FEED_EXPORT_FIELDS 指定 CSV 导出的列集合、顺序与列名；由于 CSV 使用固定表头，该设置对 CSV 尤为重要。适用于需要精确控制 CSV 输出结构时。
2. [Feed URI 动态参数注入](通用技能领域/Family技能/未分类技能/微技能/Feed URI 动态参数注入/SKILL.md)
   - 层级：微技能
   - 类型：feed_export
   - 适用条件：通过自定义 uri_params 回调函数向 feed URI 注入运行时变量（如 spider 名称），在 FEED_URI_PARAMS 中注册该函数后于 URI 模板中使用占位符，使导出文件路径按运行上下文动态生成。适用于需要按爬虫或运行上下文区分导出文件路径的场景。
3. [Feed 存储 URI 参数化配置](通用技能领域/Family技能/未分类技能/微技能/Feed 存储 URI 参数化配置/SKILL.md)
   - 层级：微技能
   - 类型：feed_export
   - 适用条件：使用 %(name)s、%(time)s 等占位符及 spider 参数构造 Feed 存储 URI，实现按 spider 或时间分目录导出到 FTP/S3 等存储。
4. [Feed 存储 URI 参数替换](通用技能领域/Family技能/未分类技能/微技能/Feed 存储 URI 参数替换/SKILL.md)
   - 层级：微技能
   - 类型：feed_export
   - 适用条件：在创建 feed 时按规则替换存储 URI 中的占位参数（%(time)s、%(name)s 及 spider 同名属性），用于生成动态输出路径。当需要按时间戳或 spider 名称动态生成输出文件路径，或在 URI 中引用 spider 自定义属性作为路径片段时使用。
5. [Feed 导出压缩配置](通用技能领域/Family技能/未分类技能/一级技能/Feed 导出压缩配置/SKILL.md)
   - 层级：一级技能
   - 类型：feed_export
   - 适用条件：为 Scrapy feed 导出选择并配置压缩方式（gzip/lzma/bz2）及其 feed_options 参数，控制输出文件的压缩行为。当需要压缩导出数据文件或指定具体压缩参数时使用。
6. [Feed 导出设置项参考](通用技能领域/Family技能/未分类技能/一级技能/Feed 导出设置项参考/SKILL.md)
   - 层级：一级技能
   - 类型：配置参考
   - 适用条件：提供 Scrapy feed 导出相关设置项的查阅参考，列出各设置项名称及其用途，用于确认某个导出设置项的名称或作用。
7. [Feed 导出配置解析与回退](通用技能领域/Family技能/未分类技能/一级技能/Feed 导出配置解析与回退/SKILL.md)
   - 层级：一级技能
   - 类型：feed_export_configuration
   - 适用条件：解析 Scrapy feed 定义中的导出配置键（format、encoding、fields、batch_item_count、overwrite、store_empty、uri_params、postprocessing 等），并在键缺失时确定其对应的 FEED_* 全局设置回退值。用于配置 FEEDS 或排查导出参数未生效时。
8. [Feed 覆盖与追加策略选择](通用技能领域/Family技能/未分类技能/微技能/Feed 覆盖与追加策略选择/SKILL.md)
   - 层级：微技能
   - 类型：feed_export_configuration
   - 适用条件：依据存储后端（本地文件系统、FTP、S3、GCS、标准输出）确定 feed 的 overwrite 取值，并处理后端不支持追加或覆盖的情况，避免数据被意外覆盖或追加失败。用于配置 feed 输出目标时选择覆盖/追加行为。
9. [Scrapy S3 Feed 存储后端配置](通用技能领域/Family技能/未分类技能/一级技能/Scrapy S3 Feed 存储后端配置/SKILL.md)
   - 层级：一级技能
   - 类型：feed_export
   - 适用条件：为 Scrapy feed 导出配置 S3 或 S3 兼容对象存储后端，包括自定义 ACL、endpoint 与 region，并明确 overwrite 默认行为。
10. [延迟文件交付时序处理](通用技能领域/Family技能/未分类技能/一级技能/延迟文件交付时序处理/SKILL.md)
   - 层级：一级技能
   - 类型：feed导出
   - 适用条件：说明部分 feed 存储后端采用延迟文件交付的时序特性，帮助调用方判断下游流程是否可以在 feed 写入后立即依赖文件存在，并据此调整等待或触发逻辑。
11. [批量输出文件命名占位符配置](通用技能领域/Family技能/未分类技能/微技能/批量输出文件命名占位符配置/SKILL.md)
   - 层级：微技能
   - 类型：feed_export
   - 适用条件：在生成多个输出文件时，通过在 feed URI 中使用 batch_time 或 batch_id 占位符来区分不同批次文件名，并可用 printf 风格格式化控制编号位数。适用于需要按批次拆分导出文件的抓取配置场景。
12. [本地文件系统 Feed 导出配置](通用技能领域/Family技能/未分类技能/一级技能/本地文件系统 Feed 导出配置/SKILL.md)
   - 层级：一级技能
   - 类型：feed_export
   - 适用条件：配置 Scrapy feed 导出到本地文件系统：使用 file URI 方案或绝对路径，也可传入 pathlib.Path 对象。适用于需要将抓取结果落盘到本机文件的场景。
13. [标准输出Feed导出](通用技能领域/Family技能/未分类技能/微技能/标准输出Feed导出/SKILL.md)
   - 层级：微技能
   - 类型：feed导出
   - 适用条件：将Scrapy抓取到的item通过stdout: URI方案直接写入进程标准输出，无需外部库。适用于需要即时查看抓取结果或通过管道传给下游进程的场景。
14. [自定义 Feed 导出器扩展](通用技能领域/Family技能/未分类技能/微技能/自定义 Feed 导出器扩展/SKILL.md)
   - 层级：微技能
   - 类型：导出格式扩展
   - 适用条件：通过 FEED_EXPORTERS 设置注册自定义导出器，以扩展 Scrapy Feed 导出支持的序列化格式；当内置导出格式无法满足输出需求时使用。
15. [配置 FTP Feed 存储](通用技能领域/Family技能/未分类技能/一级技能/配置 FTP Feed 存储/SKILL.md)
   - 层级：一级技能
   - 类型：feed_export
   - 适用条件：当需要将 Scrapy 抓取结果导出到 FTP 服务器时，使用 ftp:// URI 配置 feed 存储，并可按需切换主动/被动连接模式。
