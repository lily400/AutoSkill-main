import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

LAB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB/'src'))
from degradation_lab.io import write, read
from degradation_lab.resume import _budget_extraction_calls


class BudgetCheckpoint(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.parent = Path(self.temp.name)
        self.checkpoint = self.parent/'SkillBank/.runtime/checkpoint'
        self.windows = [{'window_id':f'w{i}', 'doc_id':'doc', 'text':f'public rule {i}', 'span':[i,i+1]} for i in range(2)]
        write(self.parent/'official_result.json', {'errors':[{'error':'P0 external observation budget exhausted'}]})
        write(self.checkpoint/'extract/windows/doc/w0.json', {'skill_drafts':[{'draft_id':'d0'}]})
        self.calls = []
        for n,wid,kind in [(1,0,'_plan_unit_skills'),(2,0,'_expand_planned_skill'),(3,1,'_plan_unit_skills'),(4,1,'_expand_planned_skill')]:
            payload={'excerpt':self.windows[wid]['text'],'section':{'span':self.windows[wid]['span']}}
            write(self.parent/'http'/f'{n:03d}'/'request.json', {'messages':[{'role':'user','content':json.dumps(payload)}]})
            write(self.parent/'http'/f'{n:03d}'/'response.json', {'fixture':'known response'})
            self.calls.append({'number':n,'logical_call_id':n,'success':True,'stack':[{'function':kind}],
                'response_sha256':hashlib.sha256((self.parent/'http'/f'{n:03d}'/'response.json').read_bytes()).hexdigest()})

    def recover(self):
        write(self.parent/'model_calls.json',self.calls)
        return _budget_extraction_calls(self.parent,self.checkpoint,self.windows,['w0'],[])

    def test_partial_window_replay_is_explicit_and_completed_window_retained(self):
        replayed,excluded=self.recover()
        self.assertEqual(replayed,[3,4]); self.assertEqual(excluded,{})

    def test_undispatched_pending_window_is_supported(self):
        self.calls=self.calls[:2]
        self.assertEqual(self.recover(),([],{}))

    def test_successful_transport_retry_is_counted_and_payload_mismatch_rejected(self):
        last = dict(self.calls[-1], number=5, logical_call_id=4, retry_of=4)
        self.calls[-1].update(success=False, transport_retry_eligible=True)
        self.calls.append(last)
        for name in ('request.json','response.json'):
            target=self.parent/'http/005'/name; target.parent.mkdir(exist_ok=True)
            target.write_bytes((self.parent/'http/004'/name).read_bytes())
        self.assertEqual(self.recover()[0],[3,4,5])
        write(self.parent/'http/005/request.json',{'messages':[]})
        with self.assertRaisesRegex(ValueError,'retry payload changed'):
            self.recover()

    def test_unknown_outstanding_post_and_response_tampering_are_rejected(self):
        self.calls[-1]['success']=False
        with self.assertRaisesRegex(ValueError,'Unresolved HTTP'):
            self.recover()
        self.calls[-1]['success']=True
        (self.parent/'http/004/response.json').write_text('tampered')
        with self.assertRaisesRegex(ValueError,'response hash'):
            self.recover()

    def test_nonbudget_failure_and_successful_compile_are_rejected(self):
        write(self.parent/'official_result.json',{'errors':[{'error':'SSL error'}]})
        with self.assertRaisesRegex(ValueError,'observation-budget'):
            self.recover()
        write(self.parent/'official_result.json',{'errors':[{'error':'P0 external observation budget exhausted'}]})
        write(self.checkpoint/'compile/result.json',{'skill_specs':[{'skill_id':'already compiled'}]})
        with self.assertRaisesRegex(ValueError,'Successful downstream'):
            self.recover()


if __name__=='__main__':
    unittest.main(verbosity=2)
