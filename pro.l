%{
    #include "pro.tab.h"
    #include <stdio.h>
    #include <stdlib.h>
    #define border printf("\n----------------------\n")
%}

%%
"print" return(PRINT);
"and"|"assert"|"break"|"class"|"def"|"del"|"elif"|"else"|"except"|"exec"|"finally"|"for"|"from"|"global" return(RARE);
"if"|"import"|"in"|"is"|"lambda"|"not"|"or"|"pass"|"raise"|"return"|"finally"|"for"|"from"|"global" return(RARE);

[0-9]+ return NUMBER;
[_a-zA-Z][_a-zA-Z]* return ID;

[ \t] ;
\=  return(EQ);
\+  return(PLUS);
\-  return(MINUS);
\*  return(MUL);
\/  return(DIVIDE);
\(  return(LBPACKET);
\)  return(PBPACKET);
\;  return(SEMICOLON);

\"([^\"\n])*\" return(STRING_LIT);
\'([^\'\n])*\'' return(STRING_LIT);

.   {printf("\n unidentified token %s\n",yytext); exit(1);}

%%