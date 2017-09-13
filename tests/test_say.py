# coding=utf-8
import ConfigParser
import unittest
import telegram

import commands.say as say
from google.appengine.ext import ndb
from google.appengine.ext import testbed

class TestSay(unittest.TestCase):
    def setUp(self):
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()
        # Next, declare which service stubs you want to use.
        self.testbed.init_urlfetch_stub()
        # Clear ndb's in-context cache between tests.
        # This prevents data from leaking between tests.
        # Alternatively, you could disable caching by
        # using ndb.get_context().set_cache_policy(False)
        ndb.get_context().clear_cache()

    def test_say(self):
        requestText = u'<voice-transformation type="Young" strength="80%">Um. I\'m terribly sorry sire. But I\'d just like to ask you a quick thing really quick it\'ll just take a second. Um. Could you kindly go fuck yourself? With a camel dick if possible.</voice-transformation>'

        keyConfig = ConfigParser.ConfigParser()
        keyConfig.read(["keys.ini", "..\keys.ini"])
        bot = telegram.Bot(keyConfig.get('Telegram', 'TELE_BOT_ID'))
        chatId = int(keyConfig.get('BotAdministration', 'TESTING_GROUP_CHAT_ID'))

        say.run(bot, chatId, 'SalamiArmy', keyConfig, requestText, 1)
