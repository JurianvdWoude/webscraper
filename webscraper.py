from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import csv
import re

class HSWebSearch():

  def __init__(self, winstats, abilities, ratings, abilitylist) -> None:
      self.hs_winstats_searchpage= winstats
      self.hs_abilities_searchpage = abilities
      self.hs_ratings_searchpage = ratings
      self.hs_abilitylist_page = abilitylist

  def start_scraping(self):
    
    driver = self.create_driver()
    index = 0

    # self.goto_page(driver, self.hs_winstats_searchpage + 'Blood of the Ancient One', 'figcaption')
    # stats_page = self.get_page(driver)
    # statistics = self.get_cardstatistics(stats_page, 'Blood of the Ancient One')
    # return

    self.goto_page(driver, self.hs_abilitylist_page, 'a')
    abilitylist_page = self.get_page(driver)
    abilitylist = self.get_list_of_possible_abilities(abilitylist_page)


    csv_labels = ['Index', 'CardName', 'Rating', 
      'InPrcntOfDecks', 'AvgCopies', 'DeckWinratePrcnt', 
      'TimesPlayed', 'Set', 'CardType', 'MinionType' 'Class', 
      'Rarity', 'Cost', 'Attack', 'Health', 'Durability'] + abilitylist


    csv_data = []

    go_to_next_page = True

    self.goto_page(driver, self.hs_ratings_searchpage, 'strong')

    

    while go_to_next_page:
      ratingspage_page = self.get_page(driver)
      
      ratingspage_cards_url = driver.current_url
      ratingspage_cards = ratingspage_page.find('div', attrs={'class': 'row aligned-row'}).find_all('div', attrs={'class': 'card-item'})

      for ratingspage_card in ratingspage_cards:
        index += 1
        rating = self.get_rating(ratingspage_card)
        searchname = self.get_searchquery(ratingspage_card)

        self.goto_page(driver, self.hs_ratings_searchpage + searchname, 'h1')
        card_page = self.get_page(driver)
        cardname = self.get_cardname(card_page)
        print('\nAdding card nr. {0}: {1}'.format(index, cardname))
        self.goto_page(driver, self.hs_winstats_searchpage + cardname, 'figcaption')


        stats_page = self.get_page(driver)
        statistics = self.get_cardstatistics(stats_page, cardname)
        self.goto_page(driver, self.hs_abilities_searchpage + cardname, 'tbody')
        abilities_page = self.get_page(driver)
        abilities = self.get_abilities(abilities_page, abilitylist)
        datarow = [str(index)] + [cardname] + [rating] + statistics + abilities
        csv_data.append(datarow)
        print('Appended {0} values to the HS data:\n{1}'.format(len(datarow), datarow))
        # print(len(csv_data))

      self.goto_page(driver, ratingspage_cards_url, 'div')
      print('\nStored {} values in total!'.format(len(csv_data)))
      go_to_next_page = self.click_next_page(driver)
      
      if(go_to_next_page):
        print('\n=-( Next page )->\n')
        print('-=-'*10)
      else:
        print('\nDone scraping!')
      

    print('Putting data into a csv file...')

    self.write_csv_file('hearthstone_cards.csv', csv_labels, csv_data)

    print('~ Finished! ~')


  def write_csv_file(self, filename, labels, data):
    with open(filename, 'w', newline='') as csvfile:
      csvwriter = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
      csvwriter.writerow(labels)
      csvwriter.writerows(data)
  
  def get_list_of_possible_abilities(self, page):
    
    abilities = []
    abilities_div = page.find('div', attrs={'id': 'toc'})

    for ability in abilities_div.find_all('li', attrs={'class': 'toclevel-2'}):
      abilities.append(ability.find('span', attrs={'class': 'toctext'}).text)
    return abilities[:-1]

  def get_abilities(self, card, abilitylist):
    
    card_infobox = card.find('div', attrs={'class': 'stdinfobox'})
    card_container = card_infobox.find_all('tr')



    card_set = self.find_card_attr(card_container, 'a', 'Set:', '')
    card_type = self.find_card_attr(card_container, 'a', 'Type:', '')
    card_miniontype = self.find_card_attr(card_container, 'a', 'Minion type:', '')
    card_class = self.find_card_attr(card_container, 'a', 'Class:', '')
    card_rarity = self.find_card_attr(card_container, 'span', 'Rarity:', '')
    card_cost = int(re.findall('[0-9]+',self.find_card_attr(card_container, 'td', 'Cost:', '0'))[0])
    card_attack = int(re.findall('[0-9]+',self.find_card_attr(card_container, 'td', 'Attack:', '0'))[0])
    card_health = int(re.findall('[0-9]+',self.find_card_attr(card_container, 'td', 'Health:', '0'))[0])
    card_durability = int(re.findall('[0-9]+',self.find_card_attr(card_container, 'td', 'Durability:', '0'))[0])

    cardvalues = [card_set, card_type, card_miniontype, card_class, card_rarity, card_cost, card_attack, card_health, card_durability]

    if card_container[-3].find('b').string == 'Abilities:':
      abilities = card_container[-3].find_all('a')
    elif card_container[-2].find('b').string == 'Abilities:':
      abilities = card_container[-2].find_all('a')
    else:
      abilities = []

    for ability in abilitylist:
      if ability in map(lambda x: x.string, abilities):
        cardvalues.append(1)
      else:
        cardvalues.append(0)

    return cardvalues

  def find_card_attr(self, card_container: ResultSet, tag, search_query, default_value):
    return next((x.find(tag).get_text() for x in card_container if x.find('b') != None and x.find('b').get_text() == search_query), default_value)
  
  def goto_page(self, driver: WebDriver, website_name, waiting_for_tag):
    driver.get(website_name)
    try:
      WebDriverWait(driver, 50).until(
        EC.presence_of_element_located((By.TAG_NAME, waiting_for_tag))
      )
    except Exception as e:
      print('Error:{}'.format(e))
      driver.execute_script('window.stop()')
    return

  def get_page(self, driver):
    return BeautifulSoup(driver.page_source, 'html.parser')

  def get_cardstatistics(self, card, cardname):
    columns = list(map(lambda x: x.string.lower(), card.find_all('figcaption', attrs={'class': 'card-name'})))
    index_column = columns.index(cardname.lower())

    in_p_of_decks = card.find('div', attrs={'aria-describedby': 'table1-row{0} table1-column0'.format(index_column)}).text[:-1]
    avg_copies = str(card.find('div', attrs={'aria-describedby': 'table1-row{0} table1-column1'.format(index_column)}).text).replace('-', '')
    deck_winrate = str(card.find('div', attrs={'aria-describedby': 'table1-row{0} table1-column2'.format(index_column)}).text).replace('-', '%')[:-1]
    times_played = card.find('div', attrs={'aria-describedby': 'table1-row{0} table1-column3'.format(index_column)}).text
    return [ in_p_of_decks, avg_copies, deck_winrate, times_played ]
  
  def click_next_page(self, driver: WebDriver):
    try:
      elem = driver.find_element_by_xpath('//a[@rel="next"]')
      elem.click()
      return True
    except:
      driver.close()
      return False

  def get_searchquery(self, card):
    ratings_card_link = card.find('a')
    return ratings_card_link.get('href').split('/')[-2]

  def get_rating(self, card):
    return str(card.find('strong').text)
  
  def get_cardname(self, card):
    return str(card.find('h1').string).replace("…", "...").replace("’", "'")


  def create_driver(self, firefox_uri):
    binary = FirefoxBinary(firefox_uri)
    profile = FirefoxProfile()
    profile.set_preference('javascript.enabled', False)
    profile.set_preference("app.update.auto", False)
    profile.set_preference("app.update.enabled", False)
    profile.set_preference('permissions.default.stylesheet', 2)
    profile.set_preference('permissions.default.image', 2)
    # profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so','false')
    # profile.set_preference("http.response.timeout", 15)
    # profile.set_preference("dom.max_script_run_time", 15)

    return webdriver.Firefox(firefox_profile=profile, firefox_binary=binary)

def main():
  winstatlink = "http://hsreplay.net/cards/#gameType=RANKED_WILD&showSparse=yes&text="
  abilitieslink = "http://hearthstone.fandom.com/wiki/"
  ratingslink = "http://www.hearthstonetopdecks.com/cards/"
  abilitylistlink = "https://hearthstone.fandom.com/wiki/Ability"
  hs_web_search = HSWebSearch(winstatlink, abilitieslink, ratingslink, abilitylistlink)
  hs_web_search.start_scraping()

if __name__ == "__main__":
  main()
