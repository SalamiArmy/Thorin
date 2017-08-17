import ConfigParser
import importlib
import json
import logging
import urllib
import sys

import urllib2
import telegram

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb

import webapp2

from commands import login

BASE_URL = 'https://api.telegram.org/bot'

# Read keys.ini file at program start (don't forget to put your keys in there!)
keyConfig = ConfigParser.ConfigParser()
keyConfig.read(["keys.ini", "..\keys.ini"])

bot = telegram.Bot(keyConfig.get('Telegram', 'TELE_BOT_ID'))

# ================================


class AllWatchesValue(ndb.Model):
    # key name: AllWatches
    currentValue = ndb.StringProperty(indexed=False, default='')

# ================================

def addToAllWatches(command, chat_id, request=''):
    es = AllWatchesValue.get_or_insert('AllWatches')
    es.currentValue += ',' + str(chat_id) + ':' + command + (':' + request.replace(',', '%2C') if request != '' else '')
    es.put()

def AllWatchesContains(command, chat_id, request=''):
    es = AllWatchesValue.get_by_id('AllWatches')
    if es:
        return (',' + str(chat_id) + ':' + command + (':' + request.replace(',', '%2C') if request != '' else '')) in str(es.currentValue) or \
               (str(chat_id) + ':' + command + (':' + request.replace(',', '%2C') if request != '' else '') + ',') in str(es.currentValue)
    return False

def setAllWatchesValue(NewValue):
    es = AllWatchesValue.get_or_insert('AllWatches')
    es.currentValue = NewValue
    es.put()

def getAllWatches():
    es = AllWatchesValue.get_by_id('AllWatches')
    if es:
        return es.currentValue
    return ''

def removeFromAllWatches(watch):
    setAllWatchesValue(getAllWatches().replace(',' + watch.replace(',', '%2C'), '').replace(watch.replace(',', '%2C'), ''))

# ================================

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(
            BASE_URL + keyConfig.get('Telegram', 'TELE_BOT_ID') + '/getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(
            BASE_URL + keyConfig.get('Telegram', 'TELE_BOT_ID') + '/getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(
                BASE_URL + keyConfig.get('Telegram', 'TELE_BOT_ID') + '/setWebhook', urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(120)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        if 'message' in body or 'edited_message' in body:
            message = body['message'] if 'message' in body else body['edited_message']
            text = message.get('text')
            fr = message.get('from')
            user = fr['username'] \
                if 'username' in fr \
                else fr['first_name'] + ' ' + fr['last_name'] \
                if 'first_name' in fr and 'last_name' in fr \
                else fr['first_name'] if 'first_name' in fr \
                else 'Dave'
            if 'edited_message' in body:
                user += '(edited)'
            chat = message['chat']
            chat_id = chat['id']
            chat_type = chat['type']

            if not text:
                logging.info('no text')
                return

            if text.startswith('/'):
                self.TryExecuteExplicitCommand(chat_id, user, text, chat_type)

    def TryExecuteExplicitCommand(self, chat_id, fr_username, text, chat_type):
        split = text[1:].lower().split(' ', 1)
        try:
            commandName = split[0].lower().replace(bot.name.lower(), '')
            totalResults = 1
            import re
            if len(re.findall('^[a-z]+\d+$', commandName)) > 0:
                totalResults = re.findall('\d+$', commandName)[0]
                commandName = re.findall('^[a-z]+', commandName)[0]
            mod = importlib.import_module('commands.' + commandName)
            mod.run(bot, chat_id, fr_username, keyConfig, split[1] if len(split) > 1 else '', totalResults)
        except ImportError:
            if chat_type == 'private':
                bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (fr_username if not fr_username == '' else 'Dave') +
                                                      ', I\'m afraid I do not recognize the ' + commandName + ' command.')
        except:
            print("Unexpected Exception running command:",  str(sys.exc_info()[0]) + str(sys.exc_info()[1]))
            try:
                bot.sendMessage(chat_id=keyConfig.get('BotAdministration', 'TESTING_GROUP_CHAT_ID'),
                                text='I\'m sorry Admins, I\'m afraid there\'s been an error. For ' + fr_username +
                                     '\'s request ' + (('\'' + split[1] + '\'') if len(split) > 1 else '') +
                                     '. Command ' + split[0] + ' threw:\n' +
                                     str(sys.exc_info()[0]) + '\n' +
                                     str(sys.exc_info()[1]))
            except:
                print("Unexpected error sending error response:",  str(sys.exc_info()[0]) + str(sys.exc_info()[1]))

    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        command = self.request.get('command')
        requestText = self.request.get('message')
        chat_id = self.request.get('username')
        loginPin = self.request.get('password')
        total_results = self.request.get('total_results')
        if loginPin == login.getLoginCodeValue(chat_id):
            self.TryExecuteExplicitCommand(chat_id, 'Web', '/' + command + (total_results if total_results is not None else '') + ' ' + requestText, 'private')


class TriggerAllWatches(webapp2.RequestHandler):
    def get(self):
        AllWatches = getAllWatches()
        watches_split = AllWatches.split(',')
        if len(watches_split) >= 1:
            for watch in watches_split:
                print('got watch ' + watch)
                split = watch.split(':')
                if len(split) >= 2:
                    removeGet = split[1].replace('get', '')
                    mod = importlib.import_module('commands.watch' + removeGet)
                    chat_id = split[0]
                    request_text = (split[2] if len(split) == 3 else '')
                    removeCommaEncoding = request_text.replace('%2C', ',')
                    mod.run(bot, chat_id, 'Watcher', keyConfig, removeCommaEncoding)
                else:
                    print('removing from all watches: ' + watch)
                    removeFromAllWatches(watch)

class ClearAllWatches(webapp2.RequestHandler):
    def get(self):
        setAllWatchesValue('')

class Login(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(10)
        login.run(bot, self.request.get('username'))
        self.response.write('A pin has been sent.')
        return self.response

app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
    ('/allwatches', TriggerAllWatches),
    ('/clearallwatches', ClearAllWatches),
    ('/login', Login)
], debug=True)
