import os
import pandas as pd
import ydb

driver_config = ydb.DriverConfig(
    endpoint=os.getenv('YDB_ENDPOINT'),
    database=os.getenv('YDB_DATABASE'),
    credentials=ydb.iam.MetadataUrlCredentials(),
)

driver = ydb.Driver(driver_config)
driver.wait(fail_fast=True, timeout=5)
pool = ydb.SessionPool(driver)


def add_user_if_needed(chat_id):
    select_query = f"""
    SELECT *
      FROM users
     WHERE chat_id = {chat_id}; 
    """

    result = pool.retry_operation_sync(lambda s: s.transaction().execute(
        select_query,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))

    if len(result[0].rows) == 1:
        return

    insert_query = f"""
    INSERT INTO users (chat_id, favorite_country_id, favorite_genre_id, favorite_duration_id, favorite_period_id, quotes_subscription)
    VALUES ({chat_id}, NULL, NULL, NULL, NULL, false);
    """

    return pool.retry_operation_sync(lambda s: s.transaction().execute(
        insert_query,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))


def get_user_preferences(chat_id):
    query = f""" 
    SELECT g.name AS genre_name
         , c.name AS country_name
         , p.name AS period_name
         , d.name AS duration_name
      FROM users u
      LEFT JOIN genres g ON u.favorite_genre_id = g.id
      LEFT JOIN countries c ON u.favorite_country_id = c.id
      LEFT JOIN durations d ON u.favorite_duration_id = d.id
      LEFT JOIN periods p ON u.favorite_period_id = p.id
     WHERE u.chat_id = {chat_id};
    """

    result = pool.retry_operation_sync(lambda s: s.transaction().execute(
        query,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))

    row = result[0].rows[0]

    return {
        'genre_name': row['genre_name'],
        'country_name': row['country_name'],
        'period_name': row['period_name'],
        'duration_name': row['duration_name']
    }


def set_favorite_genre(chat_id, genre_id):
    query = f""" 
    UPDATE users
       SET favorite_genre_id = {genre_id if genre_id > 0 else 'NULL'}
     WHERE chat_id = {chat_id};
    """

    pool.retry_operation_sync(lambda s: s.transaction().execute(
        query,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))


def set_favorite_country(chat_id, country_id):
    query = f""" 
    UPDATE users
       SET favorite_country_id = {country_id if country_id > 0 else 'NULL'}
     WHERE chat_id = {chat_id};
    """

    pool.retry_operation_sync(lambda s: s.transaction().execute(
        query,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))


def set_favorite_period(chat_id, period_id):
    query = f""" 
    UPDATE users
       SET favorite_period_id = {period_id if period_id > 0 else 'NULL'}
     WHERE chat_id = {chat_id};
    """

    pool.retry_operation_sync(lambda s: s.transaction().execute(
        query,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))


def set_favorite_duration(chat_id, duration_id):
    query = f""" 
    UPDATE users
       SET favorite_duration_id = {duration_id if duration_id > 0 else 'NULL'}
     WHERE chat_id = {chat_id};
    """

    pool.retry_operation_sync(lambda s: s.transaction().execute(
        query,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))


def get_random_suitable_film_if_possible(chat_id):
    select_user_query = f""" 
     SELECT favorite_country_id
          , favorite_genre_id
          , favorite_period_id
          , favorite_duration_id
       FROM users
      WHERE chat_id = {chat_id};
    """

    user_result = pool.retry_operation_sync(lambda s: s.transaction().execute(
        select_user_query,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))

    user = user_result[0].rows[0]
    genre_id = user['favorite_genre_id']
    country_id = user['favorite_country_id']
    period_id = user['favorite_period_id']
    duration_id = user['favorite_duration_id']

    select_film_query = f""" 
    SELECT *
     FROM films f
     WHERE id NOT IN (
        SELECT film_id AS id 
          FROM ratings
         WHERE show_again = false
           AND chat_id = 1047103216)
    """

    if genre_id is not None:
        select_film_query += f' AND f.genre_id = {genre_id}'

    if country_id is not None:
        select_film_query += f' AND f.country_id = {country_id}'

    if period_id is not None:
        select_film_query += f' AND f.period_id = {period_id}'

    if duration_id is not None:
        select_film_query += f' AND f.duration_id = {duration_id}'

    select_film_query += ' LIMIT 1;'

    result = pool.retry_operation_sync(lambda s: s.transaction().execute(
        select_film_query,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))

    return result[0].rows[0]['kp_id'] if result and result[0].rows else None


def rate_film(chat_id, film_kp_id, rating):
    film_id = get_film_id_by_kp_id(film_kp_id)

    insert_query = f""" 
    INSERT INTO ratings (chat_id, film_id, rating, show_again)
    VALUES ({chat_id}, {film_id}, {rating}, false);
    """

    pool.retry_operation_sync(lambda s: s.transaction().execute(
        insert_query,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))


def hide_film(chat_id, film_kp_id):
    film_id = get_film_id_by_kp_id(film_kp_id)

    insert_query = f""" 
        INSERT INTO ratings (chat_id, film_id, rating, show_again)
        VALUES ({chat_id}, {film_id}, NULL, false);
        """

    pool.retry_operation_sync(lambda s: s.transaction().execute(
        insert_query,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))


def get_film_id_by_kp_id(film_kp_id):
    select_query = f"""
    SELECT id
      FROM films
     WHERE kp_id = {film_kp_id}
    """

    result = pool.retry_operation_sync(lambda s: s.transaction().execute(
        select_query,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))

    return result[0].rows[0]['id']


def get_kp_id_by_film_id(film_id):
    select_query = f"""
    SELECT kp_id
      FROM films
     WHERE id = {film_id}
    """

    result = pool.retry_operation_sync(lambda s: s.transaction().execute(
        select_query,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))

    return result[0].rows[0]['kp_id']


def get_user_ratings():
    query = f"""
    SELECT chat_id, film_id, rating
      FROM ratings
    """

    result = pool.retry_operation_sync(lambda s: s.transaction().execute(
        query,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))

    data = [{"chat_id": row['chat_id'], "film_id": row['film_id'], "rating": row['rating']} for row in result[0].rows]
    return pd.DataFrame(data)


def get_all_films():
    query = f"""
    SELECT id, name, genre_id, country_id
    FROM films
    """

    result = pool.retry_operation_sync(lambda s: s.transaction().execute(
        query,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))

    data = [{"id": row['id'], "name": row['name'], "genre_id": row['genre_id'], "country_id": row['country_id']} for row in result[0].rows]
    return pd.DataFrame(data)


def get_quote_subscription_status(chat_id):
    query = f"""
    SELECT quotes_subscription
     FROM users
    WHERE chat_id = {chat_id}
    """

    result = pool.retry_operation_sync(lambda s: s.transaction().execute(
        query,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))

    return result[0].rows[0]['quotes_subscription']


def set_quote_subscription_status(chat_id, status):
    query = f"""
    UPDATE users
       SET quotes_subscription = {status}
     WHERE chat_id = {chat_id}
    """

    return pool.retry_operation_sync(lambda s: s.transaction().execute(
        query,
        commit_tx=True,
        settings=ydb.BaseRequestSettings().with_timeout(3).with_operation_timeout(2)
    ))
