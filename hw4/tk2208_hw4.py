from stop_list import closed_class_stop_words 
import math, sys, re
TFIDF = 'TFIDF'
documents = []
#stores the IDFs of all terms
document_IDF_cache = {}
pat = re.compile("[\.,!\?\:;\d/\(\)=+\*]| '|' ")
abstract_pattern = re.compile('(\.W)')
number_pattern = re.compile('(\.I \d+)')
whitespace_pattern = re.compile(' +|\-')

class DocumentSet:
    def __init__(self, name):
        self.name = name
        self.documents = []
        self.terms_idf = {}
    def getIDF(self, term):
        if self.terms_idf.get(term, False):
            return self.terms_idf[term]
        n = len(self.documents)
        documents_containing_term = 0
        for document in self.documents:
            if document.containsTerm(term):
                documents_containing_term += 1
        idf = math.log((n/documents_containing_term))
        self.terms_idf[term] = idf
        return idf
    def __getitem__(self, index):
        return self.documents[index]
    def __iter__(self):
        return iter(self.documents)
    def addDocument(self, text):
        self.documents.append(Document(text, len(self.documents)+1))
    def setDocsTFIDF(self):
        for doc in self.documents:
            doc.setAllTFIDF(self)
    def __str__(self):
        sep = ''
        s = [f'Document Set name: {self.name}\n']
        for d in self.documents:
            s.append(str(d))
        return sep.join(s)
class Document:
    def __init__(self, text, id = -1):
        self.terms = {}
        self.id = id
        self.text = pat.sub('', text).strip()
        self.document_length = len(self.text)
        for word in whitespace_pattern.split(self.text):
            if word in closed_class_stop_words:
                continue
            # if not re.match('[a-zA-Z]', word):
            #     print(word)
            # print(word)
            self.terms[word] = self.terms.get(word, 0) + 1
        # print('done')
    def getTermFrequency(self, term):
        return self.terms.get(term, 0)
    def containsTerm(self, term):
        return self.terms.get(term, False)
    #to be called after all documents are read into the program
    def setAllTFIDF(self, documentSet):
        for term in self.terms.keys():
            self.terms[term] = self.terms[term] * documentSet.getIDF(term)
    #returns the cosine simialrity between this document and the query document
    def cosineSimilarity(self, query_document):
        normal_sum = 0
        v_1 = 0
        v_2 = 0
        square_sum = 0
        for term, query_tfidf in query_document.terms.items():
            v_1 += (query_tfidf ** 2)
            # print(f'normal sum is {normal_sum}, square sum is {square_sum}')
        for term, document_idf in self.terms.items():
            normal_sum += document_idf * query_document[term]
            v_2 += (document_idf ** 2)
        v_1 = math.sqrt(v_1)
        v_2 = math.sqrt(v_2)
        try:
            return (normal_sum/(v_1*v_2))
        except ZeroDivisionError:
            return 0.0 
            
    #returns the TFIDF of a term in this document 
    def __getitem__(self, term):
        return self.terms.get(term, 0)
    def __str__(self):
        sep = ''
        s = [f'Document ID: {self.id}\n']
        for term, value in self.terms.items():
            s.append(f'{term}\t{value}\n')
        return sep.join(s)
#TF - Term Frequency
    #number of times term occurs in a document
#IDF - Inverse Document Frequency
    # log(Number of documents/numberofdocumentscontaining(term)) 
# read in each abstract
# create a document object based on this abstract
def readDocs(file_name, document_set):
    read_abstract = False
    temp_string = []
    with open(file_name, 'r') as file_handle:
        for index, line in enumerate(file_handle):
            # if index > 40:
            #     break
            if abstract_pattern.match(line):
                read_abstract = True
                continue
            if number_pattern.match(line) and read_abstract:
                join_string = ' '
                doc_abstract = join_string.join(temp_string)
                document_set.addDocument(doc_abstract)
                # concat temp string into one string and add to docset
                read_abstract = False
                temp_string = []
                continue
            if read_abstract:
                line = line.strip()
                temp_string.append(line)
                continue
def main():
    doc_file = 'cran.all.1400'
    qry_file = 'cran.qry'
    output_file_name = 'output.txt'
    if len(sys.argv) > 1:
        doc_file = sys.argv[1]
    if len(sys.argv) > 2:
        qry_file = sys.argv[2]
    if len(sys.argv) > 3:
        output_file_name = sys.argv[3]
    closed_class_stop_words.append('')
    corpus_docs = DocumentSet('corpus')
    query_docs = DocumentSet('queries')
    readDocs(doc_file, corpus_docs)
    readDocs(qry_file, query_docs)
    corpus_docs.setDocsTFIDF()
    query_docs.setDocsTFIDF()
    with open(output_file_name, 'w', newline='\n') as output_file:
        for query in query_docs:
            temp = []
            for document in corpus_docs:
                score = document.cosineSimilarity(query)
                if score == 0.0 and len(temp) > 1:
                    continue
                t = (query.id, document.id, score)
                # if t[2] > 0.40:
                #     print(query)
                #     print(document)
                temp.append(t)
            temp.sort(key= lambda tup : tup[2], reverse=True)
            for a in temp:
                output_file.write(f'{a[0]} {a[1]} {a[2]:f}\n')
    
    # for el in output_arr:
    #     for t in el:
    #         print(t)
    # corpus_docs.addDocument('The quick brown fox jumps over a lazy dog')
    # corpus_docs.addDocument('Jimmy owns a brown dog that likes to jump, and a brown cat.')
    # query_docs.addDocument('dog jump')
    # query_docs.addDocument('cat jump')
    # corpus_docs.setDocsTFIDF()
    # query_docs.setDocsTFIDF()
    # # print(corpus_docs)
    # for doc in corpus_docs:
    #     for query in query_docs:
    #         print(f'cosine similarity is {doc.cosineSimilarity(query)}')

        # print(doc)
        # print(doc['dog'])
main()