
# 当前仓库与官方 upstream 对比

| 对象 | 当前仓库 | 官方 `ECNU-ICALK/AutoSkill` | 结论 |
|---|---|---|---|
| commit | `19b660299c557431044cc07788c6232d1deb2f99` | `94c47ca488d4ba4117d20272e66d49b9877e68cf` | 提交历史不同 |
| `AutoSkill4Doc` tree | `9f4c0203e77e4263852da42389f054105333fe3a` | 同值 | 内容一致 |
| `tests` tree | `4107cf194c2a1b3703583b3d757c83fb2111312c` | 同值 | 内容一致 |
| `pyproject.toml` blob | `cc7e7c10297a50f581bed4d74a70f9346f0f147a` | 同值 | 内容一致 |
| `autoskill` tree | `1c0b4545c40b628cef86b149f90ed46bbeb5d5c3` | `094f1cfbb1b2d340528fc9c6d58efd2fd49e2b99` | tree SHA 不同 |

逐树核验仅定位到 `autoskill/offline/conversation/run_codex_reflection.sh` 这一叶节点差异；当前与 upstream 文件 blob 均为 `02b05454888a2861437c95c71159928b94c2bbae`，文本内容相同，因此这是文件模式或树元数据差异，不是业务源码内容修改。

与 document → skill 主流程相关的 `AutoSkill4Doc` 内容未发现本地修改。当前仓库额外包含 `.idea/**`、`test_doc.md`、被跟踪的 `.env/.env.example`，以及本轮新增的 `research/robustness/**`。
