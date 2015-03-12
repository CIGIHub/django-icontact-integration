# Based on icontact.py on https://code.google.com/p/python-icontact2/  released as GPL v2
# Modified by Caroline Simpson
#
# python-icontact2 - A python implementation of IContact API 2.0
# Copyright (c) 2010,2011 Alvin Delagon (http://www.alvinatorsplayground.blogspot.com/)
# All rights reserved.
#

import urllib
import httplib2
import json


class IContactConnectivityError(Exception):
    """
    Raised when iContact API calls fail
    """


class IContactInvalidResponse(Exception):
    """
    Raised when API returns a non-JSON response
    """


class IContactInvalidAccountError(Exception):
    """
    Raised when accountId is invalid
    """


class IContactNoFolderError(Exception):
    """
    Raised when there no folders for the account
    """


class IContactAccountIdNotSet(Exception):
    """
    Raised when accountId is not set yet
    """


class IContactFolderIdNotSet(Exception):
    """
    Raised when folderId is not set yet
    """


class IContactWebFormError(Exception):
    """
    Raised when there's an error on posting
    on a webform
    """


class IContactWebFormInvalidFields(Exception):
    """
    Raised when required webform fields are
    missing
    """


class IContactResponse:

    def __init__(self, headers, raw_content, json_content):
        self.headers = headers
        self.raw_content = raw_content
        self.json_content = json_content

    def pretty_print(self):
        s = "HEADERS: %s\n" % self.headers
        s += "PAYLOAD: %s\n" % self.json_content
        return s


class API(object):

    def __init__(self, url, app_id, username, password,
                 version="2.2"):
        self.url = url
        self.app_id = app_id
        self.username = username
        self.password = password
        self.version = version
        self.account_id = None
        self.folder_id = None

    def _check_ids(self, folder_check=True):
        if not self.account_id:
            raise IContactAccountIdNotSet
        if not self.folder_id and folder_check:
            raise IContactFolderIdNotSet

    def get_url(self):
        self._check_ids()
        return self.url + "a/" + self.account_id + "/c/" + self.folder_id + "/"

    def get_account_ids(self):
        url = self.url + "a/"

        response = self.call_remote(url, "GET")
        payload = response.json_content

        if not payload.get('accounts'):
            raise IContactInvalidAccountError()

        account_ids = []
        for account in payload['accounts']:
            account_ids.append(account['accountId'])

        return account_ids

    def get_folder_ids(self):
        self._check_ids(folder_check=False)
        url = self.url + "a/" + self.account_id + "/c"

        response = self.call_remote(url, "GET")
        payload = response.json_content

        if not payload.get('clientfolders'):
            raise IContactNoFolderError()

        folder_ids = []
        for folder in payload['clientfolders']:
            folder_ids.append(folder['clientFolderId'])

        return folder_ids

    def _get_headers(self):
        return {"Accept": "application/json",
                "Content-Type": "application/json",
                "Api-AppId": self.app_id,
                "Api-Version": self.version,
                "Api-Username": self.username,
                "Api-Password": self.password}

    def call_remote(self, url, operation, options={}, body=None):
        if options:
            url += "?" + urllib.urlencode(options)

        h = httplib2.Http(disable_ssl_certificate_validation=True)
        headers = ""
        content = ""

        try:
            if operation == "GET":
                headers, content = h.request(url, operation,
                                             headers=self._get_headers())
            elif operation == "POST":
                headers, content = h.request(url, operation,
                                             json.dumps([body]),
                                             headers=self._get_headers())
            elif operation == "PUT":
                headers, content = h.request(url, operation,
                                             json.dumps(body),
                                             headers=self._get_headers())
            elif operation == "DELETE":
                headers, content = h.request(url, operation,
                                             headers=self._get_headers())
        except (httplib2.ServerNotFoundError) as e:
            raise IContactConnectivityError(e)
        try:
            json_content = json.loads(content)
        except (ValueError) as e:
            raise IContactInvalidResponse(e)
        return IContactResponse(headers, content, json_content)

    def generate_single_object_functions(self, sub_path):
        api_functions = SingleObjectApiFunctions(self, self.get_url(), sub_path)
        return api_functions

    def generate_single_object_property_functions(self, sub_path,
                                                  property_path):
        api_functions = SingleObjectPropertyApiFunctions(self, self.get_url(),
                                                         sub_path,
                                                         property_path)
        return api_functions

    def generate_multi_object_functions(self, sub_path):
        api_functions = MultiObjectApiFunctions(self, self.get_url(), sub_path)
        return api_functions


class SingleObjectApiFunctions(object):
    def __init__(self, api, base_url, sub_path):
        self.api = api
        self.base_url = base_url
        self.sub_path = sub_path

    def get(self, item_id, options={}):
        url = "%s%s/%s" % (self.base_url, self.sub_path, item_id)
        return self.api.call_remote(url, "GET", options=options)

    def delete(self, item_id, options={}):
        url = "%s%s/%s" % (self.base_url, self.sub_path, item_id)
        return self.api.call_remote(url, "DELETE", options=options)

    def add(self, data):
        url = "%s%s" % (self.base_url, self.sub_path)
        return self.api.call_remote(url, "POST", body=data)

    def update(self, item_id, data):
        url = "%s%s/%s" % (self.base_url, self.sub_path, item_id)
        return self.api.call_remote(url, "POST", body=data)

    def replace(self, item_id, data):
        url = "%s%s/%s" % (self.base_url, self.sub_path, item_id)
        return self.api.call_remote(url, "PUT", body=data)


class SingleObjectPropertyApiFunctions(object):
    def __init__(self, api, base_url, sub_path, property_path):
        self.api = api
        self.base_url = base_url
        self.sub_path = sub_path
        self.property_path = property_path

    def get(self, item_id, options={}):
        url = "%s%s/%s/%s" % (self.base_url, self.sub_path, item_id,
                              self.property_path)
        return self.api.call_remote(url, "GET", options=options)


class MultiObjectApiFunctions(object):
    def __init__(self, api, base_url, sub_path):
        self.api = api
        self.base_url = base_url
        self.sub_path = sub_path

    def get(self, options={}):
        url = "%s%s" % (self.base_url, self.sub_path)
        return self.api.call_remote(url, "GET", options=options)

    def add_or_update(self, data):
        url = "%s%s" % (self.base_url, self.sub_path)
        return self.api.call_remote(url, "POST", body=data)


class IContactSession:

    def __init__(self, url, app_id, username, password,
                 version="2.2"):
        self.api = API(url, app_id, username, password, version)

        self.contact = None
        self.contacts = None
        self.list = None
        self.lists = None
        self.subscription = None
        self.subscriptions = None
        self.campaign = None
        self.campaigns = None
        self.message = None
        self.messages = None
        self.send = None
        self.sends = None

        self.clicks = None
        self.opens = None
        self.bounces = None
        self.statistics = None

        self.contact_history = None


    @classmethod
    def connect(cls, url, app_id, username, password):
        # Obtaining your iContact accountId and folderId
        ic = IContactSession(url, app_id, username, password)
        account_ids = ic.api.get_account_ids()
        account_id = account_ids[0]
        ic.api.account_id = account_id
        folder_ids = ic.api.get_folder_ids()
        folder_id = folder_ids[0]
        ic.api.folder_id = folder_id

        ic.contact = ic.api.generate_single_object_functions('contacts')
        ic.contacts = ic.api.generate_multi_object_functions('contacts')
        ic.list = ic.api.generate_single_object_functions('lists')
        ic.lists = ic.api.generate_multi_object_functions('lists')
        ic.subscription = ic.api.generate_single_object_functions(
            'subscriptions')
        ic.subscriptions = ic.api.generate_multi_object_functions(
            'subscriptions')
        ic.campaign = ic.api.generate_single_object_functions('campaigns')
        ic.campaigns = ic.api.generate_multi_object_functions('campaigns')
        ic.message = ic.api.generate_single_object_functions('messages')
        ic.messages = ic.api.generate_multi_object_functions('messages')
        ic.send = ic.api.generate_single_object_functions('sends')
        ic.sends = ic.api.generate_multi_object_functions('sends')

        ic.clicks = ic.api.generate_single_object_property_functions(
            'messages', 'clicks')
        ic.opens = ic.api.generate_single_object_property_functions(
            'messages', 'opens')
        ic.bounces = ic.api.generate_single_object_property_functions(
            'messages', 'bounces')
        ic.statistics = ic.api.generate_single_object_property_functions(
            'messages', 'statistics')
        ic.unsubscribes = ic.api.generate_single_object_property_functions(
            'messages', 'unsubscribes')

        ic.contact_history = ic.api.generate_single_object_property_functions(
            'contacts', 'actions')

        return ic
