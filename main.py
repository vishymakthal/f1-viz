import html5lib
import logging
import re
import requests
from bs4 import BeautifulSoup

log = logging.Logger(__name__, level=logging.INFO)

def get_soup(url):

    r = requests.get(url)
    if r.status_code != 200:
        log.error(f'status code: {r.status_code} [{r.reason}]')
        return None
    soup = BeautifulSoup(r.text, 'html5lib')
    return soup

def parse_results(season):
    soup = get_soup(f'https://en.wikipedia.org/wiki/{season}_Formula_One_World_Championship')

    # grab driver result table
    ddc_table = soup.find_all('table', class_='wikitable')[-4]
    rows = ddc_table.tbody.find_all('tr')

    with open(f'results_{season}.csv', 'w') as f:
        f.write('Driver,' + ','.join(map(lambda x: x.a.text, rows[0].find_all('th')[2:-1]))+'\n')

    for row in rows[1:-2]:
        cells = row.find_all('td')
        f.write(cells[0].find_all('a')[1].text + ',' + ','.join(map(lambda x: x.text.rstrip(), cells[1:]))+'\n')

def get_points(season):

    if season < 2010:
        return {
            '1' : 10,
            '2' : 8,
            '3' : 6,
            '4' : 5,
            '5' : 4,
            '6' : 3,
            '7' : 2,
            '8' : 1
        }
    
    return {
        '1' : 25,
        '2' : 18,
        '3' : 15,
        '4' : 12,
        '5' : 10,
        '6' : 8,
        '7' : 6,
        '8' : 4,
        '9' : 2,
        '10' : 1
    }

def tally_results(season):

    points = get_points(season) 
    soup = get_soup(f'https://en.wikipedia.org/wiki/{season}_Formula_One_World_Championship')

    # grab driver result table
    ddc_table = soup.find_all('table', class_='wikitable')[-4]
    rows = ddc_table.tbody.find_all('tr')
    print('==' + str(season) + '==')
    with open(f'tallies/tally_{season}.csv', 'w') as f:

        races = map(lambda x: x.a.text, rows[0].find_all('th')[2:-1])
        f.write('Driver,' + ','.join(races)+'\n')
        for row in rows[1:-2]:
            tally = []
            cells = row.find_all('td')

            driver = cells[0].find_all('a')[1].text
            
            if season < 2018:
                finishes = cells[1:]
            else:
                finishes = cells[1:-1]


            for res in finishes:
                place = res.text.rstrip()
                if 'F' in place or 'P' in place:
                    place = place.replace('P','') 
                    place = place.replace('F','')
                
                pts = points.get(place, 0)
                if 'F' in res.text.rstrip() and pts > 0:
                    pts += 1
                
                if tally:
                    tally.append(tally[-1] + pts)
                else:
                    tally.append(pts)

            if not tally[-1] == int(cells[-1].text):
                print(driver)
            
            f.write(driver + ',' + ','.join(map(lambda x: str(x), tally)) + '\n')

def main():

    log.info("starting up")
    for season in range(2019,2021):
        # parse_results(season)
        tally_results(season)
    

if __name__ == '__main__':
    main()