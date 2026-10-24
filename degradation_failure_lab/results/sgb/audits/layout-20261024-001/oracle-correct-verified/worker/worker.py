"""Candidate-only process. Receives inputs, never tests or expected values."""
import contextlib
import importlib.util
import inspect
import io
import json
import sys

request = json.loads(sys.stdin.read())
capture = io.StringIO()
try:
    with contextlib.redirect_stdout(capture), contextlib.redirect_stderr(capture):
        spec = importlib.util.spec_from_file_location('agent_output', '/submission/agent_output.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        from interface import get_target_function
        target = get_target_function(module)
        if request['operation'] == 'metadata':
            response = {'ok':True, 'operation':'metadata', 'callable':True}
        else:
            value = target(request['input'])
            # Every original value assertion requires bool; preserve failure for all other types.
            if type(value) is not bool:
                response = {'ok':True, 'unsupported_type':type(value).__name__}
            else:
                response = {'ok':True, 'value':value}
except Exception as error:
    response = {'ok':False, 'exception_type':type(error).__name__, 'message':str(error),
                'builtin_exception_bases':[cls.__name__ for cls in type(error).__mro__
                                           if cls.__module__=='builtins' and issubclass(cls,Exception)]}
response['candidate_output'] = capture.getvalue()[:2000]
print(json.dumps(response, allow_nan=False))
