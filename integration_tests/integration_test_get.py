# coding=utf-8
import unittest
from google.appengine.ext import ndb
from google.appengine.ext import testbed

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
        newRequestObject = main.WebhookHandler()
        class Object(object):
            pass
        newRequestObject.request = Object()
        newRequestObject.request.get = lambda x: 'args' if (x == 'args') else \
                                                 'chat_id' if (x == 'chat_id') else \
                                                 'gosh' if (x == 'command') else \
                                                 'gosh' if (x == 'command') else \
                                                 'gosh' if (x == 'command') else \
                                                 'gosh' if (x == 'command') else \
                                                 'gosh' if (x == 'command') else ''
        newRequestObject.response = Object()
        newRequestObject.response.write = lambda x: self.mockResponseWriter(x)
        self.responseString = ''
        newRequestObject.get()
        if self.responseString == '':
            raise Exception

    global responseString

    def mockResponseWriter(self, inputText):
        self.responseString = inputText
        return inputText