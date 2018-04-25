import conf
import telebot
from pymorphy2 import MorphAnalyzer
import flask
import random

pos_files_dict = {'NOUN': 'nouns.txt', 'ADJF': 'adjs.txt', 'ADJS': 'adjs.txt', 'COMP': 'adjs.txt', 'VERB': 'verbs.txt',  'INFN': 'verbs.txt',  'VERB': 'verbs.txt', 'PRTF': 'verbs.txt', 'PRTS': 'verbs.txt', 'GRND': 'verbs.txt', 'ADVB': 'advs.txt', 'NPRO': 'nouns.txt', 'PRCL': 'partcls.txt', 'INTJ': 'intjs.txt'}
genders_dict = {'masc': 'nounsm.txt', 'femn': 'nounsf.txt', 'neut': 'nounsn.txt'}

morph = MorphAnalyzer()

WEBHOOK_URL_BASE = "https://{}:{}".format(conf.WEBHOOK_HOST, conf.WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(conf.TOKEN)
bot = telebot.TeleBot(conf.TOKEN, threaded=False)

bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL_BASE+WEBHOOK_URL_PATH)

app = flask.Flask(__name__)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.send_message(message.chat.id, "Здравствуйте! Это бот, с которым можно разговаривать.")

@bot.message_handler(func=lambda m: True):
    def send(message):
 reply = ''
    for word in message.split(' '):
        ana = morph.parse(word.strip('.,:;?!()""'''))[0]
        if ana.tag.POS in pos_files_dict and ana.tag.POS not in ['NOUN', 'NPRO']:
            file = pos_files_dict[ana.tag.POS]
            words = (open(file, 'r').read()).split(' ')
            word_replace = random.choice(words)
            grammemes = set()
            grammemes.add(ana.tag.case)
            grammemes.add(ana.tag.gender)
            grammemes.add(ana.tag.mood)
            grammemes.add(ana.tag.number)
            grammemes.add(ana.tag.person)
            grammemes.add(ana.tag.tense)
            grammemes.add(ana.tag.voice)
            grammemes.remove(None)
            word_replace = ((morph.parse(word_replace)[0]).inflect(grammemes)).word
        elif ana.tag.POS in ['NOUN', 'NPRO'] and ana.tag.gender != None:
            file = genders_dict[ana.tag.gender]
            words = (open(file, 'r').read()).split(' ')
            word_replace = random.choice(words)
            grammemes = set()
            grammemes.add(ana.tag.case)
            grammemes.add(ana.tag.mood)
            grammemes.add(ana.tag.number)
            grammemes.add(ana.tag.person)
            grammemes.add(ana.tag.tense)
            grammemes.add(ana.tag.voice)
            grammemes.remove(None)
            word_replace = ((morph.parse(word_replace)[0]).inflect(grammemes)).word
        else:
            word_replace = word.strip('.,:;?!()""''')
        reply = reply + word_replace + ' '
            
        bot.send_message(message.chat.id, reply)
        
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return 'ok'

@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)

if __name__ == '__main__':
    bot.polling(none_stop=True)
