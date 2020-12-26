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
