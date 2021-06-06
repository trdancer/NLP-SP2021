#USE python version >= 3.0 so f strings work otherwise it will throw a syntax error
#USAGE python3 dollar_program.py <input_file_name> <verbosity>
#input_file_name must be in the same directory as this file
#verbosity can be set to v, -v, --v, V, -V, --V verbose, Verbose -verbose, -Verbose, --verbose, or --Verbose
#and it will print the full regex to the terminal

#outputs to a file named 'dollar_output.txt'

import re, sys
numbers_pattern = '(US)?((\$)?(((\d{1,3}(,\d{3})+))|\d+)([.]\d{1,2})?( (million|billion|trillion))? (dollar(s)?( and \d{1,2} cent(s)?)?))|(\$((\d{1,3}(,\d{3})+)|\d+)([.]\d{1,2})?( (million|billion|trillion))?( (dollar(s)?( and \d{1,2} cent(s)?)?))?)'
divider = '( |\-)'
irregular_teen = '((T|t)en|(T|t)welve|(E|e)leven)'
prefix = '((T|t)hir|(F|f)our|(F|f)if|(S|s)ix|(S|s)even|(E|e)igh|(N|n)ine)'
tens_prefix = f'(((T|t)wen)|{prefix})'
place = '((T|t)rillion|(B|b)illion|(M|m)illion|(T|t)housand|(H|h)undred)'
ones_place_match = '((O|o)ne|(T|t)wo|(T|t)hree|(F|f)our|(F|f)ive|(S|s)ix|(S|s)even|(E|e)ight|(N|n)ine)'
tens_place_match = f'({irregular_teen}|({prefix}teen)|({tens_prefix}ty{divider}?{ones_place_match}?))'
hundreds_place_match = f'({ones_place_match}{divider}hundred)'
fraction =f'((((O|o)ne|(T|t)hree{divider})?(Q|q)uarter(s)?|(H|h)alf)({divider}a)?)'
cents_word_match = f'( and ({tens_place_match}|{ones_place_match}) (C|c)ent(s)?)'
words_pattern = f'(({divider}?({hundreds_place_match}|{tens_place_match}|{ones_place_match}|{fraction})({divider}{place})?)+ (D|d)ollars){cents_word_match}?'
pattern = f'{numbers_pattern}|{words_pattern}'
money_pattern = re.compile(pattern)
input_file_name = "all-OANC.txt"
if len(sys.argv) > 1:
    input_file_name = sys.argv[1]
if len(sys.argv) > 2:
    m = re.search('(-){0,2}(V|v|erbose?)', sys.argv[2])
    if m:
        print(pattern)
    else :
        print("please use the verbose tag of 0, 1 or 2 dashes, v, V, or verbose")
with open(f'./{input_file_name}', 'r') as input_file:
    with open('./dollar_output.txt', 'w') as output_file:
        for line in input_file:
        # for index, line in enumerate(input_file):
            try :
                match_iterator = money_pattern.finditer(line)
                for match in match_iterator:
                    # output_file.write(f'MATCH: {match.group().strip()}\tLINE {index}: {line}\n') 
                    output_file.write(f'{match.group().strip()}\n')            
            except UnicodeDecodeError as e:
                print(e)
                print("You are running this on Windows which has weird encoding standards and will not work")
                quit(1)