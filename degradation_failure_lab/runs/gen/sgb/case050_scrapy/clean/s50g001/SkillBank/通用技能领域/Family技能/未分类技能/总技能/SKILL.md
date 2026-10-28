---
id: "2fcf2c8c-ee2d-5471-a738-db6f6386065f"
name: "未分类技能"
description: "未分类技能 的总导航技能：汇总适用场景、总流程、子技能地图与选用规则。"
version: "0.1.0"
tags:
  - "未分类技能"
  - "总导航"
  - "子技能地图"
  - "kind:parent"
  - "profile:scrapy::未分类技能"
triggers:
  - "未分类技能"
  - "未分类技能 总导航"
  - "未分类技能 子技能地图"
---

# 未分类技能

未分类技能 的总导航技能：汇总适用场景、总流程、子技能地图与选用规则。

## Prompt

## 适用场景
- 当当前问题明确属于或需要路由到 未分类技能 时，先使用本总技能决定子技能选择顺序。
- 本技能用于导航与组合，不替代子技能中的具体执行 SOP。

## 不适用/风险边界
- 不要把本技能当作具体干预脚本；真正执行时必须继续调用对应子技能。
- 如存在明显高风险或危机信号，应优先调用风险/危机类子技能。

## 总流程
1. 先判断当前问题是否适合进入该家族或领域的处理路径。
2. 再根据任务类型、阶段和风险边界选择最合适的子技能。
3. 调用对应子技能执行具体步骤、规则和输出格式。
4. 最后输出所选子技能、选择理由、执行顺序与风险提示。

## 子技能目录（一级技能目录）
- Scrapy 可调用对象导入路径配置 ｜ 类型：settings_configuration ｜ 适用条件：说明在 Scrapy 设置中引用类或函数等可调用对象时，可用导入路径字符串或对象本身两种方式指定；用于配置需要延迟导入或按路径解析的组件设置。
- 预爬虫阶段设置配置 ｜ 类型：settings_configuration ｜ 适用条件：在安装或启动 reactor 之前，配置 Scrapy 的预爬虫阶段特殊设置（ASYNCIO_EVENT_LOOP、TWISTED_REACTOR、DNS_RESOLVER 及相关 DNS 设置、REACTOR_THREADPOOL_MAXSIZE），以确保爬虫启动时使用正确的异步事件循环、DNS 解析器和线程池容量。

## 选用规则（一级技能目录）
- 当问题命中“设置项需要引用类或函数对象、需要以字符串导入路径延迟加载组件、scrapy、settings”这类线索时，优先选择 Scrapy 可调用对象导入路径配置。
- 当问题命中“需要自定义异步事件循环或 Twisted reactor、需要调整 DNS 解析器或 DNS 缓存相关参数、需要设置 reactor 线程池最大容量、scrapy”这类线索时，优先选择 预爬虫阶段设置配置。

## 输出格式
- family_route:
  - family: 未分类技能
  - selected_children: [子技能名称列表]
  - rationale: 说明为什么选择这些子技能
  - cautions: 风险边界与切换条件

## Files

- `references/children_manifest.json`
- `references/children_map.md`

## Triggers

- 未分类技能
- 未分类技能 总导航
- 未分类技能 子技能地图
