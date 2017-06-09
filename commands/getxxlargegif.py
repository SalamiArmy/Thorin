# coding=utf-8
from commands import getgif


def run(bot, chat_id, user, keyConfig, message, totalResults=1):
    requestText = message.replace(bot.name, "").strip()
    args = {'cx': keyConfig.get('Google', 'GCSE_GIF_SE_ID1'),
            'key': keyConfig.get('Google', 'GCSE_APP_ID'),
            'searchType': "image",
            'safe': "off",
            'q': requestText,
            'fileType': 'gif',
            'start': 1,
            'imgSize': 'xxlarge'}
    getgif.Send_Animated_Gifs(bot, chat_id, user, requestText, args, keyConfig, totalResults)