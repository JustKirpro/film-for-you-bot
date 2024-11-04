import json


def get_genres_keyboard():
    return json.dumps(
        {
            "inline_keyboard": [
                [
                    {"text": "Драма", "callback_data": "genre_1"},
                    {"text": "Комедия", "callback_data": "genre_2"}
                ],
                [
                    {"text": "Ужасы", "callback_data": "genre_3"},
                    {"text": "Триллер", "callback_data": "genre_4"}
                ],
                [
                    {"text": "Фантастика", "callback_data": "genre_5"},
                    {"text": "Фэнтези", "callback_data": "genre_6"}
                ],
                [
                    {"text": "Удалить", "callback_data": "genre_0"},
                    {"text": "Отмена", "callback_data": "genre_-1"}
                ]
            ]
        }
    )


def get_countries_keyboard():
    return json.dumps(
        {
            "inline_keyboard": [
                [
                    {"text": "США", "callback_data": "country_1"},
                    {"text": "Франция", "callback_data": "country_2"}
                ],
                [
                    {"text": "Великобритания", "callback_data": "country_3"},
                    {"text": "Япония", "callback_data": "country_4"}
                ],
                [
                    {"text": "Южная Корея", "callback_data": "country_5"},
                    {"text": "Россия", "callback_data": "country_6"}
                ],
                [
                    {"text": "Удалить", "callback_data": "country_0"},
                    {"text": "Отмена", "callback_data": "country_-1"}
                ]
            ]
        }
    )


def get_periods_keyboard():
    return json.dumps(
        {
            "inline_keyboard": [
                [
                    {"text": "До 1980", "callback_data": "period_1"},
                    {"text": "1980-1990", "callback_data": "period_2"}
                ],
                [
                    {"text": "1990-2000", "callback_data": "period_3"},
                    {"text": "2000-2010", "callback_data": "period_4"}
                ],
                [
                    {"text": "2010-2020", "callback_data": "period_5"},
                    {"text": "После 2020", "callback_data": "period_6"}
                ],
                [
                    {"text": "Удалить", "callback_data": "period_0"},
                    {"text": "Отмена", "callback_data": "period_-1"}
                ]
            ]
        }
    )


def get_durations_keyboard():
    return json.dumps(
        {
            "inline_keyboard": [
                [
                    {"text": "Короткие (до 1:30)", "callback_data": "duration_1"}
                ],
                [
                    {"text": "Средние (от 1:30 до 2:30)", "callback_data": "duration_2"}
                ],
                [
                    {"text": "Длинные (от 2:30)", "callback_data": "duration_3"}
                ],
                [
                    {"text": "Удалить", "callback_data": "duration_0"},
                    {"text": "Отмена", "callback_data": "duration_-1"}
                ]
            ]
        }
    )


def get_film_actions_keyboard(film_kp_id):
    return json.dumps(
        {
            "inline_keyboard": [
                [
                    {"text": "Топ ⭐", "callback_data": f"rate_{film_kp_id}_4"},
                    {"text": "Хорошо 👍", "callback_data": f"rate_{film_kp_id}_3"}
                ],
                [
                    {"text": "Пойдёт 🤷", "callback_data": f"rate_{film_kp_id}_2"},
                    {"text": "Плохо 👎", "callback_data": f"rate_{film_kp_id}_1"}
                ],
                [
                    {"text": "Пропустить", "callback_data": "skip"},
                ],
                [
                    {"text": "Больше не показывать", "callback_data": f"hide_{film_kp_id}"}
                ]
            ]
        }
    )


def get_quotes_subscription_actions_keyboard():
    return json.dumps(
        {
            "inline_keyboard": [
                [
                    {"text": "Да", "callback_data": "subscription_yes"},
                    {"text": "Нет", "callback_data": "subscription_no"}
                ]
            ]
        }
    )
