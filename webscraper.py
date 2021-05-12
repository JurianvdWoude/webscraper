from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import requests

class HSWebSearch():

  def __init__(self, winstats, abilities, ratings) -> None:
      self.hs_winstats_searchpage= winstats
      self.hs_abilities_searchpage = abilities
      self.hs_ratings_searchpage = ratings

  def start_scraping(self):

    driver = self.create_driver()
    driver.get(self.hs_ratings_searchpage)

    WebDriverWait(driver, 100).until(
      EC.title_contains('Hearthstone')
    )

    assert 'Hearthstone' in driver.title

    ratings_url = driver.current_url
    print(ratings_url)

  def create_driver(self, firefox_uri):
    binary = FirefoxBinary(firefox_uri)
    profile = FirefoxProfile()
    profile.set_preference('javascript.enabled', False)
    profile.set_preference("app.update.auto", False)
    profile.set_preference("app.update.enabled", False)

    return webdriver.Firefox(firefox_profile=profile, firefox_binary=binary)

def main():
  winstatlink = "http://hsreplay.net/cards/#gameType=RANKED_WILD&showSparse=yes&text="
  abilitieslink = "http://hearthstone.fandom.com/wiki/"
  ratingslink = "http://www.hearthstonetopdecks.com/cards/"
  hs_web_search = HSWebSearch(winstatlink, abilitieslink, ratingslink)
  hs_web_search.start_scraping()

if __name__ == "__main__":
  main()
