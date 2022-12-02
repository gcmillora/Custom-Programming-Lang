

lines = open("test.iol", "r").read().splitlines()
tokens = []
variables = []
valid_variables = []
keywords = ["ADD", "SUB", "MULT", "DIV", "MOD", "INTO",
            "IS", "BEG", "PRINT", "INT", "STR", "DEFINE", "NEWLN"]

for num in range(0, len(lines)):
    if(lines[0] == "IOL" and lines[-1] == "LOI"):
        lexemes = lines[num].split(" ")
        for word in lexemes:
            if (word != "IOL" and word != "LOI"):
                if word in keywords:
                    tokens.append((word, word, num+1))
                elif word.isnumeric():
                    tokens.append((word, "INT_LIT", num+1))
                elif word[0].isalpha():
                    if word.isalnum():
                        tokens.append((word, "IDENT", num+1))
                        variables.append((word, "IDENT", num+1))
                    else:
                        tokens.append((word, "ERR_LEX", num+1))
                else:
                    tokens.append((word, "ERR_LEX", num+1))

errors = [i for i, v in enumerate(tokens) if v[1] == "ERR_LEX"]


def syntax_analysis(token_list, var_list):
    print(token_list[35])
    currentToken = ''
    previousToken = ''
    err = False
    for ctr in range(len(token_list)):
        if ctr == 0:
            currentToken = token_list[ctr]
            continue
        currentToken = token_list[ctr]
        previousToken = token_list[ctr-1]
        if currentToken[1] in ["INT", "STR"]:
            nextToken = token_list[ctr+1]
            ctr += 1
            if nextToken[1] != "IDENT":
                print(token_list[ctr])
                print(ctr)
                return False
            valid_variables.append(nextToken)
            continue
        elif currentToken[1] == "IS":
            if previousToken[1] == "IDENT":
                nextToken = token_list[ctr+1]
                ctr += 1
                if nextToken[1] not in ["INT_LIT", "IDENT"]:
                    data = isExpr(token_list, ctr)
                    print(data)
                    ctr = data[1]
                    err = data[0]
                    if not err:
                        print(token_list[ctr])
                        print(ctr)
                        return False
                continue
        elif currentToken[1] == "PRINT":
            nextToken = token_list[ctr+1]
            ctr += 1
            if nextToken[1] not in ["IDENT", "INT_LIT"]:
                err, ctr = isExpr(token_list, ctr)
                if not err:
                    print(token_list[ctr])
                    print(ctr)
                    return False
            continue
        elif currentToken[1] == "NEWLN":
            continue
        elif currentToken[1] == "BEG":
            nextToken = token_list[ctr+1]
            ctr += 1
            if nextToken[1] != "IDENT":
                print(token_list[ctr])
                print(ctr)
                return False
            continue
    return True


def isExpr(token_list, ctr):
    currentToken = token_list[ctr]
    if currentToken[1] in ["ADD", "SUB", "MULT", "DIV", "MOD"]:
        ctr += 1
        return isExpr(token_list, ctr)
    elif currentToken[1] in ["INT_LIT", "IDENT"]:
        nextToken = token_list[ctr+1]
        ctr += 1
        if nextToken[1] in ["ADD", "SUB", "MULT", "DIV", "MOD"]:
            ctr += 1
            return isExpr(token_list, ctr)
        elif nextToken[1] in ["INT_LIT", "IDENT"]:
            return True, ctr
        return True, ctr
    else:
        print(token_list[ctr])
        return False, ctr


print(syntax_analysis(tokens, variables))


for error in errors:
    print("Error: Invalid lexeme",
          tokens[error][0], "at line", tokens[error][2])

# print("\n\nLexemes:")
# for token in tokens:
#     print(token[0] + " ----- " + token[1])

# print("\n\nVariables:")
# for var in variables:
#     print(var[0] + " ----- " + var[1])
