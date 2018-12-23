import logging
import time
import argparse

from slack_webdriver import SlackWebDriver, substring_in_list


FORMAT = '%(asctime)s - %(name)s - %(levelname)s %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)
logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
logger.addHandler(ch)


def test_slack_msg_starring(args):
    """
    Functional message starring test
        - login to slack in chrome browser
        - post unique message to default channel
        - star that message
        - verify message is present in has:star search results
        - verify message is present in "Starred Items" list
        - on success, close chrome browser
    """
    logging.info("Starting test >>>>")
    slack_team = args.team
    slack_username = args.username
    slack_password = args.password
    chrome_driver_exe = args.chromedriver
    url = "https://%s.slack.com" % slack_team
    slack = SlackWebDriver(url=url, browser="chrome", chrome_driver_exe=chrome_driver_exe)
    slack.login(slack_username, slack_password)

    logging.info("Verify message can be posted")
    unique_msg = "time: %s" % time.time()
    slack.send_msg(unique_msg)

    logging.info("Verify message can be starred")
    slack.star_msg(unique_msg)

    logging.info("Verify search has:star returns all starred messages")
    # there is a bug, the starred message is not in the results
    # one needs to press first "Show Starred Items" for the starred message to appear in the search results
    results = slack.search('has:star')
    assert substring_in_list(unique_msg, results), "Starred message not found in has:star search results"

    logging.info("Verify big star on the upper right displays all starred items")
    results = slack.get_starred_items()
    assert substring_in_list(unique_msg, results), "Starred message was not found in Starred Items"

    # close browser
    slack.close()
    logging.info("Testing done <<<<")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--team", help="slack team domain")
    parser.add_argument("--username", help="slack username")
    parser.add_argument("--password", help="slack password")
    parser.add_argument("--chromedriver", help="path to chrome webdriver executable")
    args = parser.parse_args()
    test_slack_msg_starring(args)