# coding=utf-8
import logging
import string
from threading import Thread
import urllib
import io

from google.appengine.ext import ndb

import sys
from PIL import Image

from commands import retry_on_telegram_error
from commands import get

CommandName = 'getgif'

def run(bot, chat_id, user, keyConfig, message, totalResults=1):
    requestText = str(message).replace(bot.name, "").strip()
    args = {'cx': keyConfig.get('Google', 'GCSE_GIF_SE_ID1'),
            'key': keyConfig.get('Google', 'GCSE_APP_ID'),
            'searchType': "image",
            'safe': "off",
            'q': requestText,
            'fileType': 'gif',
            'start': 1}
    Send_Animated_Gifs(bot, chat_id, user, requestText, args, keyConfig, totalResults)


def is_valid_gif(imagelink):
    global gif, image_file, fd
    try:
        fd = urllib.urlopen(imagelink)
        logging.info('can download')
        image_file = io.BytesIO(fd.read())
        logging.info('can read')
        gif = Image.open(image_file)
        logging.info('can open as a gif')
    except:
        return False
    else:
        try:
            gif.seek(1)
            logging.info('can find more than 1 frame in gif')
        except EOFError:
            pass
        else:
            total_image_size = int(sys.getsizeof(image_file))
            logging.info('image is ' + str(total_image_size) + ' bytes big.')
            is_bellow_threshhold = total_image_size < 10000000
            logging.info('this is ' + ('below' if str(is_bellow_threshhold) else 'over') +
                         ' the threshhold of ten million bytes.')
            return is_bellow_threshhold
    finally:
        try:
            if gif:
                gif.fp.close()
            if image_file:
                image_file.close()
            if fd:
                fd.close()
        except UnboundLocalError:
            print("gif, image_file or fd local not defined")
        except NameError:
            print("gif, image_file or fd global not defined")

def Send_Animated_Gifs(bot, chat_id, user, requestText, args, keyConfig, totalResults=1):
    data, total_results, results_this_page = get.Google_Custom_Search(args)
    if 'items' in data and int(total_results) > 0:
        total_sent = search_results_walker(args, bot, chat_id, data, totalResults, user + ', ' + requestText, results_this_page, total_results, keyConfig)
        if int(total_sent) < int(totalResults):
            if int(totalResults) > 1:
                bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                      ', I\'m afraid I can\'t find any more gifs for ' +
                                                      string.capwords(requestText.encode('utf-8')) + '.' +
                                                      ' I could only find ' + str(total_sent) + ' out of ' +
                                                      str(totalResults))
            else:
                bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                      ', I\'m afraid I can\'t find a gif for ' +
                                                      string.capwords(requestText.encode('utf-8')) +
                                                      '.'.encode('utf-8'))
        else:
            return True
    else:
        bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                              ', I\'m afraid I can\'t find a gif for ' +
                                              string.capwords(requestText.encode('utf-8')) + '.'.encode('utf-8'))

def search_results_walker(args, bot, chat_id, data, number, requestText, results_this_page, total_results, keyConfig,
                          total_sent=0, total_offset=0):
    offset_this_page = 0
    while int(total_sent) < int(number) and int(offset_this_page) < int(results_this_page):
        imagelink = str(data['items'][offset_this_page]['link'])
        logging.info('got image link ' + imagelink)
        offset_this_page += 1
        total_offset += 1
        if '?' in imagelink:
            imagelink = imagelink[:imagelink.index('?')]
        if not get.wasPreviouslySeenImage(chat_id, imagelink):
            get.addPreviouslySeenImagesValue(chat_id, imagelink)
            if is_valid_gif(imagelink):
                if number == 1:
                    if retry_on_telegram_error.SendDocumentWithRetry(bot, chat_id, imagelink, requestText):
                        total_sent += 1
                    get.send_url_and_tags(bot, chat_id, imagelink, keyConfig, requestText)
                else:
                    message = requestText + ': ' + (str(total_sent + 1) + ' of ' + str(number) + '\n' if int(number) > 1 else '') + imagelink
                    bot.sendMessage(chat_id, message)
                    total_sent += 1
            else:
                logging.info(imagelink + ' invalid')
    if int(total_sent) < int(number) and int(total_offset) < int(total_results):
        args['start'] = total_offset + 1
        data, total_results, results_this_page = get.Google_Custom_Search(args)
        return search_results_walker(args, bot, chat_id, data, number, requestText, results_this_page, total_results, keyConfig,
                                     total_sent, total_offset)
    return int(total_sent)

