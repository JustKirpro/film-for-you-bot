from database import *
from keyboards import *
from recomendations import *

TG_TOKEN = os.getenv('TG_TOKEN')
URL = f'https://api.telegram.org/bot{TG_TOKEN}/'


def handler(event, context):
    message = json.loads(event['body'])
    print(message)

    if is_callback_query(message):
        handle_callback_query(message)
    elif is_text_message(message):
        handle_text_message(message)
    else:
        handle_invalid_message(message)

    return {
        'statusCode': 200
    }


def is_callback_query(message):
    return 'callback_query' in message.keys()


def handle_callback_query(message):
    chat_id = message['callback_query']['message']['chat']['id']
    parts = message['callback_query']['data'].split('_')
    action = parts[0]

    if is_preference_action(action):
        handle_preference_action(chat_id, action, parts)
    elif is_rate_action(action):
        handle_rate_action(chat_id, action, parts)
    elif is_subscription_message(action):
        handle_subscription_message(chat_id, parts)
    else:
        send_text_message('Ошибка: неизвестное действие', chat_id)


def is_preference_action(action):
    return action == 'genre' or action == 'country' or action == 'period' or action == 'duration'


def handle_preference_action(chat_id, action, parts):
    chosen_id = parts[1]

    if chosen_id == '-1':
        send_text_message('Ты отменил выбор', chat_id)
        return

    if action == 'genre':
        set_favorite_genre(chat_id, int(chosen_id))
        send_text_message('Я запомнил твой выбор жанра', chat_id)
    elif action == 'country':
        set_favorite_country(chat_id, int(chosen_id))
        send_text_message('Я запомнил твой выбор страны', chat_id)
    elif action == 'period':
        set_favorite_period(chat_id, int(chosen_id))
        send_text_message('Я запомнил твой выбор временного периода', chat_id)
    elif action == 'duration':
        set_favorite_duration(chat_id, int(chosen_id))
        send_text_message('Я запомнил твой выбор длительности фильма', chat_id)
    else:
        send_text_message('Ошибка: неизвестное действие', chat_id)


def is_rate_action(action):
    return action == 'rate' or action == 'skip' or action == 'hide'


def handle_rate_action(chat_id, action, parts):
    if action == 'skip':
        send_text_message('Ты решил пропустить этот фильм', chat_id)

    film_kp_id = int(parts[1])

    if action == 'hide':
        hide_film(chat_id, film_kp_id)
        send_text_message('Больше не буду показывать тебе этот фильм', chat_id)
    elif action == 'rate':
        rating = int(parts[2])
        rate_film(chat_id, film_kp_id, rating)
        send_text_message('Я запомнил твою оценку, постараюсь использовать её для улучшения своих рекомендаций', chat_id)
    else:
        send_text_message('Ошибка: неизвестное действие', chat_id)


def is_subscription_message(action):
    return action == 'subscription'


def handle_subscription_message(chat_id, parts):
    answer = parts[1]

    if answer == 'no':
        send_text_message('Ок, ничего не делаю', chat_id)
        return

    current_status = get_quote_subscription_status(chat_id)
    status_to_set = True if current_status is False else True

    set_quote_subscription_status(chat_id, status_to_set)

    send_text_message('Готово', chat_id)


def is_text_message(message):
    return 'message' in message and 'text' in message['message']


def handle_text_message(message):
    chat_id = message['message']['chat']['id']
    text = message['message']['text']

    add_user_if_needed(chat_id)

    if text == '/start':
        handle_start_command(chat_id)
    elif text == '/preferences':
        handle_preferences_command(chat_id)
    elif text == '/favorite_genre':
        handle_favorite_genre_command(chat_id)
    elif text == '/favorite_country':
        handle_favorite_country_command(chat_id)
    elif text == '/favorite_duration':
        handle_favorite_duration_command(chat_id)
    elif text == '/favorite_period':
        handle_favorite_period_command(chat_id)
    elif text == '/film_recommendation':
        handle_film_recommendation_command(chat_id)
    elif text == '/quote_subscription':
        handle_quote_subscription_command(chat_id)
    else:
        send_text_message('Ошибка: неподдерживаемая команда\nВведи /start для ознакомления с моими возможностями', chat_id)


def handle_start_command(chat_id):
    text = ('Привет!\n'
            'Я "Film For You" бот и вот что я умею:\n'
            '/preferences - посмотреть свои предпочтения в фильмах\n'
            '/favorite_genre - выбрать любимый жанр\n'
            '/favorite_country - выбрать любимую страну производства\n'
            '/favorite_period - выбрать любимый временной период\n'
            '/favorite_duration - выбрать любимую длительность фильма\n'
            '/film_recommendation - получить рекомендацию фильма\n'
            '/quote_subscription - подписаться на получение цитат из фильмов каждый день\n\n'
            'Советую первым делом настроить свои предпочтения для получения персонализированных рекомендаций')

    send_text_message(text, chat_id)


def handle_preferences_command(chat_id):
    preferences = get_user_preferences(chat_id)
    genre = preferences['genre_name']
    country = preferences['country_name']
    period = preferences['period_name']
    duration = preferences['duration_name']

    text = ('Твои предпочтения:\n'
            f'Любимый жанр: {genre.decode("utf-8") if genre is not None else "не выбран"}\n'
            f'Любимая страна производства: {country.decode("utf-8") if country is not None else "не выбрана"}\n'
            f'Любимый временной период: {period.decode("utf-8") if period is not None else "не выбран"}\n'
            f'Любимая длительность фильма: {duration.decode("utf-8") if duration is not None else "не выбрана"}\n')

    send_text_message(text, chat_id)


def handle_favorite_genre_command(chat_id):
    url = URL + 'sendMessage'

    requests.post(url, data={
        'text': 'Выбери любимый жанр:',
        'chat_id': chat_id,
        'parse_mode': 'Markdown',
        'reply_markup': get_genres_keyboard()
    })


def handle_favorite_country_command(chat_id):
    url = URL + 'sendMessage'

    requests.post(url, data={
        'text': 'Выбери любимую страну производства:',
        'chat_id': chat_id,
        'parse_mode': 'Markdown',
        'reply_markup': get_countries_keyboard()
    })


def handle_favorite_period_command(chat_id):
    url = URL + 'sendMessage'

    requests.post(url, data={
        'text': 'Выбери любимый временной период:',
        'chat_id': chat_id,
        'parse_mode': 'Markdown',
        'reply_markup': get_periods_keyboard()
    })


def handle_favorite_duration_command(chat_id):
    url = URL + 'sendMessage'

    requests.post(url, data={
        'text': 'Выбери любимую длительность фильма:',
        'chat_id': chat_id,
        'parse_mode': 'Markdown',
        'reply_markup': get_durations_keyboard()
    })


def handle_film_recommendation_command(chat_id):
    try:
        film_details = get_film_recommendation(chat_id)

        print(f'Film details: {film_details}')

        if not film_details:
            raise ValueError("No film details found")

        name = escape_markdown(film_details.get('name', 'название отсутствует'))
        description = escape_markdown(film_details.get('description', 'описание отсутствует'))
        rating_kp = escape_markdown(str(film_details.get('rating_kp', 'нет данных')))
        rating_imdb = escape_markdown(str(film_details.get('rating_imdb', 'нет данных')))
        kp_url = escape_markdown(film_details.get('kp_url', 'URL отсутствует'))
        trailer_url = escape_markdown(film_details.get('trailer_url', 'трейлер отсутствует'))

        text = (f'Я подобрал для тебя фильм: {name}\n'
                f'Вот его описание: {description}\n'
                f'Рейтинг на КП: {rating_kp}, рейтинг на IMDb: {rating_imdb}\n'
                f'Ссылка на фильм на КП: {kp_url}\n'
                f'Ссылка на трейлер: {trailer_url}')

    except Exception as e:
        print(f"Film recommendation error: {e}")
        send_text_message('Ошибка: не смог подобрать фильм для тебя 😞', chat_id)
        return

    url = URL + 'sendMessage'

    response = requests.post(url, data={
        'text': text,
        'chat_id': chat_id,
        'parse_mode': 'MarkdownV2',
        'reply_markup': get_film_actions_keyboard(film_details.get('kp_id'))
    })

    if response.status_code != 200:
        print(f"Error sending message: {response.status_code}, {response.text}")


def escape_markdown(text):
    return (text.replace('_', '\\_').replace('*', '\\*').replace('[', '\\[').replace(']', '\\]')
                .replace('(', '\\(').replace(')', '\\)').replace('~', '\\~').replace('`', '\\`')
                .replace('>', '\\>').replace('#', '\\#').replace('+', '\\+').replace('-', '\\-')
                .replace('=', '\\=').replace('|', '\\|').replace('{', '\\{').replace('}', '\\}')
                .replace('.', '\\.').replace('!', '\\!'))


def handle_quote_subscription_command(chat_id):
    url = URL + 'sendMessage'

    current_status = get_quote_subscription_status(chat_id)
    text = 'Ты уже подписан на рассылку, отписаться?' if current_status is True else 'Ты ещё не подписан, подписаться?'

    requests.post(url, data={
        'text': text,
        'chat_id': chat_id,
        'parse_mode': 'Markdown',
        'reply_markup': get_quotes_subscription_actions_keyboard()
    })


def handle_invalid_message(message):
    chat_id = message['message']['chat']['id']
    send_text_message('Ошибка: я умею работать только с текстовыми сообщениями и нажатыми кнопками', chat_id)


def send_text_message(text, chat_id):
    url = URL + f'sendMessage?text={text}&chat_id={chat_id}'

    requests.post(url)
