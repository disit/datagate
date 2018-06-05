# -*- coding: utf-8 -*-
#Authors: Tommaso Galati (tommasogalati01@gmail.com) - Giovanni Cavallaro (cavaterza89@gmail.com)

import validators
import phonenumbers as pn
from phonenumbers import carrier
from jinja2 import utils
import urllib
import json
import sys
import re
import os


class EnhanceValidate:

    def __init__(self):
        pass

    # get categories and subcategories using sparql queries
    def get_options(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        category_file = open(current_path + "/public/category_sparql.txt", "r")
        class_url = category_file.read()
        category_file.close()
        subcategory_file = open(current_path + "/public/subcategory_sparql.txt", "r")
        category_eng_url = subcategory_file.read()
        subcategory_file.close()
        fileobj_class = urllib.urlopen(class_url)
        fileobj_cateng = urllib.urlopen(category_eng_url)
        json_class = json.loads(fileobj_class.read())
        class_list = []
        for macroclass in json_class['results']['bindings']:
            class_list.append(macroclass['macroClass']['value'])
        class_list = sorted(class_list)

        json_cateng = json.loads(fileobj_cateng.read())
        cateng_list = {}
        for macroclass in class_list:
            cateng_list.update({macroclass: []})
        for el in json_cateng['results']['bindings']:
            cateng_list[el['macroClass']['value']].append(el['subClass']['value'])

        for key in cateng_list:
            cateng_list[key] = sorted(cateng_list[key])

        return class_list, cateng_list

    # validate category
    def validate_class(self, class_name, cateng_options):
        if class_name == 'empty':
            new_list = []
            for c in cateng_options:
                new_list.extend(cateng_options[c])
            return new_list
        else:
            return cateng_options[class_name]

    # validate subcategory
    def validate_categoryEng(self, cat_name):
        (_, cateng_list) = self.get_options()
        for el in cateng_list:
            if cat_name in cateng_list[el]:
                return el

    # validate mail and a "mails" list with corresponding validity values in "valids" list
    def validate_mail(self, mail):
        # search with regex: separate mail even with one or more of these separators: space, semicolon, comma, dash
        list_mail = re.findall(r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+[^,|;|-| ])", mail)
        mails = []
        valids = []
        # valid first mail
        if len(list_mail) != 0:
            mails.append(list_mail[0])
            if validators.email(list_mail[0]):
                valids.append(1)
            else:
                valids.append(2)

            # valid second mail
            if len(list_mail) > 1:
                mails.append(list_mail[1])
                if validators.email(list_mail[1]):
                    valids.append(1)
                else:
                    valids.append(2)

                # append other mails
                if len(list_mail) > 2:
                    for l in range(2, len(list_mail)):
                        mails.append(list_mail[l])
        else:
            mails.append(mail)
            valids.append(0)
        return mails, valids

    # quality improvement and url validator
    def validate_url(self, url, is_url):
        reload(sys)
        sys.setdefaultencoding('utf-8')
        url = url.replace('-com', '.com')
        url = url.replace('.co', '.com')
        url = url.replace('.comm', '.com')
        url = url.replace(':com', '.com')
        url = url.replace(':.com', '.com')
        url = url.replace('.com.', '.com')

        url = url.replace('-it', '.it')
        url = url.replace('.i .t', '.it')
        url = url.replace('.i.t', '.it')
        url = url.replace(':it', '.it')
        url = url.replace(':.it', '.it')
        url = url.replace('.it.', '.it')

        url = url.replace('-org', '.org')
        url = url.replace(':org', '.org')
        url = url.replace(':.org', '.org')
        url = url.replace('.org.', '.org')

        url = url.replace('http://http://', 'http://')
        url = url.replace('https://https://', 'https://')

        url = url.replace('www.:', 'www.')
        url = url.replace('www..', 'www.')
        url = url.replace('www.www', 'www.')

        url = url.strip()
        url = url.replace('\'', '')
        url = url.replace('à', 'a')
        url = url.replace('è', 'e')
        url = url.replace('é', 'e')
        url = url.replace('ì', 'i')
        url = url.replace('ò', 'o')
        url = url.replace('ù', 'u')

        first_url = url
        second_url = ''
        if is_url:
            first_url, second_url = self.separate_urls(url)
            if second_url != '':
                second_url = 'Alternative url(s): ' + second_url

        if first_url.find('http://') == -1 and first_url.find('https://') == -1:
            if first_url != '':
                first_url = 'http://' + first_url
            else:
                first_url = first_url

        valid = self.control_url(first_url)

        return valid, first_url, second_url

    def control_url(self, url):
        try:
            valid = validators.url(url, True)
            if valid is not None:
                regex = re.compile(
                    r'^(?:http|ftp)s?://'  # http:// or https://
                    r'(?:(?:[A-Z0-9](?:[A-Z 0-9-]{0,61}[A-Z 0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain... 
                    r'localhost|'  # localhost...
                    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                    r'(?::\d+)?'  # optional port
                    #r'(?:/?|[/?]\S+)$', re.IGNORECASE) 
                    r'(?:/?|[/?].+)$', re.IGNORECASE)
                if re.match(regex, url) is not None:
                    return 1
                else:
                    return 2
            else:
                return 2
        except:
            return 2

    def separate_urls(self, url):
        url = url.strip()
        extensionsToCheck = ['ftp', 'http://www.', 'https://www.', 'http', 'www.']

        for ext in extensionsToCheck:
            if url.find(ext, 9) != -1:
                position = url.find(ext, 9)
                second_url = url[position:].strip()
                if second_url != '':
                    first_url = url[0:position]
                    fr, sd = self.separate_urls(second_url)
                    return first_url.strip(), fr + ' ' + sd
                else:
                    return url.strip(), ''

        return url.strip(), ''

    def validate_wsg84(self, lat, lon):
        # check existence of one or both
        lat_match = self.validate_lat(lat)
        lon_match = self.validate_lon(lon)
        if lat_match is None:
            lat_valid = 2
        else:
            lat_valid = 1
        if lon_match is None:
            lon_valid = 2
        else:
            lon_valid = 1
        return lat, lon, lat_valid, lon_valid
        
    def validate_lat(self, lat):
        lat_regex = r"^([1-8]?[1-9]|[1-9]0)\.{1}\d{1,15}$"
        lat_match = re.match(lat_regex, lat)
        return lat_match

    def validate_lon(self, lon):
        lon_regex = r"^([1]?[1-7][1-9]|[1]?[1-8][0]|[1-9]?[0-9])\.{1}\d{1,15}$"
        lon_match = re.match(lon_regex, lon)
        return lon_match

    # phone Quality Improvement
    # return phone list and validity value corresponding list
    def validate_phone(self, phone):
        if phone[0:3] == '+39':
            phone = phone[3:]
        phone_list = []
        phone_to_return = []
        valid_to_return = []
        if len(phone) > 12:  # threshold for two numbers
            while phone.find(' ', 5) != -1:
                separator_pos = phone.find(' ', 5)
                phone_list.append(phone[0:separator_pos])
                phone = phone[separator_pos+1:]
                if phone[0:3] == '+39':
                    phone = phone[3:]
                if phone[0] == ' ':
                    phone = phone[1:]
                if len(phone) < 12:
                    phone_list.append(phone)
        if not phone_list:
            phone_list.append(phone)
        for ph in phone_list:
            if ph.find('-') != -1 or ph.find('/') != -1:
                sep_pos = ph.find('-')
                if sep_pos == -1:
                    sep_pos = ph.find('/')
                num_digit = len(ph[sep_pos + 1:])
                ph_1 = ph[0:sep_pos]
                ph_2 = ph[0:sep_pos - num_digit] + ph[sep_pos + 1:]
                phone_list.append(ph_1)
                phone_list.append(ph_2)
            else:
                ph = ph.replace(' ', '')
                ph_valid, ph_num = self.parse_phone(ph)
                phone_to_return.append(ph_num)
                valid_to_return.append(ph_valid)

        return phone_to_return, valid_to_return

    # validate phone number
    def parse_phone(self, phone):
        try:
            parsed = pn.parse(phone, 'IT')
            if pn.is_possible_number(parsed):
                # if carrier.name_for_number(parsed, "it") == '' and phone[0] != '0':
                    # phone = '0' + phone
                return 1, phone
            else:
                return 2, phone
        except:
            return 2, phone

    def get_prov_by_prefix(self, prefix):
        current_path = os.path.dirname(os.path.abspath(__file__))
        json_data = open(current_path + '/public/prefix_prov.json').read()
        json_data = unicode(json_data, errors='replace')
        json_dict = json.loads(json_data)
        return json_dict['prefix']

    def get_data_by_prov(self, province):
        # return list of cities, postalcode and districts given a province
        current_path = os.path.dirname(os.path.abspath(__file__))
        json_data = open(current_path + '/public/city_objects.json').read()
        json_data = unicode(json_data, errors='replace')
        json_dict = json.loads(json_data)
        cities_list = []
        postalcode_list = []
        district_list = []
        for obj in json_dict['list']:
            if obj['province'] == province:
                cities_list.append(obj['city'])
                postalcode_list.extend(obj['postalcode'])
                district_list.extend(obj['district'])
        return cities_list, postalcode_list, district_list

    def get_data_by_city(self, city):
        # return province, list of postal code and list of districts given a city
        current_path = os.path.dirname(os.path.abspath(__file__))
        json_data = open(current_path + '/public/city_objects.json').read()
        json_data = unicode(json_data, errors='replace')
        json_dict = json.loads(json_data)
        province = ''
        postalcode_list = []
        district_list = []
        for obj in json_dict['list']:
            if obj['city'] == city:
                province = obj['province']
                postalcode_list.extend(obj['postalcode'])
                district_list.extend(obj['district'])
                break
        return province, postalcode_list, district_list

    def get_data_by_postalcode(self, postalcode):
        # return city, province and list of districts given a postalcode
        current_path = os.path.dirname(os.path.abspath(__file__))
        json_data = open(current_path + '/public/city_objects.json').read()
        json_data = unicode(json_data, errors='replace')
        json_dict = json.loads(json_data)
        province = ''
        city = ''
        district_list = []

        for obj in json_dict['list']:
            if postalcode in obj['postalcode']:
                province = obj['province']
                city = obj['city']
                district_list.extend(obj['district'])
                break
        return province, city, district_list

    # validate a single row
    # it returns a dict (rec_to_append) containing for each column a dict: {'value': validated_value, 'valid': x}
    # "value" key contains the validated value, so if you want to add a specific validation function,
    #   you have to write it in this file
    # "valid" key contains a int value that can be 0, 1 or 2
    #   0: the field does not need a specific validation
    #   1: the field has been validated successfully, the user will see a green box around the cell in the table view
    #   2: the field contains an error, the user will see a red box around the cell in the table view
    # if you want to add a new column add an if clause like the ones in this functions
    # if you want to change or delete a column constraint simply change it here
    def do_record_validation(self, rec):
        rec_to_append = {}
        # validation process

        # otherCategoryITA, otherCategoryENG
        if 'otherCategoryITA' in rec and rec['otherCategoryITA'] is not None:
            rec_to_append['otherCategoryITA'] = {'value': rec['otherCategoryITA'].strip(), 'valid': 0}
        else:
            rec_to_append['otherCategoryITA'] = {'value': '', 'valid': 0}
        if 'otherCategoryENG' in rec and rec['otherCategoryENG'] is not None:
            rec_to_append['otherCategoryENG'] = {'value': rec['otherCategoryENG'].strip(), 'valid': 0}
        else:
            rec_to_append['otherCategoryENG'] = {'value': '', 'valid': 0}

        # nameITA, nameENG, abbreviationITA, abbreviationENG
        if 'nameITA' in rec and rec['nameITA'] != '' and rec['nameITA'] is not None:
            rec_to_append['nameITA'] = {'value': rec['nameITA'].strip().upper(), 'valid': 1}
        else:
            rec_to_append['nameITA'] = {'value': '', 'valid': 2}
        if 'nameENG' in rec and rec['nameENG'] != '' and rec['nameENG'] is not None:
            rec_to_append['nameENG'] = {'value': rec['nameENG'].strip().upper(), 'valid': 0}
        else:
            rec_to_append['nameENG'] = {'value': '', 'valid': 0}
        if 'abbreviationITA' in rec and rec['abbreviationITA'] != '' and rec['abbreviationITA'] is not None:
            rec_to_append['abbreviationITA'] = {'value': rec['abbreviationITA'].strip().upper(), 'valid': 0}
        else:
            rec_to_append['abbreviationITA'] = {'value': '', 'valid': 0}
        if 'abbreviationENG' in rec and rec['abbreviationENG'] != '' and rec['abbreviationENG'] is not None:
            rec_to_append['abbreviationENG'] = {'value': rec['abbreviationENG'].strip().upper(), 'valid': 0}
        else:
            rec_to_append['abbreviationENG'] = {'value': '', 'valid': 0}

        # descriptionShortITA, descriptionShortENG, descriptionLongITA, descriptionLongENG
        if 'descriptionShortITA' not in rec or rec['descriptionShortITA'] is None:
            rec['descriptionShortITA'] = ''
        if 'descriptionShortENG' not in rec or rec['descriptionShortENG'] is None:
            rec['descriptionShortENG'] = ''
        if 'descriptionLongITA' not in rec or rec['descriptionLongITA'] is None:
            rec['descriptionLongITA'] = ''
        if 'descriptionLongENG' not in rec or rec['descriptionLongENG'] is None:
            rec['descriptionLongENG'] = ''
        rec_to_append['descriptionShortITA'] = {'value': rec['descriptionShortITA'].strip(), 'valid': 0}
        rec_to_append['descriptionShortENG'] = {'value': rec['descriptionShortENG'].strip(), 'valid': 0}
        rec_to_append['descriptionLongITA'] = {'value': rec['descriptionLongITA'].strip(), 'valid': 0}
        rec_to_append['descriptionLongENG'] = {'value': rec['descriptionLongENG'].strip(), 'valid': 0}

        # phone
        phone_list = []
        if 'phone' in rec and rec['phone'] != '' and rec['phone'] is not None:
            rec['phone'] = rec['phone'].strip()
            phone_list, phone_valid = self.validate_phone(rec['phone'])
            if len(phone_list) != 0:
                rec_to_append['phone'] = {'value': phone_list[0], 'valid': phone_valid[0]}
            else:
                rec_to_append['phone'] = {'value': '', 'valid': 0}
            if len(phone_list) > 1:
                # secondPhone
                if 'secondPhone' not in rec or rec['secondPhone'] == '' or rec['secondPhone'] is None:
                    rec_to_append['secondPhone'] = {'value': phone_list[1], 'valid': phone_valid[1]}
                    del (phone_list[1])
                else:
                    rec['secondPhone'] = rec['secondPhone'].strip()
                    phone_list_2, phone_valid_2 = self.validate_phone(rec['secondPhone'])
                    rec_to_append['secondPhone'] = {'value': phone_list_2[0], 'valid': phone_valid_2[0]}
        else:
            rec_to_append['phone'] = {'value': '', 'valid': 0}
            if 'secondPhone' in rec and rec['secondPhone'] != '' and rec['secondPhone'] is not None:
                rec['secondPhone'] = rec['secondPhone'].strip()
                phone_list_3, phone_valid_3 = self.validate_phone(rec['secondPhone'])
                rec_to_append['secondPhone'] = {'value': phone_list_3[0], 'valid': phone_valid_3[0]}
        if 'secondPhone' not in rec_to_append and (rec['secondPhone'] == '' or rec['secondPhone'] is None):
            rec_to_append['secondPhone'] = {'value': '', 'valid': 0}
        elif 'secondPhone' not in rec_to_append and (rec['secondPhone'] != '' or rec['secondPhone'] is not None):
            phone_list_2, phone_valid_2 = self.validate_phone(rec['secondPhone'])
            rec_to_append['secondPhone'] = {'value': phone_list_2[0], 'valid': phone_valid_2[0]}

        # fax
        fax_list = []
        if 'fax' in rec and rec['fax'] != '' and rec['fax'] is not None:
            rec['fax'] = rec['fax'].strip()
            fax_list, fax_valid = self.validate_phone(rec['fax'])
            if len(fax_list) != 0:
                rec_to_append['fax'] = {'value': fax_list[0], 'valid': fax_valid[0]}
            else:
                rec_to_append['fax'] = {'value': '', 'valid': 0}
            if len(fax_list) > 1:
                # secondFax
                if 'secondFax' not in rec or rec['secondFax'] == '' or rec['secondFax'] is None:
                    rec_to_append['secondFax'] = {'value': fax_list[1], 'valid': fax_valid[1]}
                    del (fax_list[1])
                else:
                    rec['secondFax'] = rec['secondFax'].strip()
                    fax_list_2, fax_valid_2 = self.validate_phone(rec['secondFax'])
                    rec_to_append['secondFax'] = {'value': fax_list_2[0], 'valid': fax_valid_2[0]}
        else:
            rec_to_append['fax'] = {'value': '', 'valid': 0}
            if 'secondFax' in rec and rec['secondFax'] != '' and rec['secondFax'] is not None:
                rec['secondFax'] = rec['secondFax'].strip()
                fax_list_3, fax_valid_3 = self.validate_phone(rec['secondFax'])
                rec_to_append['secondFax'] = {'value': fax_list_3[0], 'valid': fax_valid_3[0]}
        if 'secondFax' not in rec_to_append and (rec['secondFax'] == '' or rec['secondFax'] is None):
            rec_to_append['secondFax'] = {'value': '', 'valid': 0}
        elif 'secondFax' not in rec_to_append and (rec['secondFax'] != '' or rec['secondFax'] is not None):
            phone_list_2, phone_valid_2 = self.validate_phone(rec['secondFax'])
            rec_to_append['secondFax'] = {'value': phone_list_2[0], 'valid': phone_valid_2[0]}

        # url
        alternative_url = ''
        if 'url' in rec and rec['url'] != '' and rec['url'] is not None:
            rec['url'] = rec['url'].strip()
            (url_valid, url, alternative_url) = self.validate_url(rec['url'], 1)
            rec_to_append['url'] = {'value': url, 'valid': url_valid}
        else:
            rec_to_append['url'] = {'value': '', 'valid': 0}

        # mail
        mail_list = []
        if 'email' in rec and rec['email'] != '' and rec['email'] is not None:
            rec['email'] = rec['email'].strip()
            mail_list, mail_valid = self.validate_mail(rec['email'])
            if len(mail_list) != 0:
                rec_to_append['email'] = {'value': mail_list[0], 'valid': mail_valid[0]}
            else:
                rec_to_append['email'] = {'value': '', 'valid': 0}
            if len(mail_list) > 1:
                # secondEmail
                if 'secondEmail' in rec and rec['secondEmail'] == '':
                    rec_to_append['secondEmail'] = {'value': mail_list[1], 'valid': mail_valid[1]}
                    del (mail_list[1])
        else:
            rec_to_append['email'] = {'value': '', 'valid': 0}
            if 'secondEmail' in rec and rec['secondEmail'] != '' and rec['secondEmail'] is not None:
                rec['secondEmail'] = rec['secondEmail'].strip()
                mail_list, mail_valid = self.validate_mail(rec['secondEmail'])
                rec_to_append['secondEmail'] = {'value': mail_list[0], 'valid': mail_valid[0]}
        if 'secondEmail' not in rec_to_append and (rec['secondEmail'] == '' or rec['secondEmail'] is None):
            rec_to_append['secondEmail'] = {'value': '', 'valid': 0}
        elif 'secondEmail' not in rec_to_append and (rec['secondEmail'] != '' or rec['secondEmail'] is not None):
            mail_list_2, mail_valid_2 = self.validate_mail(rec['secondEmail'])
            rec_to_append['secondEmail'] = {'value': mail_list_2[0], 'valid': mail_valid_2[0]}

        # RefPerson
        if 'RefPerson' in rec and rec['RefPerson'] != '' and rec['RefPerson'] is not None:
            rec_to_append['RefPerson'] = {'value': rec['RefPerson'].strip(), 'valid': 0}
        else:
            rec_to_append['RefPerson'] = {'value': '', 'valid': 0}

        # build a object with province, city and postalcode to check their consistency
        pcp_obj = {}
        if 'city' in rec and rec['city'] != '' and rec['city'] is not None:
            rec['city'] = rec['city'].strip().upper()
            (province, postalcode_list, _) = self.get_data_by_city(rec['city'])
            if province == [] and postalcode_list == []:  # this city does not exist
                pcp_obj['city'] = ''
            else:
                pcp_obj['city'] = rec['city']
        else:
            pcp_obj['city'] = ''
        if 'province' in rec and rec['province'] != '' and rec['province'] is not None:
            rec['province'] = rec['province'].strip().upper()
            pcp_obj['province'] = rec['province']
        else:
            pcp_obj['province'] = ''
        if 'postalcode' in rec and rec['postalcode'] != '' and rec['postalcode'] is not None:
            rec['postalcode'] = str(rec['postalcode']).strip()
            if len(rec['postalcode']) == 2:
                rec['postalcode'] = '000' + rec['postalcode']
            if len(rec['postalcode']) == 3:
                rec['postalcode'] = '00' + rec['postalcode']
            if len(rec['postalcode']) == 4:
                rec['postalcode'] = '0' + rec['postalcode']
            pcp_obj['postalcode'] = rec['postalcode']
        else:
            pcp_obj['postalcode'] = ''
        # check consistency
        if pcp_obj['city'] != '':
            is_city_valid = 0
            (province, postalcode_list, _) = self.get_data_by_city(pcp_obj['city'])
            if pcp_obj['province'] != '' and pcp_obj['province'] == province:
                rec_to_append['province'] = {'value': pcp_obj['province'], 'valid': 1}
            elif pcp_obj['province'] != '' and pcp_obj['province'] != province:
                rec_to_append['province'] = {'value': pcp_obj['province'], 'valid': 2}
                is_city_valid += 1
            elif pcp_obj['province'] == '':
                rec_to_append['province'] = {'value': province, 'valid': 1}

            if pcp_obj['postalcode'] != '' and pcp_obj['postalcode'] in postalcode_list:
                rec_to_append['postalcode'] = {'value': pcp_obj['postalcode'], 'valid': 1}
            elif pcp_obj['postalcode'] != '' and pcp_obj['postalcode'] not in postalcode_list:
                rec_to_append['postalcode'] = {'value': pcp_obj['postalcode'], 'valid': 2}
                is_city_valid += 1
            elif pcp_obj['postalcode'] == '':
                rec_to_append['postalcode'] = {'value': pcp_obj['postalcode'], 'valid': 0}

            if is_city_valid >= 1:
                rec_to_append['city'] = {'value': pcp_obj['city'], 'valid': 2}
            else:
                rec_to_append['city'] = {'value': pcp_obj['city'], 'valid': 1}
        elif pcp_obj['city'] == '' and pcp_obj['postalcode'] != '':
            rec_to_append['city'] = {'value': pcp_obj['city'], 'valid': 2}


            (province, _, _) = self.get_data_by_postalcode(pcp_obj['postalcode'])


            if province == pcp_obj['province'] and pcp_obj['province'] != '':
                rec_to_append['postalcode'] = {'value': pcp_obj['postalcode'], 'valid': 1}
                rec_to_append['province'] = {'value': pcp_obj['province'], 'valid': 1}
            else:
                rec_to_append['postalcode'] = {'value': pcp_obj['postalcode'], 'valid': 2}
                rec_to_append['province'] = {'value': pcp_obj['province'], 'valid': 2}






        else:
            rec_to_append['city'] = {'value': pcp_obj['city'], 'valid': 2}
            rec_to_append['postalcode'] = {'value': pcp_obj['postalcode'], 'valid': 0}
            (cities_list, postalcode_list, _) = self.get_data_by_prov(rec['province'])
            if cities_list == [] and postalcode_list == []:
                rec_to_append['province'] = {'value': pcp_obj['province'], 'valid': 2}
            else:
                rec_to_append['province'] = {'value': pcp_obj['province'], 'valid': 1}

        # streetAddress
        if 'streetAddress' in rec and rec['streetAddress'] != '' and rec['streetAddress'] is not None:
            rec_to_append['streetAddress'] = {'value': rec['streetAddress'].strip(), 'valid': 0}
        else:
            rec_to_append['streetAddress'] = {'value': '', 'valid': 0}

        # secondStreetAddress
        if 'secondStreetAddress' in rec and rec['secondStreetAddress'] != '' and rec['secondStreetAddress'] is not None:
            rec_to_append['secondStreetAddress'] = {'value': rec['secondStreetAddress'].strip(), 'valid': 0}
        else:
            rec_to_append['secondStreetAddress'] = {'value': '', 'valid': 0}

        # notes
        new_notes = ''
        if 'notes' in rec and rec['notes'] is not None:
            rec['notes'] = rec['notes'].strip()
            new_notes = rec['notes']

        if alternative_url != '':
            new_notes += ' ' + alternative_url + ' '
        if len(mail_list) > 1:
            new_notes += 'Alternative e-mail(s): '
            for m in mail_list[1:]:
                new_notes += m + ' '
        if len(phone_list) > 1:
            new_notes += 'Alternative phone number(s): '
            for p in phone_list[1:]:
                new_notes += p + ' '
        if len(fax_list) > 1:
            new_notes += 'Alternative fax number(s): '
            for p in fax_list[1:]:
                new_notes += p + ' '

        rec_to_append['notes'] = {'value': new_notes, 'valid': 0}

        # civicNumber
        if 'civicNumber' in rec and rec['civicNumber'] != '' and rec['civicNumber'] is not None:
            rec_to_append['civicNumber'] = {'value': rec['civicNumber'].strip(), 'valid': 0}
        else:
            rec_to_append['civicNumber'] = {'value': '', 'valid': 0}

        # secondCivicNumber
        if 'secondCivicNumber' in rec and rec['secondCivicNumber'] != '' and rec['secondCivicNumber'] is not None:
            rec_to_append['secondCivicNumber'] = {'value': rec['secondCivicNumber'].strip(), 'valid': 0}
        else:
            rec_to_append['secondCivicNumber'] = {'value': '', 'valid': 0}

        # timetable
        if 'timetable' in rec and rec['timetable'] != '' and rec['timetable'] is not None:
            rec_to_append['timetable'] = {'value': rec['timetable'].strip(), 'valid': 0}
        else:
            rec_to_append['timetable'] = {'value': '', 'valid': 0}

        # photo
        if 'photo' in rec and rec['photo'] != '' and rec['photo'] is not None:
            rec['photo'] = rec['photo'].strip()
            (photo_valid, photo, _) = self.validate_url(rec['photo'], 0)
            rec_to_append['photo'] = {'value': photo, 'valid': photo_valid}
        else:
            rec_to_append['photo'] = {'value': '', 'valid': 0}

        # latitude
        if 'latitude' not in rec or rec['latitude'] is None or rec['latitude'] == '':
            rec_to_append['latitude'] = {'value': '', 'valid': 2}
        else:
            rec['latitude'] = rec['latitude'].strip()
            rec['latitude'] = str(rec['latitude']).replace(',', '.')
            lat_match = self.validate_lat(rec['latitude'])

            if lat_match is not None:
                rec_to_append['latitude'] = {'value': rec['latitude'], 'valid': 1}
            else:
                rec_to_append['latitude'] = {'value': rec['latitude'], 'valid': 2}
        # longitude
        if 'longitude' not in rec or rec['longitude'] is None or rec['longitude'] == '':
            rec_to_append['longitude'] = {'value': '', 'valid': 2}
        else:
            rec['longitude'] = rec['longitude'].strip()
            rec['longitude'] = str(rec['longitude'].replace(',', '.'))

            if len(rec['longitude'].split(".")[1]) > 15:
                rec['longitude'] = rec['longitude'].split(".")[0] + '.' + rec['longitude'].split(".")[1][:15]

            lon_match = self.validate_lon(rec['longitude'])

            if lon_match is not None:
                rec_to_append['longitude'] = {'value': rec['longitude'], 'valid': 1}
            else:
                rec_to_append['longitude'] = {'value': rec['longitude'], 'valid': 2}

        # streetId
        if 'streetId' in rec and rec['streetId'] != '' and rec['streetId'] is not None:
            rec['streetId'] = rec['streetId'].strip()
            rec_to_append['streetId'] = {'value': rec['streetId'], 'valid': 0}
        else:
            rec_to_append['streetId'] = {'value': '', 'valid': 0}

        return rec_to_append

    def get_toponimo(self, lat, lon):
        current_path = os.path.dirname(os.path.abspath(__file__))
        category_file = open(current_path + "/public/toponimo_sparql.txt", "r")
        toponimo_url = category_file.read()
        category_file.close()
        toponimo_url = toponimo_url.replace('xx.xxxx', str(lon))
        toponimo_url = toponimo_url.replace('yy.yyyy', str(lat))
        fileobj_class = urllib.urlopen(toponimo_url)
        json_acceptable_string = fileobj_class.read().replace("'", "\'")
        json_return = json.loads(json_acceptable_string)
        return json_return

    # validate a file record (or table row) before insert to avoid sql troubles for numeric type fields
    #   that can be inserted as string or viceversa
    # an XSS filtering is performed to avoid XSS troubles for data coming from user interface
    # if you want to add a new column add an if clause like the ones in this functions
    #   and add the field to "obj" object
    # if you want to change or delete a column constraint simply change it here and in the "obj" object
    def validate_record_format_for_insert(self, record, fields):
        # XSS filtering
        for key in record:
            if not isinstance(record[key], int) and not isinstance(record[key], float):
		#data = record[key].decode('utf-8')
		data = unicode(record[key])
                #escaped = unicode(utils.escape(data).encode('utf-8'))
                escaped = unicode(utils.escape(data))
		record[key] = escaped.replace("&#39;", "'")

        for key in record:
            if key == 'civicNumber':
                record['notes'] = record['notes'] + '[[civicNumber:' + record[key] + '-]]'
                record[key] = ''
            if key == 'secondCivicNumber':
                record['notes'] = record['notes'] + '[[secondCivicNumber:' + record[key] + '+]]'
                record[key] = ''
            if key != 'latitude' and key != 'longitude':
                record[key] = self.validate_field_type(fields, key, record[key])
            elif key == 'latitude':
                record['latitude'] = re.sub('[a-zA-Z]|[-]', '', record['latitude'])
                record['latitude'] = self.validate_field_type(fields, 'latitude', record['latitude'])
            elif key == 'longitude':
                record['longitude'] = re.sub('[a-zA-Z]|[-]', '', record['longitude'])
                record['longitude'] = self.validate_field_type(fields, 'longitude', record['longitude'])

        obj = {'email': record['email'], 'RefPerson': record['RefPerson'], 'city': record['city'],
               'civicNumber': record['civicNumber'], 'streetId': record['streetId'],
               'abbreviationENG': record['abbreviationENG'], 'abbreviationITA': record['abbreviationITA'],
               'descriptionLongENG': record['descriptionLongENG'], 'descriptionLongITA': record['descriptionLongITA'],
               'descriptionShortENG': record['descriptionShortENG'], 'descriptionShortITA': record['descriptionShortITA'],
               'fax': record['fax'], 'latitude': record['latitude'], 'longitude': record['longitude'],
               'nameENG': record['nameENG'], 'nameITA': record['nameITA'], 'notes': record['notes'],
               'otherCategoryENG': record['otherCategoryENG'], 'otherCategoryITA': record['otherCategoryITA'],
               'phone': record['phone'], 'photo': record['photo'], 'postalcode': record['postalcode'],
               'province': record['province'], 'secondCivicNumber': record['secondCivicNumber'], 'secondEmail': record['secondEmail'],
               'secondFax': record['secondFax'], 'secondPhone': record['secondPhone'], 'secondStreetAddress': record['secondStreetAddress'],
               'streetAddress': record['streetAddress'], 'timetable': record['timetable'], 'url': record['url'],
               }

        return obj

    def validate_field_type(self, fields_obj, field, data):
        if data == '':
            return None

        typefd = ''
        for f in fields_obj:
            if f['id'] == field:
                typefd = f['type']

        if typefd == 'numeric' and typefd != '' and field != 'postalcode' and field != 'phone' \
                and field != 'secondPhone' and field != 'fax' and field != 'secondFax':
            if field != 'latitude' and field != 'longitude':
                try:
                    data = int(data)
                except ValueError:
                    data = float(data)
            elif field == 'latitude' or field == 'longitude':
                data = float(data)
        elif typefd == 'text' and typefd != '':
            data = unicode(data)
        return data
