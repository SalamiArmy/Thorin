# coding=utf-8

from commands import watch

def run(bot, keyConfig, chat_id, user, message, intention_confidence=0.0):
    watch.setWatchValue(watch.getAllWatches().replace(',' + chat_id + ':' + message + ',', ',').replace(',' + chat_id + ':' + message, ''))
