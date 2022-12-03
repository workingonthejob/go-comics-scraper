import requests
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from datetime import datetime
from logging.config import fileConfig
import os
from iniparser import IniParser
from lxml import html


fileConfig('gocomics-logging-config.ini')
log = logging.getLogger()

GOCOMICS_BASE_URL = 'https://www.gocomics.com'
COMIC_IMG_XPATH = './/picture[@class="item-comic-image"]/img'
TODAY = datetime.now()


def build_url(comic, year, month, day):
    return '/'.join([GOCOMICS_BASE_URL, comic, year, month, day])


def create_folder(comic):
    norm_path = os.path.normpath(comic)
    os.makedirs(norm_path, exist_ok=True)


class Scraper():

    def __init__(self, comics):
        self.session = None
        self.url = None
        self.comics = comics

    def start_session(self):
        self.session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def save_comic_image(self, url, comic, name):
        '''
            Save comics to the current directory in
            a folder the name as the comic.
        '''
        r = self.session.get(url=url)
        path = '\\'.join([comic, name])
        norm_path = os.path.normpath(path)
        with open(norm_path, 'wb') as f:
            f.write(r.content)

    def get_comic_image_url(self):
        try:
            r = self.session.get(url=self.url)
            tree = html.fromstring(r.content)
            results = tree.find(COMIC_IMG_XPATH)
            img_url = results.attrib['src']
            return img_url
        except AttributeError:
            raise Exception(f'The xpath "{COMIC_IMG_XPATH}" '
                            f'was incorrect or there currently is '
                            f'no comic for today.')

    def run(self):
        year = str(TODAY.year)
        month = str(TODAY.month)
        day = str(TODAY.day)
        self.start_session()
        for comic in self.comics:
            try:
                log.info(f'Downloading comic "{comic}" ({year}-{month}-{day})')
                create_folder(comic)
                self.url = build_url(comic, year, month, day)
                log.debug(self.url)
                img_url = self.get_comic_image_url()
                # The few comics I checked saved them as gifs so that's
                # what i'm using but if you want it to be dynamic use the
                # PIL library to determine the image type.
                # Didn't do it because it's another dependency.
                file_name = f'{comic}-({year}-{month}-{day}).gif'
                self.save_comic_image(img_url,
                                      comic,
                                      file_name)
            except Exception as e:
                log.exception(e)


if __name__ == '__main__':
    ip = IniParser('gocomics-scraper-config.ini')
    comics = ip.get_gocomics_properties('COMICS')
    gc = Scraper(comics)
    gc.run()
