#USE python version >= 3.0 so f strings work otherwise it will throw a syntax error
#USAGE python3 telephone_regexp.py <input_file_name> <verbosity>
#input_file_name must be in the same directory as this file
#verbosity can be set to v, -v, --v, V, -V, --V verbose, Verbose -verbose, -Verbose, --verbose, or --Verbose
#and it will print the full regex to the terminal

#outputs to a file named 'telephone_output.txt'

import re, sys
pattern = '(\d{1,3})?([ \-])(\d{3})([ \-])(\d{4})'
phone_pattern = re.compile(pattern)
input_file_name = 'all-OANC.txt'
if len(sys.argv) > 1:
    input_file_name = sys.argv[1]
if len(sys.argv) > 2:
    m = re.search('(-){0,2}(V|v|erbose?)', sys.argv[2])
    if m:
        print(pattern)
    else :
        print("please use the verbose tag of 0, 1 or 2 dashes, v, V, or verbose")
print(input_file_name)
with open(f'./{input_file_name}', 'r') as input_file:
    count = 0
    with open('./telephone_output.txt', 'w') as output_file:
        for index, line in enumerate(input_file):
            try :
                match_iterator = phone_pattern.finditer(line)
                for match in match_iterator:
                    # print(line)
                    # print(match.group())
                    output_file.write(f'{match.group().strip()}\n')
                    # output_file.write(f'\t{line}\n')          
            except UnicodeDecodeError as e:
                print(e)
                print('You are running this on windows which has weird encoding standards and will not work')
                quit(1)
        