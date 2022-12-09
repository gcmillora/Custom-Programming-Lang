

lines = open("test.iol", "r").read().splitlines()
tokens = []
variables = []

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


def syntax_analysis(token_list):
    err_list = []
    valid_variables = []
    for ctr in range(len(token_list)):
        current_token = token_list[ctr]
        if current_token[1] in ["INT", "STR"]:
            next_token = token_list[ctr+1]
            ctr += 1
            if next_token[1] != "IDENT":
                err_list.append(
                    "ERROR: Line", next_token[1], "is not an identifier")
                continue
            valid_variables.append(next_token)
            continue
        elif current_token[1] == "IS":
            previous_token = token_list[ctr-1]
            if previous_token[1] == "IDENT":
                next_token = token_list[ctr+1]
                if next_token[1] == "IDENT":
                    exist = False
                    for var in valid_variables:
                        if next_token[0] == var[0]:
                            exist = True
                            break
                    if not exist:
                        err_list.append(
                            f"ERROR: At Line {next_token[2]}, {next_token[0]} is not defined")
                        continue
                ctr += 1
                if next_token[1] not in ["INT_LIT", "IDENT"]:
                    data = is_expr(token_list, ctr, err_list, valid_variables)
                    ctr = data[1]
                    err = data[0]
                    err_list = data[2]
                    if not err:
                        err_list.append(
                            f"ERROR: Invalid expression at line {token_list[ctr]}")
                        continue

                if(next_token[2] != current_token[2]):
                    print(
                        f"ERROR: Line {next_token[2]} does not match line {current_token[2]}")
                    err_list.append(
                        f"ERROR: Line {next_token[2]} does not match line {current_token[2]}")
                    continue
                continue
        elif current_token[1] == "PRINT":
            next_token = token_list[ctr+1]
            ctr += 1
            if next_token[1] not in ["IDENT", "INT_LIT"]:
                err, ctr, err_list = is_expr(
                    token_list, ctr, err_list, valid_variables)
                if not err:
                    err_list.append(
                        f"ERROR: Invalid expression at line {token_list[ctr]}")
                    continue
            if next_token[1] == "IDENT":
                exist = False
                for var in valid_variables:
                    if next_token[0] == var[0]:
                        exist = True
                        break
                if not exist:
                    print(token_list[ctr], "not in", valid_variables)
                    err_list.append(
                        f"ERROR: At Line {next_token[2]}, {next_token[0]} is not defined")
                    continue
            if(next_token[2] != current_token[2]):
                print("ERROR: No next token at line", current_token[2])
                err_list.append(
                    f"ERROR: No next token at line {current_token[2]}")
                continue
            continue
        elif current_token[1] == "NEWLN":
            continue
        elif current_token[1] == "BEG":
            next_token = token_list[ctr+1]
            ctr += 1
            if next_token[1] != "IDENT":
                err_list.append(
                    f"ERROR: Line {next_token[2]} is not an identifier")
                continue
            if next_token[1] == "IDENT":
                exist = False
                for var in valid_variables:
                    if next_token[0] == var[0]:
                        exist = True
                        break
                if not exist:
                    print(token_list[ctr], "not in", valid_variables)
                    err_list.append(
                        f"ERROR: At Line {next_token[2]}, {next_token[0]} is not defined")
                    continue
            if(next_token[2] != current_token[2]):
                print("ERROR: No next token at line", current_token[2])
                err_list.append(
                    f"ERROR: No next token at line {current_token[2]}")
                continue
            continue
    return err_list


def is_expr(token_list, ctr, err_list=[], valid_variables=[]):
    current_token = token_list[ctr]
    if current_token[1] in ["ADD", "SUB", "MULT", "DIV", "MOD"]:
        ctr += 1
        return is_expr(token_list, ctr, err_list, valid_variables)
    elif current_token[1] in ["INT_LIT", "IDENT"]:
        if current_token[1] == "IDENT":
            exist = False
            for var in valid_variables:
                print(var)
                if current_token[0] == var[0]:
                    exist = True
                    break
            if not exist:
                print(token_list[ctr], "not in", valid_variables)
                err_list.append(
                    f"ERROR: At Line {current_token[2]}, {current_token[0]} is not defined")
                return False, ctr, err_list
        next_token = token_list[ctr+1]
        ctr += 1
        if next_token[1] in ["ADD", "SUB", "MULT", "DIV", "MOD"]:
            ctr += 1
            if(next_token[2] != current_token[2]):
                print("ERROR: No next token at line", current_token[2])
                err_list.append(
                    f"ERROR: No next token at line {current_token[2]}")
                return False, ctr, err_list
            return is_expr(token_list, ctr, err_list, valid_variables)
        elif next_token[1] in ["INT_LIT", "IDENT"]:
            if(next_token[2] != current_token[2]):
                print("ERROR: No next token at line", current_token[2])
                err_list.append(
                    f"ERROR: No next token at line {current_token[2]}")
                return False, ctr, err_list
            return True, ctr, err_list
        return True, ctr, err_list
    else:
        print("ERROR: Invalid expression at line", current_token[2])
        err_list.append(
            f"ERROR: Invalid expression at line {current_token[2]}")
        return False, ctr, err_list


print(syntax_analysis(tokens))


for error in errors:
    print("Error: Invalid lexeme",
          tokens[error][0], "at line", tokens[error][2])

# print("\n\nLexemes:")
# for token in tokens:
#     print(token[0] + " ----- " + token[1])

# print("\n\nVariables:")
# for var in variables:
#     print(var[0] + " ----- " + var[1])
