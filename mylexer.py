# Lexer part
# based on PLY documents

import ply.lex as lex

# List of token names.   This is always required
tokens = [
    'ID',
    'NUMBER',
    'PLUS', 'MINUS',  # + , -
    'TIMES', 'DIVIDE', # * , /
    'LPAREN', 'RPAREN', # ( , )
    'LBRACE', 'RBRACE', # { , }
    'LE', 'GE', # <=, >=
    'EQ', 'NE', # ==, !=
    'ASSIGN',   # =
    'LT', 'GT', # < , >
    
]

# Reserved word
reserved = {
    'if': 'IF',
    'elif': 'ELIF',
    'else': 'ELSE',
    'while': 'WHILE',
    'for': 'FOR',
    'in': 'IN',
    'range': 'RANGE',
    ':': 'COLON',
    # 'not': 'NOT'
}

tokens = tokens + list(reserved.values())


# Regular expression rules for simple tokens

t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_EQ = r'=='
t_GE = r'>='
t_LE = r'<='
t_NE = r'!='
t_LT = r'<'
t_GT = r'>'
t_ASSIGN = r'='
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COLON = r':'

# A regular expression rule with some action code
def t_ID(t):
    r':|[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')  
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)    
    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

#comment handelling
def t_COMMENT(t):
    r'\#.*'
    pass
    # No return value. Token discarded

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

def write_in_token_file(output_token_file, tokens_list):
    with open(output_token_file, 'a+') as token_file:
        add_end_of_line = False
        token_file.seek(0) #go to start of the file
        token_file_data = token_file.read() #to see if it's empty
        if token_file_data:
            add_end_of_line = True
        for token in tokens_list:
            if add_end_of_line:
                token_file.write('\n')
            else:
                add_end_of_line = True
            token_file.write(token)

if __name__ == "__main__":
    with open('token_file.txt', 'r+') as token_file:
        token_file.truncate(0) #truncates the file size
    with open('python_file.txt', 'r') as python_file:
        data = python_file.read().rstrip() #removes any trailing characters (characters at the end a string)

    lexer.input(data)

    tokens_list = []

    while True:
        tokenText = ""
        t = lexer.token()
        if not t:
            break # No more input
        tokenText = t.type + " " + str(t.value)
        tokens_list.append(tokenText)
        # print(t.type, t.value, t.lineno, t.lexpos)
    write_in_token_file('token_file.txt', tokens_list)
    token_file.close()
    python_file.close()
