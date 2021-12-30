%{
    #include <stdio.h>
    #define border printf("\n--------------------------------------\n")
    int yydebug =1;
%}

%token ID NUMBER STRING_LIT STRING_VAR 
%token EQ PLUS MINUS MUL DIVIDE LBPACKET PBPACKET SEMICOLON
%token PRINT RARE

%right EQ
%left PLUS MINUS
%left MUL DIVIDE

%%

start : stmt SEMICOLON {printf("\n this is a valid python expression"); border; YYACCEPT; }

stmt: assign_arithmatic
    | assign_str
    | display

identifier: ID
    |keyword {yyerror("\nkeyword can't be used as a identifier"); YYABDET;}

keyword: PRINT
    | RARE

assign_str: identifier EQ strings

display: PRINT strings
    |PRINT strings MUL NUMBER
    |PRINT strings PLUS strings
    |PRINT expr
strings: STRING_LIT
    | STRING_VAR

assign_arithmatic: identifier EQ expr

expr: expr PLUS expr
    |expr MINUS expr
    |expr MUL expr
    |expr DIVIDE expr
    |factor
    |LBPACKET expr PBPACKET
    |SIGN factor

SIGN:PLUS
    |MINUS

factor: identifier
    |NUMBER

%%

main(){
    printf("\n--------------------pthon exp parse --------------------\n");
    printf("enter python expression");
    return yyparse();


}

yyerror(s)
{
printf("\n------------error");
border;
}
yywrap(){
    return(1);
}















