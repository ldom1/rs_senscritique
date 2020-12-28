import logging
import os

from rssenscritique.get_data_senscritique.scrapping.movies import get_all_movies_from_users_movies_info_and_write, \
    agregate_movies
from rssenscritique.get_data_senscritique.scrapping.users_movies import \
    get_all_users_movies_info_and_write, agregate_users_movies_files

logging.basicConfig(level=logging.INFO)

DB_PATH = os.getcwd().replace("rssenscritique/get_data_senscritique", "data/")

logging.info(f'Sens critique - Users')
# get_all_users_info_and_insert_in_db(db_path=DB_PATH)

logging.info(f'Sens critique - Users movies')
# get_all_users_movies_info_and_write(db_path=DB_PATH)
# agregate_users_movies_files(db_path=DB_PATH)

logging.info(f'Sens critique - Movies')
get_all_movies_from_users_movies_info_and_write(db_path=DB_PATH)
agregate_movies(data_path=DB_PATH)
