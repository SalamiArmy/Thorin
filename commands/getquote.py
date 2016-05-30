# coding=utf-8
import json
import re
import urllib


def run(bot, keyConfig, chat_id, user, message):
    requestText = message.replace(bot.name, "").strip()

    wikiUrl = \
        'https://simple.wikiquote.org/w/api.php?action=query&list=search&srlimit=1&namespace=0&format=json&srsearch='
    realUrl = wikiUrl + requestText.encode('utf-8')
    data = json.load(urllib.urlopen(realUrl))
    if len(data['query']['search']) >= 1:
        formattedQuoteSnippet = re.sub(r'<[^>]*?>', '',
            data['query']['search'][0]['snippet'].replace('<span class="searchmatch">', '*').replace(
                '</span>', '*'))
        userWithCurrentChatAction = chat_id
        urlForCurrentChatAction = (user + ': ' if not user == '' else '') + formattedQuoteSnippet + \
                                  '\nhttps://simple.wikiquote.org/wiki/' + \
                                  urllib.quote(data['query']['search'][0]['title'].encode('utf-8'))
        bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction,
                        disable_web_page_preview=True, parse_mode='Markdown')
    else:
        wikiUrl = \
            'https://en.wikiquote.org/w/api.php?action=query&list=search&srlimit=1&namespace=0&format=json&srsearch='
        realUrl = wikiUrl + requestText.encode('utf-8')
        data = json.load(urllib.urlopen(realUrl))
        if len(data['query']['search']) >= 1:
            formattedQuoteSnippet = re.sub(r'<[^>]*?>', '',
                data['query']['search'][0]['snippet'].replace('<span class="searchmatch">', '*').replace(
                    '</span>', '*'))
            bot.sendMessage(chat_id=chat_id, text=(user + ': ' if not user == '' else '') + formattedQuoteSnippet + \
                                                  '\nhttps://en.wikiquote.org/wiki/' + \
                                                  urllib.quote(data['query']['search'][0]['title'].encode('utf-8')),
                            disable_web_page_preview=True, parse_mode='Markdown')
        else:
            bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') + \
                                      ', I\'m afraid I can\'t find any quotes for ' + \
                                      requestText.encode('utf-8') + '.')