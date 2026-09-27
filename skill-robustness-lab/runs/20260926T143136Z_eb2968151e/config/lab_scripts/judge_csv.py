"""Independent deterministic comparison to frozen task standards, not reference output."""
VERSION='case001-byte-and-behavior-1'

def judge(task,execution):
    if execution['status'] in ('not_run','running','blocked'):
        return {'status':'not_run','passed':None,'checks':[],'reason':'No completed execution to judge'}
    checks=[]
    def check(name,passed,reason): checks.append({'name':name,'passed':bool(passed),'reason':reason})
    check('identity',all(execution[k]==task[k] for k in ('case_id','source_id','family_id','task_id','contract_id','judge_id')),'Execution must use this task and judge')
    check('input_unchanged',bool(execution['input_before']) and execution['input_before']==execution['input_after'],'Compare input byte hashes before and after execution')
    expected=task['expected']; actual=execution['actual_outputs']
    check('output_file_set',set(actual)==set(expected['outputs']),'No missing or extra output files')
    for name,text in expected['outputs'].items():
        check('content:'+name,actual.get(name)==text,'Exact UTF-8 content, LF, header, sorting and quoting')
    if expected['outcome']=='success':
        check('successful_exit',execution['exit_code']==0 and execution['error'] is None,'Success requires normal completion')
    else:
        error=execution['error']
        check('expected_rejection',execution['exit_code'] not in (None,0) and isinstance(error,dict) and bool(error.get('message')),'Expected invalid input must be rejected explicitly')
        for key in ('record','field'):
            target=expected['error_'+key]
            if target is not None: check('error_'+key,isinstance(error,dict) and error.get(key)==target,'Required error location')
    check('no_infrastructure_error',execution['failure_category'] not in ('infrastructure','unknown','generation'),'Infrastructure/missing evidence cannot be a task pass')
    passed=all(c['passed'] for c in checks)
    return {'status':'passed' if passed else 'failed','passed':passed,'checks':checks,
        'reason':'Frozen task criteria checked; this does not prove correctness on untested inputs'}
