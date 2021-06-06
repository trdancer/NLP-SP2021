# Troy Kelley
# tk2208
# Natural Language Processing
# Adam Meyers
# Homework 5

For this noun group tagging assignment, I chose to include the following features of a sentence:
- Token
    - The token itself
- Stemmed Token
    - The stem of the token gotten from using nltk stemmer. e.g. Running -> 'run'
- Word extension
    - The token's suffix e.g. Running -> 'ing'
- Is First
    - True/False if this is the first token in the sentence. Suspected to be useful for correctly tagging nouns as B-NP rather than I-NP.
- Is Capitalized
    - True/False whether or not this token has a capital first letter
- Has Vowel
    - True/False whether or not this token contains a vowel
- Token Length
    - The number of characters in this token
- Part of speech
    - The part of speech this word is already tagged as
- Prev/Next/Second Previous/Second Next
    - For all but the first and last two tokens in every sentence, I include the Part of Speech, capitalizing, and Token of the previous, second previous, next, and second next word.
    - For the training set, I also include the BIO tag of the previous token
I inititally created a simpler feature model and did not include the features of "previous/next" token, token length, capitalization, and token extension -- that system received these scores:
- Accuracy: 93.65
- Precision: 74.67
- Recall: 85.16
- F1: 79.57

After including the prev/next token, token length, extension, and vowels (numbers shown in parentheses are the changes in values since the last run):
- Accuracy: 95.72 (+2.07)
- Precision: 84.84 (+10.17)
- Recall: 90.34 (+5.18)
- F1: 87.51 (+7.94)

I ran intermediary tests where token length, extension, and vowel features were omitted, however the score was marginally different than the final scores shown here, with these features only contributing to a maxiumum increase in any category of 0.5. Therefore if these were omitted the overall tagging capability would not be affected.

After including the "is first" feature the scores acheived were:
- Accuracy: 95.81 (+0.09)
- Precision: 85.24 (+0.40)
- Recall: 90.51 (+0.17)
- F1: 87.80 (+0.29)
As we can see, there were very small increases in each score so it did not improve much with this feature

After including a second step back/forward for "is capital" (second value in parentheses is change since from initial scores):
- Accuracy: 95.86 (+0.05) (+2.21)
- Precision: 85.73 (+0.49) (+11.06)
- Recall: 90.77 (+0.26) (+11.2)
- F1: 88.18 (+0.38) (+8.61)

Overall, the addition of any one feature does not dramatically increase the final output scores of the system. However, when combined, they do provide whole point increases (or close to it) in some categories. Therefore adding these features is important for improving the performance of this system, even if by a small amount. However, when taking into account the variety of different systems available to most people, adding more features results in higher computational and memory overhead. Once I included the "length" feature, my system (Windows Laptop, 8gb RAM, Intel i5) would run out of heap space in the JVM, causing me to allocate more memory to the process. From a memory-to-performance cost perspective, adding these features is not very useful at all 

All these tests were completed using the key/value pair for "Prev BIO" as whatever the previous BIO tag actaully was, now here is the result of the system with that value always containing the value "@@" as demonstrated in the homework instructions.
- Accuracy: 96.36 (+0.50) (+2.71)
- Precision: 89.42 (+3.69) (+14.75)
- Recall: 92.77 (+2.00) (+13.2)
- F1: 90.75 (+2.57) (+11.18)

Here we can clearly see using the special Prev BIO tag is extremely beneficial to the output of the system, as it caused one of the biggest jumps of scores across all metrics for the inclusion of just one feature. 