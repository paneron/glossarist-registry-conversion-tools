#!/usr/bin/python

import argparse
import glob
import pathlib
from uuid import uuid5, NAMESPACE_OID as ns_oid

import yaml

import config as cfg
from specific import iev as parse_iev_specific
from utils import str_to_dt, format_values, get_status


def read_yaml(fname):
    with open(fname, 'r') as _f:
        result = {
            'file': yaml.load(_f, Loader=yaml.FullLoader)
        }
        result['uuid'] = str(uuid5(ns_oid, str(result['file'])))
        # for uuid and debug:
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

    print(f'Number of files: {i}')

    return result


def save_yaml(uuid, dname, data):
    file_path = '%s/%s' % (cfg.output_dir, dname)
    pathlib.Path(file_path).mkdir(parents=True, exist_ok=True)
    file = open('%s/%s.yaml' % (file_path, uuid), 'w')
    file.write(yaml.safe_dump(data, allow_unicode=True, default_flow_style=False))
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


def convert_concepts(parse_specific=None):
    source = read_yaml_dir('concepts')

    print('Loaded %s source file(s).' % len(source))

    for elm in source:
        term_name = elm['file'].pop('term')
        term_id = elm['file'].pop('termid')
        if elm['file'].get('related', False):
            related = elm['file'].pop('related')
        else:
            related = []

        universal = {
            'id': elm['uuid'],
            'dateAccepted': str_to_dt(cfg.default_date),
            'status': cfg.default_status,
            'related': related,
            'data': {
                'identifier': str(term_id),
                'localizedConcepts': {}
            }
        }

        for lang in elm['file']:

            # Remove _revisions
            if elm['file'][lang].get('_revisions'):
                del elm['file'][lang]['_revisions']

            def delete_without_failing(key):
                try:
                    del elm['file'][lang][key]
                except KeyError:
                    pass

            delete_without_failing('reviewDate')
            delete_without_failing('review_date')
            delete_without_failing('reviewDecisionDate')
            delete_without_failing('reviewDecisionEvent')
            delete_without_failing('review_decision')
            delete_without_failing('review_decision_date')
            delete_without_failing('review_decision_notes')
            delete_without_failing('review_decision_event')
            delete_without_failing('review_status')
            delete_without_failing('review_indicator')
            delete_without_failing('dates')

            data = {
                'id': str(uuid5(ns_oid,
                    '%s/%s' % (lang, (elm['name'])[len(cfg.input_dir):])
                    )),
                'data': elm['file'][lang]
            }

            if data['data'].get('date_accepted', False):
                date_accepted = data['data'].pop('date_accepted')
                date_accepted = str_to_dt(date_accepted)
                data['dateAccepted'] = date_accepted
            else:
                data['dateAccepted'] = str_to_dt(cfg.default_date)

            data['status'] = get_status(data['data'].pop('entry_status', cfg.default_status))

            authoritative_source = {}
            if data['data'].get('authoritative_source', False):
                authoritative_source = data['data'].pop('authoritative_source')
            data['data']['authoritativeSource'] = [authoritative_source]

            if parse_specific:
                data = parse_specific(data)

            data['data']['definition'] = format_values(data['data'].get('definition', []))
            data['data']['notes'] = format_values(data['data'].get('notes', []))
            data['data']['examples'] = format_values(data['data'].get('examples', []))

            """
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
                data['data']['examples'] = _examples
            """

            universal['data']['localizedConcepts'][lang] = data['id']

            for source in data['data'].get('sources', []):
                if "(E), " in source.get("clause", ""):
                    source["clause"] = source["clause"].replace("(E), ", "")

            save_yaml(data['id'], 'localized-concept', data)

        save_yaml(elm['uuid'], 'concept', universal)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Convert data from old (concepts) to new yaml format.'
    )

    convert_concepts(parse_iev_specific)
