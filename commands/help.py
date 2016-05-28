import ConfigParser
import os


def run(bot, keyConfig, chat_id, user, message):
    keyConfig = ConfigParser.ConfigParser()
    keyConfig.read(["keys.ini", "..\keys.ini"])

    bot = telegram.Bot(keyConfig.get('Telegram', 'TELE_BOT_ID'))

    try:
        available_commands = [f for f in os.listdir("./commands") if f.endswith(".py") and f != "__init__.py"]
        bot.sendMessage(chat_id=chat_id, text="I know:\n" + "\n".join(map(lambda x: x[:-3], available_commands)))
    except:
        bot.sendMessage(chat_id=chat_id, text='I\'m sorry ' + (user if not user == '' else 'Dave') + \
                                              ', I\'m afraid there\'s no helping you.')