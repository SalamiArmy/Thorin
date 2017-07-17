# coding=utf-8
import main
from commands import getgif
from commands import watch

def run(bot, chat_id, user, keyConfig, message, num_to_send=1):
    requestText = message.replace(bot.name, "").strip()
    args = {'cx': keyConfig.get('Google', 'GCSE_GIF_SE_ID1'),
            'key': keyConfig.get('Google', 'GCSE_APP_ID'),
            'searchType': "image",
            'safe': "off",
            'q': requestText,
            'fileType': 'gif',
            'start': 1}
    watch.single_page_watch(args, bot, chat_id, keyConfig, num_to_send, requestText, user, getgif)


def unwatch(bot, chat_id, message):
    watches = main.getAllWatches()
    if ',' + str(chat_id) + ':' + getgif.CommandName + ':' + message + ',' in watches or \
            watches.startswith(str(chat_id) + ':' + getgif.CommandName + ':' + message + ',') or \
            watches.endswith(',' + str(chat_id) + ':' + getgif.CommandName + ':' + message) or \
                    watches == str(chat_id) + ':' + getgif.CommandName + ':' + message:
        main.removeFromAllWatches(str(chat_id) + ':' + getgif.CommandName + ':' + message)
        bot.sendMessage(chat_id=chat_id, text='Watch for /' + getgif.CommandName + ' ' + message + ' has been removed.')
    else:
        bot.sendMessage(chat_id=chat_id, text='Watch for /' + getgif.CommandName + ' ' + message + ' not found.')
