import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import json


def get_acrs(filename):
    accrs = []
    with open(filename, 'r') as acrsfile:
        for entry in acrsfile.readlines():
            accrs.append(entry.strip())
    acrsfile.close()
    return accrs

def generate_card_deck_URLs(acr):
    website_paper = 'https://www.mtggoldfish.com/index/{}#paper'.format(acr)
    website_foil = 'https://www.mtggoldfish.com/index/{}_F#paper'.format(acr)
    return website_paper, website_foil

def parse_deck_page(URL):
    # https://www.mtggoldfish.com/index/LEA#paper
    result = requests.session().get(URL, timeout=60)
    if (result.status_code != 200):
        print (str(result.status_code)+' error: '+URL)
        return None
    
    cards_data = []
    cardFoil = int('_F#paper' in URL)
    html_source = result.text
    soup = BeautifulSoup(html_source, 'html.parser')
    table = soup.find('tbody')
    for row in table.find_all('tr'):
        values = row.find_all('td')
        cardName = values[0].text
        cardURL = values[0].find('a').get('href')
        cardSet = values[1].text
        cardRarity = values[2].text
        # print (cardName, cardURL, cardSet, cardFoil, cardRarity)
        card_dict = {
            'Name': cardName,
            'URL': cardURL,
            'Set': cardSet,
            'Foil': cardFoil,
            'Rarity': cardRarity
        }
        cards_data.append(card_dict)
    return cards_data

def parse_card_page(card_dict):
    URL = 'https://www.mtggoldfish.com{}'.format(card_dict['URL'])
    result = requests.session().get(URL, timeout=60)
    if (result.status_code != 200):
        print (str(result.status_code)+' error: '+URL)
        return None
    
    html_source = result.text
    histroty_data_raw = html_source.split('var d = "Date,')[1].split('g = new Dygraph')[0].strip()
    # print (histroty_data_raw[:500])
    histroty_data_splits = histroty_data_raw.split(';')
    # print (histroty_data_splits)
    pattern = 'd += "\\n'
    data_dict = {
        'Name of Card': card_dict.get('Name'),
        'Set': card_dict.get('Set'),
        'Foil or Not': card_dict.get('Foil'),
        'Rarity': card_dict.get('Rarity')
    }
    for entry in histroty_data_splits:
        if pattern in entry:
            res = entry.split(pattern)[1].split('"')[0].split(', ')
            date = res[0]
            value = res[1]
            data_dict.update({date: value})
    
    return data_dict

def save_card_data_to_json(data_dict):
    outputFile = 'data/{}-{}-{}.json'.format(data_dict['Set'], data_dict['Name of Card'].replace('/', ''), data_dict['Foil or Not'])
    with open(outputFile, 'w') as fp:
        json.dump(data_dict, fp, indent=4, ensure_ascii=False)
    fp.close()

def main():
    for acr in get_acrs('acrs.txt'):
        for url in generate_card_deck_URLs(acr):
            # print (url)
            cards_data = parse_deck_page(url)
            if cards_data:
                for card_data in cards_data:
                    print (datetime.now(), card_data['Set'], card_data['Name'])
                    data_dict = parse_card_page(card_data)
                    time.sleep(3)
                    save_card_data_to_json(data_dict)


if __name__ == "__main__":
    main()