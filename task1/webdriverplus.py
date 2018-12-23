import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, \
    StaleElementReferenceException, \
    ElementNotVisibleException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


class WebDriverPlus(object):
    """
    web driver helper class
    """
    def __init__(self, **kwargs):
        browser = kwargs.get('browser', 'chrome')
        driver_executable = kwargs.get('driver_executable')
        self.driver = self.create_driver(browser, driver_executable)

    @classmethod
    def create_driver(cls, browser, driver_executable):
        if browser == 'chrome':
            driver = webdriver.Chrome(driver_executable)
            assert driver_executable, "Driver executable must be defined for chrome"
        else:
            raise NotImplemented("for now only chrome is supported")
        return driver

    def wait_el(self, css, **kwargs):
        """
        wait for element to be found by webdrive within a timeout
        :param css: CSS of the element
        :param timeout: timeout for element to appear/disappear
        :param gone: if True, element should be gone within timeout
        :param text_only: if True, list of element texts is returned
        :return: list of webdriver elements or list of their attributes,
                like text
        """
        timeout = kwargs.get('timeout', 5)
        gone = kwargs.get('gone', False)
        text_only = kwargs.get('text_only', False)
        driver = kwargs.get('driver', self.driver)
        start_time = time.time()
        while abs(time.time() - start_time) <= timeout:
            try:
                elements = driver.find_elements_by_css_selector(css)
                if gone:
                    time.sleep(1)
                else:
                    if text_only:
                        return [el.text for el in elements]
                    else:
                        return elements
            except (NoSuchElementException,
                    StaleElementReferenceException,
                    ElementNotVisibleException) as e:
                if gone:
                    return None
                else:
                    time.sleep(1)
        return None

    def wait_el_gone(self, css, timeout=5):
        self.wait_el(css, timeout=timeout, gone=True)

    @classmethod
    def filter_displayed_only(cls, elements):
        return [el for el in elements if el.is_displayed()]

    def click_el(self, css, **kwargs):
        elements = self.wait_el(css, **kwargs)
        elements = self.filter_displayed_only(elements)
        if not elements:
            raise Exception("no element found for %s" % css)
        elif len(elements) > 1:
            raise Exception("multiple elements found for %s" % css)
        else:
            elements[0].click()

    def click_and_expect(self, css_click, css_expect, timeout=5):
        self.click_el(css_click, timeout=timeout)
        self.wait_el(css_expect, timeout=timeout)

    def click_and_expect_vanish(self, css, timeout=5):
        self.click_el(css, timeout=timeout)
        self.wait_el_gone(css, timeout=timeout)

    def get_el_text(self, css, timeout=5):
        return self.wait_el(css, text_only=True, timeout=timeout)

    def type_in_field(self, css, text, ending=None):
        elements = self.wait_el(css)
        assert elements
        el = elements[0]
        el.click()
        el.send_keys(text)
        if ending:
            el.send_keys(ending)

    def type_in_field_and_enter(self, css, text):
        self.type_in_field(css, text, ending=Keys.ENTER)

    def open(self, url):
        self.driver.get(url)

    def close(self):
        self.driver.quit()

    def hover_el(self, element):
        hov = ActionChains(self.driver).move_to_element(element)
        hov.perform()
