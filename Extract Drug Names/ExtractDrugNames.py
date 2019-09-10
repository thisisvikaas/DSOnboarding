import pandas as pd
import csv
import re
from flashtext import KeywordProcessor as kp
from nltk.corpus import stopwords
from GetGenericStemNames import StemList


# Using a static output from GetAZDrug Names (DrugFrame) - Drugs.com Blocks IP addresses when we repeatedly try to scrap
# from GetAZDrugNames import finalList
# If nltk corpous does not exist, uncomment the next line to download corpus
# nltk.download()

# Remove Duplicates Function
def RemoveDuplicates(givenList):
    return list(dict.fromkeys(givenList))


def FlattenList(givenList):
    givenList = [item for sublist in givenList for item in sublist]
    return givenList


def Find_FlashText(myList, givenList, givenKeywords):
    processor = kp(case_sensitive=False)
    processor.add_keywords_from_list(givenKeywords)
    givenList = [processor.extract_keywords(val) for val in myList]
    # Convert the nested list output to a flat list
    givenList = FlattenList(givenList)
    givenList = RemoveDuplicates(givenList)
    return givenList


def Write2CSV(filename, givenList):
    with open(filename, 'w') as myFile:
        wr = csv.writer(myFile, lineterminator="\n")
        for val in givenList:
            wr.writerow([val])


# Read the csv's into a pandas dataframe
GivenFrame = pd.read_csv('drugs_data.csv')
DrugFrame = pd.read_csv('allDrugs.csv', names=['drugs'])

# Find the count and unique elements
if len(GivenFrame) == len(GivenFrame.drugs.unique()):
    # print("No duplicate values")
    FinalDataFrame = GivenFrame
else:
    # print("Duplicate Values Exist")
    FinalDataFrame = GivenFrame.drop_duplicates(subset={"drugs"}, keep='first', inplace=False)
    # print("Unique elements in the final df:", FinalDataFrame.shape)
    # Check to see how much % of data remains after removing duplicates
    # print(int(FinalDataFrame.size) / int(GivenFrame.size)) * 100

# Change the dataframe object into a list object
WordList = FinalDataFrame['drugs'].tolist()
DrugList = DrugFrame['drugs'].tolist()

# Perform text pre-processing on the list
# Replace all instances of weights g,mg,g/Kg,g/kg,percentage to NULL along with the numbers preceeding them
EngStopWords = list(stopwords.words('english'))
MyStopWords = ['g', 'kg', 'g/Kg', 'g/kg', 'percentage', 'and', 'placebo', 'therapy', 'test', 'tests', 'surgery',
               'vitamin', 'Vitamin', 'agent', 'Agents', 'vaccine', 'Vaccine', 'alcohol', 'factor', 'lenses', 'System',
               'Lens', 'Gland', 'Oral', 'Gene', 'Stress', 'Drug', 'diet', 'acid', 'Drops', 'Soy']
EngStopWords += MyStopWords
StopWordDict = {" ": EngStopWords}

# Setup FlashText
processor = kp(case_sensitive=False)
processor.add_keywords_from_dict(StopWordDict)
WordListUpdated = []

# Remove the stopwords from this DrugList
for words in WordList:
    WordValue = " ".join(processor.replace_keywords(val) for val in words.split())
    WordListUpdated.append(WordValue.strip())
# Remove all numbers before and after text
WordListUpdated = [re.sub(r'(\s|^)\d.\d*(\s|$)', "", val) for val in WordListUpdated]
# Remove all extra whitespaces in the result
WordListUpdated = [" ".join(val.split()) for val in WordListUpdated]
# print("Len After Pre-Processing", len(WordListUpdated))
# Removing empty strings
EmptyCount = 0
for val in WordListUpdated:
    if val is "":
        EmptyCount += 1
if EmptyCount > 0:
    WordListUpdated = [drug for drug in WordListUpdated if drug]

# Remove Duplicates
WordListUpdated = RemoveDuplicates(WordListUpdated)
# print("Len After Removing Duplicates", len(WordListUpdated))

# Extract Generic Name Stems from - https://druginfo.nlm.nih.gov/drugportal/jsp/drugportal/DrugNameGenericStems.jsp
# StemList from GetGenericStemNames script - Contains all stems used in drug nomenclature
# Remove all instances of "-" from StemList
StemList = ' '.join(StemList).replace('-', '').split()
# Check if the stems are present as substrings in WordListUpdated
DrugsFromStemList = [drug for drug in WordListUpdated for stem in StemList if stem in drug]
# There can be noise too included in this process hence check with the Drugs List Present
DrugsFromStemList1 = []
DrugsFromStemList2 = []
DrugsFromStemList1 = Find_FlashText(DrugList, DrugsFromStemList1, DrugsFromStemList)
DrugsFromStemList2 = Find_FlashText(DrugsFromStemList, DrugsFromStemList2, DrugList)
DrugsFromStemList = DrugsFromStemList1 + DrugsFromStemList2
DrugsFromStemList = RemoveDuplicates(DrugsFromStemList)

# The givenList may contain shortened drug names Check for eg. Prolia in Prolia(Denosumab)
DrugsFromDrugsList = set(WordListUpdated).difference(DrugsFromStemList)
DrugsFromDrugsList = Find_FlashText(DrugsFromDrugsList, DrugsFromDrugsList, DrugList)

# The DrugList may contain shortened drug names Check for eg. Prolia in Prolia(Denosumab)
CombinedList = DrugsFromStemList + DrugsFromDrugsList
DrugsListFromDrugs = list(set(WordListUpdated).difference(CombinedList))
DrugsListFromDrugs = Find_FlashText(DrugList, DrugsListFromDrugs, DrugsListFromDrugs)

# Combined Final Result
finalList = DrugsFromStemList + DrugsFromDrugsList + DrugsListFromDrugs
finalList = RemoveDuplicates(finalList)
print("Total Drugs Found:", len(finalList))

# Writing Results to a CSV
Write2CSV('output.csv', finalList)
