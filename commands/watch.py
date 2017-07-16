# coding=utf-8
import string

import main
from commands import getgif
from commands import get
from commands import retry_on_telegram_error

def run(bot, chat_id, user, keyConfig, message, num_to_send=1):
    requestText = message.replace(bot.name, "").strip()
    args = {'cx': keyConfig.get('Google', 'GCSE_IMAGE_SE_ID1'),
            'key': keyConfig.get('Google', 'GCSE_APP_ID'),
            'searchType': 'image',
            'safe': 'off',
            'q': requestText,
            'start': 1}
    data, total_results, results_this_page = get.Google_Custom_Search(args)
    if 'items' in data and results_this_page >= 0:
        offset_this_page = 0
        total_sent = 0
        while offset_this_page < results_this_page and total_sent < num_to_send:
            imagelink = data['items'][offset_this_page]['link']
            offset_this_page += 1
            if '?' in imagelink:
                imagelink = imagelink[:imagelink.index('?')]
            if not get.wasPreviouslySeenImage(chat_id, imagelink):
                get.addPreviouslySeenImagesValue(chat_id, imagelink)
                if get.is_valid_image(imagelink):
                    if user != 'Watcher':
                        if total_sent == 0 and not main.AllWatchesContains(get.CommandName, chat_id, requestText):
                            bot.sendMessage(chat_id=chat_id, text='Now watching /' +
                                                                  get.CommandName + ' ' + requestText + '.')
                        else:
                            bot.sendMessage(chat_id=chat_id,
                                            text='Watched /' + get.CommandName + ' ' + requestText + ' changed' +
                                                 (' (' + str(total_sent) + ' out of ' + str(num_to_send) + ')' if total_sent > 0 else '') + '.')
                        if retry_on_telegram_error.SendPhotoWithRetry(bot, chat_id, imagelink, user):
                            total_sent += 1
                    else:
                        bot.sendMessage(chat_id=chat_id, text='Watched /' +
                                                              get.CommandName + ' ' + requestText + ' changed.')
                        if retry_on_telegram_error.SendPhotoWithRetry(bot, chat_id, imagelink, user):
                            total_sent += 1
        if total_sent == 0 and user != 'Watcher':
            bot.sendMessage(chat_id=chat_id, text=user + ', watch for /' +
                                                  get.CommandName + ' ' + requestText + ' has not changed.')
        if total_sent > 0 and total_sent < num_to_send and user != 'Watcher':
            bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                  ', I\'m afraid I can\'t watch ' +
                                                  'because I did not find any more results for /get ' +
                                                  string.capwords(requestText.encode('utf-8')))
        if not main.AllWatchesContains(get.CommandName, chat_id, requestText):
            main.addToAllWatches(get.CommandName, chat_id, requestText)
    else:
        if user != 'Watcher':
            bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                  ', I\'m afraid I did not find any results for /get ' +
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
