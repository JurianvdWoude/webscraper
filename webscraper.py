from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag

from selenium.webdriver import Firefox, FirefoxProfile
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

# import pandas as pd
import csv
import time
import random


class HSWebSearch:
    def __init__(self, winstats, abilities, ratings, abilitylist) -> None:
        self.hs_winstats_searchpage = winstats
        self.hs_abilities_searchpage = abilities
        self.hs_ratings_searchpage = ratings
        self.hs_abilitylist_page = abilitylist

    def start_scraping(self):
        driver = self.create_driver()
        index = 0

        # driver.get()

        # self.goto_page(driver, self.hs_winstats_searchpage + 'Blood of the Ancient One', 'figcaption')
        # stats_page = self.get_page(driver)
        # statistics = self.get_cardstatistics(stats_page, 'Blood of the Ancient One')
        # return

        self.goto_page(driver, self.hs_abilitylist_page, "a")
        abilitylist_page = self.get_page(driver)
        # abilitylist = self.get_list_of_possible_abilities(abilitylist_page)

        # csv_labels = [
        #     "Index",
        #     "CardName",
        #     "Rating",
        #     "InPrcntOfDecks",
        #     "AvgCopies",
        #     "DeckWinratePrcnt",
        #     "TimesPlayed",
        #     "Set",
        #     "CardType",
        #     "MinionType",
        #     "Class",
        #     "Rarity",
        #     "Cost",
        #     "Attack",
        #     "Health",
        #     "Durability",
        # ] + abilitylist

        csv_labels = [
            "index",
            "name",
            "rating",
            "in % of decks",
            "avg copies",
            "winrate",
            "times played",
            "set",
            "has set",
            "type",
            "has type",
            "minion type",
            "has minion type",
            "class",
            "has class",
            "rarity",
            "has rarity",
            "cost",
            "has cost",
            "attack",
            "has attack",
            "health",
            "has health",
            "durability",
            "has durability",
            "ability text",
            "charge",
            "divine shield",
            "windfury",
            "taunt",
            "poisonous",
            "battlecry",
            "deathrattle",
            "rush",
            "combo",
            "discover",
            "elusive",
            "lifesteal",
            "reborn",
            "secret",
            "stealth",
        ]
        print(csv_labels)

        csv_data = []

        go_to_next_page = True

        self.goto_page(driver, self.hs_ratings_searchpage, "strong")
        # TODO: remove the page/61/ from the above link

        while go_to_next_page:
            ratingspage_page = self.get_page(driver)

            ratingspage_cards_url = driver.current_url
            ratingspage_cards = ratingspage_page.find(
                "div", attrs={"class": "row aligned-row"}
            ).find_all("div", attrs={"class": "card-item"})

            for ratingspage_card in ratingspage_cards:
                index += 1
                rating = self.get_rating(ratingspage_card)
                searchname = self.get_searchquery(ratingspage_card)

                self.goto_page(driver, self.hs_ratings_searchpage + searchname, "h1")
                card_page = self.get_page(driver)
                cardname = self.get_cardname(card_page)
                print("\nAdding card nr. {0}: {1}".format(index, cardname))
                self.goto_page(
                    driver, self.hs_winstats_searchpage + cardname, "figcaption"
                )

                stats_page = self.get_page(driver)
                statistics = self.get_cardstatistics(stats_page, cardname)
                if cardname == "Windfury":
                    self.goto_page(
                        driver,
                        self.hs_abilities_searchpage + "Windfury_(card)",
                        "tbody",
                    )
                else:
                    self.goto_page(
                        driver,
                        self.hs_abilities_searchpage + cardname.replace(" ", "_"),
                        "img",
                    )
                # elif cardname == "A. F. Kay":
                #     self.goto_page(
                #         driver, self.hs_abilities_searchpage + "A._F._Kay", "tbody"
                #     )
                # else:
                #     print(" CARDNAME : " + cardname)
                #     # self.goto_page(driver, self.hs_abilities_searchpage + cardname.replace(' The ', ' the '), 'tbody')
                #     self.goto_page(driver, self.hs_abilities_searchpage, "input")
                #     self.search_for_card(
                #         driver, cardname.replace(" The ", " the "), "tbody"
                #     )

                # driver.implicitly_wait(10)

                time.sleep(random.choice([2, 3]))
                self.accept_cookies(driver)
                time.sleep(random.choice([1, 2]))

                abilities_page = self.get_page(driver)
                abilities = self.get_abilities(abilities_page)
                datarow = [str(index)] + [cardname] + [rating] + statistics + abilities
                csv_data.append(datarow)
                print(
                    "Appended {0} values to the HS data:\n{1}".format(
                        len(datarow), datarow
                    )
                )
                # print(len(csv_data))

            self.goto_page(driver, ratingspage_cards_url, "div")
            print("\nStored {} values in total!".format(len(csv_data)))
            go_to_next_page = self.click_next_page(driver)

            if go_to_next_page:
                print("\n=-( Next page )->\n")
                print("-=-" * 10)
            else:
                print("\nDone scraping!")

        print("Putting data into a csv file...")

        self.write_csv_file("hearthstone_cards.csv", csv_labels, csv_data)

        print("~ Finished! ~")

    def write_csv_file(self, filename, labels, data):
        with open(filename, "w", newline="") as csvfile:
            csvwriter = csv.writer(
                csvfile, delimiter=";", quotechar="|", quoting=csv.QUOTE_MINIMAL
            )
            csvwriter.writerow(labels)
            csvwriter.writerows(data)

    # def get_list_of_possible_abilities(self, page):
    #     abilities = []
    #     abilities_div = page.find("div", attrs={"id": "toc"})

    #     for ability in abilities_div.find_all("li", attrs={"class": "toclevel-2"}):
    #         abilities.append(ability.find("span", attrs={"class": "toctext"}).text)
    #     return abilities[:-1]

    def get_abilities(self, card):
        # card_infobox = card.find("div", attrs={"class": "stdinfobox"})

        card_infobox = card.find("aside", attrs={"class": "portable-infobox"})

        # INFO: Get the card set
        card_stat_container = card_infobox.find(
            "div", attrs={"data-source", "derived_cardSet"}
        )
        card_set = ""
        card_has_set = 0
        if card_stat_container:
            card_has_set = 1
            card_set = card_stat_container.find("a")["title"]
        # INFO: Get the card type
        card_stat_container = card_infobox.find("div", attrs={"data-source", "type"})
        card_type = ""
        card_has_type = 0
        if card_stat_container:
            card_has_type = 1
            card_type = card_stat_container.find("a").text
        # INFO: Get the card minion type
        card_stat_container = card_infobox.find(
            "div", attrs={"data-source", "custom_race"}
        )
        card_miniontype = ""
        card_has_miniontype = 0
        if card_stat_container:
            card_has_miniontype = 1
            card_miniontype = card_stat_container.find("a").text
        # INFO: Get the card class
        card_stat_container = card_infobox.find("div", attrs={"data-source", "class"})
        card_class = ""
        card_has_class = 0
        if card_stat_container:
            card_has_class = 1
            card_class = card_stat_container.find("a").text
        # INFO: get the card rarity
        card_stat_container = card_infobox.find("div", attrs={"data-source", "rarity"})
        card_rarity = ""
        card_has_rarity = 0
        if card_stat_container:
            card_has_rarity = 1
            card_rarity = card_stat_container.find("a", attrs={"title", "Rarity"}).text
        # INFO: Get the card attack
        card_stat_container = card_infobox.find("div", attrs={"data-source", "attack"})
        card_attack = 0
        card_has_attack = 0
        if card_stat_container:
            card_has_attack = 1
            card_attack = int(
                card_stat_container.find("div", attrs={"class": "pi-data-value"})
            )
        # INFO: Get the card health
        card_stat_container = card_infobox.find("div", attrs={"data-source", "health"})
        card_health = 0
        card_has_health = 0
        if card_stat_container:
            card_has_health = 1
            card_health = int(
                card_stat_container.find("div", attrs={"class": "pi-data-value"})
            )
        # INFO: Get the card cost
        card_stat_container = card_infobox.find(
            "div", attrs={"data-source", "manaCost"}
        )
        card_cost = 0
        card_has_cost = 0
        if card_stat_container:
            card_has_cost = 1
            card_cost = int(
                card_stat_container.find("div", attrs={"class": "pi-data-value"})
            )
        # INFO: Get the card durability
        card_stat_container = card_infobox.find(
            "div", attrs={"data-source", "durability"}
        )
        card_durability = 0
        card_has_durability = 0
        if card_stat_container:
            card_has_durability = 1
            card_durability = int(
                card_stat_container.find("div", attrs={"class": "pi-data-value"})
            )
        print(card_set)
        print(str(card_attack))
        print(str(card_health))
        print(str(card_cost))

        # card_container = card_infobox.find_all("tr")

        # card_set = self.find_card_attr(card_container, "a", "Set:", "")
        # card_type = self.find_card_attr(card_container, "a", "Type:", "")
        # card_miniontype = self.find_card_attr(card_container, "a", "Minion type:", "")
        # card_class = self.find_card_attr(card_container, "a", "Class:", "")
        # card_rarity = self.find_card_attr(card_container, "span", "Rarity:", "")
        # card_cost = int(
        #     re.findall(
        #         "[0-9]+", self.find_card_attr(card_container, "td", "Cost:", "0")
        #     )[0]
        # )
        # card_attack = int(
        #     re.findall(
        #         "[0-9]+", self.find_card_attr(card_container, "td", "Attack:", "0")
        #     )[0]
        # )
        # card_health = int(
        #     re.findall(
        #         "[0-9]+", self.find_card_attr(card_container, "td", "Health:", "0")
        #     )[0]
        # )
        # card_durability = int(
        #     re.findall(
        #         "[0-9]+", self.find_card_attr(card_container, "td", "Durability:", "0")
        #     )[0]
        # )

        cardvalues = [
            card_set,
            card_has_set,
            card_type,
            card_has_type,
            card_miniontype,
            card_has_miniontype,
            card_class,
            card_has_class,
            card_rarity,
            card_has_rarity,
            card_cost,
            card_has_cost,
            card_attack,
            card_has_attack,
            card_health,
            card_has_health,
            card_durability,
            card_has_durability,
        ]

        abilities_text = ""
        if card_infobox.find("div", attrs={"data-source", "text"}):
            abilities_text = card_infobox.find(
                "div", attrs={"data-source", "text"}
            ).text
        cardvalues.append(abilities_text)

        # if card_container[-3].find("b").string == "Abilities:":
        #     abilities = card_container[-3].find_all("a")
        # elif card_container[-2].find("b").string == "Abilities:":
        #     abilities = card_container[-2].find_all("a")
        # else:
        #     abilities = []

        # for ability in abilitylist:
        #     if ability in map(lambda x: x.string, abilities):
        #         cardvalues.append(1)
        #     else:
        #         cardvalues.append(0)

        abilities = []
        card_stat_container = card_infobox.find(
            "div", attrs={"data-source", "keywords"}
        )
        if card_stat_container:
            abilities = [item.text for item in card_stat_container.find_all("code")]

        if "CHARGE" in abilities:
            cardvalues.append(1)
        else:
            cardvalues.append(0)

        if "DIVINE_SHIELD" in abilities:
            cardvalues.append(1)
        else:
            cardvalues.append(0)

        if "WINDFURY" in abilities:
            cardvalues.append(1)
        else:
            cardvalues.append(0)

        if "TAUNT" in abilities:
            cardvalues.append(1)
        else:
            cardvalues.append(0)

        if "POISONOUS" in abilities:
            cardvalues.append(1)
        else:
            cardvalues.append(0)

        if "BATTLECRY" in abilities:
            cardvalues.append(1)
        else:
            cardvalues.append(0)

        if "DEATHRATTLE" in abilities:
            cardvalues.append(1)
        else:
            cardvalues.append(0)

        if "RUSH" in abilities:
            cardvalues.append(1)
        else:
            cardvalues.append(0)

        if "COMBO" in abilities:
            cardvalues.append(1)
        else:
            cardvalues.append(0)

        if "DISCOVER" in abilities:
            cardvalues.append(1)
        else:
            cardvalues.append(0)

        if "ELUSIVE" in abilities:
            cardvalues.append(1)
        else:
            cardvalues.append(0)

        if "LIFESTEAL" in abilities:
            cardvalues.append(1)
        else:
            cardvalues.append(0)

        if "REBORN" in abilities:
            cardvalues.append(1)
        else:
            cardvalues.append(0)

        if "SECRET" in abilities:
            cardvalues.append(1)
        else:
            cardvalues.append(0)

        if "STEALTH" in abilities:
            cardvalues.append(1)
        else:
            cardvalues.append(0)

        return cardvalues

    # def find_card_attr(
    #     self, card_container: ResultSet, tag, search_query, default_value
    # ):
    #     return next(
    #         (
    #             x.find(tag).get_text()
    #             for x in card_container
    #             if (x.find("b") != None and x.find("b").get_text() == search_query)
    #         ),
    #         default_value,
    #     )

    def goto_page(self, driver: WebDriver, website_name, waiting_for_tag):
        driver.get(website_name)
        try:
            WebDriverWait(driver, 50).until(
                EC.presence_of_element_located((By.TAG_NAME, waiting_for_tag))
            )
        except Exception as e:
            print("Error:{}".format(e))
            driver.execute_script("window.stop()")
        return

    def accept_cookies(self, driver: WebDriver):
        try:
            WebDriverWait(driver, 50).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//button[@aria-label="Accept"]')
                )
            )
        except Exception as e:
            print("Error:{}".format(e))
            driver.execute_script("window.stop()")
        elem = driver.find_element(By.XPATH, '//button[@aria-label="Accept"]')
        elem.click()
        return

    def search_for_card(self, driver: WebDriver, searchinput, waiting_for_tag):
        # elem = driver.find_element(By.ID, "searchInput")
        elem = driver.find_element(By.CLASS_NAME, "search-app__input")
        # elem.click()
        elem.send_keys(searchinput)
        elem.send_keys(Keys.RETURN)
        try:
            WebDriverWait(driver, 50).until(
                EC.presence_of_element_located((By.TAG_NAME, waiting_for_tag))
            )
        except Exception as e:
            print("Error:{}".format(e))
            driver.execute_script("window.stop()")
        return

    def get_page(self, driver):
        return BeautifulSoup(driver.page_source, "html.parser")

    def get_cardstatistics(self, card, cardname):
        columns = list(
            map(
                lambda x: x.string.lower(),
                card.find_all("figcaption", attrs={"class": "card-name"}),
            )
        )
        index_column = columns.index(cardname.lower())

        in_p_of_decks = card.find(
            "div",
            attrs={
                "aria-describedby": "table1-row{0} table1-column0".format(index_column)
            },
        ).text[:-1]
        avg_copies = str(
            card.find(
                "div",
                attrs={
                    "aria-describedby": "table1-row{0} table1-column1".format(
                        index_column
                    )
                },
            ).text
        ).replace("-", "")
        deck_winrate = str(
            card.find(
                "div",
                attrs={
                    "aria-describedby": "table1-row{0} table1-column2".format(
                        index_column
                    )
                },
            ).text
        ).replace("-", "%")[:-1]
        times_played = card.find(
            "div",
            attrs={
                "aria-describedby": "table1-row{0} table1-column3".format(index_column)
            },
        ).text
        return [in_p_of_decks, avg_copies, deck_winrate, times_played]

    def click_next_page(self, driver: WebDriver):
        try:
            elem = driver.find_element(By.XPATH, '//a[@rel="next"]')
            elem.click()
            return True
        except:
            driver.close()
            return False

    def get_searchquery(self, card):
        ratings_card_link = card.find("a")
        return ratings_card_link.get("href").split("/")[-2]

    def get_rating(self, card):
        return str(card.find("strong").text)

    def get_cardname(self, card):
        return str(card.find("h1").string).replace("…", "...").replace("’", "'")

    # def create_driver(self, firefox_uri):
    def create_driver(self):
        profile = FirefoxProfile()
        # profile.set_preference("javascript.enabled", False)
        # profile.set_preference("app.update.auto", False)
        # profile.set_preference("app.update.enabled", False)
        # profile.set_preference("permissions.default.stylesheet", 2)
        # profile.set_preference("permissions.default.image", 2)

        # options = FirefoxOptions()
        # options.set_preference("javascript.enabled", True)
        # options.set_preference("app.update.auto", False)
        # options.set_preferencprofile = webdriver.FirefoxProfile()
        options = Options()
        # options.add_argument("-headless")
        profile.set_preference(
            "general.useragent.override",
            "Mozilla/5.0 (X11; Linux i686; rv:136.0) Gecko/20100101 Firefox/136.0",
        )
        options.profile = profile

        # profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so','false')
        # profile.set_preference("http.response.timeout", 15)
        # profile.set_preference("dom.max_script_run_time", 15)

        # return webdriver.Firefox(firefox_profile=profile, firefox_binary=binary)
        return Firefox(options=options)


def main():
    winstatlink = "http://hsreplay.net/cards/#gameType=RANKED_WILD&showSparse=yes&text="
    # abilitieslink = "http://hearthstone.fandom.com/wiki/"
    abilitieslink = "http://hearthstone.wiki.gg/wiki/"
    ratingslink = "http://www.hearthstonetopdecks.com/cards/"
    abilitylistlink = "https://hearthstone.fandom.com/wiki/Ability"
    hs_web_search = HSWebSearch(
        winstatlink, abilitieslink, ratingslink, abilitylistlink
    )
    hs_web_search.start_scraping()


if __name__ == "__main__":
    main()
