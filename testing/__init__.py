import os
from pathlib import Path
from testing.compare import verify_integrity
from testing.compare import JSON, XML
type_dict = {'json': JSON, 'xml': XML}


def read_file(file):
    with open(file, 'r') as f:
        return f.read()


def test_all_files_in(directory):
    for base, dirs, files in os.walk(directory):
        base = Path(base)
        for f in files:
            xml_code = read_file(base / f)
            type_ = type_dict[f.split('.')[-1]]
            print(verify_integrity(xml_code, type_=type_))
