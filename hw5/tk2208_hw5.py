import sys, re, pprint
from nltk.stem.porter import PorterStemmer
stemmer = PorterStemmer()
pp = pprint.PrettyPrinter(indent=4)
# file format: TOKEN POS BIO-TAG
capital_pattern = re.compile("[A-Z](\w)*")
vowel_pattern = re.compile("[AEIOUaeiou]")
# mode 0: training
# mode 1: testing

def processSentence(sentence, mode):
    processed_sentence = []
    for index, feature, in enumerate(sentence):
        new_feature = feature
        # check if past first feature
        if index >= 1:
            new_feature['PREV_POS'] = sentence[index-1]['POS']
            new_feature['PREV_TOKEN'] = sentence[index-1]['TOKEN']
            new_feature['PREV_CAPITAL'] = sentence[index-1]['IS_CAPITAL']
            if mode == 0 :
                new_feature['PREV_BIO'] = "@@"
        new_feature['IS_FIRST'] = True if index == 0 else False
        # check if past second feature
        if index >= 2:
            new_feature['PREV_POS_2'] = sentence[index-2]['POS']
            new_feature['PREV_CAPITAL_2'] = sentence[index-2]['IS_CAPITAL']
        # check if before last feature
        if index <= len(sentence) - 2:
            new_feature["NEXT_TOKEN"] = sentence[index+1]['TOKEN']
            new_feature['NEXT_CAPITAL'] = sentence[index+1]['IS_CAPITAL']
            new_feature['NEXT_POS'] = sentence[index+1]['POS']
        # check if before second-to-last feature
        if index <= len(sentence) - 3:
            new_feature['NEXT_POS_2'] = sentence[index+2]['POS']
            new_feature['NEXT_CAPITAL_2'] = sentence[index+2]['IS_CAPITAL']
        processed_sentence.append(new_feature)
    return processed_sentence
def readFile(file_name, mode):
    processed_data = []
    sentence = []
    current_feature = {}
    # print(mode)
    with open(f'./{file_name}', 'r') as input_file:
        for index, line in enumerate(input_file):
            tokens = line.strip("\n").split("\t")
            # print(tokens)
            if (len(tokens) == 1):
                # print('found blank line')
                #blank line
                current_feature = {}
                sentence = processSentence(sentence, mode)
                processed_data.append(sentence)
                sentence = []
                continue
            token = tokens[0]
            stem = stemmer.stem(token)
            ext = token[len(stem):]
            current_feature = {"TOKEN": token, "POS": tokens[1], "STEM" : stem, "EXT" : ext}   
            if mode == 0:
                current_feature["BIO_TAG"] = tokens[2]
            current_feature["IS_CAPITAL"] = True if capital_pattern.match(token) else False 
            current_feature["HAS_VOWEL"] = True if vowel_pattern.match(token) else False
            current_feature["TOKEN_LENGTH"] = len(token)
            sentence.append(current_feature)
        # pp.pprint(processed_data[1])
    return processed_data
def writeFile(data, file_name):
    sep = '\t'
    with open(f'./{file_name}', 'w') as output_file:
        d = data[1:]
        for sentence in d:
            # print("sentence is of type ", type(sentence))
            output_file.write('\n')
            for feature in sentence:
                s = []
                s.append(feature['TOKEN'])
                for key, value in feature.items():
                    if key == "TOKEN" or key == "BIO_TAG":
                        continue
                    s.append(f'{key}={value}')
                if feature.get("BIO_TAG", False):
                    s.append(feature["BIO_TAG"])
                out_string = sep.join(s)
                out_string +='\n'
                output_file.write(out_string)
        output_file.write('\n')
    return
def main():
    mode = 0
    input_files = ["WSJ_02-21.pos-chunk", "WSJ_23.pos"]
    output_files = ["training.feature", "test.feature"]
    for input_file, output_file in zip(input_files, output_files):
        print(input_file, output_file)
        data = readFile(input_file, mode)
        writeFile(data, output_file)
        mode = 1
    return
main()