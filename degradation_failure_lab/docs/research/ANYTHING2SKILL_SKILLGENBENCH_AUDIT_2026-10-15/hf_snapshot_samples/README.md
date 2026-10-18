---
pretty_name: SkillGenBench
license: cc-by-4.0
language:
- en
task_categories:
- text-generation
tags:
- skill-generation
- agent-skills
- benchmark
- procedural-knowledge
- llm-agents
size_categories:
- 100<n<1K
configs:
- config_name: tasks
  default: true
  data_files:
  - split: test
    path: data/task_manifest.csv
---

# SkillGenBench

SkillGenBench is a benchmark for evaluating LLM skill generation from explicit repository- and document-grounded corpora. Each benchmark instance exposes visible generation materials and an instance-specific evaluation bundle. The official v1 task set contains 187 enabled tasks across three source types: 123 Code Repo tasks, 28 Code Doc tasks, and 36 Domain Knowledge Doc tasks.

## Repository Layout

- `data/task_manifest.csv`: the Hugging Face-loadable task index. Each row is one official enabled benchmark task and points to the corresponding source and evaluation paths.
- `data_source/`: visible corpus bundles used by skill-generation methods.
- `skill_evaluation/`: task instructions, context, references, and verifier files used to evaluate generated skills.

## Loading the Manifest

```python
from datasets import load_dataset

tasks = load_dataset("santasoda/SkillGenBench", "tasks", split="test")
print(tasks[0])
```

The manifest is the tabular entry point used by the Hugging Face viewer and automatic Croissant generation. The actual benchmark materials are stored at the paths listed in `data_source_path` and `skill_evaluation_path`.

## Evaluation Protocol

Skill-generation methods should read only the visible corpus materials under `data_source/`. Generated skills are evaluated with the corresponding task bundle under `skill_evaluation/`. The primary paper metric is pass@3 with an instance-specific verifier under the unified SkillGenBench evaluation harness.