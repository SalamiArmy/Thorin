import ConfigParser
import unittest

import telegram

import commands.watchgifs as watchgifs
#import commands.getgif as getgif
from google.appengine.ext import ndb
from google.appengine.ext import testbed


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

    def test_watchgif(self):
        keyConfig = ConfigParser.ConfigParser()
        keyConfig.read(["keys.ini", "..\keys.ini"])
        bot = telegram.Bot(keyConfig.get('Telegram', 'TELE_BOT_ID'))
        chatId = keyConfig.get('BotAdministration', 'TESTING_PRIVATE_CHAT_ID')

        #getgif.setPreviouslySeenGifsValue(0, 'https://i.giphy.com/xT0BKHsihP21C3ytgc.gif,http://memeguy.com/photos/images/money-shot-48569.gif,http://www.outofjoint.co.uk/wp-content/uploads/2016/06/crouch-web-shots.gif,http://static.fjcdn.com/gifs/Meatspin_e9bcbe_5421074.gif,https://static2.fjcdn.com/thumbnails/comments/Quot+haha+this+guy+is+so+cool+dj+dawkins+is+_26ce3a7c12f89789c5999e2debd0fad3.gif,https://images.gr-assets.com/hostedimages/1434923035ra/15278825.gif,http://33.media.tumblr.com/tumblr_lzezvhvmqA1qfqip3o1_500.gif,http://cdn.acidcow.com/pics/20130524/gifs_24.gif,https://i.kinja-img.com/gawker-media/image/upload/c_fill,fl_progressive,g_center,h_180,q_80,w_320/gwwvjgu8mcizfcyb13f6.gif,https://i.upworthy.com/nugget/578e51aab1081e003400006e/attachments/540-140e019d91bd5485bcc872204805ecb7.gif,http://cdn.lifebuzz.com/images/107501/lifebuzz-f4d5d852421cc649961839b48b6659a0-original.gif')
        watchgifs.run(bot, chatId, 'SalamiArmy', None, '', 1)
