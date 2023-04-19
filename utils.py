import datetime
import re

import yaml


def str_to_dt(date_str):
    if 'T' in date_str:
        date_str = date_str.split('T')[0]
    return datetime.datetime.strptime(
        date_str, '%Y-%m-%d'
    ).date()


def fix_stem_quotes(txt):
    opn = 0
    end = 0
    cur = 0

    for char in txt:
        if char == '[':
            opn += 1
        elif char == ']':
            opn -= 1
            if opn == -1:
                end = cur
                break

        cur += 1

    if end > 0:
        txt_array = list(txt)
        txt_array = ['`'] + txt_array
        txt_array[end+1] = '`'
        txt = ''.join(txt_array)

    return txt


def convert_stem(txt):
    if 'stem:[' in txt:
        result = ''
        output = []

        stems_marks = []
        for m in re.finditer('stem\:\[', txt):
            stems_marks.append((m.start(), m.end()))

        i = 1
        for cur in stems_marks:
            if i == 1 and cur[0] > 0:
                output.append(txt[0:cur[0]])
            if i < len(stems_marks):
                output.append(fix_stem_quotes(txt[cur[1]:stems_marks[i][0]]))
            else:
                output.append(fix_stem_quotes(txt[cur[1]:]))
            i += 1

        return ''.join(output)
    else:
        return txt


def set_str(path, d, fn):
    v = d.get_str(path, False)
    if v:
        d[path] = fn(v)
    return d


def set_lst(path, d, fn):
    # get_str_list
    v = d.get_list(path, False)
    if v:
        _l = []
        for elm in v:
            _l.append(fn(elm))
        d[path] = _l
    return d


def format_values(raw):
    """
    Given either a formatted string dict or a plain string,
    returns a plain string (formatted string’s ``content`` key).
    """
    if isinstance(raw, str):
        try:
            obj = yaml.load(raw, yaml.Loader)
        except Exception:
            pass
        else:
            return format_values(obj)
        return [{'content': raw}]
    elif isinstance(raw, list):
        output = []
        for r in raw:
            out = format_values(r)
            if isinstance(out, list):
                output.append(out[0])
            else:
                output.append(out)
        return output
    elif isinstance(raw, dict):
        return [raw]

