
# R01–R12 Stage 0 追踪矩阵

| Rule ID | Source evidence | Reference spec | Program IR field | Future witness task | Future verifier check | Stage 0 status |
|---|---|---|---|---|---|---|
| R01 | SRC-R01 | `rules.csv:R01` | `steps.P02` | planned / Task007 | planned / Task009 | complete_stage0 |
| R02 | SRC-R02 | `rules.csv:R02` | `steps.P02` | planned / Task007 | planned / Task009 | complete_stage0 |
| R03 | SRC-R03 | `rules.csv:R03` | `steps.P03; invariants[3]` | planned / Task007 | planned / Task009 | complete_stage0 |
| R04 | SRC-R04 | `rules.csv:R04` | `steps.P03` | planned / Task007 | planned / Task009 | complete_stage0 |
| R05 | SRC-R05 | `rules.csv:R05` | `steps.P04` | planned / Task007 | planned / Task009 | complete_stage0 |
| R06 | SRC-R06 | `rules.csv:R06` | `steps.P04/P05; invariants[1]` | planned / Task007 | planned / Task009 | complete_stage0 |
| R07 | SRC-R07 | `rules.csv:R07` | `branches[0:2]` | planned / Task007 | planned / Task009 | complete_stage0 |
| R08 | SRC-R08 | `rules.csv:R08` | `exceptions[0]` | planned / Task007 | planned / Task009 | complete_stage0 |
| R09 | SRC-R09 | `rules.csv:R09` | `invariants[0]; effects.forbidden` | planned / Task007 | planned / Task009 | complete_stage0 |
| R10 | SRC-R10 | `rules.csv:R10` | `steps.P01/P06; exceptions[1]` | planned / Task007 | planned / Task009 | complete_stage0 |
| R11 | SRC-R11 | `rules.csv:R11` | `exceptions; effects.forbidden` | planned / Task007 | planned / Task009 | complete_stage0 |
| R12 | SRC-R12 | `rules.csv:R12` | `outputs; checks` | planned / Task007 | planned / Task009 | complete_stage0 |

## 判定

R01–R12 均已在 source、reference spec 和 canonical IR 中表达。Task007 和 Task009 尚未开始，因此 witness 和 verifier 栏按协议保持 `planned`。这一矩阵只确认文档层可追溯性，不代表 verifier 已实现或链路已通过。
