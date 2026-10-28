# Tick 处理与快照生成流程 子技能地图

## 子技能列表

- [装卸作业工作量推进结算](通用技能领域/Family技能/未分类技能/微技能/装卸作业工作量推进结算/SKILL.md) ｜ 微技能
  - 适用：按车辆 HandlingRate 逐 tick 递减装卸作业的 WorkUnits，并在归零时结算货物状态（装载转 ON_VEHICLE，卸载转 DELIVERED 或 PENDING_AT_ORIGIN）。用于模拟车辆执行 START_LOADING/START_UNLOADING 后的多 tick 装卸过程。
  - 线索：车辆已进入 LOADING 或 UNLOADING 状态, 需要计算作业剩余 WorkUnits 或判定完成, 交通仿真, 装卸结算, WorkUnits
- [装载作业完成判定](通用技能领域/Family技能/未分类技能/微技能/装载作业完成判定/SKILL.md) ｜ 微技能
  - 适用：对 START_LOADING 发起的装载作业，按 WorkUnits=SizeUnits 与 HandlingRate 计算完成所需 tick 数，并据此更新车辆与货物状态。适用于车辆在节点开始装载货物、需要判断何时装载完成时。
  - 线索：车辆执行 START_LOADING, 需要判断货物何时装载完成, 装载阶段需要更新车辆与货物状态, 交通仿真, 装卸作业
