# coding=utf-8
import ConfigParser
import unittest

import telegram
from google.appengine.ext import ndb
from google.appengine.ext import testbed
from google.appengine.api import urlfetch
from commands import get

import main

class TestGet(unittest.TestCase):
    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_user_stub()
        self.testbed.init_urlfetch_stub()
        # Clear ndb's in-context cache between tests.
        # This prevents data from leaking between tests.
        # Alternatively, you could disable caching by
        # using ndb.get_context().set_cache_policy(False)
        ndb.get_context().clear_cache()

    def integration_test_get(self):
        newRequestObject = main.WebhookHandler()
        class Object(object):
            pass
        newRequestObject.request = Object()
        newRequestObject.request.get = lambda x: 'getxxx' if (x == 'command') else 'gosh'
        newRequestObject.response = Object()
        newRequestObject.response.write = lambda x: self.mockResponseWriter(x)
        self.responseString = ''
        newRequestObject.get()
        if self.responseString == '':
            raise Exception

    def integration_test_restful_walking(self):
        requestText = 'old ass titties'
        total_number_to_send = 11

        keyConfig = ConfigParser.ConfigParser()
        keyConfig.read(["keys.ini", "..\keys.ini"])
        chat_id = keyConfig.get('BotAdministration', 'TESTING_PRIVATE_CHAT_ID')
        args = {'cx': keyConfig.get('Google', 'GCSE_IMAGE_SE_ID1'),
                'key': keyConfig.get('Google', 'GCSE_APP_ID'),
                'searchType': 'image',
                'safe': 'off',
                'q': requestText,
                'start': 1}
        data, total_results, results_this_page = get.Google_Custom_Search(args)
        if 'items' in data and total_results > 0:
            strPayload = str({
                "args":args,
                "chat_id":chat_id ,
                "data":data,
                "total_number_to_send":total_number_to_send,
                "requestText":requestText,
                "results_this_page":results_this_page,
                "total_offset":0,
                "total_sent":0,
                "keyConfig":str(keyConfig),
                "total_results":total_results
            })
            urlfetch.fetch(keyConfig.get('BotAdministration', 'REST_URL') + '/get?', strPayload, 'POST')

    global responseString

    def mockResponseWriter(self, inputText):
        self.responseString = inputText
        return inputText