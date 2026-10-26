import inspect

def get_target_function(module):
    """
    Prefer an explicitly named function. Fall back to a single public function only
    if there is no ambiguity.
    """
    preferred_names = [
        "default_feed_overwrite",
        "get_default_overwrite",
        "determine_default_overwrite",
        "feed_export_overwrite_default",
    ]
    for name in preferred_names:
        obj = getattr(module, name, None)
        if inspect.isfunction(obj):
            return obj

    public_functions = [
        getattr(module, name)
        for name in dir(module)
        if not name.startswith("_") and inspect.isfunction(getattr(module, name))
    ]
    assert len(public_functions) == 1, (
        "Could not uniquely identify target function. "
        "Please expose a single public function or use a conventional name like "
        "`default_feed_overwrite`."
    )
    return public_functions[0]
