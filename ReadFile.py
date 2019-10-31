import os


def file_reading_gen(path, fields=3, sep='\t', header=True):
    """File reader: CWID_NAME_MAJOR OR CWID_NAME_DEPARTMENT"""
    with open(path, 'r') as fp:
        lines = fp.readlines()
        start = 1 if header else 0
        for i in range(start, len(lines)):
            line = lines[i].strip("\n").split(sep)
            if len(line) != fields:
                raise ValueError(f"‘{os.path.basename(path)}’ has {len(line)} fields "
                                 f"on line {i if header == True else i + 1} but expected {fields}")
            else:
                yield tuple(line)

