#Project program script - takes input of word to find (and what to call your output data file), finds each line in each file the word occurs at least once in, and writes a csv file of that
import os
import numpy as np
import nltk
from nltk.corpus import stopwords
import re
import spacy
import matplotlib
import matplotlib.pyplot as plt
import pandas
import sys
import csv
import xlrd

SPACY_MODEL = spacy.load("en_core_web_lg")
N_WORDS = int(sys.argv[1]) #IMPORTANT!! Command line arguement to set number of words. Suggested = 12 or however many swear words you use

#aggregate swear word dictionary
WORD_LINES = {}
WORD_COUNTS ={}
WORD_OF_INTEREST = str(input("please type a word to get lines for: "))

MY_STOPWORDS = ["?","!" ,"@" ,"," ,"-" ,"(", ")" ,"[", "]", ";", ":", "?", ",",'']

def get_file_names(): #names of all files that are English transcripts to be used later
    files_list = []
    current_wd = os.getcwd()
    os.chdir(current_wd+"/workbooks")
    files = os.listdir()
    for file in files:
        if file[0] != '.' and file[0] == 'E': #don't want the .DS store thing or any of the output csvs if you've already run this
            files_list.append(file)
    return files_list

def create_TextFile_classes(files_list):
    file_class_list = []
    for file in files_list:
        file_name = file
        file_class = TextFile(file_name)
        file_class_list.append(file_class)
    return file_class_list

def clean_up(text_file):
    text = text_file.strip("\n")
    text = text.replace('\\','') #could't make this work with regular expressions, got a bad escape error
    #text = ' '.join(word.strip(string.punctuation) for word in text_input.split())
    text = re.sub("[\(\[\{].*?[\)\]\}\]]", "", text) #removing everything in brackets, parenthese, or curly brackets
    text = re.sub("[\{.*?}]","",text)
    text = re.sub("[［].*?[］]","", text)
    text = re.sub("[[].*?[]]","", text)
    text = re.sub("[【].*?[】]","", text)
    text = re.sub("[[].*?[]]","",text)
    text = re.sub("[【].*? [】]]","",text)
    text = re.sub("[\[\［\[\【\「\[].*?[\]\】\]\］\」\］]","",text)
    text = re.sub("[｛].*?[］]","",text)
    text = re.sub("[\(\（].*?[\）\）]","",text)
    text = re.sub("[\｛].*?[\｝]","",text)
    #set of characters, starts with one of the opening brackets or parentheses, and then has any characters repeated any number of times (.*)
    text = re.sub("\**","", text) #removing any number of sequential stars
    text = re.sub("[\…\#X]","", text) #this … shows up sometimes, is different from ...
    #text = re.sub("[f,m,s,v,s,b,c,t,S]{3,}","", text) #coding scheme indicating another language
    text = re.sub("'","'",text) #??? what is that first character doing
    text = re.sub("\."," ", text)
    text = re.sub("。","",text)
    text = re.sub("sss","",text)
    text = re.sub("xpp","",text)
    text = re.sub("xpx","",text)
    text = re.sub("xmm","",text)
    text = re.sub("jjj","",text)
    text = re.sub("jxj","",text)
    text = re.sub("fxf","",text)
    text = re.sub("mmm","",text)
    text = re.sub("mxm","",text)
    text = re.sub("bbb","",text)
    text = re.sub("vvv","",text)
    text = re.sub("ccc","",text)
    text = re.sub("xkx","",text)
    text = re.sub("kxk","",text)
    text = re.sub("xaa","",text)
    text = re.sub("xax","",text)
    text = re.sub("rrr","",text)
    text = re.sub("txt","",text)
    text = re.sub("xtt","",text)
    text = re.sub("ttt","",text)
    text = re.sub("SSS","",text)
    text = re.sub("fff","",text)
    text = re.sub("aaa","",text)
    text = re.sub("eee","",text)
    text = re.sub("xjx","",text)
    text = re.sub("xxss","",text)
    text = re.sub("xss","",text)
    text = re.sub("mmx","",text)
    text = re.sub("xvx","",text)
    text = re.sub("xvv","",text)
    text = re.sub("xff","",text)
    text = re.sub("xsx","",text)
    text = re.sub("sxs","",text)
    text = re.sub("sss","",text)
    text = re.sub(":","",text)
    text = re.sub("!","",text)
    text = re.sub("/","",text)
    text = re.sub("bxb","",text)
    text = re.sub("\n","", text) #removes newline characters because for some reason that was still an issue even with the first line
    text = re.sub('"*',"",text) #removes multiple quotation characters
    text = re.sub("\s+"," ", text) #removes multiple spaces and replaces with one space
    text = re.sub("\?","",text)
    text = re.sub("é","",text)
    text = re.sub("õ", "'", text)
    text = re.sub(",","",text)
    text = re.sub("’","'", text)
    text = re.sub("[xx]{2,}","", text) #removing any number of sequential xs
    text = re.sub(" ss"," ",text)
    text = re.sub(" - "," ",text)
    tokenized_text = text.split(" ")
    final = [word.lower() for word in tokenized_text if word not in MY_STOPWORDS]
    return final

def list_to_string(list_of_words): #turning single lists into strings
    text_string = ""
    for word in list_of_words:
        text_string = text_string + word + " "
    return text_string

def list_list_to_string(list_of_lists): #THIS IS DIFFERENT FROM THE ONE ABOVE
    text_string = ""
    for individual_list in list_of_lists:
        for i in range(len(individual_list)):
            text_string = text_string + individual_list[i] + " "
    return text_string#sorry for the horrible naming conventions but this is for a list of lists, the function above is for single lists

def lemma_csv_writer(tagged_text, lemma_data_dict, output_file_name):
    counts_list = list(lemma_data_dict.values())
    counts_sum = np.sum(counts_list) #should be same as word level
    with open(output_file_name,"w",newline="") as f:
        thewriter = csv.writer(f)
        thewriter.writerow(["word","part of speech","count","fraction"])
        for word in tagged_text: #for each word that got tagged
            lemma_count = lemma_data_dict[word.lemma_] #get the count of that lemma from the dictionary that stored lemmas and their counts
            thewriter.writerow([word.lemma_,word.pos_,lemma_count,int(lemma_count)/float(counts_sum)])

def catchall_csv_writer(dictionary, file_name, label_list):
    counts_list = list(dictionary.values())
    counts_sum = np.sum(counts_list)
    with open(file_name,"w",newline="") as f:
        thewriter = csv.writer(f)
        thewriter.writerow(label_list)
        for item in dictionary.items():
            thewriter.writerow([item[0],item[1],int(item[1])/float(counts_sum)])

def bigram_csv_writer(bigram_data_dict, output_file_name):
    counts_list = list(bigram_data_dict.values())
    counts_sum = np.sum(counts_list)
    with open(output_file_name,"w",newline="") as f:
        thewriter = csv.writer(f)
        thewriter.writerow(["word","count","fraction"])
        for item in bigram_data_dict.items():
            thewriter.writerow([item[0],item[1],int(item[1])/float(counts_sum)])

def get_csv_files():
    file_list = []
    for file in os.listdir():
        if file [-4:] == ".csv":
            file_list.append(file)
    #print(file_list)
    return file_list

def nested_dictionary_csv_writer(dictionary, file_name, label_list):
    #key is the file name
    #value is the dictionary with the lines the target word appeared in
    with open(file_name,"w",newline="") as f:
        thewriter = csv.writer(f)
        thewriter.writerow(label_list)
        for item in dictionary.items():
            file_name = item[0]
            inner_dictionary = item[1]
            for kvp in inner_dictionary.items():
                row_number = kvp[0]
                words = list_to_string(kvp[1])
                thewriter.writerow([file_name,row_number,words])

def grapher_one(file):
    title = file[:-4]
    title = ' '.join(title.split("_"))
    df = pandas.read_csv(file)
    print(df)
    df = pandas.DataFrame(df)
    df = df.sort_values(by='count', ascending=False)
    df = df.head(N_WORDS)
    print(df)
    plt.bar(x=df['word'], height=df["count"],color="olivedrab")
    plt.ylabel('Count')
    plt.xlabel(' ')
    plt.title(title, fontsize=18) #set the title to
    plt.tick_params(axis = "x", labelsize = 10, labelrotation = 45)
    plt.legend('',frameon=False)

    plt.show()

class TextFile:
    def __init__(self, file_name):
        self.file_name = file_name
        self.raw_text_string = None
        self.raw_text_list = []
        self.words_per_chunk_list = []
        self.spacy_tagged_text = None
        self.num_types = 0
        self.num_tokens = 0
        self.adjs_dict_spacy = {}
        self.bigram_dict = {}

    def read_file(self,file_name): #file name comes from files_list
        file_name = file_name
        lines_list = []
        tokens = 0
        swear_dict = {}

        wb = xlrd.open_workbook(file_name)
        sheet = wb.sheet_by_index(0) #first sheet in the workbook
        for i in range(sheet.nrows):
            if i > 0: #first row just says transcript
                text_line = sheet.cell_value(i, 4) #goes through rows in column 5 to get the text
                self.words_per_chunk_list.append(len(text_line)) #keeps track of how many words each person says per sample
                raw_text = clean_up(text_line) #cleans up the raw text
                if len(raw_text) > 0: #some are empty, don't need those, already have it in words_per_chunk_list
                    lines_list.append(raw_text)
                    tokens += len(raw_text)
                    for word in Words_of_Interest:
                        if word in text_line: #need to keep the space to get regular like so you check in text_line but append the cleaned text
                            swear_dict[i] = raw_text
        self.num_tokens = tokens #number of tokens for that person
        self.raw_text_list = lines_list #returns a list of each line of raw text (basically the excel sheet cells in list form)
        self.raw_text_string = list_list_to_string(lines_list) #the above list as a string (all of it, in one string)
        return self.raw_text_list, self.raw_text_string, self.num_tokens, swear_dict

    def get_types_and_counts(self, raw_text_list):
        types = 0
        types_dict = {}
        for words_list in raw_text_list:
            for word in words_list:
                if word in types_dict:
                    types_dict[word] += 1
                else:
                    types += 1
                    types_dict[word] = 1
        self.types_count = types
        self.types_dict = types_dict
        return self.types_count, self.types_dict

    def tag_spacy(self, words):
        self.spacy_tagged_text = SPACY_MODEL(words)
        return self.spacy_tagged_text

    def create_word_dicts(self,tagged_tokens):
        word_order_list = []
        for token in tagged_tokens:
            if token.text in Words_of_Interest and token.text not in WORD_COUNTS:
                WORD_COUNTS[token.text] = 1
                word_order_list.append(token.text)
            if token.text in Words_of_Interest and token.text in WORD_COUNTS:
                WORD_COUNTS[token.text] += 1
                word_order_list.append(token.text)
        return word_order_list

def main():
    files_list = get_file_names()
    files_class_list = create_TextFile_classes(files_list) #creating class instances for the text files
    for file_class in files_class_list: #for each class instance
        name = file_class.file_name #file name so it knows which file to read
        raw_text_list, raw_text_string, num_tokens, ____, _____,_____,_____ = file_class.read_file(name)
                UM[name] = um_lines
                UH[name] = uh_lines
                LIKE[name] = like_lines
                LIKE_STAR[name] = like_star_lines

        #Using Spacy's PoS tagger
        spacy_tag = file_class.tag_spacy(raw_text_string) #Tagging on the individual level
        word_order_list = file_class.create_word_dicts(spacy_tag)
        #print(file_class.__dict__)

    if os.path.exists(os.getcwd()+"/specific_words_by_list"):
        os.chdir(os.getcwd()+"/specific_words_by_list")
    else:
        os.mkdir("specific_words_by_list")
        os.chdir(os.getcwd()+"/specific_words_by_list")
    nested_dictionary_csv_writer(WORD_LINES, "swearwords.csv", ["file_name","utterance_number","text"])
    catchall_csv_writer(WORD_COUNTS, "swearword_counts.csv", ["word","count","fraction"])
    grapher_one("swearword_counts.csv")

main()
