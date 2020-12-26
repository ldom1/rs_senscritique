import logging
import pandas as pd

from rssenscritique.get_data_senscritique.scrapping.utils import correct_figures, correct_rounded_k_figures, get_code
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)


def get_header_information(html_code):
    content = html_code('div', 'pvi-hero-overlay')[0]

    try:
        title = content.h1["title"]
    except Exception as e:
        logging.info(f'Movies - Get title - Error: {e}')
        title = None

    try:
        release_year = content('small')[0].get_text().replace('(', '').replace(')', '')
    except Exception as e:
        logging.info(f'Movies - Get release year - Error: {e}')
        release_year = None

    try:
        alternative_title = content('h2', 'pvi-product-originaltitle')[0].get_text()
    except Exception as e:
        logging.info(f'Movies - Get alternative title - Error: {e}')
        alternative_title = None

    try:
        product_id = content('div', 'pvi-product-scactions')[0]['data-sc-product-id']
    except Exception as e:
        logging.info(f'Movies - Get id - Error: {e}')
        product_id = None

    try:
        img_url = content('figure')[0].img['src']
    except Exception as e:
        logging.info(f'Movies - Get img url - Error: {e}')
        img_url = None

    return title, release_year, alternative_title, product_id, img_url


def extract_figures_from_header(html_code):
    content = html_code('div', 'pvi-product-scrating')[0]

    nb_of_ratings = None
    nb_of_reviews = None
    try:
        for elt in content('meta'):
            if elt["itemprop"] == "ratingCount":
                nb_of_ratings = correct_figures(figure_text=elt["content"], figure_type=int)
            elif elt["itemprop"] == "reviewCount":
                nb_of_reviews = correct_figures(figure_text=elt["content"], figure_type=int)
    except Exception as e:
        logging.info(f'Movies - Get ratings & reviews count - Error: {e}')

    try:
        global_rating = correct_figures(figure_text=content("span", "pvi-scrating-value")[0].get_text(),
                                        figure_type=float)
    except Exception as e:
        logging.info(f'Movies - Get global_rating - Error: {e}')
        global_rating = None

    rating_repartition = {}

    try:
        for k, elt in enumerate(content("ol", "elrg-graph product")[0]("li")):
            rating_repartition[k + 1] = correct_figures(figure_text=elt.get_text().strip(),
                                                        figure_type=int)
    except Exception as e:
        logging.info(f'Movies - Get ratings repartition - Error: {e}')

    try:
        nb_coup_de_coeur = content.findAll("li", {"title": "Coups de coeur"})[0].get_text().strip()
        nb_coup_de_coeur = correct_rounded_k_figures(figure_text=nb_coup_de_coeur)
    except Exception as e:
        logging.info(f'Movies - Get nb coup de coeurs - Error: {e}')
        nb_coup_de_coeur = None

    try:
        nb_envie = content.findAll("li", {"title": "Envies"})[0].get_text().strip()
        nb_envie = correct_rounded_k_figures(figure_text=nb_envie)
    except Exception as e:
        logging.info(f'Movies - Get nb envies - Error: {e}')
        nb_envie = None

    return nb_of_ratings, nb_of_reviews, global_rating, rating_repartition, nb_coup_de_coeur, nb_envie


def get_movie_information(html_code):
    content = html_code('div', 'd-grid-main')[0]

    try:
        director_name = content.findAll("span", {"itemprop": "director"})[0].get_text().strip()
    except Exception as e:
        logging.info(f'Movies - Get movie director name - Error: {e}')
        director_name = None

    try:
        director_url = "https://www.senscritique.com" + content.findAll("span", {"itemprop": "director"})[0].a["href"]
    except Exception as e:
        logging.info(f'Movies - Get movie director url - Error: {e}')
        director_url = None

    try:
        main_movie_genre = content.findAll("span", {"itemprop": "genre"})[0].get_text().strip()
    except Exception as e:
        logging.info(f'Movies - Get main movie genre - Error: {e}')
        main_movie_genre = None

    try:
        main_movie_genre_url = "https://www.senscritique.com" + content("a", "d-link-alt")[0]["href"]
    except Exception as e:
        logging.info(f'Movies - Get main movie genre url - Error: {e}')
        main_movie_genre_url = None

    try:
        movie_genre = ", ".join([y.get_text().strip() for y in content.findAll("span", {"itemprop": "genre"})])
    except Exception as e:
        logging.info(f'Movies - Get movie genre - Error: {e}')
        movie_genre = None

    try:
        movie_duration = content.findAll("li", "pvi-productDetails-item")[-2].get_text().strip()
    except Exception as e:
        logging.info(f'Movies - Get movie duration - Error: {e}')
        movie_duration = None

    try:
        movie_release_date = content.findAll("li", "pvi-productDetails-item")[-1].get_text().strip()
    except Exception as e:
        logging.info(f'Movies - Get movie release date - Error: {e}')
        movie_release_date = None

    return director_name, director_url, main_movie_genre, main_movie_genre_url, movie_genre, movie_duration, movie_release_date


def get_main_actors(html_code):
    content = html_code.findAll("div", {"itemprop": "actor"})

    actors = {}

    try:
        for k, elt in enumerate(html_code.findAll("div", {"itemprop": "actor"})):
            actors[f"main_actor_{k}"] = {
                "name": elt.findAll("span", {"itemprop": "name"})[0].get_text(),
                "url": "https://www.senscritique.com" + elt.a["href"]
            }
    except Exception as e:
        logging.info(f'Movies - Get movie main actors - Error: {e}')

    return actors


def get_all_info_from_one_movie(html_code):
    title, release_year, alternative_title, product_id, img_url = get_header_information(html_code=html_code)
    nb_of_ratings, nb_of_reviews, global_rating, rating_repartition, nb_coup_de_coeur, nb_envie = extract_figures_from_header(
        html_code=html_code)
    director_name, director_url, main_movie_genre, main_movie_genre_url, movie_genre, movie_duration, movie_release_date = get_movie_information(
        html_code=html_code)
    actors = get_main_actors(html_code=html_code)

    movie_info = {"title": title, "release_year": release_year, "alternative_title": alternative_title,
                  "product_id": product_id, "img_url": img_url, "nb_of_ratings": nb_of_ratings,
                  "nb_of_reviews": nb_of_reviews, "global_rating": global_rating,
                  "rating_repartition": rating_repartition, "nb_coup_de_coeur": nb_coup_de_coeur,
                  "nb_envie": nb_envie, "director_name": director_name, "director_url": director_url,
                  "main_movie_genre": main_movie_genre, "main_movie_genre_url": main_movie_genre_url,
                  "movie_genre": movie_genre, "movie_duration": movie_duration,
                  "movie_release_date": movie_release_date, "actors": actors}

    return movie_info


def get_all_movies_from_users_movies_info_and_write(db_path):
    users_movies_path = db_path + 'users_movies/users_movies.csv'
    users_movies = pd.read_csv(users_movies_path)
    movie_urls = users_movies.movie_url.unique()

    dfs = []

    logging.info(f'Movies - Get movie infos')

    for movie_url in tqdm(movie_urls):
        html_code = get_code(url=movie_url)
        movie_info = get_all_info_from_one_movie(html_code)
        dfs.append(pd.DataFrame(movie_info))

    pd.concat(dfs).to_csv(db_path + f"movies/movies.csv", index=False, header=True)
