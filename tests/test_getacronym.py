import ConfigParser
import unittest

import telegram

import commands.getacronym as getacronym


class TestGetGame(unittest.TestCase):
    def test_getgame(self):
        requestText = 'api'

        keyConfig = ConfigParser.ConfigParser()
        keyConfig.read(["keys.ini", "..\keys.ini"])
        bot = telegram.Bot(keyConfig.get('Telegram', 'TELE_BOT_ID'))
        chatId = keyConfig.get('BotAdministration', 'ADMIN_GROUP_CHAT_ID')

        getacronym.run(bot, keyConfig, chatId, 'Admin', requestText)