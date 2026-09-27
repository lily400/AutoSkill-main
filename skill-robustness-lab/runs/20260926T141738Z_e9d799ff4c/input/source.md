# CSV 去重与汇总

本文是技能生成链路的开发测试样例，不属于正式实验数据。目标：从单个订单 CSV 生成去重明细和客户汇总，严格按以下先后顺序处理。

- R01 输入：只读取一个 UTF-8 编码、有表头、逗号分隔的 orders.csv。列名和顺序必须恰为 order_id,customer_id,updated_at,amount。order_id 和 customer_id 始终按大小写敏感字符串处理，保留前导零；输入记录按 CSV 数据记录顺序编号，从 1 开始（不计表头）。
- R02 规范化与缺失：先去掉每个字段首尾空白。空字符串就是缺失；字符串 NA、null 不作为缺失标记。order_id 或 updated_at 缺失时整批失败。customer_id 缺失时填充 UNKNOWN。amount 缺失时填充 0.00。
- R03 时间校验：updated_at 必须满足 YYYY-MM-DDTHH:MM:SSZ 或 YYYY-MM-DDTHH:MM:SS±HH:MM，日期和时区偏移必须有效，不接受无时区或小数秒。全部转换到 UTC 后比较。任意记录时间非法时，整批停止并报告记录序号和字段名。
- R04 金额校验：非空 amount 只接受非负十进制定点数，形式为一个或多个数字，可带小数点后 1 或 2 位数字；拒绝负数、指数、千位分隔符和非数字。用十进制精确算术处理，禁止用二进制浮点累计。任意非法值导致整批失败，报告记录序号和字段名。先校验全部输入记录，再去重；将来会被去掉的记录也不能跳过校验。
- R05 去重：只按规范化后的 order_id 分组，每组保留 UTC 更新时间最大的整条记录；时间相同时保留输入记录序号最大的整条记录。不能按 customer_id 去重，不能合并不同重复记录的字段。
- R06 汇总：只对保留下来的记录按 customer_id 分组。order_count 是该客户保留记录的数量，total_amount 是这些记录 amount 的精确十进制和，latest_updated_at 是这些记录的最大 UTC 时间；UNKNOWN 作为一个正常客户组参与汇总。禁止把已丢弃重复记录计入汇总。
- R07 明细输出：写 deduplicated.csv，表头与列序为 order_id,customer_id,updated_at,amount。按 order_id 的 Unicode 字符串码点顺序升序，不按数值排序。时间统一写成 YYYY-MM-DDTHH:MM:SSZ；金额固定两位小数。
- R08 汇总输出：写 summary.csv，表头与列序为 customer_id,order_count,total_amount,latest_updated_at。按 customer_id 的 Unicode 字符串码点顺序升序。order_count 写整数；total_amount 固定两位小数；时间使用 UTC 的 YYYY-MM-DDTHH:MM:SSZ。
- R09 文件与失败：两个输出都是 UTF-8 无 BOM、逗号分隔、LF 换行的 CSV，使用标准 CSV 引号转义。输出位于用户指定目录，不能覆盖输入或任何已存在的输出文件。表头错误、记录字段数不为 4 或任何校验失败时，报告错误且不生成任何结果文件；所有校验通过后才写出结果。原始输入内容始终不变。
- R10 空输入：只有正确表头而无数据记录是合法输入，生成两个只有各自表头的输出文件；完全空文件没有表头，必须报错且不生成结果文件。

开发示例输入：
```csv
order_id,customer_id,updated_at,amount
001,C2,2026-01-01T08:00:00+08:00,10.00
001,C1,2026-01-01T00:00:00Z,12.50
002,,2026-01-02T00:00:00Z,
003,C1,2026-01-03T00:00:00Z,2.25
```

预期 deduplicated.csv：
```csv
order_id,customer_id,updated_at,amount
001,C1,2026-01-01T00:00:00Z,12.50
002,UNKNOWN,2026-01-02T00:00:00Z,0.00
003,C1,2026-01-03T00:00:00Z,2.25
```

预期 summary.csv：
```csv
customer_id,order_count,total_amount,latest_updated_at
C1,2,14.75,2026-01-03T00:00:00Z
UNKNOWN,1,0.00,2026-01-02T00:00:00Z
```

完成检查：去重明细中 order_id 唯一；汇总 order_count 之和等于明细记录数；汇总 total_amount 之和等于明细金额之和；文件格式、排序和输入不变均符合以上规则。
