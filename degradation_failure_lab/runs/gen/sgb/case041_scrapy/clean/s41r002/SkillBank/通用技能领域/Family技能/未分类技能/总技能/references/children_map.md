# 未分类技能 子技能地图

- parent: `未分类技能/总技能/SKILL.md`

## 子技能列表

1. [Offsite请求域名过滤](通用技能领域/Family技能/未分类技能/二级技能/Offsite请求域名过滤/SKILL.md)
   - 层级：二级技能
   - 类型：请求过滤
   - 适用条件：在请求被调度时，基于spider允许域名的正则判断请求是否属于站内；站外请求应被忽略，站内请求继续进入调度。用于控制爬虫只跟随允许域名范围内的链接。
2. [process_request 请求拦截与分流](通用技能领域/Family技能/未分类技能/微技能/process_request 请求拦截与分流/SKILL.md)
   - 层级：微技能
   - 类型：request_processing
   - 适用条件：实现下载器中间件的 process_request 钩子，在请求进入下载器前按规则改写、重调度、短路或丢弃请求。适用于需要在下载前修改请求或按条件重定向、过滤请求的场景。
3. [下载器中间件 process_exception 异常处理分派](通用技能领域/Family技能/未分类技能/微技能/下载器中间件 process_exception 异常处理分派/SKILL.md)
   - 层级：微技能
   - 类型：downloader_middleware
   - 适用条件：在下载器中间件的 process_exception 钩子中，按返回值类型分派下载处理器或 process_request 抛出的异常：返回 None 继续传递异常，返回 Response 启动 process_response 链，返回 Request 重新调度。用于实现异常恢复、重试或降级中间件。
4. [下载器中间件 process_response 返回值路由](通用技能领域/Family技能/未分类技能/微技能/下载器中间件 process_response 返回值路由/SKILL.md)
   - 层级：微技能
   - 类型：downloader_middleware
   - 适用条件：在下载器中间件的 process_response 钩子中，根据返回值类型决定后续链路走向：返回 Response 继续交给下一个中间件处理，返回 Request 中止链路并重新调度下载，抛出 IgnoreRequest 触发请求的 errback。用于编写或调试响应处理中间件时。
5. [下载器中间件激活与排序配置](通用技能领域/Family技能/未分类技能/二级技能/下载器中间件激活与排序配置/SKILL.md)
   - 层级：二级技能
   - 类型：middleware_configuration
   - 适用条件：通过 DOWNLOADER_MIDDLEWARES 设置注册自定义下载器中间件并指定执行顺序，可用 None 禁用内置中间件。适用于需要全局改变请求/响应处理链的场景。
6. [允许域名正则构建](通用技能领域/Family技能/未分类技能/微技能/允许域名正则构建/SKILL.md)
   - 层级：微技能
   - 类型：域名规则初始化
   - 适用条件：在 spider_opened 阶段根据 spider 配置构建用于匹配允许域名的 host_regex 正则对象，供后续请求过滤逻辑复用。
7. [请求hostname安全判定](通用技能领域/Family技能/未分类技能/微技能/请求hostname安全判定/SKILL.md)
   - 层级：微技能
   - 类型：请求判定
   - 适用条件：对单个请求解析其URL的hostname，并用已初始化的允许域名正则判断该请求是否应被跟随；hostname为空（如javascript链接等错误URL）时按不匹配处理。用于单请求的站内/站外判定。
