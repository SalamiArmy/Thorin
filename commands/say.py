import base64
import urllib
import requests

from google.appengine.api import urlfetch

def run(bot, chat_id, user, keyConfig, message, totalResults=1):
    IBMusername = keyConfig.get('IBM', 'username')
    IBMpassword = keyConfig.get('IBM', 'password')
    args = urllib.urlencode({'text': message})
    data = urlfetch.fetch('https://stream.watsonplatform.net/text-to-speech/api/v1/synthesize?voice=en-GB_KateVoice&' + args,
                             headers={'Authorization':'Basic %s' % base64.b64encode(IBMusername + ':' + IBMpassword)}).content
    if data:
        requests.post('https://api.telegram.org/bot' + keyConfig.get('Telegram', 'TELE_BOT_ID') + '/sendVoice?chat_id='+str(chat_id),
                      files={'voice': ('saying.ogg', data, 'audio/ogg', {'Expires': '0'})})
    else:
        bot.sendMessage(chat_id=str(chat_id), text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                  ', I\'m afraid I can\'t say that.')
