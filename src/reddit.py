import praw
import logging
from logging.config import fileConfig
from praw.exceptions import APIException, ClientException, PRAWException
from prawcore.exceptions import PrawcoreException
from requests.exceptions import ConnectionError
from iniparser import IniParser


USER_AGENT = 'Posts comics from GoComics to /r/Calvin_And_Hobbes/.'
RECOVERABLE_EXC = (
    APIException,
    ClientException,
    PRAWException,
    PrawcoreException,
    ConnectionError,
)


fileConfig('gocomics-logging-config.ini')
log = logging.getLogger()


class Reddit():
    def __init__(self,
                 username,
                 password,
                 client_id,
                 client_secret,
                 limit,
                 subreddit):
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.limit = limit
        self.subreddit = subreddit
        self.headers = {}
        self._setup = False
        self.reddit = None

    def all_checks_passed(self):
        '''
        Perform checks that must pass in order to post.
        '''
        log.info('Running checks...')
        return True

    def post_comic_image(self, subreddit, title, image_path):
        log.debug(f'Posting to {subreddit} subreddit...')
        sr = self.reddit.subreddit(subreddit)
        sr.submit_image(title=title,
                        image_path=image_path)

    def run(self):
        """
        Run the script.
        """
        try:
            if self.all_checks_passed():
                self.post_comic_image(subreddit=self.subreddit,
                                      title='Sub title',
                                      image_path='Image Path')
        except Exception as e:
            log.exception(e)

    def setup(self):
        """
        Logs into reddit and refreshs the header text.
        """
        self._login()
        self._setup = True

    def quit(self):
        self.headers = {}
        self._setup = False

    def _login(self):
        self.reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            username=self.username,
            password=self.password,
            user_agent=USER_AGENT,
        )


if __name__ == '__main__':
    ip = IniParser('gocomics-reddit-config.ini')
    username = ip.get_reddit_properties('REDDIT_USER')
    password = ip.get_reddit_properties('REDDIT_PASS')
    client_id = ip.get_reddit_properties('REDDIT_CLIENT_ID')
    client_secret = ip.get_reddit_properties('REDDIT_CLIENT_SECRET')
    limit = int(ip.get_reddit_properties('LIMIT'))
    wait = int(ip.get_reddit_properties('WAIT'))
    refresh = int(ip.get_reddit_properties('REFRESH'))
    subreddit = ip.get_reddit_properties('SUBREDDIT')
    setup_has_been_run = False

    log.info('Starting...')
    try:
        try:
            bot = Reddit(
                username,
                password,
                client_id,
                client_secret,
                limit,
                subreddit)
            bot.setup() if not setup_has_been_run else None
            bot.run()
            log.info('Script done running.')
        except RECOVERABLE_EXC as e:
            log.exception(e)
    except KeyboardInterrupt:
        pass
    finally:
        bot.quit()
    exit(0)
