import base64
from datetime import datetime, timedelta
import mimetypes

import dateutil.parser
from django.template import Context
from django.utils.timezone import localdate, make_aware
import pkg_resources

def _parse_date_string(s, default=None):
    if s:
        return dateutil.parser.parse(s)
    else:
        return default


def image_as_data_url(path):
    data = pkg_resources.resource_string('idm_card', path)
    content_type = mimetypes.guess_type(path)[0]
    return 'data:{};base64,{}'.format(content_type,
                                      base64.b64encode(data).decode())


def affiliation_sort_key(affiliation):
    tags = set(affiliation['organization']['tags'])

    if 'unit' not in tags:
        return 10

    type_group = affiliation['type_id'].split(':')[0]
    if type_group in ('staff', 'student'):
        if 'college' in tags or 'pph' in tags:
            return 1
        else:
            return 0
    elif type_group in ('reader',):
        return 2
    else:
        return 3

def get_card_context(identity, card_number, sequence_number):
    affiliations = identity['affiliations']

    primary_affiliation = None
    bodleian_affiliation, congregation_affiliation = None, None
    university_card = False

    datetime_min = make_aware(datetime.min + timedelta(365))
    datetime_max = make_aware(datetime.max - timedelta(365))

    max_end = datetime_min

    affiliations = sorted(identity['affiliations'], key=affiliation_sort_key)
    affiliations = [a for a in affiliations
                    if a['state'] in ('upcoming', 'suspended', 'active')
                    and a['type_id'].split(':')[0] in ('student', 'staff', 'retiree', 'reader')
                    and 'unit' in a['organization']['tags']]

    print(affiliations)

    for affiliation in affiliations:
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

    if primary_affiliation['type_id'].split(':')[0] == 'student' and \
            not ({'pph', 'college'} & set(primary_affiliation['organization']['tags'])):
        for affiliation in affiliations:
            if affiliation['type_id'].split(':')[0] == 'student' and \
                    ({'pph', 'college'} & set(affiliation['organization']['tags'])):
                primary_affiliation['college'] = affiliation['organization']
                break

    context = Context({
        'identity': identity,
        'primary_affiliation': primary_affiliation,
        'bodleian_affiliation': bodleian_affiliation,
        'congregation_affiliation': congregation_affiliation,
        'university_card': university_card,
        'max_expiry': max_end,
        'card_number': card_number,
        'sequence_number': sequence_number,
        'bodleian_logo': image_as_data_url('data/bodleian-logo.jpg'),
        'oxford_logo': image_as_data_url('data/ox_brand1_pos.gif'),
    })
    return context