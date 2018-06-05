# -*- coding: utf-8 -*-
#Authors: Tommaso Galati (tommasogalati01@gmail.com) - Giovanni Cavallaro (cavaterza89@gmail.com)

import ckan.plugins.toolkit as toolkit
import ckanext.datastore.logic as logicds
import ckan.logic as logic
from enhancevalidator import EnhanceValidate
import unicodecsv as csv
import urllib
import urllib2
import time
import sys
import re
import os

validator = EnhanceValidate()

# if you want to add a REST API, you have to implement it here using @toolkit.side_effect_free decorator
# and then add it to get_actions() list in "plugin.py"

@toolkit.side_effect_free
def get_toponimo(context, data_dict):
    results = validator.get_toponimo(data_dict['latitude'], data_dict['longitude'])
    return results


# Required so that GET requests work
@toolkit.side_effect_free
def upsertdata(context, data_dict=None):
    reload(sys)
    sys.setdefaultencoding('utf-8')
    ds_search = logicds.action.datastore_search(context, {'resource_id': data_dict['resource_id'], 'limit': 1})
    fields = ds_search['fields']
    records = []
    new_ids = []
    for res in data_dict['records']:
        obj = validator.validate_record_format_for_insert(res, fields)
        records.append(obj)
    logicds.action.datastore_upsert(context, {'resource_id': data_dict['resource_id'],
                                              'force': True, 'method': data_dict['method'],
                                              'records': records})

    delete = logicds.action.datastore_delete(context, {'resource_id': data_dict['resource_id'],
                                                       'force': True, 'filters':  data_dict['filters']})
    if delete['filters']['_id'] is [] or delete['filters']['_id'] is None:
        return 'delete error', new_ids

    logic.action.update.resource_update(context, {'id': data_dict['resource_id'], 'url': '___',
                                                  'package_id': data_dict['package_id'],
                                                  'categ': data_dict['category'],
                                                  'subcateg': data_dict['subcategory'],
                                                  'datastore_active': True,
                                                  'do_datapusher': 'false'})

    new_rows = logicds.action.datastore_search(context, {'resource_id': data_dict['resource_id'], 'limit': 1000000})
    for r in new_rows['records']:
        new_ids.append(r['_id'])

    if not data_dict['saveCurrentState']:
        # save csv file
        inner_dir = ''
        public_dir = ''
        post_url = ''
        current_path = os.path.dirname(os.path.abspath(__file__))
        with open(current_path + '/public/config.csv', 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in reader:
                if row[0] == 'innerdirectory':
                    inner_dir = row[1]
                if row[0] == 'outerdirectory':
                    public_dir = row[1]
                if row[0] == 'posturl':
                    post_url = row[1]
        if inner_dir[-1] != '/':
            inner_dir += '/'
        if public_dir[-1] != '/':
            public_dir += '/'

        package_info = logic.action.get.package_show(context, {'id': data_dict['package_id']})
        dataset_name = package_info['title'].replace(' ', '').replace('-', '_')
        organization = package_info['organization']['title'].replace(' ', '').replace('-', '_')
        file_name = data_dict['filename'].replace('.csv', '').replace('.xlsx', '').replace('.xls', '').replace(' ', '').replace('-', '_')
        ckan_url = data_dict['ckan_url']
        license_id = package_info['license_id']
        if 'license_url' in package_info:
            license_url = package_info['license_url']
        else:
            license_url = ''
        package_description = package_info['notes']

        process_name = organization + '_' + dataset_name + '_' + file_name
        subdirs = time.strftime('%Y_%m/%d/%H/%M%S/')
        file_dir = inner_dir + process_name + '/' + subdirs
        actual_filename = file_name + '.csv'
        try:
            os.makedirs(file_dir)
            with open(file_dir + actual_filename, 'wb') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL, encoding='utf-8')
            key_list = ['subcategory', 'otherCategoryITA', 'otherCategoryENG', 'nameITA', 'nameENG', 'abbreviationITA',
                        'abbreviationENG', 'descriptionShortITA', 'descriptionShortENG', 'descriptionLongITA',
                        'descriptionLongENG', 'phone', 'fax', 'url', 'email', 'RefPerson', 'province', 'city', 'postalcode',
                        'streetAddress', 'civicNumber', 'secondPhone', 'secondFax', 'secondEmail', 'secondCivicNumber',
                        'secondStreetAddress', 'notes', 'timetable', 'photo', 'latitude', 'longitude', 'streetId']
            # write keys
            with open(file_dir + actual_filename, 'a') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL, encoding='utf-8')
                spamwriter.writerow(key_list)
            for rec in records:
                row = []
                row.append(data_dict['subcategory'])

                # find civicNumber and secondCivicNumber in notes and write correct data
                if rec['notes'] is not None:
                    cnStart = rec['notes'].find('[[civicNumber:')
                    cnEnd = rec['notes'].find('-]]')
                    if cnStart != -1 and cnEnd != -1:
                        rec['civicNumber'] = rec['notes'][cnStart+14:cnEnd]
                        rec['notes'] = rec['notes'][0:cnStart] + rec['notes'][cnEnd+3:]

                    scnStart = rec['notes'].find('[[secondCivicNumber:')
                    scnEnd = rec['notes'].find('+]]')
                    if scnStart != -1 and scnEnd != -1:
                        rec['secondCivicNumber'] = rec['notes'][scnStart+20:scnEnd]
                        rec['notes'] = rec['notes'][0:scnStart] + rec['notes'][scnEnd+3:]

                for key in key_list[1:]:
                    row.append(rec[key])
                with open(file_dir + actual_filename, 'a') as csvfile:
                    spamwriter = csv.writer(csvfile, delimiter=';',
                                            quotechar='"', quoting=csv.QUOTE_ALL, encoding='utf-8')
                    spamwriter.writerow(row)
        except Exception as e:
            print str(e)
            return 'csv error', new_ids

        # make post request
        param = public_dir + process_name + '/' + subdirs + actual_filename
        values = {'process': process_name, 'access': 'HTTP', 'format': 'csv', 'category': 'CKAN',
                  'license_id': license_id, 'license_url': license_url,
                  'description': package_description, 'source': ckan_url, 'param': param}
        data = urllib.urlencode(values)

        try:
            resp = urllib2.urlopen(post_url, data)
            resp_code = resp.getcode()
            if resp_code != 200:
                return 'post error', new_ids
        except urllib2.URLError as e:
            print str(e)
            return 'post error', new_ids

    return 'done', new_ids


@toolkit.side_effect_free
def get_options(context, data_dict=None):
    class_options, cateng_options = validator.get_options()
    return {'class_options': class_options, 'cateng_options': cateng_options}


@toolkit.side_effect_free
def validate_class(context, data_dict=None):
    dict_options = get_options(context, data_dict)
    cateng_options = validator.validate_class(data_dict['Category'], dict_options['cateng_options'])
    cateng_options_mod = list(cateng_options)
    for idx, el in enumerate(cateng_options_mod):
        cateng_options_mod[idx] = re.sub("([a-z])([A-Z])", "\g<1> \g<2>", el)
        cateng_options_mod[idx] = cateng_options_mod[idx].replace('_', ' ')
    return {'cateng_original': sorted(cateng_options), 'cateng_modified': sorted(cateng_options_mod)}


@toolkit.side_effect_free
def validate_categoryEng(context, data_dict=None):
    cat_name = data_dict['cat_name']
    class_name = validator.validate_categoryEng(cat_name)
    class_name_mod = list(class_name)
    for idx, el in enumerate(class_name_mod):
        class_name_mod[idx] = re.sub("([a-z])([A-Z])", "\g<1> \g<2>", el)
        class_name_mod[idx] = class_name_mod[idx].replace('_', ' ')
    return {'class_original': class_name, 'class_modified': sorted(class_name_mod)}


@toolkit.side_effect_free
def validate_mail(context, data_dict=None):
    mail_list, mail_valid = validator.validate_mail(data_dict['email'])
    return {'value': mail_list[0], 'valid': mail_valid[0]}


@toolkit.side_effect_free
def validate_url(context, data_dict=None):
    url_valid = validator.control_url(data_dict['url'])
    return {'value': data_dict['url'], 'valid': url_valid}


@toolkit.side_effect_free
def validate_latitude(context, data_dict=None):
    data_dict['latitude'] = str(data_dict['latitude'].replace(',', '.'))
    lat_match = validator.validate_lat(data_dict['latitude'])
    if lat_match is not None:
        return {'value': data_dict['latitude'], 'valid': 1}
    else:
        return {'value': data_dict['latitude'], 'valid': 2}


@toolkit.side_effect_free
def validate_longitude(context, data_dict=None):
    data_dict['longitude'] = str(data_dict['longitude'].replace(',', '.'))
    lon_match = validator.validate_lon(data_dict['longitude'])
    if lon_match is not None:
        return {'value': data_dict['longitude'], 'valid': 1}
    else:
        return {'value': data_dict['longitude'], 'valid': 2}


@toolkit.side_effect_free
def validate_prefix(context, data_dict=None):
    prefix = validator.get_prov_by_prefix(data_dict['prefix'])
    return {'prefix': prefix}


@toolkit.side_effect_free
def validate_province(context, data_dict=None):
    cities_list, postalcode_list, district_list = validator.get_data_by_prov(data_dict['province'].upper())
    return {'cities_list': cities_list, 'postalcode_list': postalcode_list, 'district_list': district_list}


@toolkit.side_effect_free
def validate_city(context, data_dict=None):
    province, postalcode_list, district_list = validator.get_data_by_city(data_dict['city'].upper())
    return {'province': province, 'postalcode_list': postalcode_list, 'district_list': district_list}


@toolkit.side_effect_free
def validate_postalcode(context, data_dict=None):
    province, city, district_list = validator.get_data_by_postalcode(data_dict['postalcode'])
    return {'province': province, 'city': city, 'district_list': district_list}


@toolkit.side_effect_free
def validate_phonenumber(context, data_dict=None):
    phone_valid, phone_number = validator.parse_phone(data_dict['phone'])
    return {'value': phone_number, 'valid': phone_valid}


@toolkit.side_effect_free
def get_pagination_data(context, data_dict=None):
    res = logicds.action.datastore_search({}, {'resource_id': data_dict['resource_id'],
                                               'offset': data_dict['offset'], 'limit': 15})
    record_to_render = []
    id_list = []
    for rec in res['records']:
        # find civicNumber and secondCivicNumber in notes and write correct data
        if rec['notes'] is not None:
            cnStart = rec['notes'].find('[[civicNumber:')
            cnEnd = rec['notes'].find('-]]')
            if cnStart != -1 and cnEnd != -1:
                rec['civicNumber'] = rec['notes'][cnStart + 14:cnEnd]
                rec['notes'] = rec['notes'][0:cnStart] + rec['notes'][cnEnd + 3:]

            scnStart = rec['notes'].find('[[secondCivicNumber:')
            scnEnd = rec['notes'].find('+]]')
            if scnStart != -1 and scnEnd != -1:
                rec['secondCivicNumber'] = rec['notes'][scnStart + 20:scnEnd]
                rec['notes'] = rec['notes'][0:scnStart] + rec['notes'][scnEnd + 3:]

        rec_to_append = validator.do_record_validation(rec)
        record_to_render.append(rec_to_append)
        id_list.append(rec['_id'])
    return {'record_to_render': record_to_render, 'records_id': id_list}
