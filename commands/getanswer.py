# coding=utf-8
import tungsten


def run(bot, keyConfig, chat_id, user, message):
    requestText = message.replace(bot.name, "").strip()


    client = tungsten.Tungsten(keyConfig.get('Wolfram', 'WOLF_APP_ID'))
    result = client.query(requestText)
    if len(result.pods) >= 1:
        fullAnswer = ''
        for pod in result.pods:
            for answer in pod.format['plaintext']:
                if not answer == None:
                    fullAnswer += answer.encode('ascii', 'ignore')
        userWithCurrentChatAction = chat_id
        urlForCurrentChatAction = (user + ': ' if not user == '' else '') + fullAnswer
        bot.sendMessage(chat_id=chat_id, text=urlForCurrentChatAction)
    else:
        userWithCurrentChatAction = chat_id
        urlForCurrentChatAction = 'I\'m sorry ' + (user if not user == '' else 'Dave') + \
                                  ', I\'m afraid I can\'t find any answers for ' + \
                                  requestText.encode('utf-8')
        bot.sendMessage(chat_id=userWithCurrentChatAction, text=urlForCurrentChatAction)