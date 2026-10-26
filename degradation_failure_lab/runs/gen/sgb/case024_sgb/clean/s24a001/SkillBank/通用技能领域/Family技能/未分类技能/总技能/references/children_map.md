# 未分类技能 子技能地图

- parent: `未分类技能/总技能/SKILL.md`

## 子技能列表

1. [Feed URI 动态参数注入](通用技能领域/Family技能/未分类技能/微技能/Feed URI 动态参数注入/SKILL.md)
   - 层级：微技能
   - 类型：feed_export
   - 适用条件：通过定义 uri_params 函数并配置 FEED_URI_PARAMS，将爬虫运行时属性（如 spider.name）动态注入到 feed 导出 URI 中，实现按爬虫或运行上下文区分的动态导出文件名。适用于多个爬虫共用同一导出命令但需区分输出文件，或需要在导出文件名中包含运行时属性的场景。
2. [Feed URI 参数生成器](通用技能领域/Family技能/未分类技能/微技能/Feed URI 参数生成器/SKILL.md)
   - 层级：微技能
   - 类型：feed_export
   - 适用条件：实现一个可调用函数，接收默认参数字典与 spider，返回新的参数字典，用于生成 feed 存储 URI 的动态参数（如 batch_id、batch_time、time）。适用于需要按批次或时间动态构造 feed 文件路径、配置 FEED_URI_PARAMS 的场景。
3. [Feed 压缩导出配置](通用技能领域/Family技能/未分类技能/微技能/Feed 压缩导出配置/SKILL.md)
   - 层级：微技能
   - 类型：feed_export
   - 适用条件：为 Scrapy feed 导出选择并配置压缩方式（gzip、lzma、bz2），通过 feed_options 传入对应压缩参数，以减小导出文件体积或满足传输要求。
4. [Feed 存储后端 URI 配置](通用技能领域/Family技能/未分类技能/二级技能/Feed 存储后端 URI 配置/SKILL.md)
   - 层级：二级技能
   - 类型：feed_export
   - 适用条件：通过 FEEDS 设置使用一个或多个 URI 定义 feed 存储位置，并按 URI scheme 选择本地文件系统、FTP、S3、GCS 或标准输出等存储后端。适用于需要将导出结果写入特定存储位置的场景。
5. [Feed 存储后端选择与依赖校验](通用技能领域/Family技能/未分类技能/一级技能/Feed 存储后端选择与依赖校验/SKILL.md)
   - 层级：一级技能
   - 类型：feed_export
   - 适用条件：根据目标输出位置为 Scrapy feed 选择内置存储后端（本地文件系统、FTP、S3、GCS、标准输出），并在使用前校验所需外部库是否已安装，给出可用后端与依赖校验结论。
6. [Feed 导出设置参考清单](通用技能领域/Family技能/未分类技能/一级技能/Feed 导出设置参考清单/SKILL.md)
   - 层级：一级技能
   - 类型：数据导出配置
   - 适用条件：提供 Scrapy feed 导出相关设置项的参考清单，用于查阅有哪些导出配置项，或在排查导出行为时对照设置项；仅作参考，不执行具体配置操作。
7. [Feed 导出配置回退解析](通用技能领域/Family技能/未分类技能/一级技能/Feed 导出配置回退解析/SKILL.md)
   - 层级：一级技能
   - 类型：feed_export_configuration
   - 适用条件：根据每个 feed 定义逐键解析导出配置，缺失键回退到对应全局设置（如 FEED_EXPORT_ENCODING、FEED_EXPORT_FIELDS、FEED_STORE_EMPTY、FEED_URI_PARAMS），确定最终生效的 feed 参数及回退来源。
8. [Feed 覆盖与追加策略选择](通用技能领域/Family技能/未分类技能/一级技能/Feed 覆盖与追加策略选择/SKILL.md)
   - 层级：一级技能
   - 类型：feed_export_configuration
   - 适用条件：根据目标存储后端（本地文件系统、FTP、S3、GCS、标准输出）确定 feed 的 overwrite 取值，并判断该后端是否支持追加写入。用于配置 feed 写入模式时。
9. [FTP Feed 存储配置](通用技能领域/Family技能/未分类技能/一级技能/FTP Feed 存储配置/SKILL.md)
   - 层级：一级技能
   - 类型：feed_export
   - 适用条件：配置 Scrapy feed 导出到 FTP 服务器，包括 ftp 方案 URI 构造与主动/被动连接模式选择。适用于需要将抓取结果直接写入 FTP 的场景。
10. [Scrapy GCS Feed 导出配置](通用技能领域/Family技能/未分类技能/一级技能/Scrapy GCS Feed 导出配置/SKILL.md)
   - 层级：一级技能
   - 类型：feed_export
   - 适用条件：配置 Scrapy feed 导出到 Google Cloud Storage：使用 gs:// URI 方案，并依赖 google-cloud-storage 库完成认证与写入。当需要把抓取结果写入 GCS 存储桶时使用。
11. [Scrapy 本地文件系统 Feed 导出配置](通用技能领域/Family技能/未分类技能/一级技能/Scrapy 本地文件系统 Feed 导出配置/SKILL.md)
   - 层级：一级技能
   - 类型：feed_export
   - 适用条件：配置 Scrapy feed 导出到本地文件系统，使用 file URI scheme、Unix 绝对路径或 pathlib.Path 对象指定存储目标。
12. [Scrapy 标准输出 Feed 导出](通用技能领域/Family技能/未分类技能/微技能/Scrapy 标准输出 Feed 导出/SKILL.md)
   - 层级：微技能
   - 类型：feed_export
   - 适用条件：将抓取到的 item 通过 stdout 存储后端直接写入 Scrapy 进程的标准输出，无需任何外部库。适用于需要即时查看导出结果或通过管道交给下游进程、且不需要持久化文件的场景。
13. [延迟文件投递存储后端识别](通用技能领域/Family技能/未分类技能/一级技能/延迟文件投递存储后端识别/SKILL.md)
   - 层级：一级技能
   - 类型：feed_export
   - 适用条件：在配置 Scrapy feed 导出时，识别哪些存储后端采用延迟文件投递语义，并据此选择合适的存储后端或排查导出结果未即时出现的问题。
14. [批量 Feed 输出文件命名占位符配置](通用技能领域/Family技能/未分类技能/微技能/批量 Feed 输出文件命名占位符配置/SKILL.md)
   - 层级：微技能
   - 类型：feed_export
   - 适用条件：在 Scrapy feed 导出会生成多个输出文件时，通过在 feed URI 中使用 batch_time 或 batch_id 占位符区分不同输出文件名，并可用 printf 风格格式化控制编号位数。
15. [设置 FEEDS 导出目标](通用技能领域/Family技能/未分类技能/微技能/设置 FEEDS 导出目标/SKILL.md)
   - 层级：微技能
   - 类型：数据导出配置
   - 适用条件：在 Scrapy 的 FEEDS 设置中声明导出目标，指定 URI 与序列化格式（及可选参数），作为 feed 导出的强制入口配置。适用于需要新增或修改导出目标时。
