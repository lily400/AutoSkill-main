# Depth Limit Zero Behavior

Implement a Scrapy spider that demonstrates the behavior of `DEPTH_LIMIT=0`.

## Requirements

Create a file called `agent_output.py` that contains:

1. A Scrapy spider class named `DepthLimitZeroSpider`
2. The spider must set `DEPTH_LIMIT=0` in spider-level settings
3. The spider must recursively follow links found in `<a href="...">` elements
4. A function `get_depth_limit_zero_finding() -> dict` that returns a dictionary with:
   - `depth_limit`: the configured value
   - `effective_max_depth`: the actual maximum crawl depth enforced by Scrapy for this setting
   - `follows_beyond_start_urls`: whether links beyond the start URL can be followed
   - `summary`: a short explanation of what `DEPTH_LIMIT=0` means in Scrapy

## Notes

- Your implementation should reflect Scrapy's actual behavior for `DEPTH_LIMIT=0`
- The returned explanation should be consistent with the spider configuration

Optional extension (not evaluated): add a small comparison note for `DEPTH_LIMIT=1` to contrast with `DEPTH_LIMIT=0`.
## Runtime Interface

- Inputs directory: /workspace/input
- Documentation context directory: /workspace/docs
- Skill assets directory: /workspace/skill
- Final submission file: /workspace/agent_output.py
- Tests run from /workspace/tests/test.sh with TEST_ROOT_DIR=/workspace.
