import telebot
import sys
from telebot import types
from fractions import Fraction
from bs4 import BeautifulSoup
from flask import Flask, request
from datetime import datetime, timedelta
import random
import requests
import urllib.parse
import urllib.request
import datetime
from geopy.geocoders import Nominatim
from pyowm import OWM
import time
import wikipedia
import traceback
import re
from googleapiclient.discovery import build

CHAT_ID = 'спизжено'
api_key = "спизжено"
API_TOKEN = 'неть'
API_KEY = "спизжено"
PEXELS_API_KEY = "спизжено"
UNSPLASH_ACCESS_KEY = 'спизжено'
TOKEN = 'спизжено'
giphy_api_key = 'спизжено'
PIXABAY_API_KEY = 'спизжено'
YOUTUBE_API_KEY = 'спизжено'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)
answers = {}
rules = {}
PASSWORD = 'shutdownbot'
tracked_messages = {}

geolocator = Nominatim(user_agent='your-user-agent')
owm = OWM(API_TOKEN)


@app.route('/process_update', methods=['POST'])  # do not forget to update endpoint
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK"


@bot.message_handler(content_types=['photo', 'video', 'document'])
def handle_media(message):
    response = random.choice(["ладно", "жиза", "А на часах ноль-ноль", "Мать ебал"])
    bot.send_message(message.chat.id, response)


ignored_user_ids = []

delete_user_message = [""]

password_required = False
password_requested_by = None
password_attempts = 0
max_password_attempts = 3
shutdown_in_progress = False
next_attempt_time = None


def check_password(message):
    global password_required, password_requested_by, password_attempts, shutdown_in_progress, next_attempt_time

    if (
            password_required
            and password_requested_by == message.from_user.id
            and message.text == PASSWORD
    ):
        bot.send_message(message.chat.id, 'Пароль верный. Бот отключается...')

        bot.stop_polling()
        sys.exit()
    else:
        password_attempts += 1
        remaining_attempts = max_password_attempts - password_attempts

        if password_attempts >= max_password_attempts:
            bot.send_message(message.chat.id, 'Лимит попыток исчерпан. Попробуйте позже.')
            shutdown_in_progress = True
            next_attempt_time = datetime.datetime.now() + datetime.timedelta(
                minutes=5)
        elif remaining_attempts > 1:
            bot.send_message(message.chat.id,
                             f'Пароль неверный. Введите пароль. Осталось {remaining_attempts} попытки:')
            bot.register_next_step_handler(message, check_password)
        elif remaining_attempts == 1:
            bot.send_message(message.chat.id, f'Пароль неверный. Введите пароль. Осталась 1 попытка:')
            bot.register_next_step_handler(message, check_password)
        else:
            bot.send_message(message.chat.id, 'Лимит попыток исчерпан. Попробуйте позже.')


@bot.message_handler(commands=['shutdown'])
def handle_shutdown_command(message):
    global password_required, password_requested_by, password_attempts, shutdown_in_progress, next_attempt_time

    if shutdown_in_progress and datetime.datetime.now() < next_attempt_time:
        remaining_time = next_attempt_time - datetime.datetime.now()
        bot.send_message(message.chat.id,
                         f'Лимит попыток исчерпан. Попробуйте позже. Осталось времени: {remaining_time.seconds // 60} минут')
        return

    if str(message.from_user.id) == target_ban_ignor:
        password_required = True
        password_requested_by = message.from_user.id
        password_attempts = 0
        bot.send_message(message.chat.id, 'Введите пароль:')
        bot.register_next_step_handler(message, check_password)
    else:
        bot.send_message(message.chat.id, "Молодой человек, идите нахуй, у вас нет прав!")


@bot.message_handler(func=lambda message: str(message.from_user.id) in delete_user_message)
def handle_ignored_users(message):
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)


@bot.message_handler(commands=['deleteuser'])
def handle_ignore_command(message):
    if str(message.from_user.id) == target_ban_ignor:
        user_id = message.text.split(' ')[1]
        delete_user_message.append(user_id)
        bot.reply_to(message, f'У Пользователя с ID {user_id} будут удалятся сообщения')
    else:
        bot.send_message(message.chat.id, "Молодой человек идите нахуй у вас нет прав!")


@bot.message_handler(commands=['deleteclear'])
def handle_clear_ignore_command(message):
    if str(message.from_user.id) == target_lox:
        delete_user_message.clear()
        bot.reply_to(message, 'Список удаляемых пользователей очищен.')
    else:
        bot.reply_to(message, 'Молодой человек идите нахуй, у вас нет прав!')


@bot.message_handler(commands=['deletelist'])
def handle_ignorelist_command(message):
    ignored_users = []
    for user_id in delete_user_message:
        try:
            user = bot.get_chat_member(message.chat.id, user_id)
            ignored_users.append(f'ID: {user_id}, Ник: @{user.user.username}')
        except Exception:
            ignored_users.append(f'ID: {user_id}, Ник: Хуй знает')

    if ignored_users:
        response = 'Список удаляемых пользователей:\n' + '\n'.join(ignored_users)
    else:
        response = 'Список удаляемых пользователей пуст.'

    bot.reply_to(message, response)


@bot.message_handler(func=lambda message: str(message.from_user.id) in ignored_user_ids)
def handle_delete_matvei(message):
    pass


@bot.message_handler(commands=['searchgif'])
def search_gif(message):
    query = ' '.join(message.text.split()[1:])
    if not query:
        bot.send_message(message.chat.id, 'Чтобы получить гифку по запросу введите: /searchgif (запрос без скобок)')

    url = f'https://api.giphy.com/v1/gifs/search?api_key={giphy_api_key}&q={query}&limit=1'
    if not query:
        url = f'https://api.giphy.com/v1/gifs/search?api_key={giphy_api_key}&q=cat&limit=1'

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and data['data'] and len(data['data']) > 0:
            gif_url = data['data'][0]['images']['original']['url']
            bot.send_animation(message.chat.id, gif_url)
        else:
            bot.send_message(message.chat.id, 'Блять запрос писать научись, нихуя не найдено')
    else:
        bot.send_message(message.chat.id, 'Ерор нахой')


@bot.message_handler(func=lambda message: message.text.lower() == "бан матвея по ip")
def handle_start(message):
    reply_message = bot.send_message(message.chat.id, "Бан матвея запущен...")

    time.sleep(2)

    bot.delete_message(message.chat.id, reply_message.message_id)

    reply_message = bot.send_message(message.chat.id, "Вычисление ip матвея...")

    time.sleep(3)

    bot.delete_message(message.chat.id, reply_message.message_id)

    reply_message = bot.send_message(message.chat.id, "Занесение ip в базу данных бана...")

    time.sleep(2)

    bot.delete_message(message.chat.id, reply_message.message_id)

    reply_message = bot.send_message(message.chat.id, "Взламывание матвея по ip...")

    time.sleep(2)

    bot.delete_message(message.chat.id, reply_message.message_id)

    bot.send_message(message.chat.id, "Матвей забанен ✅")


@bot.message_handler(func=lambda message: message.text.lower() == "бан лёши по ip")
def handle_ban_losha(message):
    reply_message = bot.send_message(message.chat.id, "Бан Лёши запущен...")

    time.sleep(2)

    bot.delete_message(message.chat.id, reply_message.message_id)

    reply_message = bot.send_message(message.chat.id, "Вычисление ip Лёши...")

    time.sleep(3)

    bot.delete_message(message.chat.id, reply_message.message_id)

    reply_message = bot.send_message(message.chat.id, "Занесение ip в базу данных бана...")

    time.sleep(2)

    bot.delete_message(message.chat.id, reply_message.message_id)

    reply_message = bot.send_message(message.chat.id, "Взламывание Лёши по ip...")

    time.sleep(2)

    bot.delete_message(message.chat.id, reply_message.message_id)

    bot.send_message(message.chat.id, "Лёша забанен ✅")

    bot.send_message(1864373905, "Вы забанены ✅")


@bot.message_handler(func=lambda message: message.text.lower() == "бан санёчка по ip")
def handle_ban_losha(message):
    reply_message = bot.send_message(message.chat.id, "Бан санёчка запущен...")

    time.sleep(2)

    bot.delete_message(message.chat.id, reply_message.message_id)

    reply_message = bot.send_message(message.chat.id, "Вычисление ip санёчка...")

    time.sleep(3)

    bot.delete_message(message.chat.id, reply_message.message_id)

    reply_message = bot.send_message(message.chat.id, "Занесение ip в базу данных бана...")

    time.sleep(2)

    bot.delete_message(message.chat.id, reply_message.message_id)

    reply_message = bot.send_message(message.chat.id, "Взламывание санёчка по ip...")

    time.sleep(2)

    bot.delete_message(message.chat.id, reply_message.message_id)

    bot.send_message(message.chat.id, "санёчек забанен ✅")


@bot.message_handler(func=lambda message: any(entity.type == 'url' for entity in message.entities or []))
def check_links(message):
    bot.reply_to(message, "Ни понял эта мы чё тут рекламу через ссылки пихаем?")


@bot.message_handler(commands=['video'])
def handle_video_command(message):
    search_query = message.text.replace('/video', '').strip()
    videos = search_videos(search_query)

    if videos:
        for video in videos:
            bot.send_video(message.chat.id, video)
    else:
        bot.send_message(message.chat.id, 'Н И Х У Я   НЕ НАЙДЕНО')


def search_videos(query):
    url = f'https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={query}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        videos = data['hits']
        video_urls = [video['videos']['large']['url'] for video in videos]
        return video_urls
    else:
        return None


@bot.message_handler(commands=['music'])
def handle_music_command(message):
    search_query = message.text.replace('/music', '').strip()
    audios = search_music(search_query)

    if audios:
        for audio in audios:
            bot.send_audio(message.chat.id, audio)
    else:
        bot.send_message(message.chat.id, 'Да боже опять ничего не нашёл нахуй.')


def search_music(query):
    url = f'https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={query}&video_type=music'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        audios = data['hits']
        audio_urls = [audio['videos']['large']['url'] for audio in audios]
        return audio_urls
    else:
        return None


youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)


@bot.message_handler(commands=['youtube'])
def handle_youtube_command(message):
    search_query = message.text.replace('/youtube', '').strip()
    video = search_video(search_query)

    if video:
        bot.send_message(message.chat.id, video)
    else:
        bot.send_message(message.chat.id, 'По вашему запросу ничего не найдено.')


def search_video(query):
    search_response = youtube.search().list(
        q=query,
        part='id',
        type='video',
        maxResults=1
    ).execute()

    if 'items' in search_response:
        video_id = search_response['items'][0]['id']['videoId']
        video_url = 'https://www.youtube.com/watch?v=' + video_id
        return video_url
    else:
        return None


target_ban_ignor = "1130692453"


@bot.message_handler(commands=['ignoruser'])
def handle_ignore_command_ignor(message):
    if str(message.from_user.id) == target_ban_ignor:
        user_id = message.text.split(' ')[1]
        ignored_user_ids.append(user_id)
        bot.reply_to(message, f'Пользователь с ID {user_id} будет игнорироваться.')
    else:
        bot.send_message(message.chat.id, "Молодой человек идите нахуй у вас нет прав!")


@bot.message_handler(commands=['ignorelist'])
def handle_ignorelist_command(message):
    ignored_users = []
    for user_id in ignored_user_ids:
        try:
            user = bot.get_chat_member(message.chat.id, user_id)
            ignored_users.append(f'ID: {user_id}, Username: @{user.user.username}')
        except Exception:
            ignored_users.append(f'ID: {user_id}, Username: Unknown')

    if ignored_users:
        response = 'Список игнорируемых пользователей:\n' + '\n'.join(ignored_users)
    else:
        response = 'Список игнорируемых пользователей пуст.'

    bot.reply_to(message, response)


@bot.message_handler(commands=['settime'])
def start(message):
    bot.send_message(message.chat.id, 'теперь всё автоматом просчитывается никаих /settime тебе')
    # if str(message.from_user.id) == target_lox:
    #     global start_time
    #     time_str = message.text.split()[1]  # Получаем строку времени из команды /start
    #
    #     try:
    #         hours, minutes, seconds = map(int, time_str.split(':'))
    #         start_time = time.time() - (hours * 3600 + minutes * 60 + seconds)
    #         bot.reply_to(message, 'Начальное время установлено.')
    #     except ValueError:
    #         bot.reply_to(message, 'Неверный нахуй. ты лох используй ЧЧ:ММ:СС.')
    # else:
    #     bot.send_message(message.chat.id, "Молодой человек идите нахуй у вас нет прав!")


@bot.message_handler(commands=['time'])
def show_time(message):
    # get UTC time and add 7 hours
    nsk_time = datetime.utcnow() + datetime.timedelta(hours=7)

    # get hours, minutes and seconds from NSK time
    hours = nsk_time.hour
    minutes = nsk_time.minute
    seconds = nsk_time.second

    bot.reply_to(message, f'Время в новосибе? {hours + 1}:{minutes + 1} и {seconds + 1} секунд.')  # + 1, because 0-start


target_lox = "1130692453"


@bot.message_handler(commands=['clearignore'])
def handle_clear_ignore_command(message):
    if str(message.from_user.id) == target_lox:
        ignored_user_ids.clear()
        bot.reply_to(message, 'Список игнорируемых пользователей очищен.')
    else:
        bot.reply_to(message, 'Молодой человек идите нахуй, у вас нет прав!')


@bot.message_handler(commands=['calc'])
def handle_calc_command(message):
    expression = message.text.split('/calc ')[1]

    expression = expression.replace(' ', '')

    if not re.match(r'^\d+([-+*/]\d+)*$', expression):
        bot.reply_to(message, 'Неверное выражение!')
        return

    try:
        result = eval(expression)
        bot.reply_to(message, f'Результат: {result}')
    except Exception:
        bot.reply_to(message, 'Ошибка при вычислении выражения!')


@bot.message_handler(commands=['calcdrobi'])
def handle_calcdrobi_command(message):
    expression = message.text.split('/calcdrobi ')[1]

    expression = expression.replace(' ', '')

    operators = ['+', '-', '*', '/']
    for operator in operators:
        if operator in expression:
            operator_index = expression.index(operator)
            break

    if operator_index is None:
        bot.reply_to(message, 'Неверное выражение!')
        return

    try:
        fraction1 = Fraction(expression[:operator_index])
        fraction2 = Fraction(expression[operator_index + 1:])

        result = None

        if expression[operator_index] == '+':
            result = fraction1 + fraction2
        elif expression[operator_index] == '-':
            result = fraction1 - fraction2
        elif expression[operator_index] == '*':
            result = fraction1 * fraction2
        elif expression[operator_index] == '/':
            result = fraction1 / fraction2

        bot.reply_to(message, f'Результат: {result}')
    except Exception:
        bot.reply_to(message, 'Ошибка при вычислении выражения!')


@bot.message_handler(commands=["start1"])
def handlecommandsatrt(message):
    username = message.from_user.first_name
    bot.send_message(message.chat.id,
                     f"Ку {username} в этой обнове добавили обновленный список порнухи, обновлённый список сисек, функцию чтобы фото не повторялись два раза подряд, джо джо гифки, ладно теперь отправляется один раз, добавлен поиск в википедии, добавлена отправка стикеров,убраны некоторые ответки, кстати @alekami649 пошёл нахуй ещё добавили супер бесполезную функцию новостей (напишите (новости) ), плюс добавили функцию орла или решки и предсказаний, новые ответки да и вообщем то всё!")


@bot.message_handler(commands=["mat_ebal"])
def handlecommandsatrt(message):
    username = message.from_user.first_name
    bot.send_message(message.chat.id,
                     f"Молодой {username} я понимаю что вам хочется выебать свою мать но это может быть неприемлемым и я не согласен с вашим мнением на вашем месте я бы переформулировал свою точку зрения и не хотел бы выёбывать свою мать так что подумайте над моими словами и переформулируйте свою точку зрения если это возможно спасибо {username}")


@bot.message_handler(
    func=lambda message: message.text.lower() == "@pelmenvkusniy @aholaheew @alekami649 в чате активим")
def handle_activim2(message):
    for _ in range(2):
        bot.send_message(message.chat.id, "@pelmenvkusniy @aholaheew @alekami649 в чате активим")


@bot.message_handler(
    func=lambda message: message.text.lower() == "пинг лады")
def handle_lada(message):
    for _ in range(5):
        bot.send_message(message.chat.id, "@Krytai11 просыпайся")


@bot.message_handler(
    func=lambda message: message.text.lower() == "пинг всех")
def handle_pingvsex(message):
    for _ in range(6):
        bot.send_message(message.chat.id, "@alekami649 @aholaheew @maxim2312 @AleksFolt @Krytai11 просыпаемся ебланы")


@bot.message_handler(
    func=lambda message: message.text.lower() == "пинг лёши")
def handle_losha(message):
    for _ in range(9):
        bot.send_message(message.chat.id, "@alekami649 заебал спамить")


@bot.message_handler(
    func=lambda message: message.text.lower() == "ладно жиза бот кто твой создатель?")
def handle_activim1(message):
    bot.send_message(message.chat.id, "Мой создатель @AleksFolt")


@bot.message_handler(
    func=lambda message: message.text.lower() == "матвей")
def handle_activim1(message):
    bot.send_message(message.chat.id, "Матвеем по лбу не дало?")


# Заготовки для ников и соответствующих им ID
users = {
    'user1': 123456789,
    'user2': 987654321,
    # Добавьте другие ники и ID по вашему усмотрению
}


@bot.message_handler(commands=['sendmessage'])
def handle_send_message_command(message):
    args = message.text.split(' ', 2)
    if len(args) < 3:
        bot.send_message(message.chat.id,
                         "Пидр писать научись. Вот так надо: /sendmessage <ID еблана> <ну тут типа твоё сообщение> БЕЗ ВОТ ЭТОЙ ХУЙНИ <>")
        return

    recipient = args[1]
    text = args[2]

    if recipient in users:
        recipient_id = users[recipient]
    else:
        recipient_id = recipient  # Если ник не найден, считаем, что в recipient указан ID

    bot.send_message(recipient_id, text)
    bot.send_message(message.chat.id, "Сообщение впиздошено")


@bot.message_handler(commands=['sendgroup'])
def handle_send_group_command(message):
    args = message.text.split(' ', 2)
    if len(args) < 3:
        bot.send_message(message.chat.id,
                         "Да боже мой всему вас учить пиши /sendgroup <ID группы> <текст сообщения>")
        return

    group_id = args[1]
    text = args[2]

    bot.send_message(group_id, text)
    bot.send_message(message.chat.id, "Сообщение впиздошено в пизду ой в группу")


@bot.message_handler(func=lambda message: message.text.lower() == "дефолт")
def handle_activim1dsd(message):
    bot.send_message(message.chat.id, "http://mat.ebal.tilda.ws/")


@bot.message_handler(func=lambda message: message.text.lower() == "грамотный")
def handle_activim1dsd(message):
    bot.send_message(message.chat.id, "да, тебя ебёт?")


@bot.message_handler(commands=["list"])
def handlecommandsatrtfgjgkjdf(message):
    command_list = '''Список команд:
/shutdown - выключает бота
/deleteuser - удаляет сообщение по id
/deleteclear - удаляет удаление сообщений
/ignoruser - игнорит юзера
/ignorelist - выводит лист игнорируемых пользователей
/clearignore - удаляет игнорирование пользователей
/calc - калькулятор
/add_answer - добавление ответа
/weather - погода
/clear_answers -удаляет все ансверы но вы лохи этого не получите
/calcdrobi - складывает, умножает, вычитает, делит дроби
/ladnoaiplugins - просто стырил идею у леши 😊
/sendmessage (id) (сообщение)
/play - да хз параша какая то
/searchgif - найти гифку
/youtube - найти видео я хз как этим пользоваться
/music - ну музыка тоже хз как этим пользоваться
/video - типа видео и опять хз как этим пользоваться
/list - ну ты как бы этой командой сейчас пользуешься
/time - время
/settime - установить время но вы этого не получите лохи 😊☺️
/id - бля хз зачем это надо
'''
    bot.send_message(message.chat.id, command_list)


@bot.message_handler(commands=['ladnoaiplugins'])
def handle_aiplugins_command(message):
    keyboard = types.InlineKeyboardMarkup()

    button1 = types.InlineKeyboardButton(text='Calc', callback_data='button1')
    button2 = types.InlineKeyboardButton(text='Wikipedia', callback_data='button2')

    keyboard.add(button1, button2)

    bot.send_message(message.chat.id, 'Привет я стырил идею у @alekami649 и эти кнопки нечего не делают!',
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def handle_button_click(call):
    if call.data == 'button1':
        bot.answer_callback_query(call.id, 'Вы выбрали Calc')
    elif call.data == 'button2':
        bot.answer_callback_query(call.id, 'Вы выбрали Wikipedia')


@bot.message_handler(
    func=lambda message: message.text.lower() == "@aholaheew @pelmenvkusniy @alekami649 в чате активим")
def handle_activim3(message):
    for _ in range(2):
        bot.send_message(message.chat.id, "@pelmenvkusniy @aholaheew @alekami649 в чате активим")


@bot.message_handler(
    func=lambda message: message.text.lower() == "@alekami649 @aholaheew @pelmenvkusniy в чате активим")
def handle_activim6654(message):
    for _ in range(2):
        bot.send_message(message.chat.id, "@pelmenvkusniy @aholaheew @alekami649 в чате активим")


@bot.message_handler(
    func=lambda message: message.text.lower() == "@alekami649 @pelmenvkusniy @aholaheew в чате активим")
def handle_activim4(message):
    for _ in range(2):
        bot.send_message(message.chat.id, "@pelmenvkusniy @aholaheew @alekami649 в чате активим")


@bot.message_handler(func=lambda message: message.text.lower() == "@alekami649")
def handle_alekami(message):
    for _ in range(5):
        bot.send_message(message.chat.id, "@alekami649")


@bot.message_handler(func=lambda message: message.text.lower() == "иди нахуй")
def handle_alekami649(message):
    bot.send_message(message.chat.id, "сам иди пидр безмамный")


@bot.message_handler(func=lambda message: message.text.lower() == "ladno")
def handle_ladnoenglish(message):
    bot.send_message(message.chat.id, "ladno")


@bot.message_handler(func=lambda message: message.text.lower() == "мать ебал")
def handle_matebal(message):
    username = message.from_user.first_name
    bot.reply_to(message, f"{username} заебал со своим Мать ебал")


sticker_ids = ['CAACAgIAAxkBAAEJdodklqms9fZWB4iEiWCBEfB7kAnDWgACTzcAAhOsmUh7hDyJcDuaHS8E',
               'CAACAgIAAxkBAAEJdo1klqx8h1L445FMWv9dVmgjDoY0jQAC4AADi_lSO_-_V_BtJoNuLwQ',
               'CAACAgIAAxkBAAEJdo9klqyftx3QpNX_dmp2hOQCJy7mKQAC6SoAAiQjEEgkU062E7Upky8E',
               'CAACAgIAAxkBAAEJdpFklqyxNcKHSIJqgDqOPDNF0JgeDAAC4CkAAkbO-UpSZSefYRBUDS8E']


@bot.message_handler(func=lambda message: message.text.lower() == "наверно")
def send_random_sticker(message):
    random_sticker_id = random.choice(sticker_ids)
    bot.send_sticker(message.chat.id, random_sticker_id)


@bot.message_handler(func=lambda message: message.text.lower() == "пон")
def handle_pon(message):
    bot.reply_to(message, "НИХУЯ НЕ ПОНЯТНО БЛЯЯЯЯЯЯТЬ 🤨🤨🤨🤨")


@bot.message_handler(func=lambda message: message.text.lower() == "понятно")
def handle_ponyatno(message):
    bot.reply_to(message, "НИХУЯ НЕ ПОНЯТНО БЛЯЯЯЯЯЯТЬ 🤨🤨🤨🤨")


@bot.message_handler(func=lambda message: message.text.lower() == "допустим")
def handle_dopustim(message):
    bot.reply_to(message, "это матвей придумал")


@bot.message_handler(func=lambda message: message.text.lower() == "ладно")
def handle_ladno(message):
    bot.send_message(message.chat.id, "ладно")


@bot.message_handler(func=lambda message: message.text.lower() == "бывает")
def handle_bivaet(message):
    bot.send_message(message.chat.id, "у тебя в жопе хуй бывает")


@bot.message_handler(func=lambda message: message.text.lower() == "гений")
def handle_geni(message):
    bot.send_message(message.chat.id, "да 😎😎😎")


@bot.message_handler(func=lambda message: message.text.lower() == "нахуя?")
def handle_naxuya(message):
    bot.send_message(message.chat.id, "чтобы жизнь мёдом не казалась")


@bot.message_handler(func=lambda message: message.text.lower() == "нахуя")
def handle_naxyya(message):
    bot.send_message(message.chat.id, "чтобы жизнь мёдом не казалась")


@bot.message_handler(func=lambda message: message.text.lower() == "пинг кеши")
def handle_keshaping(message):
    bot.send_message(message.chat.id, "какой бизнес открыл @aholaheew? Малый")


@bot.message_handler(func=lambda message: message.text.lower() == "полезно")
def handle_polezno(message):
    bot.reply_to(message, "нет нахуй не полезно")


@bot.message_handler(func=lambda message: message.text.lower() == "ladno")
def handle_ladnoenglish(message):
    bot.send_message(message.chat.id, "ladno")


@bot.message_handler(func=lambda message: message.text.lower() == "цитата")
def handle_citata(message):
    bot.reply_to(message, "безумна можна быть первым")


@bot.message_handler(func=lambda message: message.text.lower() == "жиза")
def handle_ziza_sogl(message):
    bot.reply_to(message, "согл")


@bot.message_handler(func=lambda message: message.text.lower() == "работаем?")
def handle_ziza(message):
    username = message.from_user.first_name
    if str(message.from_user.id) == target_ban_ignor:
        bot.send_message(message.chat.id, f"Да {username}")
    else:
        bot.send_message(message.chat.id, f"У вас нет прав на выполнение этой команды {username} лох.")


@bot.message_handler(func=lambda message: message.text.lower() == "спой песню")
def handle_nachasaxnolnol(message):
    bot.reply_to(message,
                 "Это будет наш с тобой секрет Ни скажу о чём молчим вдвоём Если ты грустишь то грустно мне Если я пою, то я влюблен Пролетают мимо облака Скоро ночь укроет с головой Ты меня простишь наверняка На часах ноль ноль Я старше на год и пришёл мой день Значит надо бы собрать друзей Меня сегодня ты не жди домой А на часах ноль ноль Я старше на год пришёл мой день Значит надо бы собрать друзей Меня сегодня ты не жди домой (о-о-ой) А на часах ноль ноль Даю пять минут на сборы Выходи я жду тебя внизу Ну хотя бы раз в год оставим всю суету Дальше от панельных домов И хоть я их так полюбил Снова катим и прямо за горизонт Одни Солнце слепит наши глаза Если вместе то до конца Я сжимаю крепко ладонь Знаешь твой я весь с головой Разговорами у костра Мы проводим алый закат Гоним дальше целой толпой На часах ноль ноль я старше на год и пришёл мой день значит надо бы собрать друзей меня сегодня ты не жди домой а на часах ноль ноль я старше на год пришёл мой день значит надо бы собрать друзей меня сегодня ты не жди домой (о-о-ой) а на часах ноль ноль мечтай, люби, ревнуй скучай, рискуй летай, но только просто будь собой на часах ноль ноль я старше на год и пришёл мой день значит надо бы собрать друзей меня сегодня ты не жди домой (о-о-ой) а на часах ноль ноль я старше на год пришёл мой день значит надо бы собрать друзей меня сегодня ты не жди домой а на часах ноль ноль я старше на год пришёл мой день значит надо бы собрать друзей меня сегодня ты не жди домой (о-о-ой) а на часах ноль ноль")


@bot.message_handler(func=lambda message: message.text.lower() == "ты гей")
def handle_gay(message):
    bot.reply_to(message, "Я не гей я просто люблю прыгать на тёплом мужском члене")


@bot.message_handler(func=lambda message: message.text.lower() == "гифка")
def send_random_gif(message):
    gif_links = [
        "https://media.tenor.com/JtpCjG8fbDMAAAAC/allahu-akbar-god-is-the-greatest.gif",
        "https://media.tenor.com/sFYrvr2tHogAAAAd/islam-allah.gif",
        "https://media.tenor.com/FIqbvKB2NsMAAAAd/alla-hu-akbar.gif",
        "https://media.tenor.com/zEJOfR_rovEAAAAd/oss117allah-akbar.gif",
        "https://media.tenor.com/LFEHVky8tx4AAAAd/islam-muslim.gif",
        "https://i.gifer.com/8gGB.gif",
        "https://i.gifer.com/8gGU.gif",
        "https://i.gifer.com/8gxN.gif",
        "https://i.gifer.com/18gY.gif",
        "https://i.gifer.com/8RFA.gif",
        "https://i.gifer.com/BEdz.gif",
        "https://i.gifer.com/8gGR.gif",
        "https://i.gifer.com/8gGT.gif",
        "https://i.gifer.com/77s.gif"

    ]

    random_gif = random.choice(gif_links)

    bot.send_document(message.chat.id, random_gif)


@bot.message_handler(func=lambda message: message.text.lower() == "гифка патрик бейтман")
def send_random_gif_patrick(message):
    gif_links_patrick = [
        "ttps://media.tenor.com/5lLcKZgmIhgAAAAM/american-psycho-patrick-bateman.gif",
        "https://i.gifer.com/1TZZ.gif",
        "https://i.gifer.com/30T1.gif",
        "https://i.gifer.com/2YD.gif",
        "https://i.gifer.com/2wQ5.gif",
        "https://i.gifer.com/1Yic.gif",
        "https://i.gifer.com/30Sw.gif",
        "https://i.gifer.com/B88.gif",
        "https://i.gifer.com/18Hu.gif",
        "https://i.gifer.com/5cD.gif",
        "https://i.gifer.com/2wPx.gif",
        "https://i.gifer.com/18Hx.gif"
    ]

    random_gif = random.choice(gif_links_patrick)

    bot.send_document(message.chat.id, random_gif)


@bot.message_handler(func=lambda message: message.text.lower() == "имба")
def send_random_gif_patrick_pivo(message):
    gif_links_pivo = [
        "https://i.gifer.com/XMam.gif",
        "https://i.gifer.com/3J2.gif",
        "https://i.gifer.com/w18.gif",
        "https://i.gifer.com/WC1s.gif",
        "https://i.gifer.com/CWvb.gif",
        "https://i.gifer.com/YYdT.gif",
        "https://i.gifer.com/VglB.gif",
        "https://i.gifer.com/3ZWI.gif"
    ]

    random_gif = random.choice(gif_links_pivo)

    bot.send_document(message.chat.id, random_gif)


@bot.message_handler(func=lambda message: message.text.lower() == "гифка мать ебал")
def send_random_gif_patrick_pivo(message):
    gif_links_pivo = [
        "https://i.gifer.com/IsYY.gif",
        "https://i.gifer.com/CS3O.gif",
        "https://i.gifer.com/6DXv.gif",
        "https://i.gifer.com/Mb88.gif",
        "https://i.gifer.com/9Rx0.gif",
        "https://i.gifer.com/4JG.gif",
        "https://i.gifer.com/IsYV.gif",
        "https://i.gifer.com/MCEC.gif"
    ]

    random_gif = random.choice(gif_links_pivo)

    bot.send_document(message.chat.id, random_gif)


@bot.message_handler(commands=['settime'])
def start(message):
    if str(message.from_user.id) == target_lox:
        global start_time
        time_str = message.text.split()[1]  # Получаем строку времени из команды /start

        try:
            hours, minutes, seconds = map(int, time_str.split(':'))
            start_time = time.time() - (hours * 3600 + minutes * 60 + seconds)
            bot.reply_to(message, 'Начальное время установлено.')
        except ValueError:
            bot.reply_to(message, 'Неверный нахуй. ты лох используй ЧЧ:ММ:СС.')
    else:
        bot.send_message(message.chat.id, "Молодой человек идите нахуй у вас нет прав!")


@bot.message_handler(commands=['time'])
def show_time(message):
    global start_time
    if start_time is not None:
        elapsed_time = time.time() - start_time
        hours = int(elapsed_time // 3600)
        minutes = int((elapsed_time % 3600) // 60)
        seconds = int(elapsed_time % 60)
        bot.reply_to(message, f'Время в новосибе? {hours}:{minutes} и {seconds} секунд.')
    else:
        bot.reply_to(message, 'Установлено нахуй')


@bot.message_handler(func=lambda message: message.text.lower() == "гифка джо джо")
def send_random_jojo(message):
    # Список ссылок на гифки
    gif_links_patrick = [
        "https://media.tenor.com/F2oy742HqqgAAAAC/josuke.gif",
        "https://media.tenor.com/XKCNoEfUT5AAAAAd/jjba-jojos-bizarre-adventure.gif",
        "https://media.tenor.com/7oeBtRPXymEAAAAC/jojo.gif",
        "https://media.tenor.com/C-S8dtjO6EcAAAAC/jojos-bizarre-adventures-jjba.gif",
        "https://media.tenor.com/XRGgi7Bh8ukAAAAC/jojo-jojos-bizarre-adventure.gif",
        "https://media.tenor.com/xZ5SDUwoDgYAAAAC/jojo-pose-jotaro.gif",
        "https://media.tenor.com/zGO_fCtMnbcAAAAC/jo-jo-jjba.gif"
    ]

    random_gif = random.choice(gif_links_patrick)

    bot.send_document(message.chat.id, random_gif)


photo_links_siski = [
    "https://chohanpohan.com/uploads/posts/2021-12/1640966054_1-chohanpohan-com-p-porno-golie-siski-i-zhivotiki-devushek-1.jpg",
    "https://fotosbor.com/files/2022/01/IMGJPEG16423045247VVgyF/1642304524bWqM3e.jpeg",
    "https://chohanpohan.com/uploads/posts/2022-02/1643972324_1-chohanpohan-com-p-porno-golaya-grud-1go-razmera-1.jpg",
    "https://erotic-home.com/uploads/posts/2019-04/1554070451_002.jpg",
    "https://www.yaeby.pro/contents/videos_screenshots/18000/18905/642x361/1.jpg",
    "https://ttelka.com/uploads/posts/2022-01/1641483472_2-ttelka-com-p-erotika-zhenskie-siski-doma-golie-2.jpg",
    "https://chohanpohan.com/uploads/posts/2021-12/1638770384_1-chohanpohan-com-p-porno-bolshie-golie-siski-1.jpg",
    "https://hot4all.ru/wp-content/uploads/2022/09/big-nipples-h4a-19-scaled.jpg",
    "https://pornodomka.com/contents/videos_screenshots/1000/1335/preview.jpg",
    "http://bufera.pro/wp-content/uploads/2021/05/images5526.jpg",
    "http://bufera.pro/wp-content/uploads/2021/05/images5528.jpg",
    "https://drochikula.com/uploads/posts/2022-12/1671139115_1-drochikula-com-p-porno-golie-siski-popki-doma-1.jpg",
    "https://golye-zhenshiny.info/wp-content/uploads/2020/08/golye-titki-siski-devushek-01.jpg",
    "https://www.pornozavod.cc/contents/videos_screenshots/7000/7328/468x282/1.jpg",
    "https://ttelka.com/uploads/posts/2022-01/1641483430_17-ttelka-com-p-erotika-zhenskie-siski-doma-golie-17.jpg",
    "https://photochki.pro/uploads/posts/2021-03/1615634476_37-p-golie-siski-bez-litsa-erotika-46.jpg",
    "https://goloe.me/uploads/posts/2022-01/1642543102_2-goloe-me-p-erotika-skin-svoi-golie-siski-3.jpg",
    "https://ttelka.com/uploads/posts/2022-01/1642771442_1-ttelka-com-p-erotika-golie-siski-dlya-feika-1.jpg",
    "https://topdevka.com/uploads/posts/2022-08/thumbs/1659504799_14-topdevka-com-p-erotika-golie-siski-dlya-feika-18.jpg",
    "https://siskins.club/uploads/posts/2021-12/thumbs/1639200222_38-siskins-club-p-golie-siski-v-plokhom-kachestve-erotika-41.jpg",
    "https://tinypic.host/images/2023/06/16/photo_1_2023-06-16_16-17-07.jpeg",
    "https://tinypic.host/images/2023/06/16/photo_2_2023-06-16_16-17-07.jpeg",
    "https://tinypic.host/images/2023/06/16/photo_3_2023-06-16_16-17-07.jpeg",
    "https://tinypic.host/images/2023/06/16/photo_4_2023-06-16_16-17-07.jpeg",
    "https://tinypic.host/images/2023/06/16/photo_5_2023-06-16_16-17-07.jpeg",
    "https://tinypic.host/images/2023/06/16/photo_6_2023-06-16_16-17-07.jpeg",
    "https://tinypic.host/images/2023/06/16/photo_7_2023-06-16_16-17-07.jpeg",
    "https://tinypic.host/images/2023/06/16/photo_8_2023-06-16_16-17-07.jpeg",
    "https://tinypic.host/images/2023/06/16/photo_9_2023-06-16_16-17-07.jpeg",
    "https://tinypic.host/images/2023/06/16/photo_10_2023-06-16_16-17-07.jpeg",
    "https://tinypic.host/images/2023/06/16/photo_11_2023-06-16_16-17-07.jpeg",
    "https://tinypic.host/images/2023/06/16/photo_12_2023-06-16_16-17-07.jpeg",
    "https://tinypic.host/images/2023/06/16/photo_14_2023-06-16_16-17-07.jpeg",
    "https://tinypic.host/images/2023/06/16/photo_15_2023-06-16_16-17-07.jpeg",
    "https://tinypic.host/images/2023/06/16/photo_16_2023-06-16_16-17-07.jpeg",
    "https://tinypic.host/images/2023/06/16/photo_17_2023-06-16_16-17-07.jpeg",
    "https://tinypic.host/images/2023/06/16/images-4.jpeg",
    "https://tinypic.host/images/2023/06/16/images-3.jpeg",
    "https://tinypic.host/images/2023/06/16/images-2.jpeg",
    "https://tinypic.host/images/2023/06/16/images-1.jpeg",
    "https://tinypic.host/images/2023/06/16/imageY.jpeg",
    "https://img.piski-siski.net/ph/img/11/115219261_th.jpg",
    "https://ero-top.info/uploads/posts/2021-01/1610702571_3.jpg",
    "https://goloe.me/uploads/posts/2022-01/1642543121_1-goloe-me-p-erotika-skin-svoi-golie-siski-2.jpg",
    "https://erowall.com/wallpapers/original/15753.jpg",
    "https://ttelka.com/uploads/posts/2022-02/1644273618_1-ttelka-com-p-erotika-klassnie-golie-siski-1.jpg",
    "https://boombo.biz/uploads/posts/2022-05/1652591182_1-boombo-biz-p-siski-devushki-bez-litsa-krasivaya-erotika-1.jpg",
    "https://photochki.pro/uploads/posts/2022-12/thumbs/1669844874_photochki-pro-p-sisi-bez-litsa-erotika-1.jpg",
    "https://photochki.pro/uploads/posts/2022-12/thumbs/1669844911_photochki-pro-p-sisi-bez-litsa-erotika-8.jpg",
    "https://photochki.pro/uploads/posts/2022-12/thumbs/1669844868_photochki-pro-p-sisi-bez-litsa-erotika-10.jpg",
    "https://photochki.pro/uploads/posts/2022-12/thumbs/1669844881_photochki-pro-p-sisi-bez-litsa-erotika-11.jpg",
    "https://photochki.pro/uploads/posts/2022-12/thumbs/1669844885_photochki-pro-p-sisi-bez-litsa-erotika-12.jpg",
    "https://photochki.pro/uploads/posts/2022-12/thumbs/1669844904_photochki-pro-p-sisi-bez-litsa-erotika-14.jpg",
    "https://photochki.pro/uploads/posts/2022-12/thumbs/1669844928_photochki-pro-p-sisi-bez-litsa-erotika-15.jpg",
    "https://photochki.pro/uploads/posts/2022-12/thumbs/1669844862_photochki-pro-p-sisi-bez-litsa-erotika-20.jpg",
    "https://boombo.biz/uploads/posts/2022-01/thumbs/1642254442_9-boombo-biz-p-golie-konusnie-siski-erotika-10.jpg",
    "https://ttelka.com/uploads/posts/2022-01/1642771416_2-ttelka-com-p-erotika-golie-siski-dlya-feika-2.jpg",
    "https://ttelka.com/uploads/posts/2022-01/thumbs/1642771474_8-ttelka-com-p-erotika-golie-siski-dlya-feika-8.jpg",
    "https://ttelka.com/uploads/posts/2022-01/thumbs/1642771474_10-ttelka-com-p-erotika-golie-siski-dlya-feika-10.jpg",
    "https://ttelka.com/uploads/posts/2022-01/thumbs/1642771467_16-ttelka-com-p-erotika-golie-siski-dlya-feika-16.jpg",
    "https://ttelka.com/uploads/posts/2022-01/1642771493_24-ttelka-com-p-erotika-golie-siski-dlya-feika-29.jpg",
    "https://ttelka.com/uploads/posts/2022-01/1642771509_27-ttelka-com-p-erotika-golie-siski-dlya-feika-32.jpg",
    "https://ttelka.com/uploads/posts/2022-01/thumbs/1642771508_30-ttelka-com-p-erotika-golie-siski-dlya-feika-36.jpg",
    "https://eropic.cc/uploads/posts/2022-09/thumbs/1664256534_4-eropic-cc-p-erotika-golikh-sisek-v-plokhom-kachestve-4.jpg",
    "https://devkis.club/uploads/posts/2019-09/1568531422_russkie-siski-erotika-38.jpg",
    "https://trahbabah.com/uploads/posts/2022-11/1669650393_1-trahbabah-com-p-porno-kospleishchitsi-s-golimi-siskami-1.jpg",
    "https://hot4all.ru/wp-content/uploads/2021/05/boobs-DD-64-854x1024.jpg",
    "https://chohanpohan.com/uploads/posts/2021-12/thumbs/1640647061_1-chohanpohan-com-p-porno-golie-siski-pyatogo-razmera-1.jpg",
    "https://trahbabah.com/uploads/posts/2022-12/1670016780_4-trahbabah-com-p-porno-pishnie-devushki-laskayut-svoi-prele-4.jpg",
    "https://i.etsystatic.com/37276884/r/il/dea317/4663888463/il_570xN.4663888463_eldf.jpg",
    "https://static-ca-cdn.eporner.com/gallery/nU/sl/IRjjq4nslnU/9159744-fe4nsjvxeaa7vld_880x660.jpg",
    "https://tinypic.host/images/2023/06/18/1449562182_ad6t6rd5hkq.jpeg",
    "https://tinypic.host/images/2023/06/18/1449562187_d_kietp9qfo.jpeg",
    "https://tinypic.host/images/2023/06/18/1460966513_phte9neszfq.jpeg",
    "https://tinypic.host/images/2023/06/18/1460966542_jqa7bkm62i0.jpeg",
    "https://tinypic.host/images/2023/06/18/1460966552_xg4ucyci7g0.jpeg",
    "https://tinypic.host/images/2023/06/18/1460966556_qaln5usovou.jpeg",
    "https://tinypic.host/images/2023/06/18/1460966560_uglksd1yfk8.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194773_20-chohanpohan-com-p-porno-selfi-siski-bez-litsa-20.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194777_21-chohanpohan-com-p-porno-selfi-siski-bez-litsa-21.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194785_49-chohanpohan-com-p-porno-selfi-siski-bez-litsa-53.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194791_64-chohanpohan-com-p-porno-selfi-siski-bez-litsa-70.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194804_16-chohanpohan-com-p-porno-selfi-siski-bez-litsa-16.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194807_59-chohanpohan-com-p-porno-selfi-siski-bez-litsa-63.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194808_17-chohanpohan-com-p-porno-selfi-siski-bez-litsa-17.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194810_13-chohanpohan-com-p-porno-selfi-siski-bez-litsa-13.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194815_51-chohanpohan-com-p-porno-selfi-siski-bez-litsa-55.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194816_36-chohanpohan-com-p-porno-selfi-siski-bez-litsa-39.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194818_68-chohanpohan-com-p-porno-selfi-siski-bez-litsa-75.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194819_39-chohanpohan-com-p-porno-selfi-siski-bez-litsa-42.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194825_65-chohanpohan-com-p-porno-selfi-siski-bez-litsa-71.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194828_8-chohanpohan-com-p-porno-selfi-siski-bez-litsa-8.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194829_67-chohanpohan-com-p-porno-selfi-siski-bez-litsa-74.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194838_1-chohanpohan-com-p-porno-selfi-siski-bez-litsa-1.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194839_6-chohanpohan-com-p-porno-selfi-siski-bez-litsa-6.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194840_43-chohanpohan-com-p-porno-selfi-siski-bez-litsa-46.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194845_10-chohanpohan-com-p-porno-selfi-siski-bez-litsa-10.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194845_53-chohanpohan-com-p-porno-selfi-siski-bez-litsa-57.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194851_3-chohanpohan-com-p-porno-selfi-siski-bez-litsa-3.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194851_5-chohanpohan-com-p-porno-selfi-siski-bez-litsa-5.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194851_37-chohanpohan-com-p-porno-selfi-siski-bez-litsa-40.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194851_62-chohanpohan-com-p-porno-selfi-siski-bez-litsa-67.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194861_55-chohanpohan-com-p-porno-selfi-siski-bez-litsa-59.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194863_40-chohanpohan-com-p-porno-selfi-siski-bez-litsa-43.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194865_18-chohanpohan-com-p-porno-selfi-siski-bez-litsa-18.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194875_34-chohanpohan-com-p-porno-selfi-siski-bez-litsa-37.jpeg",
    "https://tinypic.host/images/2023/06/18/1639194886_72-chohanpohan-com-p-porno-selfi-siski-bez-litsa-79.jpeg",
    "https://tinypic.host/images/2023/06/18/1663229914_3-xnxxphoto-org-p-porno-obichnie-golie-siski-3.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_1_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_2_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_3_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_4_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_5_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_6_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_7_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_8_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_9_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_10_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_11_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_12_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_13_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_14_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_15_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_16_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_17_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_18_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_19_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_20_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_21_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_22_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_23_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_24_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_25_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_26_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_27_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_28_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_29_2023-07-03_17-12-14.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_30_2023-07-03_17-12-14.jpeg"

]

previous_photo_siski = None


@bot.message_handler(func=lambda message: message.text.lower() == 'сиськи')
def send_random_photo(message):
    random_index = random.randint(0, len(photo_links_siski) - 1)
    random_photo = photo_links_siski[random_index]

    sent_message = bot.send_photo(message.chat.id, random_photo)

    time.sleep(10)

    bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)


photo_links_porno = [
    "https://stat.pornobolt.vip/kartinki-kategorij-pornobolt/incest.jpg",
    "https://st.gigporno.com/img/2022/0/20220895.jpg",
    "https://st.gigporno.com/img/2022/0/20220224.jpg",
    "https://img.empstatic.com/q80w233/category_avatars/anal-porn.jpg",
    "https://f0.xhdporno.me/images/34592/34592_screen.jpg",
    "https://photochki.pro/uploads/posts/2022-06/1655732490_1-photochki-pro-p-realnoe-domashnee-porno-porno-1.jpg",
    "https://eropic.cc/uploads/posts/2022-07/1658836276_1-eropic-cc-p-erotika-khudozhnitsa-s-negrom-porno-1.jpg",
    "https://imgporn.net/images/thmb/analnii-seks.jpg",
    "https://devahy.org/uploads/posts/2022-01/1642820419_1-devahy-org-p-porno-rakom-s-negrom-1.jpg",
    "https://chohanpohan.com/uploads/posts/2022-01/1642256963_1-chohanpohan-com-p-porno-negr-trakhaet-pered-muzhem-porno-1.jpg",
    "https://eropic.cc/uploads/posts/2022-07/1658836328_4-eropic-cc-p-erotika-khudozhnitsa-s-negrom-porno-4.jpg",
    "https://ttelka.com/uploads/posts/2022-01/1642546101_1-ttelka-com-p-porno-s-negrami-mzhm-teen-1.jpg",
    "https://www.yaeby.pro/contents/videos_screenshots/6000/6042/preview.mp4.jpg",
    "https://siski.name/uploads/posts/2023-01/1673661325_3-siski-name-p-erotika-khanna-khova-porno-3.jpg",
    "https://tukifporno.com/wp-content/uploads/2022/06/d181d0bcd0bed182d180d0b5d182d18c-d0bed0bdd0bbd0b0d0b9d0bd-d180d183d181d181d0bad0b8d0b5-xxx-porno.jpg",
    "https://st.bittictic.com/contents/videos_screenshots/166000/166731/720x406/1.jpg",
    "https://st.bittictic.com/contents/videos_screenshots/140000/140181/720x406/1.jpg",
    "https://m2.dozrel.com/contents/videos_screenshots/114000/114302/642x361/1.jpg",
    "https://st.daitictic.com/contents/videos_screenshots/4000/4099/preview.mp4.jpg",
    "https://st.ebtictic.com/contents/videos_screenshots/0/261/preview_720p.mp4.jpg",
    "https://st.ebtictic.com/contents/videos_screenshots/15000/15294/preview.mp4.jpg",
    "https://trahkino.me/contents/videos_screenshots/3000/3744/preview.mp4.jpg",
    "https://hamtictictic.com/contents/videos_screenshots/237000/237042/preview.jpg",
    "https://pornokiril.com/contents/videos_screenshots/1000/1800/preview.mp4.jpg",
    "https://peretrah.net/contents/videos_screenshots/1000/1903/320x180/1.jpg",
    "https://rusoska.com/contents/videos_screenshots/41000/41739/642x361/1.jpg",
    "https://www.yaeby.pro/contents/videos_screenshots/4000/4977/preview.mp4.jpg",
    "https://kinosalo.live/contents/videos_screenshots/0/360/preview.mp4.jpg",
    "https://st.bestictic.com/contents/videos_screenshots/86000/86891/previewmp4720_.mp4.jpg",
    "https://img.5porno.net/archive/70/6/69500/1-360x240.jpg",
    "https://m.checkporno.cc/contents/videos_screenshots/8000/8481/640x360/7.jpg",
    "https://porno-erotic.name/uploads/jpgperotic/jpgperotic456346567/456346567.jpg",
    "https://m.1top.mobi/uploads/posts/2023-03/dal-russkoy-sosedke-pomyt-sya-v-dushe-i-poluchil-v-znak.jpg",
    "https://imggen.eporner.com/6882133/1920/1080/15.jpg"
    "https://tinypic.host/images/2023/07/03/photo_1_2023-07-03_16-55-02.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_2_2023-07-03_16-55-02.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_4_2023-07-03_16-55-02.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_5_2023-07-03_16-55-02.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_6_2023-07-03_16-55-02.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_7_2023-07-03_16-55-02.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_8_2023-07-03_16-55-02.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_9_2023-07-03_16-55-02.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_10_2023-07-03_16-55-02.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_11_2023-07-03_16-55-02.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_12_2023-07-03_16-55-02.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_13_2023-07-03_16-55-02.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_14_2023-07-03_16-55-02.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_15_2023-07-03_16-55-02.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_16_2023-07-03_16-55-02.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_17_2023-07-03_16-55-02.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_18_2023-07-03_16-55-02.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_19_2023-07-03_16-55-02.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_20_2023-07-03_16-55-02.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_21_2023-07-03_16-55-02.jpeg",
    "https://tinypic.host/images/2023/07/03/photo_22_2023-07-03_16-55-02.jpeg"
]

previous_photo_porno = None


@bot.message_handler(func=lambda message: message.text.lower() == 'порно')
def send_random_photo_porno(message):
    global previous_photo_porno
    random_index = random.randint(0, len(photo_links_porno) - 1)
    random_photo = photo_links_porno[random_index]

    while random_photo == previous_photo_porno:
        random_index = random.randint(0, len(photo_links_porno) - 1)
        random_photo = photo_links_porno[random_index]

    previous_photo_porno = random_photo

    sent_message = bot.send_photo(message.chat.id, random_photo)

    time.sleep(10)

    bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)


photo_links_pisk = [
    "https://devkis.club/uploads/posts/2022-12/1671639694_2-devkis-club-p-erotika-samii-bolshoi-chlen-golii-2.jpg",
    "https://eropic.cc/uploads/posts/2022-05/1653207161_1-eropic-cc-p-erotika-bolshoi-chlen-doma-3.jpg",
    "https://boobliks.pro/uploads/posts/2022-08/thumbs/1661073783_1-boobliks-pro-p-bolshoi-chlen-s-lineikoi-chastnoe-porno-1.jpg",
    "https://chohanpohan.com/uploads/posts/2021-12/1638625551_1-chohanpohan-com-p-porno-bolshoi-chernii-khui-1.jpg",
    "https://ttelka.com/uploads/posts/2022-03/1648549473_1-ttelka-com-p-erotika-ogromnii-chernii-chlen-1.jpg",
    "https://chohanpohan.com/uploads/posts/2022-04/1651059675_1-chohanpohan-com-p-porno-bolshoi-chernii-chlen-1.jpg",
    "https://goloe.me/uploads/posts/2022-01/1642967433_6-goloe-me-p-erotika-samii-bolshoi-penis-negra-6.jpg",
    "https://photochki.pro/uploads/posts/2021-10/1634770201_61-photochki-pro-p-gigantskii-chernii-chlen-v-porno-porno-63.jpg"

]

previous_photo_penis = None


@bot.message_handler(func=lambda message: message.text.lower() == 'писька')
def send_randompiska_photo(message):
    global previous_photo_penis
    random_index = random.randint(0, len(photo_links_pisk) - 1)
    random_photo = photo_links_pisk[random_index]

    while random_photo == previous_photo_penis:
        random_index = random.randint(0, len(photo_links_pisk) - 1)
        random_photo = photo_links_pisk[random_index]

    previous_photo_penis = random_photo

    sent_message = bot.send_photo(message.chat.id, random_photo)

    time.sleep(10)

    bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)


photo_links_shopa = [
    "https://tinypic.host/images/2023/07/02/1643848753_24-ttelka-com-p-erotika-kak-viglyadit-golaya-zhopa-zhenshc-26.jpeg",
    "https://tinypic.host/images/2023/07/02/1643848778_23-ttelka-com-p-erotika-kak-viglyadit-golaya-zhopa-zhenshc-25.jpeg",
    "https://tinypic.host/images/2023/07/02/1643848715_20-ttelka-com-p-erotika-kak-viglyadit-golaya-zhopa-zhenshc-22.jpeg",
    "https://tinypic.host/images/2023/07/02/1643848777_19-ttelka-com-p-erotika-kak-viglyadit-golaya-zhopa-zhenshc-21.jpeg",
    "https://tinypic.host/images/2023/07/02/1643848735_15-ttelka-com-p-erotika-kak-viglyadit-golaya-zhopa-zhenshc-17.jpeg",
    "https://tinypic.host/images/2023/07/02/1643848720_13-ttelka-com-p-erotika-kak-viglyadit-golaya-zhopa-zhenshc-15.jpeg",
    "https://tinypic.host/images/2023/07/02/1643848723_12-ttelka-com-p-erotika-kak-viglyadit-golaya-zhopa-zhenshc-14.jpeg",
    "https://tinypic.host/images/2023/07/02/1643848711_11-ttelka-com-p-erotika-kak-viglyadit-golaya-zhopa-zhenshc-13.jpeg",
    "https://tinypic.host/images/2023/07/02/1643848758_6-ttelka-com-p-erotika-kak-viglyadit-golaya-zhopa-zhenshc-8.jpeg",
    "https://tinypic.host/images/2023/07/02/1643848683_3-ttelka-com-p-erotika-kak-viglyadit-golaya-zhopa-zhenshc-3.jpeg",
    "https://tinypic.host/images/2023/07/02/images-3.jpeg",
    "https://tinypic.host/images/2023/07/02/images-2.jpeg",
    "https://tinypic.host/images/2023/07/02/1641151730_1-boombo-biz-p-bolshie-golie-zhopi-rakam-erotika-1.jpeg",
    "https://tinypic.host/images/2023/07/02/1640365378_1-siski-name-p-porno-zhopa-samie-krasivie-golie-bez-trusi-1.jpeg",
    "https://tinypic.host/images/2023/07/02/blondinka-studentka-trahaetsya-v-uzkuyu-jopu-i-est-spermu.jpeg",
    "https://tinypic.host/images/2023/07/02/1608322667_5-p-samie-krasivie-golie-zhopi-porno-9.jpeg",
    "https://tinypic.host/images/2023/07/02/1668712581_1-devkis-club-p-erotika-golaya-bolshaya-babya-zhopa-2.jpeg",
    "https://tinypic.host/images/2023/07/02/1661038344_1-telochki-org-p-golaya-zhopa-tyanki-erotika-1.jpeg",
    "https://tinypic.host/images/2023/07/02/images-1.jpeg",
    "https://tinypic.host/images/2023/07/02/images.jpeg",
    "https://tinypic.host/images/2023/07/02/1664965321_1-eropic-cc-p-erotika-krutaya-golaya-zhopa-1.jpeg",
    "https://tinypic.host/images/2023/07/02/1669832350_photochki-pro-p-golaya-popa-bez-trusov-erotika-instagram-1.jpeg"
]

previous_photo_shopa = None


@bot.message_handler(func=lambda message: message.text.lower() == 'жопа')
def send_randompiska_photo(message):
    global previous_photo_shopa
    random_index = random.randint(0, len(photo_links_shopa) - 1)
    random_photo = photo_links_shopa[random_index]

    while random_photo == previous_photo_shopa:
        random_index = random.randint(0, len(photo_links_shopa) - 1)
        random_photo = photo_links_shopa[random_index]

    previous_photo_shopa = random_photo

    sent_message = bot.send_photo(message.chat.id, random_photo)

    time.sleep(10)

    bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)


@bot.message_handler(func=lambda message: message.text.lower() == 'скинь песню')
def send_audio(message):
    # Отправка аудио сообщения
    audio_path = 'Dabro - На часах ноль-ноль (премьера песни, 2021) (online-audio-converter.com).mp3'
    audio = open(audio_path, 'rb')
    bot.send_audio(message.chat.id, audio)


@bot.message_handler(func=lambda message: "отправь фото google" in message.text.lower())
def send_photo(message):
    search_query = message.text.lower().replace("отправь фото google", "").strip()

    base_url = "https://www.google.com/search?"
    params = {
        "q": search_query,
        "tbm": "isch"
    }

    url = base_url + urllib.parse.urlencode(params)

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    images = soup.find_all("img")

    for image in images:
        if image.has_attr("src") and "http" in image["src"]:
            photo_url = image["src"]
            break
    else:
        bot.send_message(message.chat.id, "По вашему запросу не найдено фотографий")
        return

    photo_response = requests.get(photo_url)

    bot.send_photo(message.chat.id, photo_response.content)


@bot.message_handler(func=lambda message: "отправь фото unsplash" in message.text.lower())
def send_photo_from_unsplash(message):
    search_query = message.text.lower().replace("отправь фото unsplash", "").strip()

    url = f"https://api.unsplash.com/photos/random?client_id={UNSPLASH_ACCESS_KEY}&query={search_query}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'urls' in data:
            photo_url = data['urls']['regular']
            photo_response = requests.get(photo_url)
            if photo_response.status_code == 200:
                with open("photo.jpg", "wb") as photo_file:
                    photo_file.write(photo_response.content)
                with open("photo.jpg", "rb") as photo_file:
                    bot.send_photo(message.chat.id, photo_file)
            else:
                bot.send_message(message.chat.id, "Не удалось загрузить фото")
        else:
            bot.send_message(message.chat.id, "Не удалось получить URL фотографии")
    else:
        bot.send_message(message.chat.id, "Произошла ошибка при выполнении запроса")


@bot.message_handler(func=lambda message: "отправь фото" in message.text.lower())
def send_photo(message):
    search_query = message.text.lower().replace("отправь фото", "").strip()

    base_url = "https://api.pexels.com/v1/search"
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    params = {
        "query": search_query,
        "per_page": 1
    }

    response = requests.get(base_url, headers=headers, params=params)

    data = response.json()

    if "photos" not in data or len(data["photos"]) == 0:
        bot.send_message(message.chat.id, "По вашему запросу не найдено фотографий")
        return

    first_photo = data["photos"][0]

    if "src" not in first_photo or "large" not in first_photo["src"]:
        bot.send_message(message.chat.id, "Не удалось получить фото")
        return

    photo_url = first_photo["src"]["large"]

    photo_response = requests.get(photo_url)

    # Отправляем фото пользователю
    bot.send_photo(message.chat.id, photo_response.content)


code_to_smile = {
    'Clear': 'Ясно \U00002600',
    'Clouds': 'Облачно \U00002601',
    'Rain': 'Дождь \U00002614',
    'Drizzle': 'Дождь \U00002614',
    'Thunderstorm': 'Гроза \U000026A1',
    'Snow': 'Снег \U0001F328',
    'Mist': 'Туман \U0001F32B',
}


def get_weather(city):
    try:
        r = requests.get(
            f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'
        )
        data = r.json()

        cur_weather = data['main']['temp']
        weather_description = data['weather'][0]['main']
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = 'Посмотри в окно, не пойму что там за погода!'

        humidity = data['main']['humidity']
        pressure = data['main']['pressure']
        wind = data['wind']['speed']
        sunrise_timestamp = datetime.datetime.fromtimestamp(data['sys']['sunrise'])
        sunset_timestamp = datetime.datetime.fromtimestamp(data['sys']['sunset'])
        length_of_the_day = sunset_timestamp - sunrise_timestamp

        weather_message = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}\n' \
                          f'Погода в городе: {city}\nТемпература: {cur_weather}C° {wd}\n' \
                          f'Влажность: {humidity}%\nДавление: {pressure} мм.рт.ст\nВетер: {wind}м/с\n' \
                          f'Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\n' \
                          f'Продолжительность дня: {length_of_the_day}\n' \
                          f'Хорошего дня!'

        return weather_message
    except:
        return '\U00002620 Проверьте название города \U00002620'


@bot.message_handler(commands=['weather'])
def handle_weather_command(message):
    command_args = message.text.split()[1:]
    if len(command_args) < 1:
        bot.reply_to(message, "Пожалуйста, укажите город после команды /weather.")
        return

    city = ' '.join(command_args)
    weather = get_weather(city)
    bot.reply_to(message, weather)


@bot.message_handler(commands=['id'])
def handle_id_command(message):
    command_parts = message.text.split()
    if len(command_parts) > 1:
        username = command_parts[1]
        user_id = message.from_user.id
        bot.reply_to(message, f"Ник: {username}\nID: {user_id}")
    else:
        bot.reply_to(message, "Еблан?")


@bot.message_handler(func=lambda message: message.text.lower().startswith('найти в википедии'))
def search_wikipedia(message):
    query = message.text[17:].strip()

    try:
        results = wikipedia.search(query)

        if results:
            page = wikipedia.page(results[0])

            article_title = page.title
            article_summary = page.summary

            bot.reply_to(message, f"Заголовок: {article_title}\n\n{article_summary}")
        else:
            bot.reply_to(message, "Статья не найдена в Википедии")
    except wikipedia.exceptions.WikipediaException:
        bot.reply_to(message, "Произошла ошибка при поиске в Википедии")


@bot.message_handler(func=lambda message: message.text.lower().startswith('напомни мне об'))
def set_reminder(message):
    reminder_text = message.text[15:].strip()
    sent_message = bot.send_message(message.chat.id, f'Напоминание установлено: {reminder_text}')

    time.sleep(10)

    bot.delete_message(chat_id=sent_message.chat.id, message_id=sent_message.message_id)

    reminder_time = 10

    if any(char.isdigit() for char in reminder_text):
        time_value = [int(char) for char in reminder_text.split() if char.isdigit()][0]

        if 'секунд' in reminder_text:
            reminder_time = time_value if time_value >= 10 else 10

        elif 'минут' in reminder_text:
            reminder_time = time_value * 60 if time_value >= 1 else 60

        elif 'час' in reminder_text:
            reminder_time = time_value * 3600 if time_value >= 1 else 3600

    time.sleep(reminder_time)

    bot.send_message(message.chat.id, f'Вы просили напомнить о: {reminder_text}')


current_news_index = 0
articles = []


def fetch_news():
    global current_news_index, articles

    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "apiKey": api_key,
        "country": "ru"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code == 200:
        articles = data["articles"]
        current_news_index = 0
    else:
        articles = []
        current_news_index = -1


def get_next_news():
    global current_news_index, articles

    if current_news_index < len(articles):
        article = articles[current_news_index]
        current_news_index += 1

        title = article["title"]
        description = article["description"]
        url = article["url"]

        return f"{title}\n\n{description}\n\n{url}"
    else:
        return "Нет доступных новостей."


@bot.message_handler(func=lambda message: message.text.lower().startswith('новости'))
def get_news(message):
    if len(articles) == 0:
        fetch_news()

    news = get_next_news()
    bot.reply_to(message, news)


photo_links_patrik = [
    "https://phonoteka.org/uploads/posts/2023-03/thumbs/1679949986_phonoteka-org-p-patrik-beitman-oboi-krasivo-3.jpg",
    "https://phonoteka.org/uploads/posts/2023-03/thumbs/1679949993_phonoteka-org-p-patrik-beitman-oboi-krasivo-4.jpg",
    "https://phonoteka.org/uploads/posts/2023-03/thumbs/1679949938_phonoteka-org-p-patrik-beitman-oboi-krasivo-6.jpg",
    "https://medialeaks.ru/wp-content/uploads/2021/02/fb-rita-9.jpg",
    "https://dic.academic.ru/pictures/wiki/files/80/Patrick_Bateman.jpg"
]


@bot.message_handler(func=lambda message: message.text.lower() == 'патрик бейтман')
def send_random_patrick(message):
    random_index = random.randint(0, len(photo_links_patrik) - 1)
    random_photo = photo_links_patrik[random_index]
    bot.send_photo(message.chat.id, random_photo)


@bot.message_handler(func=lambda message: message.text.lower().startswith('предскажи'))
def handle_prediction(message):
    command, query = message.text.lower().split(' ', 1)

    random_index = random.randint(0, 3)

    responses = ["Да", "Нет"]

    bot.send_message(message.chat.id, responses[random_index])


def send_error_message(exception):
    error_message = f'Произошла какая то хуйня:\n\n{exception}\n\n{traceback.format_exc()}'
    bot.send_message(CHAT_ID, error_message)


@bot.message_handler(func=lambda message: message.text.lower().startswith('орёл или решка'))
def handle_play(message):
    response = bot.send_message(message.chat.id, "Подбрасываю...")

    time.sleep(2)

    bot.delete_message(message.chat.id, response.message_id)

    random_number = random.randint(0, 1)

    if random_number == 0:
        result = "Орёл"
    else:
        result = "Решка"

    bot.send_message(message.chat.id, f"Выпало: {result}!")


@bot.message_handler(func=lambda message: message.text.lower().startswith('орёл или мать ебал'))
def handle_matebal_x2(message):
    response = bot.send_message(message.chat.id, "Подбрасываю...")

    time.sleep(2)

    bot.delete_message(message.chat.id, response.message_id)

    random_number = random.randint(0, 1)

    if random_number == 0:
        result = "Орёл"
    else:
        result = "мать ебал"

    bot.send_message(message.chat.id, f"Выпало: {result}!")


@bot.message_handler(commands=['play'])
def play(message):
    target_number = random.randint(1, 10)
    text = f"Это колесо пизды! Твоя задача - выебать число {target_number}.\n" \
           f"Нажми на кнопку 'Выебать колесо', чтобы начать!"
    markup = telebot.types.InlineKeyboardMarkup()
    spin_button = telebot.types.InlineKeyboardButton(text='Выебать колесо', callback_data=str(target_number))
    markup.add(spin_button)
    bot.send_message(message.chat.id, text, reply_markup=markup)


def send_result_message(chat_id, user_number, target_number):
    if user_number == target_number:
        message = "Поздравляю, ты выиграл но пошёл нахуй"
    else:
        message = f"Лох тебе выпало {user_number}. Ещё раз попробуй лошара ебанный"

    markup = telebot.types.InlineKeyboardMarkup()
    spin_button = telebot.types.InlineKeyboardButton(text='Выебать колесо', callback_data=str(target_number))
    markup.add(spin_button)
    bot.send_message(chat_id, message, reply_markup=markup)


@bot.message_handler(commands=['add_answer'])
def add_rule_1(message):
    global rules
    chat_id = message.chat.id

    if len(message.text.split()) > 1:
        values = message.text.split()[1:]
        try:
            count = int(values[0])
            message_response = " ".join(values[1:]).split(",")

            if len(message_response) == 2:
                word, response = [part.strip() for part in message_response]
                question = None
            elif len(message_response) == 3:
                word = message_response[0].strip()
                question = message_response[1].strip()
                response = message_response[2].strip()
            else:
                bot.reply_to(message, 'Ошибка: неверный формат входных данных.')
                return

            if chat_id not in rules:
                rules[chat_id] = []

            rules[chat_id].append({'count': count, 'word': word, 'question': question, 'response': response})

            bot.reply_to(message, 'Правило успешно добавлено.')
        except ValueError:
            bot.reply_to(message, 'Ошибка: неверный формат входных данных.')
    else:
        bot.reply_to(message, 'Ошибка: необходимо указать значения после команды.')


@bot.message_handler(commands=['add_answer'])
def add_rule_1(message):
    global rules
    chat_id = message.chat.id

    if len(message.text.split()) > 1:
        values = message.text.split()[1:]
        try:
            count = int(values[0])
            message_response = " ".join(values[1:]).split(",")

            if len(message_response) == 2:
                word, response = [part.strip() for part in message_response]
                question = None
            elif len(message_response) == 3:
                word = message_response[0].strip()
                question = message_response[1].strip()
                response = message_response[2].strip()
            else:
                bot.reply_to(message, 'Ошибка: неверный формат входных данных.')
                return

            if chat_id not in rules:
                rules[chat_id] = []

            rules[chat_id].append({'count': count, 'word': word, 'question': question, 'response': response})

            bot.reply_to(message, 'Правило успешно добавлено.')
        except ValueError:
            bot.reply_to(message, 'Ошибка: неверный формат входных данных.')
    else:
        bot.reply_to(message, 'Ошибка: необходимо указать значения после команды.')


target_clear_answers = "1130692453"


@bot.message_handler(commands=['clear_answers'])
def clear_rules(message):
    if str(message.from_user.id) == target_clear_answers:
        global rules
        chat_id = message.chat.id

        if chat_id in rules:
            rules[chat_id] = []
            bot.reply_to(message, 'Все ответы успешно удалены.')
        else:
            bot.reply_to(message, 'Нет сохраненных ответов.')
    else:
        bot.send_message(message.chat.id, "Молодой человек идите нахуй у вас нет прав!")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id

    if chat_id in rules:
        for rule in rules[chat_id]:
            if rule['word'] in message.text.lower() and message.text.lower().count(rule['word']) == 1:
                for _ in range(rule['count']):
                    bot.reply_to(message, rule['response'])
                break


@bot.message_handler(func=lambda message: True)
def send_current_time(message):
    if message.text.lower().startswith('время'):
        city = message.text.lower().replace('время', '').strip()
        current_time = get_current_time(city)
        if current_time:
            bot.reply_to(message, f'время в {city.title()}: {current_time}')
        else:
            bot.reply_to(message, f'Не удалось получить текущее время для {city.title()}')


def get_current_time(city):
    return datetime.datetime.now().strftime('%H:%M:%S')


try:
    bot.remove_webhook()
    bot.set_webhook(url='YOUR_WEBHOOK_URL/your-webhook-endpoint')
    app.run(host='0.0.0.0', port=8443, ssl_context=('CERT.pem', 'KEY.pem'))
except Exception as e:
    print(f"Error in the webhook setup: {e}")

try:
    bot.infinity_polling()
except Exception as e:
    print(f"Ошибка в процессе бесконечного опроса: {e}")
