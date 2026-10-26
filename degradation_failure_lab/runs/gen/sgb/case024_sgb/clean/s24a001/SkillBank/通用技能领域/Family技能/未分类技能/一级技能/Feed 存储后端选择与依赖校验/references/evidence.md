# Feed 存储后端选择与依赖校验 Evidence

- family: 未分类技能
- skill_id: b7e8d5c2-dfcf-59cd-ba27-6299829dcbf3
- support_count: 1

## Evidence 1

- support_id: 4ccac22f-83d1-5c3d-bf9c-3531c5546b62
- relation_type: support
- document: input001\feed-exports.md
- doc_id: f7a76d82-16fa-5d4e-9e08-dcfb60e9f311
- source_file: D:\AS\AutoSkill-main\degradation_failure_lab\runs\gen\sgb\case024_sgb\clean\s24a001\inputs\input001\feed-exports.md
- section: Feed exports
- span: 2739:3253
- confidence: 0.70
- quote: The storages backends supported out of the box are:

- Local filesystem
- FTP
- S3 (requires [boto3](https://github.com/boto/boto3))
- Google Cloud Storage (GCS) (requires [google-cloud-storage](https://cloud.google.com/storage/docs/reference/libraries#client-libraries-install-python))
- Standard output

Some storage backends may be unavailable if the required external libraries are
not available. For example, the S3 backend is only available if the [boto3](https://github.com/boto/boto3)
library is installed.
