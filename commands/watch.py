# coding=utf-8
import string

import main
from commands import get
from commands import getgif
from commands import retry_on_telegram_error

def run(bot, chat_id, user, keyConfig, message, num_to_send=1):
    requestText = message.replace(bot.name, "").strip()
    args = {'cx': keyConfig.get('Google', 'GCSE_IMAGE_SE_ID1'),
            'key': keyConfig.get('Google', 'GCSE_APP_ID'),
            'searchType': 'image',
            'safe': 'off',
            'q': requestText,
            'start': 1}
    single_page_watch(args, bot, chat_id, keyConfig, num_to_send, requestText, user, get)


def send_image_with_watch_message(bot, chat_id, imagelink, keyConfig, requestText, total_sent, user, watch_message):
    bot.sendMessage(chat_id=chat_id, text=watch_message)
    ImageTags = get.Image_Tags(imagelink, keyConfig)
    image_caption = user + ', ' + requestText + (' (I see ' + ImageTags + ')' if ImageTags != '' else '')
    if imagelink[-len('.gif'):] == '.gif':
        if retry_on_telegram_error.SendDocumentWithRetry(bot, chat_id, imagelink, image_caption):
            total_sent += 1
    else:
        if retry_on_telegram_error.SendPhotoWithRetry(bot, chat_id, imagelink, image_caption):
            total_sent += 1
    return total_sent


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

def single_page_watch(args, bot, chat_id, keyConfig, num_to_send, requestText, user, watched_command):
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
                if imagelink[-len('.gif'):] == '.gif':
                    is_valid = getgif.is_valid_gif(imagelink)
                else:
                    is_valid = get.is_valid_image(imagelink)
                if is_valid:
                    if user != 'Watcher':
                        if total_sent == 0 and not main.AllWatchesContains(watched_command.CommandName, chat_id,
                                                                           requestText):
                            watch_message = 'Now watching /' + watched_command.CommandName + ' ' + requestText + '.'
                        else:
                            watch_message = 'Watched /' + watched_command.CommandName + ' ' + requestText + ' changed' + \
                                            (' (' + str(total_sent) + ' out of ' + str(
                                                num_to_send) + ')' if total_sent > 0 else '') + '.'
                        total_sent = send_image_with_watch_message(bot, chat_id, imagelink, keyConfig, requestText,
                                                                   total_sent, user, watch_message)
                    else:
                        total_sent = send_image_with_watch_message(bot, chat_id, imagelink, keyConfig, requestText,
                                                                   total_sent, user,
                                                                   'Watched /' + watched_command.CommandName +
                                                                   ' ' + requestText + ' changed.')
        if total_sent == 0 and user != 'Watcher':
            bot.sendMessage(chat_id=chat_id, text=user + ', watch for /' +
                                                  watched_command.CommandName + ' ' + requestText + ' has not changed.')
        if total_sent > 0 and total_sent < num_to_send and user != 'Watcher':
            bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                  ', I\'m afraid I can\'t find any more results for /' +
                                                  watched_command.CommandName + ' ' +
                                                  string.capwords(requestText.encode('utf-8')))
        if not main.AllWatchesContains(watched_command.CommandName, chat_id, requestText):
            main.addToAllWatches(watched_command.CommandName, chat_id, requestText)
    else:
        if user != 'Watcher':
            bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                  ', I\'m afraid I can\'t find any results for /' +
                                                  watched_command.CommandName + ' ' +
                                                  string.capwords(requestText.encode('utf-8')))