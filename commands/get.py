# coding=utf-8
import json
import string
import urllib

import sys

import io

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
    tags = ''
    strPayload = str({
        "requests":
            [
                {
                    "features":
                        [
                            {
                                "type": "LABEL_DETECTION"
                            },
                            {
                                "type": "SAFE_SEARCH_DETECTION"
                            }
                        ],
                    "image":
                        {
                            "source":
                                {
                                    "imageUri": str(imagelink)
                                }
                        }
                }
            ]
    })
    raw_data = urlfetch.fetch(
        url='https://vision.googleapis.com/v1/images:annotate?key=' + keyConfig.get('Google', 'GCSE_APP_ID'),
        payload=strPayload,
        method='POST',
        headers={'Content-type': 'application/json'})
    visionData = json.loads(raw_data.content)
    if 'error' not in visionData:
        if 'error' not in visionData['responses'][0]:
            strAdult = visionData['responses'][0]['safeSearchAnnotation']['adult']
            if strAdult == 'POSSIBLE' or \
                strAdult == 'LIKELY' or \
                strAdult == 'VERY_LIKELY':
                tags += strAdult.replace('VERY_LIKELY', '').lower() + ' obscene adult content, '
            strViolence = visionData['responses'][0]['safeSearchAnnotation']['violence']
            if strViolence == 'POSSIBLE' or \
                strViolence == 'LIKELY' or \
                strViolence == 'VERY_LIKELY':
                tags += strViolence.replace('VERY_LIKELY', '').lower() + ' offensive violence, '
            strMedical = visionData['responses'][0]['safeSearchAnnotation']['medical']
            if strMedical == 'POSSIBLE' or \
                strMedical == 'LIKELY' or \
                strMedical == 'VERY_LIKELY':
                tags += strMedical.replace('VERY_LIKELY', '').lower() + ' shocking medical content, '
            strSpoof = visionData['responses'][0]['safeSearchAnnotation']['spoof']
            if strSpoof == 'POSSIBLE' or \
                strSpoof == 'LIKELY' or \
                strSpoof == 'VERY_LIKELY':
                tags += strSpoof.replace('VERY_LIKELY', '').lower() + ' a meme, '
            if 'labelAnnotations' in visionData['responses'][0]:
                for tag in visionData['responses'][0]['labelAnnotations']:
                    if (tag['description'] + ', ') not in tags:
                        tags += tag['description'] + ', '
        else:
            print(visionData['responses'][0]['error']['message'])
    else:
        print(visionData['error']['message'])
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
    if int(total_sent) < int(number) and int(total_offset) < int(total_results):
        args['start'] = total_offset + 1
        data, total_results, results_this_page = Google_Custom_Search(args)
        return search_results_walker(args, bot, chat_id, data, number, requestText, results_this_page, total_offset, keyConfig,
                                     total_results, total_sent)
    return total_offset, total_results, total_sent
