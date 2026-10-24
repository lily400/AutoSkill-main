# Feed 存储 URI 参数替换 Evidence

- family: 未分类技能
- skill_id: 100c7e33-dfd6-594b-929c-0a53ce77829e
- support_count: 1

## Evidence 1

- support_id: 83479ffa-741b-57ff-90ce-1a475311b002
- relation_type: support
- document: input001\feed-exports.md
- doc_id: 746b8660-57be-5a86-bc5c-fdd89bdae86d
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\case024_scrapy\clean\s24m005\inputs\input001\feed-exports.md
- section: Feed exports
- span: 3255:3718
- confidence: 0.85
- quote: Storage URI parameters
The storage URI can also contain parameters that get replaced when the feed is
being created. These parameters are:

- `%(time)s` - gets replaced by a timestamp when the feed is being created
- `%(name)s` - gets replaced by the spider name

Any other named parameter gets replaced by the spider attribute of the same
name. For example, `%(site_id)s` would get replaced by the `spider.site_id`
attribute the moment the feed is being created.
