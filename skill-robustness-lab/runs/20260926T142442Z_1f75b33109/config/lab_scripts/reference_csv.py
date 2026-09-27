"""Developer reference for case001 only; never a generated-skill result.

Amounts use arbitrary-size integer cents, avoiding Decimal context rounding.
This reference is hidden from future generated-skill executors.
"""
import csv
from datetime import datetime, timezone
import io
from pathlib import Path
import re

VERSION='case001-reference-1'
HEADER=['order_id','customer_id','updated_at','amount']
SUMMARY=['customer_id','order_count','total_amount','latest_updated_at']
TIME=re.compile(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(Z|[+-][0-9]{2}:[0-9]{2})$')
MONEY=re.compile(r'^[0-9]+(?:\.[0-9]{1,2})?$')

class InputError(ValueError):
    def __init__(self,message,record=None,field=None):
        super().__init__(message); self.record=record; self.field=field

def stamp(value,record):
    if not TIME.fullmatch(value): raise InputError('Invalid timezone-aware timestamp',record,'updated_at')
    if value[-1]!='Z' and (int(value[-5:-3])>23 or int(value[-2:])>59):
        raise InputError('Invalid UTC offset',record,'updated_at')
    try: return datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(timezone.utc)
    except (ValueError,OverflowError): raise InputError('Invalid date/time',record,'updated_at')

def cents(value,record):
    if not MONEY.fullmatch(value): raise InputError('Invalid nonnegative fixed-point amount',record,'amount')
    whole,_,fraction=value.partition('.')
    return int(whole)*100+int((fraction+'00')[:2])

def money(value): return str(value//100)+'.'+str(value%100).zfill(2)
def time_text(value): return value.isoformat(timespec='seconds').replace('+00:00','Z')
def encode_csv(header,rows):
    out=io.StringIO(newline=''); w=csv.writer(out,lineterminator='\n'); w.writerow(header); w.writerows(rows)
    return out.getvalue()

def transform(text):
    reader=csv.reader(io.StringIO(text,newline=''),strict=True)
    try: header=next(reader,None)
    except csv.Error as exc: raise InputError(str(exc),field='header')
    if header!=HEADER: raise InputError('Header must match exactly',field='header')
    rows=[]; record=0
    try:
        for record,row in enumerate(reader,1):
            if len(row)!=4: raise InputError('Expected four fields',record)
            oid,cid,ts,amount=(v.strip() for v in row)
            if not oid: raise InputError('Missing order_id',record,'order_id')
            if not ts: raise InputError('Missing updated_at',record,'updated_at')
            rows.append((oid,cid or 'UNKNOWN',stamp(ts,record),cents(amount or '0.00',record),record))
    except csv.Error as exc: raise InputError(str(exc),record+1)
    # Validation of EVERY record is complete before any selection.
    selected={}
    for row in rows:
        old=selected.get(row[0])
        if old is None or (row[2],row[4])>(old[2],old[4]): selected[row[0]]=row
    groups={}
    for oid,cid,ts,amount,_ in selected.values():
        count,total,latest=groups.get(cid,(0,0,ts))
        groups[cid]=(count+1,total+amount,max(latest,ts))
    detail=[[oid,row[1],time_text(row[2]),money(row[3])] for oid,row in sorted(selected.items())]
    summary=[[cid,str(v[0]),money(v[1]),time_text(v[2])] for cid,v in sorted(groups.items())]
    return {'deduplicated.csv':encode_csv(HEADER,detail),'summary.csv':encode_csv(SUMMARY,summary)}

def execute(input_file,output_dir):
    input_file=Path(input_file).resolve(); output_dir=Path(output_dir).resolve()
    names=('deduplicated.csv','summary.csv'); targets=[output_dir/n for n in names]
    if any(p==input_file or p.exists() for p in targets): raise InputError('Refusing to overwrite an existing file',field='output')
    try: text=input_file.read_bytes().decode('utf-8')
    except UnicodeError: raise InputError('Input is not UTF-8',field='encoding')
    output=transform(text)
    output_dir.mkdir(parents=True,exist_ok=True)
    created=[]
    try:
        for name in names:
            path=output_dir/name
            with path.open('xb') as handle:
                created.append(path); handle.write(output[name].encode('utf-8'))
    except BaseException:
        for path in created: path.unlink()
        raise
    return output
