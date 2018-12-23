import logging
import time

from webdriverplus import WebDriverPlus


def substring_in_list(s, l):
    for m in l:
        if s in m:
            return True
    return False


class SlackWebDriver(object):
    EMAIL_ID = '#email'
    PASSWORD_ID = '#password'
    SIGNIN_ID = '#signin_btn'
    MSG_INPUT_ID = '#msg_input'
    MSG_CSS = 'ts-message[id^=msg_]'
    SEARCH = '#search_terms'
    STARS_TOGGLE_ID = '#stars_toggle'
    SEARCH_RESULTS_TEXT = '#search_results_items .search_result_with_extract'
    STARRED_ITEMS = '#member_stars_list .star_item'

    def __init__(self, **kwargs):
        browser = kwargs.get('browser', 'chrome')
        self.url = kwargs.get('url')
        self.chrome_driver_exe = kwargs.get('chrome_driver_exe')
        self.web = WebDriverPlus(browser=browser, driver_executable=self.chrome_driver_exe)
        self.logger = logging.getLogger(self.__class__.__name__)

    def logged_in(self):
        """
        if message input is present, we assume we are logged in
        :return: True/False
        """
        return self.web.wait_el(self.MSG_INPUT_ID, timeout=1)

    def login(self, username, password):
        """
        open url, login with credentials, wait for message input field
        :param username:
        :param password:
        """
        self.web.open(self.url)
        self.web.type_in_field(self.EMAIL_ID, username)
        self.web.type_in_field(self.PASSWORD_ID, password)
        self.web.click_and_expect_vanish(self.SIGNIN_ID)
        self.web.wait_el(self.MSG_INPUT_ID, timeout=10)

    def get_msg_texts(self, timeout=5):
        """
        get message texts
        :param timeout:
        :return: list of message texts
        """
        return self.web.get_el_text(self.MSG_CSS, timeout=timeout)

    def send_msg(self, msg, timeout=10):
        """
        send message, verify message posted
        :param msg:
        :return: None
        """
        self.logger.info("Posting msg: [%s]" % msg)
        self.web.type_in_field_and_enter(self.MSG_INPUT_ID, msg)
        start_time = time.time()
        while abs(time.time() - start_time) <= timeout:
            messages = self.get_msg_texts()
            if substring_in_list(msg, messages):
                self.logger.info("Message posted")
                return
            else:
                self.logger.info("posting...")
                time.sleep(1)
        raise Exception("message not posted")

    def close(self):
        self.web.close()

    def star_msg(self, msg):
        """
        find message by text and star it
        :param msg: text of message to star
        :return: None
        """
        self.logger.info("Starring a message %s" % msg)
        messages = self.get_msg_texts()
        if not substring_in_list(msg, messages):
            raise Exception("cannot find message with given text")
        elements = self.web.wait_el(self.MSG_CSS)
        for el in elements:
            if msg in el.text:
                self.logger.info("Message found, starting to star it")
                web_id = el.get_attribute('id')
                self.web.hover_el(el)
                self.web.click_el('#%s button.star' % web_id)
                self.logger.info("Messaged starred")
                return
        raise Exception("cannot star a message")

    def search(self, text):
        """
        search messages
        :param text: search string
        :return: list of message texts
        """
        self.web.type_in_field_and_enter(self.SEARCH, text)
        time.sleep(5)
        texts = self.web.get_el_text(self.SEARCH_RESULTS_TEXT)
        return texts

    def get_starred_items(self):
        """
        click starred items
        :return: list of message texts from starred items
        """
        self.web.click_and_expect(self.STARS_TOGGLE_ID, self.STARRED_ITEMS)
        time.sleep(5)
        texts = self.web.get_el_text(self.STARRED_ITEMS)
        return texts

