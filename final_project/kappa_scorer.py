import sys, re


# structure of conversation object:
# {
#   sentences : array - sentence dictionaries
#   result : string - success|failure|neutral 
# }

# sentence is an array of strings containing sentence data 
# example ["A: Hello", "OPENING", "positive"]

# kappa score = p_o - p_e / (1 - p_e)
# p_o = relative observed agreement
#   (number of identically tagged items) / total number of tagged items
# p_e = hypothetical probability of chance agreement
#   (p ((A=true) * p(B = true)) + (p(A=false) * p(B=false)))
#   where p(X=bool) = (number of times x=bool) / (total number of items)
# TODO allow score to account for ommission of a tag 
class Annotation():
    all_tags = {
        "action_tag": ["STATEMENT", "BACKCHANNEL/ACKNOWLEDGE", "OPINION", "ABANDONED/UNINTERPRETABLE", "AGREEMENT/ACCEPT",
            "APPRECIATION", "YES-NO-QUESTION", "YES-ANSWERS", "CONVENTIONAL-CLOSING", "WH-QUESTION", "NO-ANSWERS", "RESPONSE-ACKNOWLEDGMENT",
            "HEDGE", "DECLARATIVE-YES-NO-QUESTION", "OTHER", "BACKCHANNEL-QUESTION", "QUOTATION", "SUMMARIZE/REFORMULATE", "AFFIRMATIVE-NON-YES-ANSWERS", 
            "ACTION-DIRECTIVE", "COLLABORATIVE-COMPLETION", "REPEAT-PHRASE", "OPEN-QUESTION", "RHETORICAL-QUESTIONS", "HOLD-BEFORE-ANSWER/AGREEMENT",
            "REJECT", "NEGATIVE-NON-NO-ANSWERS", "SIGNAL-NON-UNDERSTANDING", "OTHER-ANSWERS", "CONVENTIONAL-OPENING", "OR-CLAUSE", "DISPREFERRED-ANSWERS ",
            "3RD-PARTY-TALK", "OFFERS-OPTIONS-COMMITS", "SELF-TALK", "DOWNPLAYER", "MAYBE/ACCEPT-PART", "TAG-QUESTION", "DECLARATIVE-WH-QUESTION",
            "APOLOGY", "THANKING", "UNCONVENTIONAL-OPENING", "PICKUP-LINE", "CORRECTION", "CONVENTIONAL-CLOSING"],
        "positivity": ["positive", "negative", "neutral"],
        "humor" : ["humorous", "serious"],
        "subject" : ["self", "other", "both"],
        "sexual" : ["sexual-intent", "sexual-response", "sexual-decline"],
        "information" : ["unsolicited-information", "unsolicited-information-response"]
    }
    all_results = ["success", "failure", "neutral"]
    def processSentence(self, sentence):
        sent_dict = {
            "text" : sentence[0]
        }
        for tag in sentence[1:]:
            self.tag_counter[tag] = self.tag_counter.get(tag, 0) + 1
            sent_dict[tag] = True
            # if self.postivity_match.match(tag):
            #     sent_dict["positivity"] = tag
            # if self.humor_match.match(tag):
            #     sent_dict["humor"] = tag
            # if self.subject_match.match(tag):
            #     sent_dict["subject"] = tag
            # if self.sexual_match.match(tag):
            #     sent_dict["sexual"] = tag
            # if self.information_match.match(tag):
            #     sent_dict["information"] = tag
        return sent_dict
    def __init__(self, file_name):
        # self.postivity_match = re.compile("negative|positive|neutral")
        # self.humor_match = re.compile("humorous|serious")
        # self.sexual_match = re.compile("sexual-intent|sexual-decline|sexual-response")
        # self.subject_match = re.compile("self|other|both")
        # self.information_match = re.compile("unsolicited-information|unsolicited-information-response")
        # self.result_match = re.compile("success|failure|neutral")
        self.conv_end_match = re.compile(r'CONV (\w+)')

        self.numberOfSentences = 0
        self.numberOfConversations = 0
        # counts how many times each tag occurs
        self.tag_counter = {}
        # counts how many times each conversation result occurs
        self.results_counter = {}
        # all the conversations in this file
        self.conversations = []
        #the temporary conversation object
        conversation = {}
        # the sentences within a conversation 
        sentences = []
        with open(file_name, 'r') as file_handle:
            for line in file_handle:
                if (re.match("\n", line)):
                    # empty line signifying new conversation
                    continue
                line = line.strip()
                if (self.conv_end_match.match(line)):
                    # end of conversation
                    result = self.conv_end_match.match(line)[1]
                    conversation["sentences"] = sentences
                    conversation["result"] = result
                    self.numberOfSentences += len(sentences)
                    self.numberOfConversations += 1
                    self.results_counter[result] = self.results_counter.get(result, 0) + 1
                    self.conversations.append(conversation)
                    # print("read an end of conversation")
                    conversation = {}
                    sentences = []
                    continue
                split_line = re.sub("( )*\t{2,}( )*", "\t", line).split("\t")
                processed_sentence = self.processSentence(split_line)
                sentences.append(processed_sentence)
def scoreTag(annotation_a, annotation_b, tag_name):
    total_items = annotation_a.numberOfSentences
    num_agreement = 0
    for conversation_a, conversation_b in zip(annotation_a.conversations, annotation_b.conversations):
        for sentence_a, sentence_b in zip(conversation_a["sentences"], conversation_b["sentences"]):
            if sentence_a.get(tag_name, False) == sentence_b.get(tag_name, False):
                num_agreement += 1
    p_o = num_agreement / total_items
    occurences_of_tag_a = annotation_a.tag_counter.get(tag_name, 0)
    occurences_of_tag_b = annotation_b.tag_counter.get(tag_name, 0)
    occurences_of_not_tag_a = total_items - occurences_of_tag_a
    occurences_of_not_tag_b = total_items - occurences_of_tag_b
    p_e = ((occurences_of_tag_a/total_items)*(occurences_of_tag_b/total_items)) + ((occurences_of_not_tag_a/total_items)*(occurences_of_not_tag_b/total_items))
    if p_e == 1:
        return 1.0
    return (p_o - p_e) / (1 - p_e)
def scoreResult(annotation_a, annotation_b, result_name):
    total_items = annotation_a.numberOfConversations
    num_agreement = 0
    for conversation_a, conversation_b in zip(annotation_a.conversations, annotation_b.conversations):
        if conversation_a["result"] == conversation_b["result"]:
            num_agreement += 1
    p_o = num_agreement / total_items
    occurences_of_result_a = annotation_a.results_counter.get(result_name, 0)
    occurences_of_result_b = annotation_b.results_counter.get(result_name, 0)
    occurences_of_not_result_a = total_items - occurences_of_result_a
    occurences_of_not_result_b = total_items - occurences_of_result_b
    p_e = ((occurences_of_result_a/total_items)*(occurences_of_result_b/total_items)) + ((occurences_of_not_result_a/total_items)*(occurences_of_not_result_b/total_items))
    if p_e == 1:
        return 1.0
    return (p_o - p_e) / (1 - p_e)
def scoreAnnotations(annotation_a, annotation_b):
    tag_scores = {}
    results_scores = {}
    tag_score_total = 0
    results_score_total = 0
    for category_name, tag_values in Annotation.all_tags.items():
        category_score_total = 0
        tag_scores[category_name] = {}
        for tag in tag_values:
            score = scoreTag(annotation_a, annotation_b, tag)
            tag_scores[category_name][tag] = score
            tag_score_total += score
            category_score_total += score
        num_tags_in_category = len(tag_values)
        tag_scores[category_name]["AVERAGE"] = category_score_total/num_tags_in_category
    for result in Annotation.all_results:
        score = scoreResult(annotation_a, annotation_b, result)
        results_scores[result] = score
        results_score_total += score
    total_tags_count = {}
    total_results_count = {}
    # find total number of tags observed between both annotations
    for tag, count in annotation_a.tag_counter.items():
        total_tags_count[tag] =  total_tags_count.get(tag, 0) + count
    for tag_, count_ in annotation_b.tag_counter.items():
        total_tags_count[tag_] =  total_tags_count.get(tag_, 0) + count_
    for result, count_1 in annotation_a.results_counter.items():
        total_results_count[result] =  total_results_count.get(result, 0) + count_1
    for result_, count_2 in annotation_b.results_counter.items():
        total_results_count[result_] =  total_results_count.get(result_, 0) + count_2
    
    num_tags = sum([len(a) for a in Annotation.all_tags.values()])
    tag_average = tag_score_total/num_tags
    tag_scores["AVERAGE"] = tag_average
    
    num_results = 3
    results_average = results_score_total/num_results
    results_scores["AVERAGE"] = results_average
    
    grand_average = (tag_score_total+results_score_total)/(num_tags+num_results)

    # calculate average per tag category

    return (tag_scores, results_scores, total_tags_count, total_results_count, grand_average)
def printScores(scores):
    _category, _tag, _score, _result, space, _count = "CATEGORY", "TAG", "KAPPA SCORE", "RESULT", " ", "COUNT"
    print(f'{_category:10s}{_tag:35s}{_score:17s}{_count:11s}')
    print("==================================================================")
    for category_name, tag_values in scores[0].items():
        if category_name == "AVERAGE":
            print(f'\n{category_name:45s}{tag_values:.3f}')
            continue
        print(category_name)
        for a in range(len(category_name)+2):
            print("-", end="")
        print()
        for tag, score in tag_values.items():
            print(f'{space:10s}{tag:35s}{score:7.3f}', end="")
            print(f'{scores[2].get(tag, 0):15d}')
    print(f'\n{_result:10s}{_score:17s}{_count:11s}')
    print("==================================================================")
    for result, score in scores[1].items():
        print(f'{result:10s}{score:7.3f}', end="")
        print(f'{scores[3].get(result, 0):14d}')
    print(f'\nAVERAGE KAPPA SCORE:\t\t{scores[4]:16.3f}')
def main():
    if len(sys.argv) != 3:
        print("please use 2 arguments <input_file_1> <input_file_2>")
        exit(1)
    file_1 = sys.argv[1]
    file_2 = sys.argv[2]
    annotation_1 = Annotation(file_1)
    annotation_2 = Annotation(file_2)
    scores = scoreAnnotations(annotation_1, annotation_2)
    printScores(scores)
main()