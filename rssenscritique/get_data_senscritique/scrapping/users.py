import logging
from tqdm import tqdm
import pandas as pd

from rssenscritique.config.global_variables import URSL_USERS_LIST
from rssenscritique.get_data_senscritique.scrapping.utils import get_code

logging.basicConfig(level=logging.INFO)


def get_user_info(html_user_info):
    try:
        user_url = html_user_info.a["href"]
    except Exception as e:
        logging.info(f'Users - Get user url - Error: {e}')
        user_url = None

    try:
        user_name = html_user_info('span')[0].get_text()
        if user_name == '':
            user_name = user_url.split('/')[-1]
    except Exception as e:
        logging.info(f'Users - Get user name - Error: {e}')
        user_name = None

    try:
        user_nb_followers = html_user_info('span')[1].get_text()
    except Exception as e:
        logging.info(f'Users - Get nb followers users - Error: {e}')
        user_nb_followers = None

    try:
        user_nb_notes = html_user_info('span')[2].get_text().split()[0]
    except Exception as e:
        logging.info(f'Users - Get nb notes users - Error: {e}')
        user_nb_notes = None

    return user_url, user_name, user_nb_followers, user_nb_notes


def get_all_user_info_from_one_page(html_code):
    html_user_list = html_code('div', 'SearchUserComponent__MainContainer-a3l3tb-3 OWIdn')
    users_info = {'url': [],
                  'name': [],
                  'nb_followers': [],
                  'nb_notes': []}

    for html_user_info in tqdm(html_user_list):
        user_url, user_name, user_nb_followers, user_nb_notes = get_user_info(html_user_info=html_user_info)
        users_info['url'].append(user_url)
        users_info['name'].append(user_name)
        users_info['nb_followers'].append(user_nb_followers)
        users_info['nb_notes'].append(user_nb_notes)

    return pd.DataFrame(users_info)


def get_all_users_info_and_insert_in_db(db_path):

    dfs = []

    for k, url in enumerate(tqdm(URSL_USERS_LIST)):
        logging.info(f'Users - Get users - page: {k + 1}')
        html_code = get_code(url=url)
        df = get_all_user_info_from_one_page(html_code)

        if not df.empty:
            dfs.append(df)

    pd.concat(dfs).to_csv(db_path + f"users/user.csv",
                          index=False, header=True)
