from benedict import benedict
from utils import set_str, set_lst, str_to_dt, convert_stem


def iev(data):

    d = benedict(data, keypath_separator='/')

    # convert_stem:
    d = set_str('data/definition', d, convert_stem)
    d = set_str('data/designation', d, convert_stem)
    d = set_lst('data/notes', d, convert_stem)
    d = set_lst('data/examples', d, convert_stem)

    terms = []
    for elm in d.get_list('data/terms'):
        term_designation = elm.get('designation', False)
        if term_designation:
            elm['designation'] = convert_stem(elm['designation'])
        terms.append(elm)
    del term_designation

    if terms:
        d['data/terms'] = terms
    del terms

    # convert dates:
    if 'data/review_date' in d:
        d = set_str('data/review_date', d, str_to_dt)
        d.rename('data/review_date', 'data/reviewDate')

    if 'data/review_decision_date' in d:
        d = set_str('data/review_decision_date', d, str_to_dt)
        d.rename('data/review_decision_date', 'data/reviewDecisionDate')

    if 'data/review_decision_event' in d:
        d.rename('data/review_decision_event', 'data/reviewDecisionEvent')

    if 'data/date_amended' in d:
        d = set_str('data/date_amended', d, str_to_dt)
        d.rename('data/date_amended', 'data/dateAmended')

    return d.dict()
