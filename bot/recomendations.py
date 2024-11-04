import os
import random
import requests
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from database import get_random_suitable_film_if_possible, get_user_ratings, get_all_films, get_kp_id_by_film_id

KP_API_KEY = os.getenv('KP_API_KEY')
KP_URL = 'https://www.kinopoisk.ru/film/'


def get_film_recommendation(chat_id):
    suitable_film_kp_id = get_random_suitable_film_if_possible(chat_id)

    if suitable_film_kp_id is None:
        suitable_film_kp_id = predict_film_to_recommend(chat_id)

    print(f'Recommended film kp id: {suitable_film_kp_id}')

    return get_film_details(suitable_film_kp_id)


def predict_film_to_recommend(chat_id):
    ratings_data = get_user_ratings()
    all_films = get_all_films()

    if ratings_data.empty or all_films.empty:
        print("No data for prediction")
        return None

    user_item_matrix = ratings_data.pivot_table(index='chat_id', columns='film_id', values='rating').fillna(0)

    user_similarity = cosine_similarity(user_item_matrix)
    user_similarity_df = pd.DataFrame(user_similarity, index=user_item_matrix.index, columns=user_item_matrix.index)

    user_ratings = user_item_matrix.loc[chat_id]

    predicted_ratings = user_similarity_df.loc[chat_id].dot(user_item_matrix) / user_similarity_df.loc[chat_id].sum()

    unseen_films = user_ratings[user_ratings == 0].index
    recommendations = predicted_ratings[unseen_films]

    recommendations = recommendations.sort_values(ascending=False)
    best_film_id = recommendations.index[0] if not recommendations.empty else None

    if not best_film_id:
        best_film_id = random.choice(all_films['id'].tolist())

    return get_kp_id_by_film_id(best_film_id)


def get_film_details(kp_id):
    response = requests.get(
        f'https://api.kinopoisk.dev/v1.4/movie/{kp_id}',
        headers={'X-API-KEY': KP_API_KEY})

    data = response.json()

    return {
        'kp_id': kp_id,
        'name': data.get('name'),
        'description': data.get('description'),
        'rating_kp': data.get('rating', {}).get('kp'),
        'rating_imdb': data.get('rating', {}).get('imdb'),
        'kp_url': KP_URL + str(kp_id),
        'trailer_url': data.get('videos', {}).get('trailers', [{}])[0].get('url')
    }
