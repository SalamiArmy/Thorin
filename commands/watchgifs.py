# coding=utf-8
import json

from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from commands import retry_on_telegram_error
from commands import getgif

watchedCommandName = 'watchgifs'


class WatchValue(ndb.Model):
    # key name: str(chat_id)
    currentValue = ndb.StringProperty(indexed=False, default='')
    all_chat_ids = ndb.StringProperty(indexed=False, default='')


# ================================

def setWatchValue(chat_id, NewValue):
    es = WatchValue.get_or_insert(watchedCommandName + ':' + str(chat_id))
    es.currentValue = NewValue
    es.put()


def getWatchValue(chat_id):
    es = WatchValue.get_by_id(watchedCommandName + ':' + str(chat_id))
    if es:
        return es.currentValue
    return ''

def addToAllWatches(chat_id):
    es = WatchValue.get_or_insert(watchedCommandName + ':' + 'AllWatchers')
    es.all_chat_ids += ',' + str(chat_id)
    es.put()

def AllWatchesContains(chat_id):
    es = WatchValue.get_by_id(watchedCommandName + ':' + 'AllWatchers')
    if es:
        return (',' + str(chat_id)) in str(es.all_chat_ids) or \
               (str(chat_id) + ',') in str(es.all_chat_ids)
    return False

def setAllWatchesValue(NewValue):
    es = WatchValue.get_or_insert(watchedCommandName + ':' + 'AllWatchers')
    es.all_chat_ids = NewValue
    es.put()

def getAllWatches():
    es = WatchValue.get_by_id(watchedCommandName + ':' + 'AllWatchers')
    if es:
        return es.all_chat_ids
    return ''

def removeFromAllWatches(watch):
    setAllWatchesValue(getAllWatches().replace(',' + watch + ',', ',')
                       .replace(',' + watch, '')
                       .replace(watch + ',', ''))

def run(bot, chat_id, user='Dave', keyConfig=None, message='', totalResults=1):
    if not AllWatchesContains(chat_id):
        addToAllWatches(chat_id)
    data, results_this_page, after = reddit_top_gifs_search()
    topGifs = multipage_top_gifs_walker(after, bot, chat_id, data, totalResults)
    data, results_this_page, after = reddit_top_contentawarescale_gifs_search()
    topContentAwareScaleGifs = multipage_top_gifs_walker(after, bot, chat_id, data, totalResults)
    if topGifs <= 0 and topContentAwareScaleGifs <= 0:
        bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                              ', I\'m afraid you\'ve seen all the best gifs I can find.')


def reddit_top_gifs_search(after=''):
    if after =='':
        topgifs = 'https://www.reddit.com/r/gifs/top.json?t=all'
    else:
        topgifs = 'https://www.reddit.com/r/gifs/top.json?t=all&after=' + after
    topgifsUrlRequest = urlfetch.fetch(url=topgifs, headers={
        'User-Agent': 'App Engine:Scenic-Oxygen:ImageBoet:v0.9 (by /u/SalamiArmy)'})
    data = json.loads(topgifsUrlRequest.content)
    return data, len(data['data']['children']), data['data']['after']

def reddit_top_contentawarescale_gifs_search(after=''):
    if after =='':
        topgifs = 'https://www.reddit.com/r/contentawarescale/top.json?t=all'
    else:
        topgifs = 'https://www.reddit.com/r/contentawarescale/top.json?t=all&after=' + after
    topgifsUrlRequest = urlfetch.fetch(url=topgifs, headers={
        'User-Agent': 'App Engine:Scenic-Oxygen:ImageBoet:v0.9 (by /u/SalamiArmy)'})
    data = json.loads(topgifsUrlRequest.content)
    return data, len(data['data']['children']), data['data']['after']

def multipage_top_gifs_walker(after, bot, chat_id, data, number=1, results_this_page=25, total_sent=0):
    offset_this_page = 0
    while int(total_sent) < int(number) and int(offset_this_page) < results_this_page:
        gif_url = data['data']['children'][offset_this_page]['data']['url']
        imagelink = gif_url[:-1] if gif_url.endswith('.gifv') else gif_url
        caption = data['data']['children'][offset_this_page]['data']['title'].replace(' - Create, Discover and Share GIFs on Gfycat', '')# + '\n https://www.reddit.com' + \
                      #data['data']['children'][offset_this_page]['data']['permalink']
        offset_this_page += 1
        if '?' in imagelink:
            imagelink = imagelink[:imagelink.index('?')]
        if not getgif.wasPreviouslySeenGif(chat_id, imagelink):
            getgif.addPreviouslySeenGifsValue(chat_id, imagelink)
            if getgif.is_valid_gif(imagelink):
                if retry_on_telegram_error.SendDocumentWithRetry(bot, chat_id, imagelink, caption +
                        (' ' + str(total_sent + 1) + ' of ' + str(number) if int(number) > 1 else '')):
                    total_sent += 1
    if int(total_sent) < int(number):
        data, results_this_page, after = reddit_top_gifs_search(after)
        return multipage_top_gifs_walker(after, bot, chat_id, data, number, results_this_page, total_sent)
    return int(total_sent)

def unwatch(bot, chat_id):
    if AllWatchesContains(chat_id):
        removeFromAllWatches(str(chat_id))
        bot.sendMessage(chat_id=chat_id, text='This chat is no longer watching gifs.')
    else:
        bot.sendMessage(chat_id=chat_id, text='This chat is not watching gifs.')
