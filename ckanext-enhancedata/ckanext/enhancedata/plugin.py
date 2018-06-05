# -*- coding: utf-8 -*-
#Authors: Tommaso Galati (tommasogalati01@gmail.com) - Giovanni Cavallaro (cavaterza89@gmail.com)

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckanext.datapusher.interfaces import IDataPusher
import ckanext.datastore.logic as logicds
import ckan.logic as logic
from enhancevalidator import EnhanceValidate
import customAPI as CA
import math
import time
import json
import re
import os
import logging

log = logging.getLogger(__name__)

DEFAULT_DATA_FORMATS = ['xls', 'xlsx', 'csv']


# implements SingletonPlugin to create an extension
class EnhancedataPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IResourceView, inherit=True)
    plugins.implements(plugins.IResourceController, inherit=True)
    plugins.implements(plugins.interfaces.IActions)
    plugins.implements(IDataPusher)

    site_url = None
    validator = None
    storage_path = None

    # IConfigurer
    # configure directories and class variables
    def update_config(self, config_):
        log.debug('update_config')
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'enhancedata')
        self.site_url = config_.get('ckan.site_url', '')
        self.storage_path = config_.get('ckan.storage_path', '')
        self.validator = EnhanceValidate()

    # IResourceController
    # it's called before any resource create or update
    # current: current resource dict
    # resource: new resource dict
    # add or modify extra field (do_datapusher, datastore_active, categ, subcateg)
    def before_update(self, context, current, resource):
        if 'last_modified' not in resource:
            # update resource
            if 'do_datapusher' not in resource:
                # edit from interface
                if 'upload' in resource and resource['upload'] != '':
                    # new file to upload
                    resource['do_datapusher'] = 'true'
                    # print 'new file to upload'
                else:
                    # edit from interface without file change
                    resource['do_datapusher'] = 'false'
                    # print 'edit from interface'

                if 'categ' in current and current['categ'] != '':
                    resource['categ'] = current['categ']
                if 'subcateg' in current and current['subcateg'] != '':
                    resource['subcateg'] = current['subcateg']
            # elif 'do_datapusher' in resource and resource['do_datapusher'] == 'false':
            #     # save or pubblish
            #     print 'save or pubblish'

        if 'do_datapusher' not in resource:
            resource['do_datapusher'] = 'false'
        resource['datastore_active'] = True
        pass

    # IDataPusher interface
    # they are called only if file format is good; checking ckan.datapusher.formats in config option
    def can_upload(self, resource_id):
        try:
            context = {}
            # populate context variable
            logicds.action.datastore_search(context, {'resource_id': resource_id, 'limit': 1})
            resource_info = logic.action.get.resource_show(context, {'id': resource_id})
            if 'do_datapusher' not in resource_info or resource_info['do_datapusher'] == 'true':
                return True
            return False
        except:
            return True

    # IDataPusher interface
    # check if data is valid, improve, validate field and update resource into the DataStore
    # create EnhanceData view if needed
    def after_upload(self, context, resource_dict, dataset_dict):
        log.debug('after_upload')
        data_dict = {'resource_id': resource_dict['id'], 'title': 'EnhanceData View',
                     'view_type': 'enhancedata'}
        is_valid = (resource_dict.get('format', '').lower() in DEFAULT_DATA_FORMATS)
        # if the file is in a format allowed, check if it contains the mandatory columns
        res = logicds.action.datastore_search(context, {'resource_id': data_dict['resource_id'], 'limit': 1000000})

        is_valid_columns = False
        if is_valid:
            columns = res['records'][0]
            fields = res['fields']
            (is_valid_columns, _, _, _) = self.check_columns(columns, fields)
        if is_valid_columns:
            records = []
            id_list = []
            for rec in res['records']:
                rec_val = self.validator.do_record_validation(rec)
                id_list.append(rec['_id'])
                dict_to_validate_for_insert = {}  # create a dict without 'valid' fields
                for r in rec_val:
                    dict_to_validate_for_insert[r] = rec_val[r]['value']
                obj = self.validator.validate_record_format_for_insert(dict_to_validate_for_insert, fields)
                records.append(obj)
            logicds.action.datastore_delete(context, {'resource_id': data_dict['resource_id'], 'force': True,
                                                      'filters': {'_id': id_list}})
            logicds.action.datastore_upsert(context, {'resource_id': data_dict['resource_id'], 'force': True,
                                                      'method': 'insert', 'records': records})
            if len(logic.action.get.resource_view_list(context, {'id': data_dict['resource_id']})) == 0:
                logic.action.create.resource_view_create(context, data_dict)
        else:
            if len(logic.action.get.resource_view_list(context, {'id': data_dict['resource_id']})) == 0:
                logic.action.create.resource_view_create(context, data_dict)
        pass

    # IResourceView interface
    # info about EnhanceData view
    def info(self):
        return {'name': 'enhancedata',
                'title': plugins.toolkit._('EnhanceData'),
                'icon': 'gamepad',
                'iframed': False,
                'always_available': True,
                'default_title': plugins.toolkit._('EnhanceData'),
                }

    def get_json_from_virtuoso(self):
        class_options, cateng_options = self.validator.get_options()
        return class_options, cateng_options

    # get city list, province list and postalcode list from city_objects.json
    def get_data_lists(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        json_data = open(current_path + '/public/city_objects.json').read()
        json_data = unicode(json_data, errors='replace')
        json_dict = json.loads(json_data)
        city_list = []
        province_list = set()
        postalcode_list = []
        for obj in json_dict['list']:
            city_list.append(obj['city'])
            province_list.add(obj['province'])
            postalcode_list.extend(obj['postalcode'])
        postalcode_list = list(set(postalcode_list))
        return sorted(city_list), sorted(list(province_list)), sorted(postalcode_list)

    # IResourceView interface
    # send proper data to html template when resource is opened by users
    # if resource is not valid, show error message and enable template download
    def setup_template_variables(self, context, data_dict):
        resource_id = data_dict['resource']['id']
        search_success = False
        counter = 0
        # wait in case of DataStore upload
        while not search_success and counter < 50:
            try:
                res = logicds.action.datastore_search(context, {'resource_id': resource_id, 'limit': 1000000})
                search_success = True
            except:
                print 'sleeping... wait for rows in datastore'
                counter += 1
                time.sleep(3)

        columns = res['records'][0]
        fields = res['fields']
        is_valid, wrong_field, missing_field, wrong_type = self.check_columns(columns, fields)
        if is_valid:
            try:
                current_user = logic.action.get.user_show(context, {'id': context['user']})
                api_key = current_user['apikey']
                if len(logic.action.get.organization_list_for_user(context, {'permission': 'update_dataset'})) == 0:
                    api_key = ''
            except Exception as e:
                print str(e)
                api_key = ''
            record_to_render = []
            id_list = []
            class_options, cateng_options = self.get_json_from_virtuoso()
            class_options_mod = list(class_options)
            for idx, el in enumerate(class_options_mod):
                class_options_mod[idx] = re.sub("([a-z])([A-Z])",  "\g<1> \g<2>", el)
                class_options_mod[idx] = class_options_mod[idx].replace('_', ' ')

            city_list, province_list, postalcode_list = self.get_data_lists()

            actual_categ = ''
            actual_subcateg = ''
            if 'categ' in data_dict['resource']:
                actual_categ = data_dict['resource']['categ']
            if 'subcateg' in data_dict['resource']:
                actual_subcateg = data_dict['resource']['subcateg']

            offset = 15
            num_pages = int(math.ceil(len(res['records'])/float(offset)))

            records_list = sorted(res['records'][0:offset], key=lambda k: k['_id'])
            for rec in records_list:
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

                rec_to_append = self.validator.do_record_validation(rec)
                record_to_render.append(rec_to_append)
                id_list.append(rec['_id'])

            subcat = []
            for item in cateng_options:
                subcat.extend(cateng_options[item])
            subcat_mod = list(subcat)
            for idx, el in enumerate(subcat_mod):
                subcat_mod[idx] = re.sub("([a-z])([A-Z])",  "\g<1> \g<2>", el)
                subcat_mod[idx] = subcat_mod[idx].replace('_', ' ')

            return {'user_key': api_key, 'resource_id': resource_id, 'records': record_to_render,
                    'records_id': id_list, 'num_pages': num_pages, 'package_id': data_dict['resource']['package_id'],
                    'class_original': sorted(class_options), 'class_modified': sorted(class_options_mod),
                    'cateng_original': sorted(subcat), 'cateng_modified': sorted(subcat_mod), 'urlckan': self.site_url,
                    'city_list': city_list, 'province_list': province_list, 'postalcode_list': postalcode_list,
                    'actual_categ': actual_categ, 'actual_subcateg': actual_subcateg,
                    'is_valid': 'true'}
        else:
            return {'is_valid': 'false', 'wrong_field': wrong_field,
                    'missing_field': missing_field, 'wrong_type': wrong_type}

    # IResourceView interface
    def view_template(self, context, data_dict):
        return 'enhanceview.html'

    # Registers the custom API method defined above
    def get_actions(self):
        return {'get_options': CA.get_options, 'validate_class': CA.validate_class,
                'validate_categoryEng': CA.validate_categoryEng, 'validate_mail': CA.validate_mail,
                'validate_url': CA.validate_url, 'validate_latitude': CA.validate_latitude,
                'validate_longitude': CA.validate_longitude, 'validate_province': CA.validate_province,
                'validate_prefix': CA.validate_prefix, 'validate_city': CA.validate_city,
                'validate_postalcode': CA.validate_postalcode, 'validate_phonenumber': CA.validate_phonenumber,
                'upsertdata': CA.upsertdata, 'get_pagination_data': CA.get_pagination_data,
                'get_toponimo': CA.get_toponimo}

    # check if the file contains all columns
    # if you want to add a constraint, add
    #   "and 'new_columns_to_check' in columns"
    # at the end of the if expression
    # if you want to change a column name, simply change its name in the if expression
    # if you want to delete a column constraint, simply delete the
    #   "and 'columns_to_delete' in columns" in the if expression
    def check_columns(self, columns, fields):
        wrong_field = []
        missing_field = []
        wrong_type = {}
        # check columns types
        for f in fields:
            if f['id'] == 'latitude' and f['type'] == 'timestamp':
                wrong_type['latitude'] = 'i valori di questo campo non devono contenere virgole'
            if f['id'] == 'longitude' and f['type'] == 'timestamp':
                wrong_type['longitude'] = 'i valori di questo campo non devono contenere virgole'
            # if f['id'] == 'civicNumber' and f['type'] == 'numeric':
            #     wrong_type['civicNumber'] = 'questo campo deve essere formattato come testo'
            # if f['id'] == 'secondCivicNumber' and f['type'] == 'numeric':
            #     wrong_type['secondCivicNumber'] = 'questo campo deve essere formattato come testo'

        if 'otherCategoryITA' in columns and 'otherCategoryENG' in columns and 'nameITA' in columns and \
                'nameENG' in columns and 'abbreviationITA' in columns and 'abbreviationENG' in columns and \
                'descriptionShortITA' in columns and 'descriptionShortENG' in columns and \
                'descriptionLongITA' in columns and 'descriptionLongENG' in columns and \
                'phone' in columns and 'fax' in columns and 'url' in columns and 'email' in columns and \
                'RefPerson' in columns and 'province' in columns and 'city' in columns and 'postalcode' in columns and \
                'streetAddress' in columns and 'civicNumber' in columns and 'secondPhone' in columns and \
                'secondFax' in columns and 'secondEmail' in columns and 'secondCivicNumber' in columns and \
                'secondStreetAddress' in columns and 'notes' in columns and 'timetable' in columns and \
                'photo' in columns and 'latitude' in columns and 'longitude' in columns and 'streetId' in columns and \
                not bool(wrong_type):
            is_valid = True
        else:
            key_list = ['otherCategoryITA', 'otherCategoryENG', 'nameITA', 'nameENG', 'abbreviationITA',
                        'abbreviationENG', 'descriptionShortITA', 'descriptionShortENG', 'descriptionLongITA',
                        'descriptionLongENG', 'phone', 'fax', 'url', 'email', 'RefPerson', 'province', 'city',
                        'postalcode', 'streetAddress', 'civicNumber', 'secondPhone', 'secondFax', 'secondEmail',
                        'secondCivicNumber', 'secondStreetAddress', 'notes', 'timetable', 'photo', 'latitude',
                        'longitude', 'streetId']
            # search wrong keys (case insensitive)
            for k in key_list:
                if k not in columns:
                    cols = [c.lower() for c in columns]
                    if k.lower() in cols:
                        wrong_field.append(k)

            # search missing keys
            for k in key_list:
                if k not in columns and k not in wrong_field:
                    missing_field.append(k)

            is_valid = False
        return is_valid, wrong_field, missing_field, wrong_type
