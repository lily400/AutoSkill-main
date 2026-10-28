# Scrapy 设置分层配置 Evidence

- family: 未分类技能
- skill_id: 753efc90-ea75-5d01-a982-81f189f64bc9
- support_count: 1

## Evidence 1

- support_id: fa9dc8b3-bcb4-544f-a611-bb8f529beff5
- relation_type: support
- document: input002\settings.md
- doc_id: 63a3e42d-b022-53bd-918f-7256d9f5f5a2
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case050_scrapy\clean\s50g001\inputs\input002\settings.md
- section: Settings
- span: 3093:3607
- confidence: 0.70
- quote: @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        if "some_argument" in kwargs:
            spider.settings.set(
                "SOME_SETTING", kwargs["some_argument"], priority="spider"
            )
        return spider
```

3. Project settings
Scrapy projects include a settings module, usually a file called
`settings.py`, where you should populate most settings that apply to all your
spiders.

Designating the settings
