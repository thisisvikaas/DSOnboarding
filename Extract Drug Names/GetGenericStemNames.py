from bs4 import BeautifulSoup
import requests

# Define URL and Requests object

url = 'https://druginfo.nlm.nih.gov/drugportal/jsp/drugportal/DrugNameGenericStems.jsp'
page = requests.get(url)

# Create a Beautiful Soup Object
soup = BeautifulSoup(page.text, 'html.parser')

# Get into inspect element of the URL and find the class of the table ; Pull all text from the table stemTable
DrugStemList = soup.find(class_='stemTable')
DrugStem = DrugStemList.find_all('a')

StemList = []
# Get all stems into stemList
for val in DrugStem:
    stems = val.contents[0]
    StemList.append(stems)
