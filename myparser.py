# # Yacc part
# # based on PLY documents


import ply.yacc as yacc
from mylexer import tokens, lexer, reserved


class Parser(object):
    


    precedence = (
        ('nonassoc', 'GE', 'GT', 'LE', 'LT', 'EQ', 'NE',),
        ('left', 'TIMES', 'DIVIDE'),
        ('left', 'PLUS', 'MINUS')
    )

    assign_symbols = ['=']
    operation_symbols = ['+', '-', '*', '/', '==', '>', '>=', '<', '<=', '!=']

    def __init__(self):
        self.tokens = tokens
        self.lexer = lexer
        self.keywords = reserved.keys()
        self.parser = yacc.yacc(module=self)
        self.parse_tree = None
        self.three_address_code = None
        self.symbol_table = {}
        self.tIndex = 0
        self.lIndex = 0
    
    
    def p_stmts(self, p):
        """
        stmts : stmts stmt
        | empty
        """
        if len(p) == 3: #stmts : stmts stmt
            if not p[1]:
                p[1] = []
            p[0] = p[1] + [p[2]]
            self.parse_tree = p[0]

    def p_statement(self, p):
        """
        stmt : assignment
        | for
        | if
        | while
        | expression
        """
        p[0] = p[1]

    def p_if(self, p):
        """
        if : IF expression COLON LBRACE stmts RBRACE elif
        """
        p[0] = list((p[1], p[2], p[5], p[7]))

    def p_elif(self, p):
        """
        elif : ELIF expression COLON LBRACE stmts RBRACE elif
        | else
        """
        if len(p) != 2:
            p[0] = list((p[1], p[2], p[5], p[7]))
        else:
            p[0] = p[1]

    def p_else(self, p):
        """
        else : ELSE COLON LBRACE stmts RBRACE
        | empty
        """
        if len(p) != 2:
            p[0] = list((p[1], p[4]))

    def p_while(self, p):
        """
        while : WHILE expression COLON LBRACE stmts RBRACE
        """
        p[0] = list((p[1], p[2], p[5]))

    def p_for(self, p):
        """
        for : FOR ID IN RANGE LPAREN NUMBER RPAREN COLON LBRACE stmts RBRACE
        """
        p[0] = list((p[1], p[2], p[6], p[10]))

    def p_assignment(self, p):
        """
        assignment : ID ASSIGN expression
        """
        p[0] = list((p[2], p[1], p[3]))

    def p_expr_operator(self, p):
        """
        expression : expression PLUS term
        | expression MINUS term
        | expression GE term
        | expression EQ term
        | expression NE term
        | expression LT term
        | expression LE term
        | expression GT term
        | term
        """
        if len(p) != 2:
            p[0] = list([p[2], p[1], p[3]])
        else:
            p[0] = p[1]

    def p_term(self,p):
        """
        term : term TIMES factor
        | term DIVIDE factor
        | factor
        """
        if len(p) != 2:
            p[0] = list([p[2], p[1], p[3]])
        else:
            p[0] = p[1]

    def p_factor(self,p):
        """
        factor : NUMBER
        | ID
        | LPAREN expression RPAREN
        """
        if len(p) != 2:
            p[0] = p[2]
        else:
            p[0] = p[1]

    def p_empty(self, p):
        'empty :'
        p[0] = None

    # Error rule for syntax errors
    def p_error(self, p):
        print("Syntax error in input!")


    def parsing(self, input_file):
        python_program_code = ''
        with open(input_file, 'r') as python_file:
            python_program_code = python_file.read()

        self.parser.parse(python_program_code, lexer=self.lexer)
        return self.parse_tree

    def generate_code(self, instruction):
        if type(instruction) != list:
            return "", instruction

        if instruction[0] in self.assign_symbols:
            return self.assign_code(instruction)
        elif instruction[0] in self.operation_symbols :
            return self.operator_code(instruction)
        elif instruction[0] == 'if':
            return self.if_code(instruction)
        elif instruction[0] == 'while':
            return self.while_code(instruction)
        elif instruction[0] == 'for':
            return self.for_code(instruction)
        else:
            raise Exception("Invalid instruction: %s" % str(instruction))

    

    def for_code(self, instruction):
        id = instruction[1]
        
        end_number = instruction[2]
        start_number = '0'
        step = 1
        
        stmts = instruction[3]
        statement_code = self.program(stmts)

        start_label = self.labelindex_generator()
        end_label = self.labelindex_generator()

        if_code_body = ""

        if id not in self.symbol_table:
            if_code_body += f"float {id};\n"
            self.symbol_table[id] = 'float'

        if_code_body += f"{id} = {start_number};\n"
        
        operator = ''
        if step > 0 :
            operator = '<='
        else:
            operator = '>='

        if_code_body += start_label+':\n' \
                     +"if ("+id+" "+operator+" "+ str(end_number)+') goto '+end_label+";\n" \
                     +statement_code+"\n" \
                     +id+" += "+str(step)+";\n" \
                     +"goto "+start_label+";\n" \
                     +end_label+":\n"
        return if_code_body, None

   
    def while_code(self, instruction):
        condition = instruction[1]
        statements = instruction[2]

        condition_code, condition_root = self.generate_code(condition)
        statements_code = self.program(statements)

        start_while_label = self.labelindex_generator()
        end_while_label = self.labelindex_generator()

        condition_code_repeat = condition_code.replace('float ', '')

        while_code_body = start_while_label +':\n' \
                    +"if (!" +condition_root+') goto '+end_while_label+'\n' \
                    + statements_code +'\n' \
                    +condition_code_repeat+'\n' \
                    +"goto "+start_while_label+';\n' \
                    +end_while_label+':\n'

        return condition_code + while_code_body, None

    def if_code(self, instruction):      
        stack = []
        instruction_copy = instruction

        #when we have several elif and else that are connected to an if
        while instruction_copy:
            new_condition = instruction_copy[0]

            if new_condition == 'else':
                stack.append({
                    'condition_name': 'else',
                    'statements_code': self.program(instruction_copy[1])
                })
                break #each if has jus one else (dangeling else is solved)

            if new_condition == 'elif':
                new_condition = 'else if'
            stack.append({
                'condition_name': 'else if', 
                'condition_code': self.generate_code(instruction_copy[1]),
                'statements_code': self.program(instruction_copy[2])
            })

            instruction_copy = instruction_copy[3]

        conditions_code = ""
        statement_code = ""
        if_ended_label = self.labelindex_generator()

        #generating  address code for any elif or if (condition) that is  attached to an  if
        for condition in stack:
            condition_name = condition.get('condition_name')
            if condition_name == 'else':
                statement_code += f"{condition.get('statements_code')}\n"
                continue
            _condition_code, condition_root = condition.get('condition_code')
            conditions_code += f"{_condition_code}\n"

            statements_end = self.labelindex_generator()

            statement_code += "if (!"+condition_root+") goto "+statements_end+";\n" \
                            +condition.get('statements_code')+"\n" \
                            +"goto "+if_ended_label+";\n" \
                            +statements_end+":\n"

        statement_code += if_ended_label+":;\n"
        return conditions_code + statement_code, None

    
    


    def operator_code(self, instruction):
        leftHandSide = instruction[1]
        rightHandSide = instruction[2]
        operator = instruction[0]

        lefHandSide_code, a_root = self.generate_code(leftHandSide)
        rightHandSide_code, b_root = self.generate_code(rightHandSide)

        t = self.tindex_generator() #temproraty variable in 3AddressCode

        op_code = lefHandSide_code + rightHandSide_code
        op_code += f"float {t} = {a_root} {operator} {b_root};\n"

        return op_code, t
    
    

    def assign_code(self, instruction):
        lefHandSide = instruction[1]
        rightHandSide = instruction[2]
        operator = instruction[0]
        if lefHandSide in self.symbol_table.keys():
            type_of_id = ''
        else:
            type_of_id = 'float ' #because id could be int or float
            self.symbol_table[lefHandSide] = 'float' #add type of new id to symbol table
        rightHandSide_code, rightHandSide_root = self.generate_code( rightHandSide)
        code_str = type_of_id+" "+str(lefHandSide)+" "+operator+" "+str(rightHandSide_root)+";\n"
        return rightHandSide_code + code_str, lefHandSide


    def program(self, p):
            if not p:
                return "\n"
            all_code = ""
            for instruction in p:
                instruction_code, root = self.generate_code(instruction)
                all_code += instruction_code
            return all_code

    def generate_three_address_code(self):
        three_address_code_body = self.program(self.parse_tree)
        return three_address_code_body

    def tindex_generator(self):
        self.tIndex += 1
        return "t%d" % self.tIndex

    def labelindex_generator(self):
        self.lIndex += 1
        return "l%d" % self.lIndex


if __name__ == "__main__":
    p = Parser()
    p.parsing('python_file.txt')
    c_file = open('c_file.txt', 'w')
    c_code = p.generate_three_address_code()
    c_file.write(c_code)
    c_file.close()