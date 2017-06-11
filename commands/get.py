# coding=utf-8
import json
import string
import urllib

import sys

import io
import urllib2

from google.appengine.ext import ndb
from google.appengine.api import urlfetch

from commands import retry_on_telegram_error

CommandName = 'get'


class SeenImages(ndb.Model):
    # key name: get:str(chat_id)
    allPreviousSeenImages = ndb.StringProperty(indexed=False, default='')


# ================================

def setPreviouslySeenImagesValue(chat_id, NewValue):
    es = SeenImages.get_or_insert(CommandName + ':' + str(chat_id))
    es.allPreviousSeenImages = NewValue.encode('utf-8')
    es.put()


def addPreviouslySeenImagesValue(chat_id, NewValue):
    es = SeenImages.get_or_insert(CommandName + ':' + str(chat_id))
    if es.allPreviousSeenImages == '':
        es.allPreviousSeenImages = NewValue.encode('utf-8')
    else:
        es.allPreviousSeenImages += ',' + NewValue.encode('utf-8')
    es.put()


def getPreviouslySeenImagesValue(chat_id):
    es = SeenImages.get_or_insert(CommandName + ':' + str(chat_id))
    if es:
        return es.allPreviousSeenImages.encode('utf-8')
    return ''


def wasPreviouslySeenImage(chat_id, gif_link):
    allPreviousLinks = getPreviouslySeenImagesValue(chat_id)
    if ',' + gif_link + ',' in allPreviousLinks or \
            allPreviousLinks.startswith(gif_link + ',') or \
            allPreviousLinks.endswith(',' + gif_link) or \
                    allPreviousLinks == gif_link:
        return True
    return False


def run(bot, chat_id, user, keyConfig, message, totalResults=1):
    requestText = message.replace(bot.name, "").strip()
    args = {'cx': keyConfig.get('Google', 'GCSE_IMAGE_SE_ID1'),
            'key': keyConfig.get('Google', 'GCSE_APP_ID'),
            'searchType': 'image',
            'safe': 'off',
            'q': requestText,
            'start': 1}
    Send_Images(bot, chat_id, user, requestText, args, keyConfig, totalResults)


def Google_Custom_Search(args):
    googurl = 'https://www.googleapis.com/customsearch/v1'
    realUrl = googurl + '?' + urllib.urlencode(args)
    data = json.load(urllib.urlopen(realUrl))
    total_results = 0
    results_this_page = 0
    if 'searchInformation' in data and 'totalResults' in data['searchInformation']:
        total_results = data['searchInformation']['totalResults']
    if 'queries' in data and 'request' in data['queries'] and len(data['queries']['request']) > 0 and 'count' in \
            data['queries']['request'][0]:
        results_this_page = data['queries']['request'][0]['count']
    return data, total_results, results_this_page

def is_valid_image(imagelink):
    return imagelink != '' and \
           not imagelink.startswith('x-raw-image:///') and \
           ImageIsSmallEnough(imagelink)


def ImageIsSmallEnough(imagelink):
    global image_file, fd
    try:
        fd = urllib.urlopen(imagelink)
        image_file = io.BytesIO(fd.read())
    except IOError:
        return False
    else:
        return int(sys.getsizeof(image_file)) < 10000000
    finally:
        try:
            if image_file:
                image_file.close()
            if fd:
                fd.close()
        except UnboundLocalError:
            print("image_file or fd local not defined")
        except NameError:
            print("image_file or fd global not defined")

def Image_Tags(imagelink, keyConfig):
    vision_url = 'https://westeurope.api.cognitive.microsoft.com/vision/v1.0/tag'
    headers = {'Content-Type': 'application/json',
               'Ocp-Apim-Subscription-Key': keyConfig.get('Bing', 'VisionApiKey')}
    requestPayload = '{"url":"' + imagelink + '"}'
    result = urlfetch.fetch(
        url=vision_url,
        payload=requestPayload,
        method=urlfetch.POST,
        headers=headers)
    data = json.loads(result.content)
    tags = ''
    if 'tags' in data:
        for tag in data['tags']:
            tags += tag['name'] + ', '
    return tags.rstrip(', ')

def Send_Images(bot, chat_id, user, requestText, args, keyConfig, number=1):
    data, total_results, results_this_page = Google_Custom_Search(args)
    if 'items' in data and total_results > 0:
        total_offset, total_results, total_sent = search_results_walker(args, bot, chat_id, data, number, user + ', ' + requestText,
                                                                        results_this_page, total_results, keyConfig)
        if int(total_sent) < int(number):
            if int(number) > 1:
                bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                      ', I\'m afraid I can\'t find any more images for ' +
                                                      string.capwords(requestText.encode('utf-8') + '.' +
                                                                      ' I could only find ' + str(
                                                          total_sent) + ' out of ' + str(number)))
            else:
                bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                      ', I\'m afraid I can\'t find any images for ' +
                                                      string.capwords(requestText.encode('utf-8')))
        else:
            return True
    else:
        if 'error' in data:
            bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                  data['error']['message'])
        else:
            bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                  ', I\'m afraid I can\'t find any images for ' +
                                                  string.capwords(requestText.encode('utf-8')))


def search_results_walker(args, bot, chat_id, data, number, requestText, results_this_page, total_results, keyConfig,
                          total_offset=0, total_sent=0):
    offset_this_page = 0
    while int(total_sent) < int(number) and int(offset_this_page) < int(results_this_page):
        imagelink = data['items'][offset_this_page]['link']
        offset_this_page += 1
        total_offset += 1
        if '?' in imagelink:
            imagelink = imagelink[:imagelink.index('?')]
        if not wasPreviouslySeenImage(chat_id, imagelink):
            addPreviouslySeenImagesValue(chat_id, imagelink)
            if is_valid_image(imagelink):
                ImageTags = Image_Tags(imagelink, keyConfig)
                if retry_on_telegram_error.SendPhotoWithRetry(bot, chat_id, imagelink, requestText +
                        (' ' + str(total_sent + 1) + ' of ' + str(number) if int(number) > 1 else '') +
                        (' (I see ' + ImageTags + ')' if ImageTags != '' else '')):
                    total_sent += 1
                    send_detect_porn_debugging(bot, chat_id, imagelink, keyConfig)
    if int(total_sent) < int(number) and int(total_offset) < int(total_results):
        args['start'] = total_offset + 1
        data, total_results, results_this_page = Google_Custom_Search(args)
        return search_results_walker(args, bot, chat_id, data, number, requestText, results_this_page, total_offset, keyConfig,
                                     total_results, total_sent)
    return total_offset, total_results, total_sent

def send_detect_porn_debugging(bot, chat_id, image_link, key_config):
    if str(chat_id) == key_config.get('BotAdministration', 'TESTING_PRIVATE_CHAT_ID') or str(chat_id) == key_config.get('BotAdministration', 'TESTING_GROUP_CHAT_ID'):
        full_nude_detection_debug_info = 'Might I add, I\'m testing porn detection APIs.\n'

        req = urllib2.Request('https://sightengine-nudity-and-adult-content-detection.p.mashape.com/nudity.json'+ '?' + urllib.urlencode({'url': image_link}))
        req.add_header('X-Mashape-Key', key_config.get('Mashape', 'key'))
        resp = urllib2.urlopen(req)
        response_content = resp.read()
        Sight_Engine_data = json.loads(response_content)
        if 'status' not in Sight_Engine_data or Sight_Engine_data['status'] != 'success':
            return
        is_porn_percent = 100 - (Sight_Engine_data['nudity']['safe'] * 100)
        full_nude_detection_debug_info += str(is_porn_percent) + '% porn according to Sight Engine\'s API\n'

        req = urllib2.Request('https://sphirelabs-advanced-porn-nudity-and-adult-content-detection.p.mashape.com/v1/get/index.php' + '?' + urllib.urlencode({'url': image_link}))
        req.add_header('X-Mashape-Key', key_config.get('Mashape', 'key'))
        resp = urllib2.urlopen(req)
        response_content = resp.read()
        Sphire_Labs_data = json.loads(response_content)
        if 'Is Porn' not in Sphire_Labs_data:
            return
        is_porn = Sphire_Labs_data['Is Porn']
        full_nude_detection_debug_info += ('Is porn' if is_porn == 'True' else 'Is not porn') + ' according to Sphire Labs\'s API\n'

        if is_porn == 'True' and is_porn_percent > 50:
            full_nude_detection_debug_info += 'Admin, I would consider this porn.'
        else:
            full_nude_detection_debug_info += 'Admin, this is safe.'
        full_nude_detection_debug_info += '\n' + image_link

        bot.sendMessage(chat_id=chat_id, text=full_nude_detection_debug_info, disable_web_page_preview=True)
