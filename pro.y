%{

    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>
    #define border printf("\n--------------------------------------\n")

    extern int yylex();
    void yyerror(char *msg) ;
    int yywrap() ;
    
%}

%token ID NUMBER STRING_LIT STRING_VAR 
%token EQ PLUS MINUS MUL DIVIDE LBPACKET PBPACKET SEMICOLON
%token PRINT RARE

%right EQ
%left PLUS MINUS
%left MUL DIVIDE

%%

start : stmt SEMICOLON {printf("\n this is a valid python expression"); border; }

stmt: assign_arithmatic
    | assign_str
    | display

identifier: ID
    |keyword {printf("error0");}

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
void yyerror(char *msg)  {
    fprintf(stderr,"%s\n",msg);
    exit(1);
}
int yywrap(){
    return (1);
}
int main(){
    printf("\n--------------------pthon exp parse --------------------\n");
    printf("enter python expression");
    return yyparse();


}














