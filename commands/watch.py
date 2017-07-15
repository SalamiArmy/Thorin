# coding=utf-8
import string

import main
from commands import getgif
from commands import get
from commands import retry_on_telegram_error

def run(bot, chat_id, user, keyConfig, message, totalResults=1):
    requestText = message.replace(bot.name, "").strip()
    args = {'cx': keyConfig.get('Google', 'GCSE_IMAGE_SE_ID1'),
            'key': keyConfig.get('Google', 'GCSE_APP_ID'),
            'searchType': 'image',
            'safe': 'off',
            'q': requestText,
            'start': 1}
    data, total_results, results_this_page = get.Google_Custom_Search(args)
    if 'items' in data and results_this_page >= 0:
        if user != 'Watcher':
            total_offset, total_results, total_sent = get.search_results_walker(args, bot, chat_id, data, 1,
                                                                                user + ', ' + requestText,
                                                                                results_this_page, total_results,
                                                                                keyConfig)
            if int(total_sent) > 0:
                if not main.AllWatchesContains(get.CommandName, chat_id, requestText):
                    bot.sendMessage(chat_id=chat_id, text='Now watching /' + get.CommandName + ' ' + requestText + '.')
            else:
                bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                      ', I\'m afraid I can\'t find any images for ' +
                                                      string.capwords(requestText.encode('utf-8')))
        else:
            total_offset, total_results, total_sent = get.search_results_walker(args, bot, chat_id, data, 1,
                                                                                user + ', ' + requestText,
                                                                                results_this_page, total_results,
                                                                                keyConfig)
            if int(total_sent) > 0:
                bot.sendMessage(chat_id=chat_id, text='Watched /' +
                                                      get.CommandName + ' ' + requestText + ' changed.')
        if not main.AllWatchesContains(get.CommandName, chat_id, requestText):
            main.addToAllWatches(get.CommandName, chat_id, requestText)
    else:
        if user != 'Watcher':
            bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                  ', I\'m afraid I can\'t watch ' +
                                                  'because I did not find any results for /get ' +
                                                  string.capwords(requestText.encode('utf-8')))

def unwatch(bot, chat_id, message):
    watches = main.getAllWatches()
    if ',' + str(chat_id) + ':' + get.CommandName + ':' + message + ',' in watches or \
            watches.startswith(str(chat_id) + ':' + get.CommandName + ':' + message + ',') or \
            watches.endswith(',' + str(chat_id) + ':' + get.CommandName + ':' + message) or \
                    watches == str(chat_id) + ':' + get.CommandName + ':' + message:
        main.removeFromAllWatches(str(chat_id) + ':' + get.CommandName + ':' + message)
        bot.sendMessage(chat_id=chat_id, text='Watch for /' + get.CommandName + ' ' + message + ' has been removed.')
    else:
        bot.sendMessage(chat_id=chat_id, text='Watch for /' + get.CommandName + ' ' + message + ' not found.')
