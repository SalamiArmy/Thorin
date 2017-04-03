# coding=utf-8
import string

from google.appengine.ext import ndb

import main
from commands import getgif
from commands import retry_on_telegram_error

watchedCommandName = 'getgif'


class WatchValue(ndb.Model):
    # key name: str(chat_id)
    currentValue = ndb.StringProperty(indexed=False, default='')
    allPreviousAddedLinks = ndb.StringProperty(indexed=False, default='')


# ================================

def setWatchValue(chat_id, request, NewValue):
    es = WatchValue.get_or_insert(watchedCommandName + ':' + str(chat_id) + ':' + request)
    es.currentValue = NewValue
    es.put()

def addPreviouslyAddedLinkValue(chat_id, NewValue):
    es = WatchValue.get_or_insert(watchedCommandName + ':' + str(chat_id))
    if (es.allPreviousAddedLinks != ''):
        es.allPreviousAddedLinks += '\n' + NewValue
    else:
        es.allPreviousAddedLinks += NewValue
    es.put()


def getWatchValue(chat_id, request):
    es = WatchValue.get_by_id(watchedCommandName + ':' + str(chat_id) + ':' + request)
    if es:
        return es.currentValue
    return ''

def getPreviouslyAddedLinksValue(chat_id):
    es = WatchValue.get_by_id(watchedCommandName + ':' + str(chat_id))
    if es:
        return es.allPreviousAddedLinks.encode('utf-8')
    return ''

def wasPreviouslyAddedLink(chat_id, gif_link):
    allPreviousLinks = getPreviouslyAddedLinksValue(chat_id)
    if '\n' + gif_link + '\n' in allPreviousLinks or \
        allPreviousLinks.startswith(gif_link + '\n') or  \
        allPreviousLinks.endswith('\n' + gif_link) or  \
        allPreviousLinks == gif_link:
        return True;
    return False;

def get_add_removed_links(chat_id, new_list, old_list):
    added_games = ''
    newly_added_games = ''
    for item in new_list.split('\n'):
        if item not in old_list:
            added_games += '\n' + item
            if not wasPreviouslyAddedLink(chat_id, item):
                addPreviouslyAddedLinkValue(chat_id, item)
                newly_added_games += '\n' + item
    return added_games, newly_added_games


def run(bot, chat_id, user, keyConfig, message, intention_confidence=0.0):
    requestText = message.replace(bot.name, "").strip()
    data = getgif.search_google_for_gifs(keyConfig, requestText)
    if 'items' in data and len(data['items']) >= 9:
        OldValue = getWatchValue(chat_id, requestText)
        imagelinks = data['items'][0]['link']
        for link in data['items'][:5]:
            imagelinks += '\n' + link['link']
        links_added, newly_added_links = get_add_removed_links(chat_id, imagelinks, OldValue)
        print('got image links for ' + requestText + ' as ' + imagelinks)
        count = 0
        for link in data['items'][:5]:
            imagelink = link['link']
            count += 1
            if getgif.isGifAnimated(imagelink):
                if OldValue != imagelinks:
                    if user != 'Watcher':
                        bot.sendMessage(chat_id=chat_id, text='Now watching /' +
                                                              watchedCommandName + ' ' + requestText + '.' +
                                                              '\nThis is number ' + str(count) + ' of 10.')
                        retry_on_telegram_error.SendDocumentWithRetry(bot, chat_id, imagelink, user)
                    else:
                        bot.sendMessage(chat_id=chat_id, text='Watched /' +
                                                              watchedCommandName + ' ' + requestText + ' changed' +
                                                              (' order.' if (links_added == '' and newly_added_links == '') else '.') +
                                                              '\nThis is number ' + str(count) + ' of 10.')
                        retry_on_telegram_error.SendDocumentWithRetry(bot, chat_id, imagelink, user)
                else:
                    if user != 'Watcher':
                        bot.sendMessage(chat_id=chat_id, text=user + ', watch for /' +
                                                              watchedCommandName + ' ' + requestText + ' has not changed.' +
                                                              '\nThis is number ' + str(count) + ' of 10.')
                        retry_on_telegram_error.SendDocumentWithRetry(bot, chat_id, imagelink, user)
            else:
                if user != 'Watcher':
                    bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                          ', I\'m afraid gif is not animated.' +
                                                          '\nThis is number ' + str(count) + ' of 10.\n' + imagelink)
        if links_added != '':
            count = 0
            for link in links_added.split('\n'):
                count += 1
                bot.sendMessage(chat_id=chat_id, text='Watched /' +
                                                      watchedCommandName + ' ' + requestText + ' has new gifs.' +
                                                      '\nThis is new gif number ' + str(count) + '.')
                retry_on_telegram_error.SendDocumentWithRetry(bot, chat_id, link, user)
        if newly_added_links != '':
            count = 0
            for link in newly_added_links.split('\n'):
                count += 1
                bot.sendMessage(chat_id=chat_id, text='Watched /' +
                                                      watchedCommandName + ' ' + requestText + ' has new new gifs.' +
                                                      '\nThis is new new gif number ' + str(count) + '.')
                retry_on_telegram_error.SendDocumentWithRetry(bot, chat_id, link, user)

        if OldValue != imagelinks:
            print('Setting watch value to ' + imagelinks)
            setWatchValue(chat_id, requestText, imagelinks)
        if not main.AllWatchesContains(watchedCommandName, chat_id, requestText):
            main.addToAllWatches(watchedCommandName, chat_id, requestText)
    else:
        if user != 'Watcher':
            bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                  ', I\'m afraid I can\'t watch ' +
                                                  'because I did not find enough results for /getgif ' +
                                                  string.capwords(requestText.encode('utf-8')))


def unwatch(bot, chat_id, message):
    watches = main.getAllWatches()
    if ',' + str(chat_id) + ':' + watchedCommandName + ':' + message + ',' in watches or ',' + str(chat_id) + ':' + watchedCommandName + ':' + message in watches:
        main.removeFromAllWatches(str(chat_id) + ':' + watchedCommandName + ':' + message)
        bot.sendMessage(chat_id=chat_id, text='Watch for /' + watchedCommandName + ' ' + message + ' has been removed.')
    else:
        bot.sendMessage(chat_id=chat_id, text='Watch for /' + watchedCommandName + ' ' + message + ' not found.')
    if getWatchValue(chat_id, message) != '':
        setWatchValue(chat_id, message, '')
