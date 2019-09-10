from bs4 import BeautifulSoup
import requests
import csv
from my_fake_useragent import UserAgent

# Mimic the access to the website like a browser
ua = UserAgent(family='chrome')
BrowserUserAgent = ua.random()

# Define URL and Requests object
f = csv.writer(open('drug-names.csv', 'w'))
f.writerow(['Name'])
pages = []
headers = BrowserUserAgent

firstAlphaNumeric = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                     'u', 'v', 'w', 'x', 'y', 'z', '0-9','']
# secondAlphaNumeric = firstAlphaNumeric
finalList = []

for first in firstAlphaNumeric:
    for second in firstAlphaNumeric:
        url = 'https://www.drugs.com/alpha/' + str(first) + str(second) + '.html'
        pages.append(url)

for item in pages:
    page = requests.get(item, headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    for ultag in soup.find_all('ul', {'class': 'ddc-list-column-2'}):
        for litag in ultag.find_all('li'):
            finalList.append(litag.text)

print("Total Number of Drugs Scrapped From Drugs.Com", len(finalList))

# Writing Results to a CSV
with open('allDrugs1.csv', 'w', encoding="utf-8", newline="\n") as myFile:
    wr = csv.writer(myFile, lineterminator="\n")
    for drugs in finalList:
        wr.writerow([drugs])
