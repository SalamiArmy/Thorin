# coding=utf-8
from commands import getgif


def run(bot, chat_id, user, keyConfig, message):
    requestText = message.replace(bot.name, "").strip()
    args = {'cx': keyConfig.get('Google', 'GCSE_SE_ID'),
            'key': keyConfig.get('Google', 'GCSE_APP_ID'),
            'searchType': "image",
            'safe': "off",
            'q': requestText,
            'fileType': 'gif',
            'start': 1,
            'imgSize': 'xlarge'}
    getgif.Send_First_Animated_Gif(bot, chat_id, user, requestText, args)