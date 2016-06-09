import ConfigParser
import unittest
import telegram

import commands.gethugegif as gethugegif


class TestGetHugeGif(unittest.TestCase):
    def test_gethugegif(self):
        requestText = 'trippy swirl'

        keyConfig = ConfigParser.ConfigParser()
        keyConfig.read(["keys.ini", "..\keys.ini"])
        bot = telegram.Bot(keyConfig.get('Telegram', 'TELE_BOT_ID'))
        chatId = keyConfig.get('BotAdministration', 'ADMIN_GROUP_CHAT_ID')

        gethugegif.run(bot, keyConfig, chatId, 'Admin', requestText)