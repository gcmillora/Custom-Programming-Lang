
lines = open("test.iol", "r").read().splitlines()
tokens = []
variables = []
keywords = ["ADD","SUB","MULT","DIV","MOD","INTO","IS","BEG","PRINT", "INT","STR","DEFINE","NEWLN"]

for num in range(0,len(lines)):
  if(lines[0] == "IOL" and lines[-1] == "LOI"):
    lexemes = lines[num].split(" ")
    for word in lexemes:
      if (word != "IOL" and word != "LOI"):
        if word in keywords:
          tokens.append((word,word,num+1))
        elif word.isnumeric():
          tokens.append((word,"INT_LIT",num+1))
        elif word[0].isalpha():
          if word.isalnum():
            variables.append((word,"IDENT",num+1))
          else:
            tokens.append((word,"ERR_LEX",num+1))
        else:
          tokens.append((word,"ERR_LEX",num+1))
      
errors = [i for i, v in enumerate(tokens) if v[1] == "ERR_LEX"]


for error in errors:
  print("Error: Invalid lexeme",tokens[error][0],"at line",tokens[error][2])

print("\n\nLexemes:")
for token in tokens:
  print(token[0] + " ----- " + token[1])
  
print("\n\nVariables:")
for var in variables:
  print(var[0] + " ----- " + var[1])