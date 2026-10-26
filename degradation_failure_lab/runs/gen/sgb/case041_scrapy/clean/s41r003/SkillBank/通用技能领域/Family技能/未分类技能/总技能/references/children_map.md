# 未分类技能 子技能地图

- parent: `未分类技能/总技能/SKILL.md`

## 子技能列表

1. [FormRequest 表单提交构造](通用技能领域/Family技能/未分类技能/微技能/FormRequest 表单提交构造/SKILL.md)
   - 层级：微技能
   - 类型：请求构造
   - 适用条件：使用 FormRequest 构造带 formdata 的 POST 请求，并绑定 callback 处理响应，用于向表单 action 端点提交结构化字段数据。
2. [FormRequest.from_response 登录模拟](通用技能领域/Family技能/未分类技能/微技能/FormRequest.from_response 登录模拟/SKILL.md)
   - 层级：微技能
   - 类型：登录模拟
   - 适用条件：用 FormRequest.from_response() 基于已有响应中的表单自动预填隐藏字段（如会话数据、认证令牌），仅覆盖用户名密码等少数字段以模拟登录提交。适用于登录页含隐藏令牌字段、需要保留预填值只覆盖关键字段的场景。
3. [FormRequest.from_response 表单预填充与提交](通用技能领域/Family技能/未分类技能/微技能/FormRequest.from_response 表单预填充与提交/SKILL.md)
   - 层级：微技能
   - 类型：表单提交
   - 适用条件：从响应中的 HTML 表单预填充字段并构造 FormRequest，支持按 name/id/xpath/css/number 选择表单、覆盖字段、模拟点击控件或禁用点击。用于需要基于已有页面表单发起 POST 提交的爬取场景。
4. [process_spider_input 返回值契约](通用技能领域/Family技能/未分类技能/微技能/process_spider_input 返回值契约/SKILL.md)
   - 层级：微技能
   - 类型：middleware_implementation
   - 适用条件：确保自定义 Spider 中间件的 process_spider_input 钩子符合 Scrapy 框架契约：对每个进入 Spider 的响应调用，必须返回 None 或抛出异常；返回 None 时处理链继续执行后续中间件直至交给 Spider。用于实现该钩子时校验返回值行为。
5. [Request errback 异常捕获处理](通用技能领域/Family技能/未分类技能/微技能/Request errback 异常捕获处理/SKILL.md)
   - 层级：微技能
   - 类型：异常处理
   - 适用条件：为 Scrapy Request 配置 errback 回调以捕获请求处理过程中的异常，并在 errback 中访问 meta 附加数据进行失败分支处理。适用于需要逐请求容错与失败分支处理的爬取流程。
6. [Response 选择器快捷提取](通用技能领域/Family技能/未分类技能/微技能/Response 选择器快捷提取/SKILL.md)
   - 层级：微技能
   - 类型：response_parsing
   - 适用条件：在已获得的 TextResponse 对象上直接调用 css/xpath/jmespath 快捷方法执行选择器查询，返回匹配的 SelectorList（或空结果）供后续解析使用。适用于已持有响应、需要按 CSS/XPath/JMESPath 语法定位或提取页面元素的场景。
7. [Scrapy Request 回调与错误回调路由配置](通用技能领域/Family技能/未分类技能/微技能/Scrapy Request 回调与错误回调路由配置/SKILL.md)
   - 层级：微技能
   - 类型：请求配置
   - 适用条件：为 Scrapy Request 指定 callback 或 errback，并处理 None/NO_CALLBACK 默认行为，使响应或异常被路由到正确的处理函数。适用于需要自定义响应处理或捕获请求处理异常的场景。
8. [Scrapy Request 复制与替换](通用技能领域/Family技能/未分类技能/微技能/Scrapy Request 复制与替换/SKILL.md)
   - 层级：微技能
   - 类型：请求对象操作
   - 适用条件：使用 Request.copy() 或 Request.replace() 基于现有请求派生新请求，仅覆盖指定字段，并默认浅拷贝 cb_kwargs 与 meta。适用于需要在保留原请求上下文的前提下修改 URL、回调、优先级等字段时。
9. [Scrapy Request.meta 特殊键配置参考](通用技能领域/Family技能/未分类技能/一级技能/Scrapy Request.meta 特殊键配置参考/SKILL.md)
   - 层级：一级技能
   - 类型：request_configuration
   - 适用条件：列举并说明 Scrapy Request.meta 中可用的特殊键（如 bindaddress、download_timeout、max_retry_times、proxy、dont_redirect 等），用于在构造请求时按需设置下载行为。适用于需要查阅或选择 meta 键来调整单个请求行为的场景。
10. [Scrapy 响应类型选择与解析](通用技能领域/Family技能/未分类技能/一级技能/Scrapy 响应类型选择与解析/SKILL.md)
   - 层级：一级技能
   - 类型：response_handling
   - 适用条件：根据响应的 Content-Type 与内容特征选择合适的 Scrapy Response 子类（TextResponse/HtmlResponse/XmlResponse/JsonResponse），并调用其解析方法（json、urljoin 等）提取数据或构造绝对 URL。适用于处理已获取的响应对象，而非发起请求。
11. [Scrapy 响应编码解析优先级](通用技能领域/Family技能/未分类技能/一级技能/Scrapy 响应编码解析优先级/SKILL.md)
   - 层级：一级技能
   - 类型：response_handling
   - 适用条件：按固定优先级解析 Scrapy 响应文本的编码来源：先取 __init__ 传入的 encoding，再取 Content-Type 头声明，再取响应体声明（HtmlResponse/XmlResponse 支持），最后回退到从响应体推断。用于需要确定响应文本编码或排查乱码时。
12. [Scrapy 回调附加数据传递](通用技能领域/Family技能/未分类技能/微技能/Scrapy 回调附加数据传递/SKILL.md)
   - 层级：微技能
   - 类型：请求上下文传递
   - 适用条件：通过 Request 的 cb_kwargs 向回调函数传递额外上下文数据（如 main_url、foo），使回调能访问请求构造阶段产生的数据。适用于回调需要复用请求阶段上下文信息的场景。
13. [Scrapy 自定义请求指纹器配置](通用技能领域/Family技能/未分类技能/二级技能/Scrapy 自定义请求指纹器配置/SKILL.md)
   - 层级：二级技能
   - 类型：请求去重
   - 适用条件：当默认请求去重指纹不满足需求时，通过 REQUEST_FINGERPRINTER_CLASS 选择或实现自定义请求指纹器，以控制请求去重行为。
14. [Scrapy 请求 errback 失败处理](通用技能领域/Family技能/未分类技能/微技能/Scrapy 请求 errback 失败处理/SKILL.md)
   - 层级：微技能
   - 类型：异常处理
   - 适用条件：为 Scrapy 请求设置 errback 回调，在请求处理失败时接收 Failure 对象并执行降级、重试或记录；适用于需要容错处理的抓取请求。
15. [Scrapy 请求去重过滤控制](通用技能领域/Family技能/未分类技能/微技能/Scrapy 请求去重过滤控制/SKILL.md)
   - 层级：微技能
   - 类型：请求调度控制
   - 适用条件：通过设置 Request 的 dont_filter 属性，控制支持过滤的组件是否跳过对该请求的去重过滤。适用于需要重复抓取同一 URL，或确保起始 URL 不被过滤的场景。
16. [Scrapy 请求构造与回调数据传递](通用技能领域/Family技能/未分类技能/二级技能/Scrapy 请求构造与回调数据传递/SKILL.md)
   - 层级：二级技能
   - 类型：请求构造
   - 适用条件：构造 scrapy.Request 时正确设置 url、callback、errback、cb_kwargs、cookies、priority、dont_filter 等参数，并把附加数据通过 cb_kwargs 传给回调。适用于需要发起请求并向下游回调传递上下文数据的场景。
17. [Scrapy 请求错误回调处理](通用技能领域/Family技能/未分类技能/微技能/Scrapy 请求错误回调处理/SKILL.md)
   - 层级：微技能
   - 类型：请求异常处理
   - 适用条件：为 Request 配置 errback 回调，捕获并分类处理请求处理过程中的异常（连接超时、DNS 错误、HTTP 错误等），并记录或转交错误。适用于需要稳健处理下载失败的爬虫。
18. [Spider 中间件异常处理钩子实现](通用技能领域/Family技能/未分类技能/微技能/Spider 中间件异常处理钩子实现/SKILL.md)
   - 层级：微技能
   - 类型：spider_middleware
   - 适用条件：实现 process_spider_exception 钩子，在 Spider 或上游 process_spider_output 抛异常时，决定返回 None 让异常继续传播，或返回 Request/item 可迭代对象接管输出管道。
19. [Spider中间件异步输出钩子实现](通用技能领域/Family技能/未分类技能/微技能/Spider中间件异步输出钩子实现/SKILL.md)
   - 层级：微技能
   - 类型：spider_middleware
   - 适用条件：实现 process_spider_output_async 异步生成器方法，在 Spider 输出结果为异步可迭代对象时替代同步 process_spider_output 被调用，用于异步爬虫管道中处理异步结果流。
20. [Spider输出处理钩子实现](通用技能领域/Family技能/未分类技能/微技能/Spider输出处理钩子实现/SKILL.md)
   - 层级：微技能
   - 类型：spider_middleware
   - 适用条件：实现 process_spider_output(response, result) 钩子，对 Spider 处理响应后返回的 Request/item 可迭代结果进行拦截与改写，并返回新的可迭代对象。适用于需要在爬虫输出进入后续中间件前统一过滤或转换结果的场景。
21. [Spider输出逐项过滤与改写](通用技能领域/Family技能/未分类技能/微技能/Spider输出逐项过滤与改写/SKILL.md)
   - 层级：微技能
   - 类型：spider_output_processing
   - 适用条件：对spider输出或start seeds中的单个item/request进行逐项处理：保留原样、改写为不同对象，或返回None丢弃，从而实现输出过滤与转换。
22. [WeakKeyDictionary 指纹缓存](通用技能领域/Family技能/未分类技能/微技能/WeakKeyDictionary 指纹缓存/SKILL.md)
   - 层级：微技能
   - 类型：指纹缓存
   - 适用条件：在自行实现请求指纹算法（未使用 scrapy.utils.request.fingerprint()）时，使用 WeakKeyDictionary 缓存指纹，确保每个请求只计算一次，同时避免请求对象因缓存引用而无法释放。
23. [下载器中间件激活与排序配置](通用技能领域/Family技能/未分类技能/二级技能/下载器中间件激活与排序配置/SKILL.md)
   - 层级：二级技能
   - 类型：middleware_configuration
   - 适用条件：当默认去重逻辑无法满足需求时，通过配置 REQUEST_FINGERPRINTER_CLASS 指定请求指纹器类，或编写自定义请求指纹器类来控制 Scrapy 的请求去重判断逻辑。适用于默认指纹不满足去重需求、需要按自定义字段组合判定请求唯一性时。
24. [从 cURL 命令构造 Scrapy Request](通用技能领域/Family技能/未分类技能/微技能/从 cURL 命令构造 Scrapy Request/SKILL.md)
   - 层级：微技能
   - 类型：请求构造
   - 适用条件：使用 Request.from_curl 从 cURL 命令字符串创建 Scrapy Request，自动填充 HTTP 方法、URL、头、cookie 和 body；当已有 cURL 命令（如从浏览器复制）需要转为 Scrapy 请求时使用。
25. [使用 errback 捕获请求处理异常](通用技能领域/Family技能/未分类技能/微技能/使用 errback 捕获请求处理异常/SKILL.md)
   - 层级：微技能
   - 类型：异常处理
   - 适用条件：为 Request 指定 errback 回调，在下载或处理失败时接收 Failure 对象并访问其中的附加数据，实现自定义异常处理。当请求可能失败且需要自定义错误处理，或需要在失败时访问请求附加数据时使用。
26. [启用并排序 Spider 中间件](通用技能领域/Family技能/未分类技能/二级技能/启用并排序 Spider 中间件/SKILL.md)
   - 层级：二级技能
   - 类型：middleware_configuration
   - 适用条件：通过 SPIDER_MIDDLEWARES 设置注册自定义 Spider 中间件并指定执行顺序，可用 None 禁用内置中间件。适用于需要插入或替换 Spider 处理链中某个中间件时。
27. [响应批量链接跟进生成器](通用技能领域/Family技能/未分类技能/微技能/响应批量链接跟进生成器/SKILL.md)
   - 层级：微技能
   - 类型：crawl_navigation
   - 适用条件：使用 response.follow_all 通过 urls、css 或 xpath 参数批量生成跟进 Request 的生成器，自动跳过无法获取链接的选择器。适用于需要遍历页面所有链接的场景。
28. [响应链接跟进生成请求](通用技能领域/Family技能/未分类技能/微技能/响应链接跟进生成请求/SKILL.md)
   - 层级：微技能
   - 类型：crawl_navigation
   - 适用条件：使用 response.follow 从相对 URL、Link、Selector 或属性 Selector 构造并返回单个 Request 以跟进链接；适用于解析阶段需要跳转到下一页面时。
29. [回调参数透传至 errback](通用技能领域/Family技能/未分类技能/微技能/回调参数透传至 errback/SKILL.md)
   - 层级：微技能
   - 类型：上下文传递
   - 适用条件：通过 cb_kwargs 向回调传递上下文参数，并在 errback 中经 Failure.request.cb_kwargs 取回，用于失败时仍能基于原始上下文处理。
30. [编写自定义 Spider 中间件钩子方法](通用技能领域/Family技能/未分类技能/二级技能/编写自定义 Spider 中间件钩子方法/SKILL.md)
   - 层级：二级技能
   - 类型：middleware_implementation
   - 适用条件：实现 SpiderMiddleware 子类的钩子方法（process_start、process_start_requests、process_spider_input），用于定制 Spider 启动输出、进入 Spider 的响应以及 Spider 产出的请求与 item 的处理逻辑。
31. [自定义 Request 指纹器实现](通用技能领域/Family技能/未分类技能/二级技能/自定义 Request 指纹器实现/SKILL.md)
   - 层级：二级技能
   - 类型：请求去重
   - 适用条件：通过 REQUEST_FINGERPRINTER_CLASS 配置或编写自定义请求指纹器，为请求生成去重指纹，并遵守指纹限制（如不得依赖响应数据）。用于默认指纹不满足去重需求的爬取场景。
32. [自定义Spider中间件基类实现](通用技能领域/Family技能/未分类技能/微技能/自定义Spider中间件基类实现/SKILL.md)
   - 层级：微技能
   - 类型：spider_middleware_development
   - 适用条件：使用BaseSpiderMiddleware基类简化异步process_spider_output()和process_start()方法的实现，通过get_processed_item/get_processed_request逐项处理spider输出，减少样板代码。
33. [自定义请求指纹器](通用技能领域/Family技能/未分类技能/二级技能/自定义请求指纹器/SKILL.md)
   - 层级：二级技能
   - 类型：请求去重
   - 适用条件：当默认请求指纹不满足去重需求时，实现自定义 REQUEST_FINGERPRINTER_CLASS，按业务比较规则规范化 URL（大小写、片段、查询参数、请求头等）生成请求唯一标识，从而控制去重行为。适用于需要定制去重比较规则的 Scrapy 爬虫。
34. [自定义请求指纹器实现](通用技能领域/Family技能/未分类技能/微技能/自定义请求指纹器实现/SKILL.md)
   - 层级：微技能
   - 类型：请求去重
   - 适用条件：实现一个 RequestFingerprinter 类，通过 fingerprint(request) 方法为 Scrapy 请求生成去重指纹，可优先读取 request.meta 中的预置指纹；适用于需要覆盖默认请求指纹算法或自定义去重/缓存键逻辑的场景。
35. [自定义请求指纹器实现](通用技能领域/Family技能/未分类技能/二级技能/自定义请求指纹器实现-2/SKILL.md)
   - 层级：二级技能
   - 类型：请求去重配置
   - 适用条件：实现并配置自定义 RequestFingerprinter，用于按需纳入特定请求头或 URL 片段计算请求指纹，或完全自定义指纹逻辑，从而改变 Scrapy 默认去重指纹行为。适用于需要定制请求去重指纹的场景。
36. [请求指纹格式约束校验](通用技能领域/Family技能/未分类技能/二级技能/请求指纹格式约束校验/SKILL.md)
   - 层级：二级技能
   - 类型：指纹合规
   - 适用条件：在把请求指纹交给依赖指纹的内置组件（如 FilesystemCacheStorage）之前，校验指纹满足该组件要求的格式限制（至少 1 字节长），避免缓存或去重组件报错。
37. [请求指纹规范化计算](通用技能领域/Family技能/未分类技能/微技能/请求指纹规范化计算/SKILL.md)
   - 层级：微技能
   - 类型：请求去重
   - 适用条件：在自定义 RequestFingerprinter 的 fingerprint() 方法内复用标准指纹逻辑：对 request.url 做 canonicalize_url 规范化，结合 method 与 body 生成 SHA1 哈希，从而忽略参数顺序、会话 cookie 等随机成分，得到唯一标识请求资源的指纹。
38. [请求错误回调处理（errback）](通用技能领域/Family技能/未分类技能/微技能/请求错误回调处理（errback）/SKILL.md)
   - 层级：微技能
   - 类型：错误处理
   - 适用条件：为 Scrapy 请求配置 errback，并按失败类型（HttpError、DNSLookupError、TimeoutError/TCPTimedOutError）分支记录与处理异常。适用于需要区分不同下载失败并做针对性处理的爬虫。
39. [通过 cb_kwargs 向回调传递附加数据](通用技能领域/Family技能/未分类技能/微技能/通过 cb_kwargs 向回调传递附加数据/SKILL.md)
   - 层级：微技能
   - 类型：请求构造
   - 适用条件：在构造 scrapy.Request 时使用 cb_kwargs 将上下文数据传入后续回调函数，并在回调中读取这些参数，实现跨请求的状态传递。适用于需要在第二个回调中复用第一个回调的上下文数据，或回调函数需要额外参数而非仅 response 的场景。
