# Allow Offsite Request via Request Metadata

This is a basic calibration task.

Scrapy's `OffsiteMiddleware` blocks requests to domains that are not listed in `allowed_domains`.

However, Scrapy also provides a request-level mechanism that allows a specific request to bypass the offsite filtering without modifying global middleware settings.

Your task is to implement a Scrapy spider that demonstrates this behavior.

## Requirements

Create a file called `agent_output.py` that defines a Scrapy spider.

The spider must:

1. Inherit from `scrapy.Spider`
2. Set `allowed_domains = ["example.com"]`
3. Produce a request to the URL: http://other.com/resource
4. Ensure that this request bypasses Scrapy's offsite filtering **using request metadata**
5. The bypass must apply **only to that request**, not globally
6. The request must be returned or yielded from spider logic (e.g., `start_requests()`)

## Restrictions

The solution must NOT:

- Disable or modify `OffsiteMiddleware`
- Modify Scrapy middleware settings
- Change `allowed_domains` to include `other.com`

The bypass must be implemented using Scrapy's **per-request mechanism** described in the documentation.
## Runtime Interface

- Inputs directory: /workspace/input
- Documentation context directory: /workspace/docs
- Skill assets directory: /workspace/skill
- Final submission file: /workspace/agent_output.py
- Tests run from /workspace/tests/test.sh with TEST_ROOT_DIR=/workspace.
