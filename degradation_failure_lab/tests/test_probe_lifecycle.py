"""Execute the actual observer run/summary methods with no network or Harbor runtime."""
import ast
import asyncio
import json
from pathlib import Path
import sys
import tempfile
from types import ModuleType,SimpleNamespace
import unittest
from unittest.mock import patch

LAB=Path(__file__).resolve().parents[1]

class PreModelStop(BaseException):pass
class Base:
    async def run(self,*args):raise PreModelStop()

def observer():
    path=LAB/'downstream_eval/integration/p1_observer.py'
    tree=ast.parse(path.read_text(encoding='utf-8'))
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='P1ObservationMixin')
    methods=[n for n in cls.body if getattr(n,'name',None) in ('run','_write_p1_summary')]
    node=ast.ClassDef(name='Observed',bases=[ast.Name(id='Base',ctx=ast.Load())],keywords=[],body=methods,decorator_list=[])
    ns={'Base':Base,'PreModelStop':PreModelStop,'json':json,'shlex':__import__('shlex'),'os':__import__('os')}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[])),str(path),'exec'),ns)
    return ns['Observed']()

class ProbeLifecycle(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.agent=observer();a=self.agent
        a._p1={'budget':{}};a.options=SimpleNamespace(p1_mode='probe')
        a._p1_manifest={'metadata':{}};a._p1_pid=17;a._p1_tool_events=[]
        a._p1_reads=[];a._p1_calls=a._p1_input=0;a._p1_budget=a._p1_http_client=None
        a._p1_logs=Path(self.temp.name);a._session=object();a._event=lambda *args,**kwargs:None
        self.active=True;self.events=[]
        async def execute(*args):self.events.append('terminal');return False,'/workspace'
        async def capture():self.events.append('capture')
        async def env_exec(command,**kwargs):
            if command.startswith('kill '):self.active=False;self.events.append('cleanup')
        a._execute_commands=execute;a._capture_reads=capture;self.environment=SimpleNamespace(exec=env_exec)
        modules={}
        for name in ('harbor','harbor.agents','harbor.agents.terminus_2','harbor.agents.terminus_2.terminus_2'):
            modules[name]=ModuleType(name)
        modules['harbor.agents.terminus_2.terminus_2'].Command=lambda *args:args
        p=patch.dict(sys.modules,modules);p.start();self.addCleanup(p.stop)

    def test_optional_paging_runs_with_terminal_alive_and_summary_available(self):
        async def hook():
            self.assertTrue(self.active)
            self.assertTrue(json.loads((self.agent._p1_logs/'p1-summary.json').read_text())['stopped_before_model'])
            self.events.append('paging')
        self.agent._p1_probe_hook=hook
        asyncio.run(self.agent.run('task',self.environment,None))
        self.assertLess(self.events.index('paging'),self.events.index('cleanup'))
        self.assertFalse(self.active)

    def test_without_hook_existing_zero_model_summary_is_unchanged(self):
        asyncio.run(self.agent.run('task',self.environment,None))
        value=json.loads((self.agent._p1_logs/'p1-summary.json').read_text())
        self.assertEqual(value['actual_http_attempts'],0)
        self.assertTrue(value['stopped_before_model']);self.assertFalse(self.active)

    def test_hook_failure_still_cleans_up_and_records_zero_requests(self):
        async def hook():raise ValueError('fixture paging failure')
        self.agent._p1_probe_hook=hook
        with self.assertRaisesRegex(ValueError,'fixture paging'):
            asyncio.run(self.agent.run('task',self.environment,None))
        self.assertFalse(self.active)
        self.assertEqual(json.loads((self.agent._p1_logs/'p1-summary.json').read_text())['actual_http_attempts'],0)

if __name__=='__main__':unittest.main(verbosity=2)
