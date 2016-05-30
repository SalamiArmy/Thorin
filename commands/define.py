# coding=utf-8
import random
import urllib

import xmltodict


def run(bot, keyConfig, chat_id, user, message):
    requestText = message.replace(bot.name, "").strip()

    dicUrl = 'http://www.dictionaryapi.com/api/v1/references/collegiate/xml/'
    realUrl = dicUrl + requestText.encode('utf-8') + '?key=' + keyConfig.get('Merriam-Webster', 'API_KEY')
    getXml = urllib.urlopen(realUrl).read()
    data = xmltodict.parse(getXml)
    getAllEntries = data['entry_list']
    if len(getAllEntries) >= 1:
        if 'suggestion' not in getAllEntries:
            getEntry = getAllEntries['entry']
            if type(getEntry) is list:
                entry = getEntry[random.randint(0, len(getEntry) - 1)]
            else:
                entry = getEntry
            send_formatted_entry(entry, bot, chat_id, user, requestText)
        else:
            bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                                  ', I\'m afraid I can\'t find any definitions for the word ' +
                                                  requestText +
                                                  '. Did you mean ' + ' '.join(getAllEntries['suggestion']) + '?')
    else:
        bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                              ', I\'m afraid I can\'t find any definitions for the word ' +
                                              requestText + '.')


def send_formatted_entry(entry, bot, chat_id, user, requestText):
    if 'fl' in entry:
        partOfSpeech = entry['fl']
        if len(partOfSpeech) >= 1:
            getAllDefs = entry['def']['dt']
            if type(getAllDefs) is list:
                getDefinition = getAllDefs[random.randint(0, len(getAllDefs) - 1)]
            else:
                getDefinition = getAllDefs
            if '#text' in getAllDefs:
                definitionText = getDefinition['#text'].replace(':', '')
            else:
                definitionText = getDefinition.replace(':', '')
            soundFilename = entry['sound']['wav']
            soundUrl = 'http://media.merriam-webster.com/soundc11/' + soundFilename[:1] + '/' + soundFilename
            bot.sendMessage(chat_id=chat_id, text=(user + ': ' if not user == '' else '') +
                                                  requestText.title() + "\n" +
                                                  partOfSpeech + ".\n\n" + definitionText + '\n' + soundUrl)
    elif 'cx' in entry:
        bot.sendMessage(chat_id=chat_id, text=(user + ': ' if not user == '' else '') +
                                              requestText.title() + ":\n" +
                                              entry['cx']['cl'] + ' ' + entry['ew'])
    else:
        bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                              ', I\'m afraid I can\'t find any definitions for the word ' +
                                              requestText + '.')


        ############################# Ashley: http://dictionaryapi.net/ is down! ###############################
        # dicUrl = 'http://dictionaryapi.net/api/definition/'
        # realUrl = dicUrl + requestText.encode('utf-8')
        # data = json.load(urllib.urlopen(realUrl))
        # if len(data) >= 1:
        #     partOfSpeech = data[random.randint(0, len(data) - 1)]
        #     if len(partOfSpeech['Definitions']) >= 1:
        #         definitionText = partOfSpeech['Definitions'][0]
        #         bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
        #         userWithCurrentChatAction = chat_id
        #         urlForCurrentChatAction = (user + ': ' if not user == '' else '') +\
        #                                   requestText.title() + ":\n" + \
        #                                   partOfSpeech['PartOfSpeech'] + ".\n\n" + definitionText
        #         bot.sendMessage(chat_id=chat_id, text=urlForCurrentChatAction)
        #     else:
        #         bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
        #         userWithCurrentChatAction = chat_id
        #         urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
        #                                   ', I\'m afraid I can\'t find any definitions for the word ' +\
        #                                   requestText + '.'
        #         bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)
        # else:
        #     bot.sendChatAction(chat_id=chat_id, action=telegram.ChatAction.TYPING)
        #     userWithCurrentChatAction = chat_id
        #     urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') +\
        #                               ', I\'m afraid I can\'t find any definitions for the word ' +\
        #                               requestText + '.'
        #     bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)