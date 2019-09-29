import pandas as pd
import csv
import re
from flashtext import KeywordProcessor as kp
from nltk.corpus import stopwords
from GetGenericStemNames import StemList


# Using a static output from GetAZDrug Names (DrugFrame) - Drugs.com
# Using a static output from GetDrugNamesFromClinicalTrials - clinicaltrials.gov - AACT Database Connection using PostgreSQL
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
    with open(filename, 'w', encoding="utf-8", newline="\n") as myFile:
        wr = csv.writer(myFile, lineterminator="\n")
        for val in givenList:
            wr.writerow([val])


def CleanText(givenList):
    EngStopWords = list(stopwords.words('english'))
    MyStopWords = ['g', 'kg', 'g/Kg', 'g/kg', 'percentage', 'and', 'placebo', 'therapy', 'test', 'tests', 'surgery',
                   'vitamin', 'Vitamin', 'agent', 'Agents', 'vaccine', 'Vaccine', 'alcohol', 'factor', 'lenses',
                   'System', 'Lens', 'Gland', 'Oral', 'Gene', 'Stress', 'Drug', 'diet', 'acid', 'Drops', 'Soy',
                   'Placebo', 'Single oral dose', 'mg', 'iv infusion', '%',
                   'Exercise', 'A', 'B', 'C', 'D', 'E', '1', '2', 'ix', 'transplant', 'imaging', 'management',
                   'intensity', 'vision', 'ointment', 'fat', 'single', 'implant']
    EngStopWords += MyStopWords
    StopWordDict = {" ": EngStopWords}

    # Setup FlashText
    processor = kp(case_sensitive=False)
    processor.add_keywords_from_dict(StopWordDict)
    givenListUpdated = []

    # Remove the stopwords from this DrugList
    for words in givenList:
        givenValue = " ".join(processor.replace_keywords(val) for val in words.split())
        givenListUpdated.append(givenValue.strip())
    # Remove all numbers before and after text
    givenListUpdated = [re.sub(r'(\s|^)\d.\d*(\s|$)', "", val) for val in givenListUpdated]
    # Remove all extra whitespaces in the result
    givenListUpdated = [" ".join(val.split()) for val in givenListUpdated]
    # Remove everything in brackets
    givenListUpdated = [re.sub(r'(.*?)\s?\(.*?\)', "", val) for val in givenListUpdated]

    # print("Len After Pre-Processing", len(WordListUpdated))
    # Removing empty strings
    EmptyCount = 0
    for val in givenListUpdated:
        if val is "":
            EmptyCount += 1
    if EmptyCount > 0:
        givenListUpdated = [drug for drug in givenListUpdated if drug]

    # Remove Duplicates
    givenListUpdated = RemoveDuplicates(givenListUpdated)
    return givenListUpdated
    # print("Len After Removing Duplicates", len(WordListUpdated))


# Read the csv's into a pandas dataframe
GivenFrame = pd.read_csv('drugs_data.csv')
DrugFrame = pd.read_csv('allDrugs.csv', names=['drugs'])
TrialFrame = pd.read_csv('drugsfromtrials.csv', names=['drugs'])

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
TrialDrugList = TrialFrame['drugs'].tolist()

# Perform text pre-processing on the list
# Replace all instances of weights g,mg,g/Kg,g/kg,percentage to NULL along with the numbers preceeding them
WordListUpdated = CleanText(WordList)
TrialDrugList = [re.sub(r'[(\',)]', '', val) for val in TrialDrugList]

# Extract Generic Name Stems from - https://druginfo.nlm.nih.gov/drugportal/jsp/drugportal/DrugNameGenericStems.jsp
# StemList from GetGenericStemNames script - Contains all stems used in drug nomenclature
# Remove all instances of "-" from StemList
StemList = ' '.join(StemList).replace('-', '').split()
# Check if the stems are present as substrings in WordListUpdated
DrugsFromStemList = [drug for drug in WordListUpdated for stem in StemList if stem in drug]
# Check for drugs from ClinicalTrials.gov
DrugsCheck = DrugList + TrialDrugList + DrugsFromStemList
DrugsList1 = []
DrugsList2 = []
# The givenList may contain shortened drug names Check for eg. Prolia in Prolia(Denosumab)
DrugsList1 = Find_FlashText(WordListUpdated, DrugsList1, DrugsCheck)
# The DrugList may contain shortened drug names Check for eg. Prolia(Denosumab) in Prolia
DrugsList2 = Find_FlashText(DrugsCheck, DrugsList2, WordListUpdated)
DrugsFinalList = DrugsList1 + DrugsList2
DrugsFinalList = RemoveDuplicates(DrugsFinalList)
print("Total Drugs Found:", len(DrugsFinalList))
# Writing Results to a CSV
Write2CSV('output.csv', DrugsFinalList)
