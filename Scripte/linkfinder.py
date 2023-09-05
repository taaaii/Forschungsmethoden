from bs4 import BeautifulSoup
from Scripte.settings import Settings
import requests

my_settings = Settings()


def _find_link(string):
    soup = BeautifulSoup(string.decode('utf-8'), "html.parser")
    storylist = soup.find_all("div", class_="storylist-item")

    for tag in storylist:
        sub_soup = BeautifulSoup(str(tag), "html.parser")
        author_link = sub_soup.find("a", class_="no-wrap")["href"]
        word_count_tag = sub_soup.find("span", title="Wörter")
        word_count = int(word_count_tag.find_next("span").text.replace(".", "").strip())

        if word_count > my_settings.word_limit:
            print(f"found one")
            title_link = f'https://fanfiktion.de{sub_soup.find("a")["href"]}'
            try:
                result = _check_profile(author_link)
                yield title_link, result

            except Exception as e:
                print(e)
                yield title_link, None
        else:
            continue


def link_collect(string):
    page_result = [f"'{x}'" for x, y in _find_link(string)]
    if not page_result: return
    with open(f"{my_settings.current_topic}_links.txt", "a", encoding="utf-8") as f:
        f.write(",".join(page_result) + ",\n")


def _check_profile(link):
    x = requests.get(f"https://fanfiktion.de{link}")
    soup = BeautifulSoup(x.content.decode("utf-8"), "html.parser")
    gender = soup.find(
        "#ffcbox-bio-layer-SL > div > div > div > div > div.floatleft.userprofile-bio-table-outer > div > div:nth-child(3) > div.cell.semibold")
    if gender:
        return gender
    else:
        return False
