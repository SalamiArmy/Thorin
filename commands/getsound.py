# coding=utf-8

import soundcloud


def run(bot, keyConfig, chat_id, user, message):
    requestText = message.replace(bot.name, "").strip()

    client = soundcloud.Client(client_id=keyConfig.get('Soundcloud', 'SC_CLIENT_ID'))
    track = client.get('/tracks', q=requestText.encode('utf-8'), sharing='public')
    if len(track) >= 1:
        bot.sendMessage(chat_id=chat_id, text=(user + ': ' if not user == '' else '') + track[0].permalink_url)
    else:
        bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') +
                                              ', I\'m afraid I can\'t find the sound of ' +
                                              requestText.encode('utf-8') + '.')