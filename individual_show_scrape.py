from bs4 import BeautifulSoup
import re
from tv_shows_webscraping import download_page


def convert_title(title):
    """Converts the title into a new title string"""
    new_title = title.replace(" ", "_").lower()
    return new_title


def get_individual_show(new_title):
    """Returns the soup of the individual show"""
    url = f"https://www.rottentomatoes.com/tv/{new_title}"
    html = download_page(url)
    soup = BeautifulSoup(html, "html.parser")
    return soup


def parse_for_critic_consensus(soup):
    """Returns the critic consensus of the individual show from the soup"""
    try:
        season_list_section = soup.find("section", {"data-qa": "section:season-list"})
        season_item = season_list_section.find("season-list-item")
        consensus = season_item.get("consensus")
        consensus = re.sub(r"<em>|</em>", "", consensus)
    except AttributeError:
        consensus = "Unknown"

    return consensus


def parse_for_creator(soup):
    """Returns the creator of the individual show from the soup"""

    try:
        creator = (
            soup.find("li", {"class": "info-item"}, {"b": {"text": "Creator:"}})
            .find("a", {"data-qa": "creator"})
            .text.strip()
        )
    except AttributeError:
        creator = "Unknown"

    return creator


def parse_for_synoposis(soup):
    """Returns the synposis of the individual show from the soup"""
    try:
        synopsis = (
            soup.find("div", {"class": "content"})
            .find("p", {"data-qa": "series-info-description"})
            .text.strip()
        )
    except AttributeError:
        synopsis = "Unknown"

    return synopsis


def parse_for_exec_producers(soup):
    """Returns the executive producers of the individual show from the soup"""
    try:
        exec_producers_list = []
        series_info = soup.find("section", {"data-qa": "section:series-info"})
        producer_links = series_info.find_all(
            "a", {"data-qa": "series-details-producer"}
        )
        for link in producer_links:
            exec_producers_list.append(link.string.strip())
        exec_producers = " ".join(exec_producers_list)
    except AttributeError:
        exec_producers = "Unknown"

    return exec_producers


def parse_for_stars(soup):
    """Returns the cast member stars of the individual show from the soup"""
    try:
        stars_list = []
        series_info = soup.find("section", {"data-qa": "section:series-info"})
        star_links = series_info.find_all("a", {"data-qa": "cast-member"})
        for link in star_links:
            stars_list.append(link.text.strip())
        stars = " ".join(stars_list)
    except AttributeError:
        stars = "Unknown"

    return stars


def parse_for_genre(soup):
    """Returns the genre of the individual show from the soup"""
    try:
        genre = soup.find("b", string="Genre: ").find_next_sibling("span").text.strip()
    except AttributeError:
        genre = "Unknown"

    return genre


if __name__ == "__main__":
    title = "The Society"
    new_title = convert_title(title)
    soup = get_individual_show(new_title)

    consensus = parse_for_critic_consensus(soup)
    print(consensus)

    creator = parse_for_creator(soup)
    print(creator)

    synopsis = parse_for_synoposis(soup)
    print(synopsis)

    exec_producers = parse_for_exec_producers(soup)
    print(exec_producers)

    stars = parse_for_stars(soup)
    print(stars)

    genre = parse_for_genre(soup)
    print(genre)
