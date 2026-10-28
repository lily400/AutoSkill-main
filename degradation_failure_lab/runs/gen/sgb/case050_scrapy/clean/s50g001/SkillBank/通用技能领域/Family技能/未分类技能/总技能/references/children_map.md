# 未分类技能 子技能地图

- parent: `未分类技能/总技能/SKILL.md`

## 子技能列表

1. [Scrapy 可调用对象导入路径配置](通用技能领域/Family技能/未分类技能/一级技能/Scrapy 可调用对象导入路径配置/SKILL.md)
   - 层级：一级技能
   - 类型：settings_configuration
   - 适用条件：说明在 Scrapy 设置中引用类或函数等可调用对象时，可用导入路径字符串或对象本身两种方式指定；用于配置需要延迟导入或按路径解析的组件设置。
2. [Scrapy 设置分层配置](通用技能领域/Family技能/未分类技能/二级技能/Scrapy 设置分层配置/SKILL.md)
   - 层级：二级技能
   - 类型：配置管理
   - 适用条件：按命令行、Spider、项目 settings.py、插件、命令默认、全局默认的优先级顺序放置并覆盖 Scrapy 设置项，用于需要定制爬虫行为时。
3. [Spider 内动态设置覆盖](通用技能领域/Family技能/未分类技能/微技能/Spider 内动态设置覆盖/SKILL.md)
   - 层级：微技能
   - 类型：配置管理
   - 适用条件：在 Spider 的 from_crawler 中通过 settings.set 以 spider 优先级动态写入设置，用于按传入参数定制单个 Spider 的行为；当某个 Spider 需要根据参数调整设置时使用。
4. [命令行覆盖 Scrapy 设置](通用技能领域/Family技能/未分类技能/微技能/命令行覆盖 Scrapy 设置/SKILL.md)
   - 层级：微技能
   - 类型：配置管理
   - 适用条件：使用 -s/--set 命令行选项在运行时显式覆盖一个或多个 Scrapy 设置，优先级最高；适用于需要临时覆盖设置而不修改项目文件、或调试时快速切换设置值的场景。
5. [预爬虫与反应器设置作用域约束](通用技能领域/Family技能/未分类技能/二级技能/预爬虫与反应器设置作用域约束/SKILL.md)
   - 层级：二级技能
   - 类型：配置约束
   - 适用条件：约束预爬虫设置不可按 Spider 定义、反应器设置在同一进程多 Spider 运行时不应按 Spider 取不同值；用于配置多 Spider 同进程运行或考虑在 Spider 中定义受限设置时，避免因按 Spider 覆盖受限设置导致运行异常。
6. [预爬虫阶段设置配置](通用技能领域/Family技能/未分类技能/一级技能/预爬虫阶段设置配置/SKILL.md)
   - 层级：一级技能
   - 类型：settings_configuration
   - 适用条件：在安装或启动 reactor 之前，配置 Scrapy 的预爬虫阶段特殊设置（ASYNCIO_EVENT_LOOP、TWISTED_REACTOR、DNS_RESOLVER 及相关 DNS 设置、REACTOR_THREADPOOL_MAXSIZE），以确保爬虫启动时使用正确的异步事件循环、DNS 解析器和线程池容量。
