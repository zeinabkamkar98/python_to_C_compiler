import os

if __name__ == "__main__":  
    os.system("python3 mylexer.py")
    print("\n\n")
    print("_____________lexical analyzing is done____________\n")
    print("check token_file.txt to see the output of lexical process\n\n")
    os.system("python3 myparser.py")
    print("_____________three address code generating is done____________\n")
    print("check c_file.txt to see the output of parsing process\n")