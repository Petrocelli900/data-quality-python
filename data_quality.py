"""Validate comma-separated UTF-8 CSV files using an explicit schema."""
import argparse
import csv
import json
import re
import sys
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation

@dataclass(frozen=True)
class Rule:
    kind: str = "text"
    required: bool = True
    unique: bool = False
    def __post_init__(self):
        if self.kind not in {"text","integer","decimal","email"}:
            raise ValueError("Unsupported kind")
        if type(self.required) is not bool or type(self.unique) is not bool:
            raise ValueError("required and unique must be booleans")

@dataclass(frozen=True)
class Issue:
    record: int
    column: str
    code: str

def valid(value,kind):
    if kind=="integer": return re.fullmatch(r"[+-]?[0-9]+",value) is not None
    if kind=="decimal":
        try: return Decimal(value).is_finite()
        except InvalidOperation: return False
    if kind=="email": return re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+",value) is not None
    return True

def validate(stream,schema):
    if not schema or any(not isinstance(k,str) or not k for k in schema):
        raise ValueError("Nonempty named schema required")
    reader=csv.reader(stream,strict=True)
    header=next(reader,None)
    if header is None or len(header)!=len(set(header)):
        raise ValueError("Missing or duplicated header")
    if set(header)!=set(schema): raise ValueError("Header must match schema exactly")
    seen={key:set() for key,rule in schema.items() if rule.unique}
    issues=[]
    count=0
    for count,row in enumerate(reader,1):
        if len(row)!=len(header):
            issues.append(Issue(count,"*","column_count"))
            continue
        for column,raw in zip(header,row):
            value=raw.strip(); rule=schema[column]
            if not value:
                if rule.required: issues.append(Issue(count,column,"required"))
                continue
            if not valid(value,rule.kind): issues.append(Issue(count,column,"invalid_type"))
            if rule.unique:
                if value in seen[column]: issues.append(Issue(count,column,"duplicate"))
                seen[column].add(value)
    return {"records":count,"valid":not issues,"issues":[asdict(i) for i in issues]}

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv"); parser.add_argument("schema")
    args=parser.parse_args(argv)
    try:
        with open(args.schema,encoding="utf-8") as file: raw=json.load(file)
        if not isinstance(raw,dict): raise ValueError("Schema must be an object")
        schema={key:Rule(**value) for key,value in raw.items()}
        with open(args.csv,encoding="utf-8-sig",newline="") as file: result=validate(file,schema)
    except (OSError,ValueError,TypeError,csv.Error) as error:
        print(str(error),file=sys.stderr); return 2
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result["valid"] else 1

if __name__=="__main__": sys.exit(main())
