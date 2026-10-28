# Scrapy 设置分层配置 子技能地图

## 子技能列表

- [Spider 内动态设置覆盖](通用技能领域/Family技能/未分类技能/微技能/Spider 内动态设置覆盖/SKILL.md) ｜ 微技能
  - 适用：在 Spider 的 from_crawler 中通过 settings.set 以 spider 优先级动态写入设置，用于按传入参数定制单个 Spider 的行为；当某个 Spider 需要根据参数调整设置时使用。
  - 线索：Spider 需根据传入参数调整设置, 需要在 Spider 初始化阶段覆盖某个设置值, 配置仅适用于单个 Spider 而非全部 Spider, scrapy, settings
- [命令行覆盖 Scrapy 设置](通用技能领域/Family技能/未分类技能/微技能/命令行覆盖 Scrapy 设置/SKILL.md) ｜ 微技能
  - 适用：使用 -s/--set 命令行选项在运行时显式覆盖一个或多个 Scrapy 设置，优先级最高；适用于需要临时覆盖设置而不修改项目文件、或调试时快速切换设置值的场景。
  - 线索：需要临时覆盖某设置而不修改项目文件, 调试时快速切换设置值, 需要在命令行运行时显式指定设置项, scrapy, settings
