from math import log
import nltk
from nltk.corpus import stopwords
import re
import os
import json


def preprocessing(filename):
    global collectionDictionary
    collectionDictionary = {}
    file = open(filename, "r")
    lines = file.readlines()
    global index_terms
    global index_terms_with_space
    global arrayLines
    global docNumbers
    docNumbers = []
    index_terms = []
    index_terms_with_space = []
    arrayLines = []

    for line in lines:
        if "<DOC>" in line:
            line = line.lower()
            clean = re.compile('<.*?>')
            line = re.sub(clean, '', line)
            line = re.sub(r'[^\w\s]', '', line)
            line = re.sub(r'\d+', '', line)
            key = filename.replace("coll\\", "")
            # docNumbers.append(key)
            # print(docNumbers)
        else:
            if "<DOCNO>" in line:
                clean = re.compile('<.*?>')
                line = re.sub(clean, '', line)
                line = line.strip()
                key = line
                docNumbers.append(key)
                # print(docNumbers)
                collectionDictionary[key] = []
                index_terms = []
            if "<DOCNO>" not in line:
                line = line.lower()
                clean = re.compile('<.*?>')
                line = re.sub(clean, '', line)
                line = re.sub(r'[^\w\s]', '', line)
                line = re.sub(r'\d+', '', line)
                # print(line)
                arrayLines.append(line)
                words = nltk.word_tokenize(line)
                stop_words = set(stopwords.words('english'))
                index_terms.append([w for w in words if not w in stop_words])
                index_terms_with_space.append(
                    [w for w in words if not w in stop_words])  # This is ONLY for indexing() | Read Below
                # I did this because in index_terms, [] are being removed.
                # Example: Line 0 = [] , Line 1 = ['ap'] | <--- Original index_terms replaces Line 0 with Line 1 aka Line 0 = ['ap']
                # This clearly does not work with indexing if you are not syncing per line with the correct number
                # And will Cause word's dissappearance during indexing ,
                # print("Line: " + str(i) + str(index_terms[i])), #print("Line: " + str(i) + str(index_terms_with_space[i])) <-- Use this to understand the difference in indexing()
                index_terms = [ele for ele in index_terms if ele != []]
                for s in range(len(index_terms)):
                    for j in range(len(index_terms[s])):
                        # print(index_terms[s][j])
                        collectionDictionary[key].append(index_terms[s][j])
    # print(ele)
    # print(index_terms) //Print THIS TO CHECK TOKENED TERMS
    # print(collectionDictionary["AP880212-0001"])
    # print(collectionDictionary["AP880212-0002"])
    # return index_terms


def indexing():
    global dictIndex
    dict = {}
    for i in range(len(arrayLines)):
        check = arrayLines[i]
        # print("Line: " + str(i) + str(index_terms[i])) <--- Look desc above
        for item in index_terms_with_space[i]:  # Loop over index_terms
            if item in check:  # If check (current Line) includes words in index_terms | Cannot use reduced spaces , or else syncing will be off
                if item not in dict:  # If word never in hashmap
                    dict[item] = []  # Create Line List
                if item in dict:  # If word exist in hashmap
                    dict[item].append(i + 1)  # Append Line Number , + 1 is needed because i starts from 0
    # print(dict)
    dictIndex = dict
    # print(dictIndex)
    return dictIndex


def ReadAndloop():
    directory = 'coll'
    global filenames
    filenames = []
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            filenames.append(f)


def ranking():
    file = open("queries.txt", "r")
    lines = file.readlines()
    query_words = {}
    count = 0
    counter = 0
    query_words[0] = []
    for line in lines:
        if "<num>" in line:
            count = count + 1
        line = line.lower()
        line = line.strip()
        clean = re.compile('<.*?>')
        line = re.sub(clean, '', line)
        line = re.sub(r'[^\w\s]', '', line)
        if line.isnumeric() == True:
            counter += 1
            query_words[counter] = []
        line = re.sub(r'\d+', '', line)
        if line.isnumeric() == False:

            words = nltk.word_tokenize(line)
            words = [ele for ele in words if ele != []]

            if words != []:
                for i in range(len(words)):
                    query_words[counter].append(words[i])

    # print(query_words)
    return query_words


def termFrequency(term, doc):
    global tf_value
    term_in_document = 0
    normalizeTermFreq = collectionDictionary[doc]
    term = term.lower()
    if (term in normalizeTermFreq):
        term_in_document += 1
    if (term_in_document == 0):
        return 0
    len_of_document = float(len(normalizeTermFreq))
    tf_value = term_in_document / len_of_document

    return tf_value


def inverseDocumentFrequency(term):
    global idf_val
    term_num = 0
    if term in allInverted:
        term_num = len(allInverted[term])
        if term_num > 0:
            total_num_docs = len(docNumbers)
            idf_val = log(float(total_num_docs) / term_num)
            return idf_val
    else:
        return 0


def retrievalnRanking(tf, idf):
    wiq = tf * idf
    return wiq


def main():
    global allInverted
    allInverted = {}
    result = {}
    ReadAndloop()
    for file in filenames:
        preprocessing(file)
        # file = "coll\\AP880212"
        # preprocessing("coll\\AP880212")
        temp = indexing()
        fixedFileName = file.replace("coll\\", "")
        for key in temp:
            if key in allInverted:
                allInverted[key].append([fixedFileName, "Line:" + str(temp[key])])
            if key not in allInverted:
                allInverted[key] = [fixedFileName, "Line:" + str(temp[key])]

        # print(allInverted) #<-- Print Result Here
        Query_Dictionary = ranking()
        # print(Query_Dictionary)
        for i in range(len(Query_Dictionary)):
            if Query_Dictionary[i] != []:
                for j in range(len(docNumbers)):
                    wordIndex = 0
                    if wordIndex < len(Query_Dictionary[i]):
                        tf = termFrequency(Query_Dictionary[i][wordIndex], docNumbers[j])
                        # print(tf)
                        idf = inverseDocumentFrequency(Query_Dictionary[i][wordIndex])
                        # print("idf:" , idf)
                        if (tf and idf != 0):
                            # print("tf: " + str(tf) + "idf: " + str(idf))
                            # if retrievalnRanking(tf,idf) and retrievalnRanking(tf,idf):
                            if i not in result:
                                result[i] = []
                            wqAndDocNumber = {}
                            wqAndDocNumber[(retrievalnRanking(tf, idf))] = {docNumbers[j]}
                            result[i].append(wqAndDocNumber)
                        wordIndex += 1
    rearrange = list(result.keys())
    rearrange.sort()
    result = {i: result[i] for i in rearrange}
    with open("Results.txt", 'w') as f:
        for key, value in result.items():
            count = 1
            for x in value:
                f.write(str(key) + ' Q0 ' + str(x).strip('{}').replace(': {',' ').strip("'").replace("'","")+ " " + str(count) + ' q'+ str(key) + 'r' + str(count) + '\n' )
                count = count + 1

    print(result)

    # print(Query_Dictionary)

    # print(len(collectionDictionary))
    # for i in range(len(Query_Dictionary)):
    #     for j in range(len(Query_Dictionary[i])):
    #         termFrequency(Query_Dictionary[i][j], doc)


if __name__ == "__main__":
    main()

# Query_Dictionary: Words in Query File and split by num
# dictIndex: Current File Word as Key and show lines that appeared in the document
# allinverted - words as key , show filename then which line