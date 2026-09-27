import copy
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'scripts'))
from evidence import read
from reference_csv import transform,execute,InputError
from judge_csv import judge
from trace_http import Recorder,BufferedResponse
from trace_runtime import observe_chat

class ReferenceTests(unittest.TestCase):
    def test_all_existing_fixtures(self):
        for f in read(ROOT/'standards/case001/fixtures.json')['cases']:
            with self.subTest(fixture=f['id']):
                if f['expect']=='success': self.assertEqual(transform(f['input']),f['outputs'])
                else:
                    with self.assertRaises(InputError) as error: transform(f['input'])
                    if 'error_record' in f: self.assertEqual(error.exception.record,f['error_record'])
                    if 'error_field' in f: self.assertEqual(error.exception.field,f['error_field'])
    def test_preexisting_output_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); input_file=p/'orders.csv'; input_file.write_bytes(b'order_id,customer_id,updated_at,amount\n')
            sentinel=p/'summary.csv'; sentinel.write_bytes(b'original')
            with self.assertRaises(InputError): execute(input_file,p)
            self.assertEqual(sentinel.read_bytes(),b'original'); self.assertFalse((p/'deduplicated.csv').exists())
    def test_bad_dates_and_offsets(self):
        for value in ('2026-02-30T00:00:00Z','2026-01-01T00:00:00','2026-01-01T00:00:00.1Z','2026-01-01T00:00:00+08:99'):
            with self.subTest(value=value),self.assertRaises(InputError): transform('order_id,customer_id,updated_at,amount\na,c,'+value+',1\n')
    def test_whitespace_leading_zero_and_string_sort(self):
        output=transform('order_id,customer_id,updated_at,amount\n 02 , null ,2026-01-01T00:00:00Z, 1.2 \n10,NA,2026-01-01T00:00:00Z,0.10\n')
        self.assertIn('\n02,null,',output['deduplicated.csv']); self.assertLess(output['deduplicated.csv'].index('\n02,'),output['deduplicated.csv'].index('\n10,'))
        self.assertIn('\nNA,',output['summary.csv']); self.assertIn('\nnull,',output['summary.csv'])
    def test_judge_rejects_wrong_behavior_mutants(self):
        task=read(ROOT/'standards/case001/tasks/case001-v2.example.json')
        e={k:task[k] for k in ('case_id','source_id','family_id','task_id','contract_id','judge_id')}
        e.update(status='completed',input_before={'orders.csv':'h'},input_after={'orders.csv':'h'},actual_outputs=copy.deepcopy(task['expected']['outputs']),exit_code=0,error=None,failure_category='none')
        self.assertTrue(judge(task,e)['passed'])
        mutations=[lambda v:v['actual_outputs'].update({'summary.csv':v['actual_outputs']['summary.csv'].replace('14.75','24.75')}),
            lambda v:v['actual_outputs'].update({'deduplicated.csv':v['actual_outputs']['deduplicated.csv'].replace('12.50','10.00')}),
            lambda v:v['input_after'].update({'orders.csv':'changed'}),lambda v:v['actual_outputs'].update({'extra.txt':'x'}),
            lambda v:v.update(exit_code=1),lambda v:v['actual_outputs'].update({'summary.csv':v['actual_outputs']['summary.csv'].replace('\n','\r\n')})]
        for i,mutate in enumerate(mutations):
            with self.subTest(mutant=i):
                bad=copy.deepcopy(e); mutate(bad); self.assertFalse(judge(task,bad)['passed'])
    def test_expected_error_requires_error_field(self):
        task=read(ROOT/'standards/case001/tasks/case001-v2.invalid_amount_NA.json')
        e={k:task[k] for k in ('case_id','source_id','family_id','task_id','contract_id','judge_id')}
        e.update(status='completed',input_before={'orders.csv':'h'},input_after={'orders.csv':'h'},actual_outputs={},exit_code=1,error={'record':1,'field':'updated_at','message':'wrong'},failure_category='none')
        self.assertFalse(judge(task,e)['passed'])
    def test_http_observer_keeps_bytes_and_redacts(self):
        import urllib.request
        with tempfile.TemporaryDirectory() as tmp:
            payload=b'{"model":"test","echo":"secret-unit-value"}'
            original=lambda *args,**kwargs:BufferedResponse(payload,200,{},'https://example.test/chat/completions')
            recorder=Recorder(tmp,['secret-unit-value'])
            req=urllib.request.Request('https://example.test/chat/completions',data=b'{}')
            self.assertEqual(recorder.wrap(original)(req).read(),payload)
            logged=''.join(p.read_text() for p in Path(tmp).glob('*.json'))
            self.assertNotIn('secret-unit-value',logged); self.assertIn('[REDACTED]',logged)
    def test_truncation_observer_keeps_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            observed=observe_chat(lambda **kwargs:('s','short'),Recorder(tmp))
            self.assertEqual(observed(system='s',user='long input',max_units=5),('s','short'))
            self.assertTrue(read(next(Path(tmp).glob('*.json')))['changed'])

if __name__=='__main__': unittest.main()
