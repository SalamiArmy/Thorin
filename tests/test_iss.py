import ConfigParser
import unittest
import telegram

import commands.iss as iss


class TestISS(unittest.TestCase):
    def test_iss(self):
        requestText = 'Durban'

        keyConfig = ConfigParser.ConfigParser()
        keyConfig.read(["keys.ini", "..\keys.ini"])
        bot = telegram.Bot(keyConfig.get('Telegram', 'TELE_BOT_ID'))
        chatId = keyConfig.get('BotAdministration', 'ADMIN_GROUP_CHAT_ID')

        iss.run(bot, keyConfig, chatId, 'Admin', requestText)

    def test_isspos(self):
        keyConfig = ConfigParser.ConfigParser()
        keyConfig.read(["keys.ini", "..\keys.ini"])
        bot = telegram.Bot(keyConfig.get('Telegram', 'TELE_BOT_ID'))
        chatId = keyConfig.get('BotAdministration', 'ADMIN_GROUP_CHAT_ID')

        iss.run(bot, keyConfig, chatId, 'Admin', '')