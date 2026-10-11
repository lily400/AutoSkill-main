---
pretty_name: SkillGym
license: other
language:
- en
source_datasets:
- original
tags:
- ai-agents
- benchmark
- skills
- task-generation
- agent-evaluation
- long-horizon
- tool-use
- verifier
- text
---

<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)"
          srcset="https://raw.githubusercontent.com/ECNU-ICALK/SkillGym/main/assets/brand-dark.png">
  <source media="(prefers-color-scheme: light)"
          srcset="https://raw.githubusercontent.com/ECNU-ICALK/SkillGym/main/assets/brand-light.png">
  <img
    src="https://raw.githubusercontent.com/ECNU-ICALK/SkillGym/main/assets/brand-light.png"
    alt="SkillGym"
    width="360">
</picture>

<h2>SkillGym Dataset</h2>

<p>
  <strong>Human-written skills, executable environments, and verified long-horizon agent trajectories</strong>
</p>

<p>
  <strong>English</strong> ·
  <a href="https://huggingface.co/datasets/ecnu-icalk/SkillGym/blob/main/README_zh-CN.md">简体中文</a>
</p>

<p>
  <a href="https://github.com/ECNU-ICALK/SkillGym">GitHub</a> ·
  <a href="https://huggingface.co/ecnu-icalk/SkillGym-Agent">SkillGym-Agent</a> ·
  <a href="https://github.com/ECNU-ICALK/SkillGym/blob/main/assets/Internalizing_Large_Scale_Human_Written_Skills_into_LLMs_for_Real_World_Problem_Solving.pdf">Paper</a>
</p>

</div>

## Dataset Summary

**SkillGym** is the data release accompanying the SkillGym framework. It connects human-written procedural knowledge to executable task environments, code-based outcome verifiers, paired with-skill / without-skill executions, and long-horizon agent trajectories.

The dataset is intended to support research on skill-grounded task construction, agent training, verifier-based evaluation, procedural transfer, and outcome-based learning.

| Statistic | Value |
| --- | ---: |
| **Accepted environments** | **2,756** |
| **Paired task variants** | **5,512** |
| **Skill-Dep. / Verifier-Passed** | **1,081 / 1,675** |
| **Successful trajectories** | **8,364** |
| **Sampled trials** | **48,152** |
| **Overall sampled-trial success rate** | **17.4%** |
| **Deduplicated task coverage** | **2,302 unique tasks** |
| **Taxonomy** | **12 major / 63 sub-categories** |

Successful trajectories cover 62 of the 63 sub-categories represented by accepted environments.

## Released Artifacts

| Artifact | Contents | Use it for |
| --- | --- | --- |
| [`Tasks.tar.zst`](https://huggingface.co/datasets/ecnu-icalk/SkillGym/resolve/main/Tasks.tar.zst?download=true) | Published skill-derived task environments, paired variants, and verifiers | Re-running or studying executable tasks |
| [`skill_library.tar.zst`](https://huggingface.co/datasets/ecnu-icalk/SkillGym/resolve/main/skill_library.tar.zst?download=true) | Human-written skills and supporting assets | Skill analysis or new task construction |
| [`task_templates.tar.zst`](https://huggingface.co/datasets/ecnu-icalk/SkillGym/resolve/main/task_templates.tar.zst?download=true) | Reusable seed-task templates and fixtures | Extending the task-construction pipeline |
| [`Trajectories/`](https://huggingface.co/datasets/ecnu-icalk/SkillGym/tree/main/Trajectories) | Eight trajectory collections organized by result type, harness, and teacher model | SFT, trajectory analysis, and procedural-learning research |

### Release Snapshot

The large-artifact dataset snapshot is associated with GitHub commit [`6ebabba`](https://github.com/ECNU-ICALK/SkillGym/commit/6ebabba).

The GitHub codebase, dataset repository, and model repository are versioned independently. For exact reproduction, record the revision used from each repository.

## Quick Start

### Download Trajectory Collections

```bash
python -m pip install -U huggingface_hub datasets

hf download ecnu-icalk/SkillGym \
  --include "Trajectories/*.jsonl" \
  --repo-type dataset \
  --local-dir .hf/skillgym
```

### Stream One Collection with 🤗 Datasets

```python
from datasets import load_dataset

records = load_dataset(
    "json",
    data_files={
        "train": (
            "hf://datasets/ecnu-icalk/SkillGym/"
            "Trajectories/"
            "skill_dependent_claude_code_deepseek_v4_pro.jsonl"
        )
    },
    split="train",
    streaming=True,
)

example = next(iter(records))
print(example["session_id"])
```

### Download Task-Construction Artifacts

```bash
hf download ecnu-icalk/SkillGym \
  Tasks.tar.zst skill_library.tar.zst task_templates.tar.zst \
  --repo-type dataset \
  --local-dir .hf/skillgym
```

For building new environments, use the [SkillGym Task Builder](https://github.com/ECNU-ICALK/SkillGym/tree/main/task_builder).

## Dataset Organization

```text
SkillGym/
├── Tasks.tar.zst
├── skill_library.tar.zst
├── task_templates.tar.zst
└── Trajectories/
    ├── skill_dependent_*.jsonl
    └── verifier_passed_*.jsonl
```

The task archives contain the source skill/task relationship, task instructions, environment configuration, task-specific verification logic, and paired execution variants used during construction and validation.

Trajectory collections preserve agent interaction traces and verification outcomes for successful sampled executions.

## Terminology

| Context | Skill available | Skill removed |
| --- | --- | --- |
| **Paper / benchmark tables** | `w/ Skills` | `w/o Skills` |
| **Released dataset variants** | `withskill` | `withoutskill` |
| **Task Builder internals** | `with_skill` | `no_skill` |

These names refer to the same paired evaluation concept; the differences reflect presentation, released-storage, and implementation conventions.

## Task Labels and Paired Variants

SkillGym distinguishes **task-construction labels** from **trajectory-level outcomes**.

### Skill-Dep.

A task is labeled **Skill-Dep.** when, under the reference construction configuration:

1. the environment and verifier are valid;
2. the paired **with-skill** execution succeeds; and
3. the paired **without-skill** execution produces a valid reward failure.

### Verifier-Passed

A **Verifier-Passed** task has a valid executable environment and outcome verifier but does not satisfy the stricter contrastive Skill-Dep. criterion under the reference configuration.

These labels characterize accepted environments at construction time. They do **not** guarantee that every later model or harness will succeed or fail in the same way.

## Trajectory Data

Successful trajectories retain the interaction sequence that led to a verifier-confirmed outcome. Depending on the source harness, records may include:

- task and session identifiers;
- task prompt and skill metadata;
- environment/runtime metadata;
- actions and tool calls;
- observations and tool outputs;
- final outputs or artifacts;
- verifier results and execution logs;
- available diagnostic fields.

### Schema Note

The eight trajectory files preserve source-specific trace structures. Some nested fields differ across harness/model collections, so the release should **not** be assumed to have one perfectly uniform nested JSON schema across every file.

For the most robust loading behavior:

- load one trajectory collection at a time; or
- explicitly normalize compatible files before concatenating them.

Using an explicit `data_files` path, as in the streaming example above, is preferable to treating every trajectory JSONL file as a single homogeneous split.

## Trajectory Statistics

| Statistic | Value |
| --- | ---: |
| Successful trajectories from Skill-Dep. tasks | **3,722** |
| Successful trajectories from Verifier-Passed tasks | **4,642** |
| Explicit target-skill invocation | **3,077 (36.8%)** |
| Average tool calls per successful trajectory | **49.0** |
| Average logged text tokens | **63.4k** |
| Average interaction steps | **35.2** |
| Corpus-wide maximum tool calls | **350** |
| Corpus-wide maximum logged text tokens | **342.9k** |
| Corpus-wide maximum interaction steps | **318** |

The maxima above are corpus-wide maxima for their respective measures and need not come from the same trajectory. Logged/saved text-token counts are dataset statistics and should not be interpreted as API billing usage or as a single-request context length.

## Collection Configurations

| Harness | Teacher model | Successful trajectories |
| --- | --- | ---: |
| Claude Code | DeepSeek V4 Pro | 1,722 |
| Claude Code | GLM-5.2 | 1,769 |
| Codex | GPT-5.4 | 1,967 |
| Codex | Nex-N2-Pro | 2,906 |

This diversity broadens the interaction traces beyond one agent configuration, but the released trajectory distribution should not be treated as representative of every model, harness, task domain, or deployment setting.

## Intended Uses

SkillGym can support research on:

- supervised fine-tuning from verified agent trajectories;
- agentic problem solving and long-horizon workflow learning;
- skill-conditioned versus skill-free execution;
- executable-environment and verifier-based evaluation;
- outcome-based reinforcement learning;
- task-generation and verifier design;
- trajectory analysis and procedural failure modes.

## Limitations

- Skill-Dep. and Verifier-Passed are reference-configuration labels, not universal properties.
- Category coverage is broad but uneven.
- Trajectory collections are generated by a finite set of harness–model configurations.
- Successful trajectories are a selected subset of sampled executions and should not be interpreted as an unbiased behavioral distribution.
- Some trajectory files preserve harness-specific schema differences.
- Source skills, fixtures, and supporting assets may carry upstream notices or additional licensing requirements.

## Related Resources

| Resource | Scope |
| --- | --- |
| [GitHub / SkillGym](https://github.com/ECNU-ICALK/SkillGym) | Task Builder, construction pipeline, documentation, and paper materials |
| [SkillGym-Agent](https://huggingface.co/ecnu-icalk/SkillGym-Agent) | Released **All Teachers** checkpoint trained on successful SkillGym trajectories |
| [Task Builder guide](https://github.com/ECNU-ICALK/SkillGym/blob/main/task_builder/README.md) | Building and validating new skill-grounded environments |
| [Paper](https://github.com/ECNU-ICALK/SkillGym/blob/main/assets/Internalizing_Large_Scale_Human_Written_Skills_into_LLMs_for_Real_World_Problem_Solving.pdf) | Full method, dataset analysis, experiments, and ablations |

## Citation

```bibtex
@misc{skillgym2026,
  title = {Internalizing Large-Scale Human-Written Skills into LLMs for Real-World Problem Solving},
  year  = {2026},
  url   = {https://github.com/ECNU-ICALK/SkillGym}
}
```

## License

The dataset is marked **`license: other`** because it aggregates artifacts that may retain distinct upstream notices or additional terms.

Repository-level SkillGym code is released under the **MIT License**. The SkillGym-Agent checkpoint is released separately under **Apache-2.0**.

When redistributing source skills, fixtures, or supporting assets, preserve the corresponding upstream notices and licensing terms.
