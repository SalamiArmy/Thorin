# coding=utf-8
import json
import string
import urllib

from google.appengine.ext import ndb

import main
from commands import define

watchedCommandName = 'define'


class WatchValue(ndb.Model):
    # key name: str(chat_id)
    currentValue = ndb.StringProperty(indexed=False, default='')


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


def run(bot, keyConfig, chat_id, user, message, intention_confidence=0.0):
    getData = define.get_define_data(keyConfig, user, message, intention_confidence)
    if ('<blockquote>' not in getData):
        OldValue = getWatchValue(chat_id)
        if OldValue != getData:
            setWatchValue(chat_id, getData)
            if user != 'Watcher':
                if OldValue == '':
                    bot.sendMessage(chat_id=chat_id, text='Now watching /' + watchedCommandName + '\n' + getData)
                else:
                    bot.sendMessage(chat_id=chat_id,
                                    text='Now watching /' + watchedCommandName + '\n' + getData)
            else:
                bot.sendMessage(chat_id=chat_id,
                                text='Watch for /' + watchedCommandName + ' has changed.\n' + getData)
        else:
            if user != 'Watcher':
                bot.sendMessage(chat_id=chat_id,
                                text='Watch for /' + watchedCommandName + ' has not changed:\n' + getData)
        if not main.AllWatchesContains(watchedCommandName, chat_id):
            main.addToAllWatches(watchedCommandName, chat_id)
    else:
        bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                              ', I\'m afraid I can\'t watch ' +
                                              'because I did not find any results from /' + watchedCommandName)
