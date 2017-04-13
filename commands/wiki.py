# coding=utf-8
import json
import urllib


def run(bot, chat_id, user, keyConfig, message, totalResults=1):
    requestText = message.replace(bot.name, "").strip()


    wikiUrl = \
        'https://simple.wikipedia.org/w/api.php?action=opensearch&limit=1&namespace=0&format=json&search='
    realUrl = wikiUrl + requestText.encode('utf-8')
    data = json.load(urllib.urlopen(realUrl))
    if len(data[2]) and data[2][0] != '' >= 1:
        bot.sendMessage(chat_id=chat_id, text=(user + ': ' if not user == '' else '') +
                                              data[2][0] + '\nLink: ' +
                                              data[3][0].replace('https://simple.wikipedia.org', 'https://en.wikipedia.org')
                        , disable_web_page_preview=True)
        return True
    else:
        wikiUrl = \
            'https://en.wikipedia.org/w/api.php?action=opensearch&limit=1&namespace=0&format=json&search='
        realUrl = wikiUrl + requestText.encode('utf-8')
        data = json.load(urllib.urlopen(realUrl))
        if len(data[2]) >= 1 and data[2][0] != '':
            bot.sendMessage(chat_id=chat_id, text=(user + ': ' if not user == '' else '') +
                                                  data[2][0] + '\nLink: ' + data[3][0],
                            disable_web_page_preview=True)
            return True
        else:
            bot.sendMessage(chat_id=chat_id,
                            text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                 ', I\'m afraid I can\'t find any wiki articles for ' +
                                 requestText.encode('utf-8') + '.')