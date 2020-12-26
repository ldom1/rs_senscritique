import time
import requests
from user_agent import generate_user_agent
from bs4 import BeautifulSoup as soup
import logging
import unidecode

from rssenscritique.config.global_variables import STANDARD_HTML

logging.basicConfig(level=logging.INFO)


def get_code(url):
    """Return the code html"""
    # Define the user agent
    headers = {'User-Agent': generate_user_agent(device_type="desktop",
                                                 os=('mac', 'linux'))}
    # Open the url file and get the html code of the page
    try:
        req = requests.get(url, headers=headers)
        time.sleep(1)
        return soup(req.text, "lxml")
    except Exception as e:
        logging.info(f'Get html code - {e}')
        return soup(STANDARD_HTML, "lxml")


def remove_accent_from_text(text):
    return unidecode.unidecode(text)


def correct_rounded_k_figures(figure_text):
    try:
        if 'K' in figure_text:
            return int(float(figure_text.replace('K', '')) * 1000)
        else:
            return int(figure_text)
    except Exception as e:
        logging.info(f'Movies - correct figures rounded K - Error: {e}')
        return figure_text


def correct_figures(figure_text, figure_type):
    try:
        if figure_type:
            return figure_type(figure_text)
        else:
            return float(figure_text)
    except Exception as e:
        logging.info(f'Movies - correct figures - Error: {e}')
        return figure_text
