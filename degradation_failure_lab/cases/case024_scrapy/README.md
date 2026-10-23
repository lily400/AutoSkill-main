# Scrapy024 手动生成入口

源文位于 data/raw_sources/scrapy/5a8bd61d8191e34fa1bbbffbff7f70db1d2a027d/feed-exports.md，与冻结审计源逐字节相同。仅为SGB task-curated材料，不是已验证完整的最新手册。

从主工程 degradation_failure_lab 目录运行：

```powershell
python scripts/lab.py plan --case case024_scrapy --condition clean --repeat 1
python scripts/lab.py run --case case024_scrapy --condition clean --repeat 1 --run-id s24m001
```

plan不调用模型；run真实调用已配置DeepSeek，依赖当前进程DEEPSEEK_API_KEY，不是GPT下游Agent。已有run ID不得覆盖；再次排查必须使用新ID并保留旧记录。输出在 runs/case024_scrapy/clean/s24m001/，原版canonical包在其SkillBank/Users/docskill/。

沿用原生成配置，pipeline_overrides为空；未调整domain、taxonomy、提示或模型。独立手动运行不能自动归入原三阶段隔离校准成绩，不会自动启动六次Agent。此前中断记录保留在审计目录，未覆盖。
