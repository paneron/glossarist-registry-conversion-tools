#!/usr/bin/python

import datetime
import pathlib
import argparse

from uuid import uuid5, NAMESPACE_OID as ns_oid
import glob

import re

import yaml

import config as cfg


def str_to_dt(date_str):
    return datetime.datetime.strptime(
        date_str, '%Y-%m-%d'
    ).date()


def read_yaml(fname):
    with open(fname, 'r') as _f:
        result = {
            'file': yaml.load(_f, Loader=yaml.FullLoader)
        }
        result['uuid'] = str(uuid5(ns_oid, str(result['file'])))
        # for debug:
        result['name'] = fname
        return result


def read_yaml_dir(subdir):
    result = []
    yaml_dir = '%s/%s' % (cfg.input_dir, subdir)

    print('Reading %s' % yaml_dir)

    files = glob.glob('%s/*.yaml' % yaml_dir)
    i = 0
    for fname in files:
        if not cfg.source_limit or i < cfg.source_limit:
            data = read_yaml(fname)
            result.append(data)
            i += 1
        else:
            break

    return result


def save_yaml(uuid, dname, data):
    file_path = '%s/subregisters/%s' % (cfg.output_dir, dname)
    pathlib.Path(file_path).mkdir(parents=True, exist_ok=True)
    file = open('%s/%s.yaml' % (file_path, uuid), 'w')
    file.write(yaml.dump(data, allow_unicode=True))
    file.close()


def save_items(items, dname):
    for item in items:
        uuid = item.pop('uuid')
        date_accepted = item.pop('dateAccepted')
        status = item.pop('status')

        data = {
            'id': uuid,
            'dateAccepted': date_accepted,
            'status': status,
            'data': item,
        }

        save_yaml(uuid, dname, data)


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
            if i < len(stems_marks):
                output.append(fix_stem_quotes(txt[cur[1]:stems_marks[i][0]]))
                pass
            else:
                output.append(fix_stem_quotes(txt[cur[1]:]))
            i += 1

        return ''.join(output)
    else:
        return txt


def convert_concepts():
    source = read_yaml_dir('concepts')

    print('Loaded %s source file(s).' % len(source))

    items = []
    for elm in source:
        term_name = elm['file'].pop('term')
        term_id = elm['file'].pop('termid')

        universal = {
            'id': elm['uuid'],
            'dateAccepted': str_to_dt(cfg.default_date),
            'status': cfg.default_status,
            'data': {
                'identifier': str(term_id),
                'localizedConcepts': {}
            }
        }

        for lang in elm['file']:
            data = {
                'data': elm['file'][lang]
            }

            if data['data'].get('date_accepted', False):
                date_accepted = data['data'].pop('date_accepted')
                date_accepted = str_to_dt(date_accepted.split('T')[0])
                data['dateAccepted'] = date_accepted
            else:
                data['dateAccepted'] = str_to_dt(cfg.default_date)

            data['status'] = data['data'].pop('entry_status', cfg.default_status)

            authoritative_source = {}
            if data['data'].get('authoritative_source', False):
                authoritative_source = data['data'].pop('authoritative_source')
            data['data']['authoritativeSource'] = [authoritative_source]

            data['id'] = str(uuid5(ns_oid, str(data)))

            designation = data['data'].get('designation', False)
            if designation:
                data['data']['designation'] = convert_stem(designation)

            definition = data['data'].get('definition', False)
            if definition:
                data['data']['definition'] = convert_stem(definition)

            notes = data['data'].get('notes', False)

            if notes:
                _notes = []
                for note in notes:
                    _notes.append(convert_stem(note))
                data['data']['notes'] = _notes

            terms = data['data'].get('terms', False)
            if terms:
                _terms = []
                for _term in terms:
                    _term_designation = _term.get('designation', False)
                    if _term_designation:
                        _term['designation'] = convert_stem(_term['designation'])
                    _terms.append(_term)
                data['data']['terms'] = _terms

            examples = data['data'].get('examples', False)
            if examples:
                _examples = []
                for example in examples:
                    _examples.append(convert_stem(example))
                data['data']['notes'] = _examples

            universal['data']['localizedConcepts'][lang] = data['id']

            save_yaml(data['id'], '%s/localized-concept' % lang, data)

        save_yaml(elm['uuid'], 'universal/concept', universal)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Convert data from old (concepts) to new yaml format.'
    )

    convert_concepts()
