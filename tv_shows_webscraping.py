from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import urllib.request
import urllib.error
from bs4 import BeautifulSoup
import sqlite3
import random


def init_driver():
    options = webdriver.ChromeOptions()
    options.add_experimental_option(
        "excludeSwitches", ["enable-logging"]
    )  # Source: https://stackoverflow.com/questions/65080685/usb-usb-device-handle-win-cc1020-failed-to-read-descriptor-from-node-connectio
    driver = webdriver.Chrome(options=options)
    return driver


def navigate_to_RT_page(driver, network):
    """Navigate to tv show popular page on rotten tomatoes"""
    driver.get(
        f"https://www.rottentomatoes.com/browse/tv_series_browse/affiliates:{network}~sort:popular"
    )


def load_page(driver, selector):
    """Wait for the page to load the additional content and element is visible"""
    wait = WebDriverWait(driver, 10)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))


def find(driver, selector):
    """Find the specified element"""
    element = driver.find_element(By.CSS_SELECTOR, selector)
    return element


def click(element, max_clicks=None):
    """Click the found element up to maximum number of times"""
    clicks = 0
    while element.is_displayed() and (max_clicks is None or clicks < max_clicks):
        element.click()
        clicks += 1


"""-------------------------------------------------------------------------------------------------------"""


def download_page(url):
    """Open the specified URL and return the contents of the html page"""
    try:
        html = urllib.request.urlopen(url)
        return html
    except urllib.request.HTTPError as e:
        if e.code == 404:
            return "Not Found"
        else:
            raise e


def get_tvshows(html):
    """Get the parsed HTML of the loaded content"""
    soup = BeautifulSoup(html, "html.parser")
    tv_shows = soup.find(
        "div", attrs={"data-id": "tv_series_browse_affiliates:netflix~sort:popular"}
    )
    return tv_shows


"""-------------------------------------------------------------------------------------------------------"""


def parse_html(soup):
    from individual_show_scrape import (
        convert_title,
        get_individual_show,
        parse_for_critic_consensus,
        parse_for_creator,
        parse_for_exec_producers,
        parse_for_genre,
        parse_for_stars,
        parse_for_synoposis,
    )

    tv_shows_list = []
    for show in soup.find_all("tile-dynamic"):
        if show is not None:
            title = show.find(
                "span", attrs={"data-qa": "discovery-media-list-item-title"}
            ).text.strip()
            # print(title)

            tomatometer = (
                show.find("score-pairs")["criticsscore"]
                if show.find("score-pairs")["criticsscore"]
                else "Unknown"
            )

            critic_sentiment = (
                show.find("score-pairs")["criticssentiment"]
                if show.find("score-pairs")["criticssentiment"]
                else "Unknown"
            )
            # print(tomatometer, critic_sentiment)

            audience_score = (
                show.find("score-pairs")["audiencescore"]
                if show.find("score-pairs")["audiencescore"]
                else "Unknown"
            )
            audience_sentiment = (
                show.find("score-pairs")["audiencesentiment"]
                if show.find("score-pairs")["audiencesentiment"]
                else "Unknown"
            )
            # print(audience_score, audience_sentiment)

            latest_episode = show.find(
                "span", {"data-qa": "discovery-media-list-item-start-date"}
            )
            if latest_episode:
                latest_episode_date = latest_episode.text.strip()
            else:
                latest_episode_date = "Unknown"
            # print(latest_episode_date)

            new_title = convert_title(title)

            soup = get_individual_show(new_title)

            consensus = parse_for_critic_consensus(soup)

            creator = parse_for_creator(soup)

            synopsis = parse_for_synoposis(soup)

            exec_producers = parse_for_exec_producers(soup)

            stars = parse_for_stars(soup)

            genre = parse_for_genre(soup)

            tv_show_dict = {
                "Title": title,
                "Synopsis": synopsis,
                "Genre": genre,
                "Tomatometer": tomatometer,
                "Critic Sentiment": critic_sentiment,
                "Critic Consensus": consensus,
                "Audience Score": audience_score,
                "Audience Sentiment": audience_sentiment,
                "Latest Episode Date": latest_episode_date,
                "Creator": creator,
                "Executive Producers": exec_producers,
                "Cast Members": stars,
            }

            tv_shows_list.append(tv_show_dict)

    # Sort the list by tomatometer first, and then by audience score in case of ties
    tv_shows_list = sorted(
        tv_shows_list,
        key=lambda x: (x["Tomatometer"], x["Audience Score"]),
        reverse=True,
    )

    return tv_shows_list


"""-------------------------------------------------------------------------------------------------------"""


def write_csv(tv_shows_list):
    """Write TV show data to the CSV file"""
    with open("tv_shows.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "Title",
                "Synopsis",
                "Genre",
                "Tomatometer",
                "Critic Sentiment",
                "Critic Consensus",
                "Audience Score",
                "Audience Sentiment",
                "Latest Episode Date",
                "Creator",
                "Executive Producers",
                "Cast Members",
            ],
        )
        writer.writeheader()
        for show in tv_shows_list:
            writer.writerow(show)


def connect(database_name):
    """Connect to database file"""
    db = sqlite3.connect(database_name)
    return db


def cursor(db):
    """Create cursor"""
    c = db.cursor()
    return c


def create_table(c):
    """Create a table to store TV show data"""
    c.execute(
        "CREATE TABLE IF NOT EXISTS tv_shows (title TEXT, synopsis TEXT, genre TEXT, tomatometer REAL, critic_sentiment TEXT, consensus TEXT, audience_score REAL, audience_sentiment TEXT, latest_episode_date TEXT, creator REAL, exec_producers REAL, stars REAL)"
    )


def input_list(db, c):
    """Loop through the list and insert each dictionary from csv as a row into the database"""
    with open("tv_shows.csv", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for show in reader:
            c.execute(
                "INSERT INTO tv_shows VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    show["Title"],
                    show["Synopsis"],
                    show["Genre"],
                    show["Tomatometer"],
                    show["Critic Sentiment"],
                    show["Critic Consensus"],
                    show["Audience Score"],
                    show["Audience Sentiment"],
                    show["Latest Episode Date"],
                    show["Creator"],
                    show["Executive Producers"],
                    show["Cast Members"],
                ),
            )
        db.commit()


"""-------------------------------------------------------------------------------------------------------"""


def preference_filter(db_path, min_tomatometer=0, min_audience_score=0):
    """Apply the tomatometer and audience score preferences to create a filtered shows list"""

    conn = sqlite3.connect((db_path))
    c = conn.cursor()
    filtered_shows = []
    for row in c.execute(
        'SELECT DISTINCT * FROM tv_shows WHERE tomatometer > ? AND audience_score > ? AND audience_score != "" ORDER BY tomatometer DESC',
        (min_tomatometer, min_audience_score),
    ):
        new_picks = list(row)
        filtered_shows.append(new_picks)
    conn.close()
    return filtered_shows


def random_pick(filtered_shows):
    """return the chosen title and data in a neat format"""
    random_title = random.choice(filtered_shows)
    # not implemented: no repeat picks

    results = ""
    for i, key in enumerate(
        [
            "Title",
            "Synopsis",
            "Genre",
            "Tomatometer",
            "Critic Sentiment",
            "Critic Consensus",
            "Audience Score",
            "Audience Sentiment",
            "Latest Episode Date",
            "Creator",
            "Executive Producers",
            "Cast Members",
        ]
    ):
        if random_title[i] != "":
            results += f"{key}: {random_title[i]}\n"
    return results


"""-------------------------------------------------------------------------------------------------------"""

if __name__ == "__main__":
    # """Selenium"""

    # driver = init_driver()
    # navigate_to_RT_page(driver, "netflix")

    # selector = '[data-discoverygridsmanager="btnLoadMore"]'
    # load_page(driver, selector)

    # load_more_button = find(driver, selector)

    # click(
    #     load_more_button, 20
    # )  # Beyond 20 clicks: UnicodeEncodeError: 'ascii' codec can't encode character '\xeb' in position 37: ordinal not in range(128)

    # """ Beautiful Soup """

    # # url = 'https://www.rottentomatoes.com/browse/tv_series_browse/affiliates:netflix~sort:popular'

    # # html = download_page(url).read()

    # tv_shows = get_tvshows(driver.page_source)
    # print(tv_shows.prettify())

    # tv_shows_list = parse_html(tv_shows)
    # print(tv_shows_list)

    # # for titles in tv_shows_list:
    # #     print(titles)

    # # 2 minutes and 16 seconds to load 150 titles

    # """ CSV """

    # write_csv(tv_shows_list)

    """ SQlite3 """

    db = connect('tv_shows.db')
    c = cursor(db)

    create_table(c)

    input_list(db, c)

    # App needs to prompt the user to enter the minimum tomatometer and audience score tolerance out of 0 and 100

    min_tomatometer = 70
    min_audience_score = 70

    # Filter by minimum tomatometer and filter by minimum audience score

    # # print('\nPreferred Titles:')
    # for row in db.execute('SELECT DISTINCT * FROM tv_shows WHERE tomatometer > ? AND audience_score > ? AND audience_score != "" ORDER BY tomatometer DESC',
    #                     (min_tomatometer, min_audience_score)):
    #     print(row)

    #: Last Output: ('Wednesday'...'Jenna Ortega, Gwendoline Christie, Riki Lindhome, Christina Ricci, Jamie McShane'))

    """ Show Generator """

    filtered_shows = preference_filter("tv_shows.db", min_tomatometer, min_audience_score)
    # print(filtered_shows)

    chosen_title = random_pick(filtered_shows)
    print(chosen_title)
