# coding=utf-8
from commands import get


def run(bot, chat_id, user, keyConfig, message, totalResults=1):
    requestText = message.replace(bot.name, "").strip()
    args = {'cx': keyConfig.get('Google', 'GCSE_IMAGE_SE_ID1'),
            'key': keyConfig.get('Google', 'GCSE_APP_ID'),
            'searchType': 'image',
            'safe': 'off',
            'q': 'fig',
            'start': 1}
    get.Send_Images(bot, chat_id, user, requestText, args, keyConfig, totalResults)
