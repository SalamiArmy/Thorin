import base64
import urllib
import requests

from google.appengine.api import urlfetch

def run(bot, chat_id, user, keyConfig, message, totalResults=1):
    voices = ['en-US_AllisonVoice']
    sent = False
    for voice in voices:
        data = get_voice(message, keyConfig, voice)
        if data:
            requests.post('https://api.telegram.org/bot' + keyConfig.get('Telegram', 'TELE_BOT_ID') +
                          '/sendVoice?chat_id='+str(chat_id),
                          files={'voice': ('saying.ogg', data, 'audio/ogg', {'Expires': '0'})})
            sent = True
    if not sent:
        bot.sendMessage(chat_id=str(chat_id), text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                  ', I\'m afraid I can\'t say that.')

def get_voice(text, keyConfig, voice):
    IBMusername = keyConfig.get('IBM', 'username')
    IBMpassword = keyConfig.get('IBM', 'password')
    args = urllib.urlencode({'text': text.encode('utf-8'),
                             'voice': voice,
                             'caption': voice})
    return urlfetch.fetch('https://stream.watsonplatform.net/text-to-speech/api/v1/synthesize?' + args,
                          headers={'Authorization':'Basic %s' %
                                                   base64.b64encode(IBMusername + ':' + IBMpassword)}).content

