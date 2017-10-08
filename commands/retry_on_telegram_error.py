# coding=utf-8
import sys
import urllib2
from time import sleep
from google.appengine.api import urlfetch

import telegram


def IsTooLongForCaption(text):
    return len(text) > 200

def SendDocumentWithRetry(bot, chat_id, imagelink, requestText):
    encodedImageLink = imagelink.encode('utf-8')
    numberOfRetries = 5
    sendException = True
    while sendException and numberOfRetries > 0:
        try:
            if not IsTooLongForCaption(requestText):
                bot.sendDocument(chat_id=chat_id,
                                 document=encodedImageLink,
                                 filename=requestText.replace('.',''),
                                 caption=requestText)
            else:
                bot.sendDocument(chat_id=chat_id,
                                 document=encodedImageLink,
                                 filename=requestText.replace('.',''))
            sendException = False
        except telegram.error.BadRequest:
            break
        except urlfetch.DeadlineExceededError:
            break
        except urllib2.HTTPError:
            break
        except urllib2.URLError:
            break
        except:
            sendException = True
            numberOfRetries -= 1
            print(sys.exc_info()[0])
            sleep(10)
    DidSend = not sendException and numberOfRetries > 0
    if DidSend and IsTooLongForCaption(requestText):
        bot.sendMessage(chat_id=chat_id, text=requestText, disable_web_page_preview=True)
    return DidSend

def SendPhotoWithRetry(bot, chat_id, imagelink, requestText):
    encodedImageLink = imagelink.encode('utf-8')
    numberOfRetries = 5
    sendException = True
    while sendException and numberOfRetries > 0:
        try:
            if not IsTooLongForCaption(requestText):
                bot.sendPhoto(chat_id=chat_id,
                              photo=encodedImageLink,
                              caption=requestText)
            else:
                bot.sendPhoto(chat_id=chat_id,
                              photo=encodedImageLink)
            sendException = False
        except telegram.error.BadRequest:
            break
        except urlfetch.DeadlineExceededError:
            break
        except urllib2.HTTPError:
            break
        except urllib2.URLError:
            break
        except:
            sendException = True
            numberOfRetries -= 1
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])
            sleep(10)
    DidSend = not sendException and numberOfRetries > 0
    if DidSend and IsTooLongForCaption(requestText):
        bot.sendMessage(chat_id=chat_id, text=requestText, disable_web_page_preview=True)
    return DidSend
