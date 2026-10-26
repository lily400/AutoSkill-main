"""Backward-compatible Scrapy041 entry; all workflow logic is shared."""
if __package__:
    from .pilot import main
else:
    from pilot import main

if __name__ == "__main__":
    raise SystemExit(main(default_task="scrapy-task-041", default_generator="s41r003"))
