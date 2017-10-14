# coding=utf-8
import unittest
from google.appengine.ext import ndb
from google.appengine.ext import testbed

import main

class TestPost(unittest.TestCase):
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

    def test_integration_test_post(self):
        newRequestObject = main.WebhookHandler()
        class Object(object):
            pass
        newRequestObject.request = Object()
        newRequestObject.request.body = '{"message": {"from": {"username": "SalamiArmy", "first_name": "Ashley", "last_name": "Lewis"}, "text": "/getgif cork screw sex position", "chat": {"id": -55348600, "type": "group"}}}'
        newRequestObject.response = Object()
        newRequestObject.response.write = lambda x: None
        newRequestObject.post()
