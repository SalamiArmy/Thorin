# coding=utf-8
import sys
from time import sleep

import telegram


def IsTooLongForCaption(text):
    return len(text) > 200


def SendDocumentWithRetry(bot, chat_id, imagelink, requestText):
    encodedImageLink = imagelink.encode('utf-8')
    numberOfRetries = 5
    sendException = True
    while sendException and numberOfRetries > 0:
        caption_text = requestText + ': ' + encodedImageLink
        try:
            if not IsTooLongForCaption(caption_text):
                bot.sendDocument(chat_id=chat_id,
                                 document=encodedImageLink,
                                 filename=requestText.replace('.',''),
                                 caption=caption_text)
            else:
                bot.sendDocument(chat_id=chat_id,
                                 document=encodedImageLink,
                                 filename=requestText.replace('.',''))
            sendException = False
        except telegram.error.BadRequest:
            break
        except:
            sendException = True
            numberOfRetries -= 1
            print(sys.exc_info()[0])
            sleep(10)
    DidSend = not sendException and numberOfRetries > 0
    if DidSend and IsTooLongForCaption(caption_text):
        bot.sendMessage(chat_id=chat_id, text=caption_text,disable_web_page_preview=True)
    return DidSend


def SendPhotoWithRetry(bot, chat_id, imagelink, requestText):
    encodedImageLink = imagelink.encode('utf-8')
    if imagelink[:4] == '.gif':
        return False
    numberOfRetries = 5
    sendException = True
    while sendException and numberOfRetries > 0:
        caption_text = requestText + ': ' + encodedImageLink
        try:
            if not IsTooLongForCaption(caption_text):
                bot.sendPhoto(chat_id=chat_id,
                              photo=encodedImageLink,
                              caption=caption_text)
            else:
                bot.sendPhoto(chat_id=chat_id,
                              photo=encodedImageLink)
            sendException = False
        except telegram.error.BadRequest:
            break
        except:
            sendException = True
            numberOfRetries -= 1
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])
            sleep(10)
    DidSend = not sendException and numberOfRetries > 0
    if DidSend and IsTooLongForCaption(caption_text):
        bot.sendMessage(chat_id=chat_id, text=caption_text, disable_web_page_preview=True)
    return DidSend
