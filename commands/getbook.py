# coding=utf-8
import json
import urllib
from bs4 import BeautifulSoup

from google.appengine.ext import ndb

CommandName = 'get'

class SeenBooks(ndb.Model):
    # key name: get:str(chat_id)
    allPreviousSeenBooks = ndb.StringProperty(indexed=False, default='')


# ================================

def setPreviouslySeenBooksValue(chat_id, NewValue):
    es = SeenBooks.get_or_insert(CommandName + ':' + str(chat_id))
    es.allPreviousSeenBooks = NewValue.encode('utf-8')
    es.put()

def addPreviouslySeenBooksValue(chat_id, NewValue):
    es = SeenBooks.get_or_insert(CommandName + ':' + str(chat_id))
    if es.allPreviousSeenBooks == '':
        es.allPreviousSeenBooks = NewValue.encode('utf-8').replace(',', '')
    else:
        es.allPreviousSeenBooks += ',' + NewValue.encode('utf-8').replace(',', '')
    es.put()

def getPreviouslySeenBooksValue(chat_id):
    es = SeenBooks.get_or_insert(CommandName + ':' + str(chat_id))
    if es:
        return es.allPreviousSeenBooks.encode('utf-8')
    return ''

def wasPreviouslySeenBook(chat_id, book_title):
    allPreviousLinks = getPreviouslySeenBooksValue(chat_id)
    if ',' + book_title + ',' in allPreviousLinks or \
            allPreviousLinks.startswith(book_title + ',') or  \
            allPreviousLinks.endswith(',' + book_title) or  \
            allPreviousLinks == book_title:
        return True
    return False


def run(bot, chat_id, user, keyConfig, message):
    requestText = message.replace(bot.name, "").strip()
    args = {'key': keyConfig.get('GoodReads', 'KEY'),
            'search[field]': 'all',
            'safe': 'off',
            'q': requestText,
            'page': 1}
    realUrl = 'https://www.goodreads.com/search/index.xml?' + urllib.urlencode(args)
    raw_xml_data = urllib.urlopen(realUrl).read()
    bookTitles, ratings, total_ratings, bookIDs, bookDescriptions = book_results_parser(raw_xml_data, keyConfig)

    offset = 0
    while offset < len(bookTitles):
        offset += 1
        bookTitle = bookTitles[offset].string
        if not wasPreviouslySeenBook(chat_id, bookTitle):
            bookData = FormatDesc(bookDescriptions[offset])
            url = 'https://www.goodreads.com/book/show/' + bookIDs[offset].string + '-' + requestText.replace(' ', '-')
            rating = ratings[offset].string
            total_rating = total_ratings[offset].string
            bot.sendMessage(chat_id=chat_id, text=(user + ': *' if not user == '' else '*') + bookTitle + '*\n' +
                                                  '_Rated ' + rating.encode('utf-8') + ' out of 5 by ' +
                                                  total_rating + ' GoodReads users._\n' + bookData + '\n' +
                                                  url,
                            parse_mode='Markdown')
            addPreviouslySeenBooksValue(chat_id, bookTitle)
            break
    if offset == len(bookTitles):
        bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                              ', I\'m afraid I can\'t find any books' +
                                              (' that you haven\'t already seen' if len(bookTitles) > 0 and offset > 0 else '') +
                                              ' for ' + requestText.encode('utf-8') + '.')

def FormatDesc(Desc):
    return Desc.replace('<br />', '\n').replace('<i>', '_').replace('</i>', '_').replace('<em>', '*').replace('</em>', '*')



def book_results_parser(rawMarkup, keyConfig):
    soup = BeautifulSoup(rawMarkup)
    bookDescriptions = []
    for id in soup.findAll('id'):
        realUrl = 'https://www.goodreads.com/book/show.xml?key=' + keyConfig.get('GoodReads', 'KEY') + '&id=' + id.string
        raw_xml_object = urllib.urlopen(realUrl).read()
        data = BeautifulSoup(raw_xml_object)
        try_find_description = data.findAll('description')
        if len(try_find_description)>0:
            bookDescriptions += try_find_description[0]
    return soup.findAll('title'), soup.findAll('average_rating'), soup.findAll('ratings_count'), soup.findAll('id'), bookDescriptions