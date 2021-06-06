import sys, re, pprint
# WSJ_02-21.pos ===> Training corpus
# WSJ_24.pos ===> Dev Corpus
pp = pprint.PrettyPrinter(indent=4)
#the number of times a given POS occurs in the corpus
pos_dict = {}
# {POS : COUNT}
#the number of times a word occurs as a POS in the corpus
word_dict = {}
# {WORD : {POS : COUNT}}
#the number of times a word occurs in the corpus
word_freq = {}
# {WORD : COUNT}
#the number of times a POS follows another POS in the corpus
transition_dict = {}
#{CUR_POS : {NEXT_POS : COUNT, TOTAL_OCCURENCES : COUNT_2}}
# Dt -> NN : 7
# POS that have few words 
oov_dict = {}
# {POS : COUNT}
#constant for low frequency words
OOV_THRESHOLD = 1
# counter for how many total words with low frequency
OOV_COUNT = 0
# 
OOV_CONSTANT = 0.0001

TOTAL_OCCURENCES = '_TOTAL_OCCURENCES_OF_KEY'
TRANSITION_FREQ = 'TRANSITION_FREQ'
#emission probability of a word: number_of_times a word occurs as POS / number_of_times POS occurs in corpus
#transition probability: number of times POS_1 goes to POS_2 / all occurences of POS_1 in corpus

# TODO: Calculate probabilities of words being a given POS with certain morphology such as capitalization, plurality (-s, -es), ending in -ing, -ed
# if unknown word does not match any of those categories, use probability of words that only occur once to be a given POS.
def updateEmissionCount(word, pos):
    # word = word.lower()
    cur_freqs = word_dict.get(word, {pos : 0})
    cur_freqs[pos] = cur_freqs.get(pos, 0) + 1
    word_dict[word] = cur_freqs
    pos_dict[pos] = pos_dict.get(pos, 0) + 1
    word_freq[word] = word_freq.get(word, 0) + 1
def updateTransistionCount(cur_pos, next_pos) :
    cur_freqs = transition_dict.get(cur_pos, {next_pos : 0})
    cur_freqs[next_pos] = cur_freqs.get(next_pos, 0) + 1
    cur_freqs[TOTAL_OCCURENCES] = cur_freqs.get(TOTAL_OCCURENCES, 0) + 1
    transition_dict[cur_pos] = cur_freqs
def calculateTransistionFrequency():
    for cur_pos, next_pos_dict in transition_dict.items():
        total = next_pos_dict[TOTAL_OCCURENCES]
        for next_pos, count in next_pos_dict.items():
            if next_pos == TOTAL_OCCURENCES:
                continue
            next_pos_dict[next_pos] = next_pos_dict[next_pos]/total
            transition_dict[cur_pos] = next_pos_dict
            
def calculateEmissionFrequency():
    global OOV_COUNT
    #iterate over all words found in the corpus
    for word, _pos_dict in word_dict.items():
        #iterate over all the POS this word is marked as
        
        for pos, count in _pos_dict.items():
            # check if this word occurs only once
            if word_freq[word] <= OOV_THRESHOLD:
                OOV_COUNT += 1
                # update the count that this pos occurs only once
                oov_dict[pos] = oov_dict.get(pos, 0) + 1
            #set this words POS value as the ratio of this word occurring as this POS to the total num of times this POS occurred
            _pos_dict[pos] = _pos_dict[pos] / pos_dict[pos]
            word_dict[word] = _pos_dict
def calculateOOVFrequency():
    # iterate through each POS and set the its OOV probability to either be the calcualted probabilty 
    # or if no word of that POS had few words with a low frequency (for example every IN had at least 2 entries)
    # then set that POS to a constant
    for pos in pos_dict.keys():
        # calculate the probability that a low frequency word will be this POS
        value = oov_dict.get(pos, False)
        if value:
            oov_dict[pos] = value / OOV_COUNT
        else:
            oov_dict[pos] = OOV_CONSTANT
def train(file_name):
    p = '(.+)\t(.+)|(\n)'
    pattern = re.compile(p)
    
    
    with open(file_name) as training_file:
        prev_pos = ''
        word = ''
        cur_pos = ''
        for index, line in enumerate(training_file):
            match = pattern.search(line)
            if match[3]:
                #end of sentence
                word = ''
                cur_pos = ''
                # print("found an end of sentence")
                # continue
            else :
                word = match[1]
                cur_pos = match[2]
                updateEmissionCount(word, cur_pos)
            updateTransistionCount(prev_pos, cur_pos)
            prev_pos = cur_pos
            # if index > 100:
            #     break
    # pp.pprint(pos_dict)
    # pp.pprint(transition_dict)
    pp.pprint(transition_dict[''])
    # pp.pprint(transition_dict)
#next POS tag is the tag that has the highest score.
#score defined by (transition probability from state 1 -> state 2) * (emission probability) that this token is a given POS
def calculate():
    calculateEmissionFrequency()
    calculateTransistionFrequency()
    calculateOOVFrequency()
def getEmissionProbabilities(word):
    # word = word.lower()
    #get the emission dictionary for this word (return false if not found)
    scores = word_dict.get(word, False)
    if scores:
        return scores
    # since this word is not in the dictionary, use the OOV dict to best predict what POS this word will be
    return oov_dict
#returns the transition probability that a given POS (cur_pos) will follow the previous POS (prev_pos)
# if the training set never encountered this transition, it is assumed that this transition cannot exist (returns 0)
def getTransitionProbability(prev_pos, cur_pos):
    return transition_dict[prev_pos].get(cur_pos, 0)

# takes an array of tokens as an argument
# the first and last elements in the array must be empty strings representing the beginning and ends of sentences
# creates a lookup table for previous tokens and finds the max score for each column per the viterbi algorithm
#returns an array of labeled words as tuples -> (WORD, POS)
def processSentence(sentence):
    #create an empty array of dictionaries the size of this sentence
    #[{POS : SCORE}...]
    lookup = [{} for x in sentence]
    # since lookup stores the likelihood that the current state is this POS, beginning must be likelihood 1
    lookup[0] = {'' : 1}
    # since lookup stores the likelihood that the current state is this POS, end must be likelihood 1
    lookup[len(sentence) - 1] = {'' : 1}
    answer = []
    for index, word in enumerate(sentence):
        #ignore the beginning and end tokens
        if index == 0 or index == len(sentence) - 1:
            continue
        # create the empty dictionary to represent the probabilities that this token will be a given POS
        score_dict = {}
        #redefine max to -1 each iteration so max can be calculated
        best_score = -1
        # get the likelihoods that this token will be a given POS
        emission_scores = getEmissionProbabilities(word)
        for potential_pos, emission_probability in emission_scores.items():
            # look at all the possibilities of what the previous POS might be
            for prev_pos, prev_score in lookup[index-1].items():
                # calculate the score that this token will be potential_pos given that the previous pos is prev_pos 
                this_probability = prev_score * emission_probability * getTransitionProbability(prev_pos, potential_pos)
                # print(f'The score for "{word}" to be a "{potential_pos}" after a "{prev_pos}" is {this_probability}.')
                score_dict[potential_pos] = this_probability
                #set the max value and best POS for this token
                if this_probability > best_score:
                    best_score = this_probability
                    best_pos = potential_pos
        #assign the dictioanry to the lookup table
        lookup[index] = score_dict
        # print(f'The best score was {best_score} and the part of speech is {best_pos}')
        #append the labelled word as a tuple to the answer array
        answer.append((word, best_pos))
    return answer
def predict(test_file_name, output_file_name):
    with open(test_file_name) as test_file:
        with open(output_file_name, 'w') as output_file:
            sentence = ['']
            # counter = 0
            for index, line in enumerate(test_file):
                # if (index > 100):
                #     break
                if re.match('^\n$', line):
                    sentence.append('')
                    a = processSentence(sentence)
                    for label in a:
                        output_file.write(f'{label[0]}\t{label[1]}\n')
                    output_file.write('\n')
                    # pp.pprint(a)
                    sentence = ['']
                    # counter = 0
                    continue
                # unique_word_key = f'{line.strip()}_{counter}'
                # print(sentence)
                sentence.append(line.strip())
                # counter += 1
def run(training_files, test_files, output_files):
    for training_file_name in training_files:
        train(training_file_name)
    calculate()
    for index, test_file_name in enumerate(test_files):
        predict(test_file_name, output_files[index])
#command line args:
#   <flag> -- options: -t | -d | -test'
#           -t is used for only training data sets
#           -d is used for only development data sets
#           -test is used to train on both training and dev sets, and then test using WSJ_23.words, outputs 'submission.pos'
#   <training_file> -- if given this file will be used for training the tagger. Defaults to training on WSJ_24 and WSJ_02-21
#   <test_file> -- if given this file will be used to test the POS tagger. Defaults to WSJ_24 and WSJ_02-21
#   <output_file> -- if given this is the name of the file used to output tags. Defaults to 'submission_<INDEX>.pos'
def main():
    training_files = ['WSJ_24.pos', 'WSJ_02-21.pos']
    test_files = ['WSJ_24.words']
    output_files = []
    if len(sys.argv) > 1:
        # use only training dataset
        if sys.argv[1] == '-t':
            training_files.pop(1)
        # use only development dataset
        elif sys.argv[1] == '-d':
            training_files.pop(0)
            test_files.pop(0)
        elif sys.argv[1] == '-test':
            test_files = ['WSJ_23.words']
            output_files = ['submission.pos']
            run(training_files, test_files, output_files)
            return
        # otherwise use specified filename for training data
        else :
            training_files = [sys.argv[1]]
    if len(sys.argv) > 2:
        #use specified filename as testing data
        test_files = [sys.argv[2]]
    if len(sys.argv) > 3:
        #use specified filename as output filename
        output_files = [sys.argv[3]]
    if len(output_files) == 0:
        for index, file_name in enumerate(test_files):
            output_files.append(f'tk2208_{file_name[:-6]}.pos')
    # pp.pprint(training_files)
    # pp.pprint(test_files)
    # pp.pprint(output_files)
    run(training_files, test_files, output_files)
main()