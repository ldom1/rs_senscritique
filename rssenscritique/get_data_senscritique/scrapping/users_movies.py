from tqdm import tqdm
import logging
import os
import pandas as pd

from rssenscritique.config.global_variables import get_url_user_movie
from rssenscritique.get_data_senscritique.scrapping.utils import remove_accent_from_text, get_code

logging.basicConfig(level=logging.INFO)


def get_nb_pages(html_code):
    try:
        nb_page = html_code('li', 'eipa-page')[-1].a['data-sc-pager-page']
    except Exception as e:
        nb_page = 1
        logging.info(f'Movie - get total nb of pages - Error: {e}. Setup {nb_page} pages by default')
    return int(nb_page)


def generate_urls(user_name, html_code):
    nb_page = get_nb_pages(html_code=html_code)
    return [f'https://www.senscritique.com/{user_name}/collection/all/films/all/all/all/all/all/all/all/page-{i + 1}'
            for i in range(nb_page)]


def get_user_rating(movie_info):
    tmp = movie_info('div', 'elco-collection-rating user')[0]

    try:
        if tmp.get_text().strip() == '':
            user_rating = 1
        else:
            user_rating = int(tmp.get_text().strip())
    except Exception as e:
        logging.info(f'Movie - get user rating - Error: {e}')
        user_rating = None
    return user_rating


def get_user_movie_info(movie_info):
    content = movie_info('div', 'elco-collection-content collection')

    try:
        movie_url = 'https://www.senscritique.com' + content[0].a['href']
    except Exception as e:
        logging.info(f'Movie - get movie url - Error: {e}')
        movie_url = None

    try:
        movie_name = content[0].a.get_text()
    except Exception as e:
        logging.info(f'Movie - get movie name - Error: {e}')
        movie_name = None

    try:
        movie_id = content[0].a['id']
    except Exception as e:
        logging.info(f'Movie - get movie id - Error: {e}')
        movie_id = None

    return movie_url, movie_name, movie_id


def get_movie_global_rating(movie_info):
    content = movie_info('div', 'erra user')[0]
    try:
        global_rating = float(content.a.get_text().strip())
    except Exception as e:
        logging.info(f'Movie - get global rating - Error: {e}')
        global_rating = None

    try:
        url_critic = 'https://www.senscritique.com' + content.a['href']
    except Exception as e:
        logging.info(f'Movie - get critic url - Error: {e}')
        url_critic = None

    try:
        nb_raters = int(content.a['title'].split(':')[-1].replace('avis', '').strip())
    except Exception as e:
        logging.info(f'Movie - get global rating - Error: {e}')
        nb_raters = None

    return global_rating, url_critic, nb_raters


def get_all_users_movies_from_one_page(html_code, user_url, user_name):
    all_movie_info = html_code('li', 'elco-collection-item')

    users_movies_info = {
        'user_url': [],
        'user_name': [],
        'movie_url': [],
        'movie_name': [],
        'movie_product_id': [],
        'user_rating': [],
        'user_interest': [],
        'global_rating': [],
        'url_critic': [],
        'nb_raters': [],
    }

    for movie_info in all_movie_info:

        user_rating = get_user_rating(movie_info=movie_info)

        if user_rating == 1:
            users_movies_info["user_rating"].append(None)
            users_movies_info["user_interest"].append(1)
        else:
            users_movies_info["user_rating"].append(user_rating)
            users_movies_info["user_interest"].append(0)

        movie_url, movie_name, movie_id = get_user_movie_info(movie_info=movie_info)
        global_rating, url_critic, nb_raters = get_movie_global_rating(movie_info=movie_info)

        users_movies_info["user_url"].append(user_url)
        users_movies_info["user_name"].append(user_name)
        users_movies_info["movie_url"].append(movie_url)
        users_movies_info["movie_name"].append(movie_name)
        users_movies_info["movie_product_id"].append(movie_id)
        users_movies_info["global_rating"].append(global_rating)
        users_movies_info["url_critic"].append(url_critic)
        users_movies_info["nb_raters"].append(nb_raters)

    return pd.DataFrame(users_movies_info)


def get_all_users_movies_info_and_write(db_path):
    users = pd.read_csv(db_path + "users/users.csv")
    users = users.drop_duplicates(subset=['url', 'name'])

    exclude_users_movies_df = pd.read_csv(db_path + "users_movies/users_movies.csv")
    users = users[~users.name.isin(exclude_users_movies_df.user_name)]
    users = users.sort_values(by='nb_notes', ascending=True)

    dfs = []

    for i in tqdm(range(users.shape[0])):
        dfs_temp = []
        user_serie = users.iloc[i]

        user_name_tmp = remove_accent_from_text(user_serie["name"])

        logging.info(f'Movie - get data from {user_name_tmp}')

        url_user = get_url_user_movie(user_name=user_name_tmp)
        html_code = get_code(url=url_user)
        users_movies_url = generate_urls(user_name=user_name_tmp, html_code=html_code)

        for url in tqdm(users_movies_url):
            html_code = get_code(url=url)
            df = get_all_users_movies_from_one_page(html_code=html_code,
                                                    user_url=user_serie["url"],
                                                    user_name=user_name_tmp)

            if not df.empty:
                dfs.append(df)
                dfs_temp.append(df)

        try:
            pd.concat(dfs_temp).to_csv(
                db_path + f"users_movies/users/users_movies_{user_name_tmp}.csv",
                index=False, header=True)
        except Exception as e:
            logging.info(f'Movie - concatenate dataset - Error: {e}')
            df_empty = pd.DataFrame({
                'user_url': [user_serie["url"]],
                'user_name': [user_name_tmp],
                'movie_url': [None],
                'movie_name': [None],
                'movie_product_id': [None],
                'user_rating': [None],
                'user_interest': [None],
                'global_rating': [None],
                'url_critic': [None],
                'nb_raters': [None],
            })
            df_empty.to_csv(db_path + f"users_movies/users/users_movies_{user_name_tmp}.csv", index=False, header=True)

    pd.concat(dfs).to_csv(db_path + f"users_movies/users_movies.csv",
                          index=False, header=True)


def get_one_user_movies(db_path, user_name, user_url):
    user_name_tmp = remove_accent_from_text(user_name)

    dfs = []

    logging.info(f'Movie - get data from {user_name_tmp}')

    url_user = get_url_user_movie(user_name=user_name_tmp)
    html_code = get_code(url=url_user)
    users_movies_url = generate_urls(user_name=user_name_tmp, html_code=html_code)

    for url in tqdm(users_movies_url):
        html_code = get_code(url=url)
        df = get_all_users_movies_from_one_page(html_code=html_code,
                                                user_url=user_url,
                                                user_name=user_name_tmp)

        if not df.empty:
            dfs.append(df)

    try:
        pd.concat(dfs).to_csv(
            db_path + f"users_movies/users/users_movies_{user_name_tmp}.csv",
            index=False, header=True)
    except Exception as e:
        logging.info(f'Movie - concatenate dataset - Error: {e}')


def agregate_users_movies_files(db_path):
    logging.info(f'Movie - agregate users movies')
    df = pd.concat(
        [pd.read_csv(db_path + f"users_movies/users/" + y) for y in tqdm(os.listdir(db_path + f"users_movies/users/"))])

    df.to_csv(db_path + f"users_movies/users_movies.csv", index=False, header=True)
