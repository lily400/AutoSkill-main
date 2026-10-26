"""Controlled zero-model terminal paging; separate from model-directed reading."""
from pathlib import Path
from degradation_lab.io import read, write


async def probe_body_chunks(trial):
    """Verify paging through existing terminal tools; never inject text into paid prompts."""
    import hashlib
    from harbor.agents.terminus_2.terminus_2 import Command
    from downstream_eval.integration.p1_observer import body_visible
    observer=trial.paths.trial_dir/'p1-observer'
    summary=read(observer/'p1-summary.json')
    manifest=trial.agent._p1_manifest
    visible=set(summary['full_body_visible_ids_ignoring_terminal_whitespace'])
    records=[]
    for sid in sorted(set(manifest['metadata'])-visible):
        text=(Path(manifest['staged_root'])/sid/'SKILL.md').read_text()
        pieces=[];current=''
        for line in text.splitlines(keepends=True):
            if current and (len(current)+len(line)>500 or current.count('\n')>=8):
                pieces.append(current);current=''
            while len(line)>500:
                if current:pieces.append(current);current=''
                pieces.append(line[:500]);line=line[500:]
            current+=line
        if current:pieces.append(current)
        offset=0;proof=[]
        for piece in pieces:
            end=offset+len(piece)
            command=("python -c \"from pathlib import Path; print(Path('/harbor/skills/"
                     +sid+"/SKILL.md').read_text()["+str(offset)+":"+str(end)+"],end='')\"\n")
            timed_out,observation=await trial.agent._execute_commands(
                [Command(command,0.2)],trial.agent._session)
            ok=not timed_out and (not piece.strip() or body_visible(piece,observation))
            proof.append({'start':offset,'end':end,'sha256':hashlib.sha256(piece.encode()).hexdigest(),
                          'visible':ok,'observation':observation})
            if not ok:raise RuntimeError('Paged Skill body not visible: '+sid)
            offset=end
        if offset!=len(text):raise ValueError('Incomplete paging')
        visible.add(sid);records.append({'skill_id':sid,'chunks':proof})
    write(trial.paths.trial_dir/'body-visibility.json',{'status':'PASS','single_read_ids':
        summary['full_body_visible_ids_ignoring_terminal_whitespace'],'paged_records':records,
        'all_visible_ids':sorted(visible),'model_calls':0,
        'scope':'Controlled read availability, not evidence of model-directed reading'})

