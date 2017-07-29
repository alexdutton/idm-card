from datetime import datetime, timedelta

import dateutil.parser
from django.template import Context
from django.utils.timezone import localdate, make_aware


def _parse_date_string(s, default=None):
    if s:
        return dateutil.parser.parse(s)
    else:
        return default


def get_card_context(identity, card_number):
    affiliations = identity['affiliations']

    primary_affiliation = None
    bodleian_affiliation, congregation_affiliation = None, None
    university_card = False

    datetime_max = make_aware(datetime.max - timedelta(365))

    max_end = datetime_max

    for affiliation in identity['affiliations']:
        tags = affiliation['organization']['tags']
        print(affiliation)
        if affiliation['type_id'] == 'reader' and 'bodleian' in tags:
            bodleian_affiliation = affiliation
        if affiliation['type_id'] == 'member' and 'congregation' in tags:
            congregation_affiliation = affiliation
        if 'unit' not in tags:
            continue

        if affiliation['type_id'].startswith('student:') or affiliation['type_id'].startswith('reader:'):
            university_card = True

        if not primary_affiliation:
            primary_affiliation = affiliation

        max_end = max(max_end,
                      min(_parse_date_string(affiliation['review_date'], datetime_max),
                          _parse_date_string(affiliation['end_date'], datetime_max)))

    import pprint; pprint.pprint(max_end)

    context = Context({
        'identity': identity,
        'primary_affiliation': primary_affiliation,
        'bodleian_affiliation': bodleian_affiliation,
        'congregation_affiliation': congregation_affiliation,
        'university_card': university_card,
        'max_expiry': max_end,
        'card_number': card_number,
    })
    return context