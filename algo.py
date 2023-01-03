
lines = open("test.iol", "r").read().splitlines()
tokens = []
variables = []

keywords = ["ADD", "SUB", "MULT", "DIV", "MOD", "INTO",
            "IS", "BEG", "PRINT", "INT", "STR", "NEWLN"]

operators = ["ADD", "SUB", "MULT", "DIV", "MOD"]


for num in range(0, len(lines)):
    if lines[0] == "IOL" and lines[-1] == "LOI":
        lexemes = lines[num].split(" ")
        for word in lexemes:
            if word != "IOL" and word != "LOI":
                if word in keywords:
                    tokens.append((word, word, nu m +1))
                elif word.isnumeric():
                    tokens.append((word, "INT_LIT", nu m +1))
                elif word[0].isalpha():
                    if word.isalnum():
                        tokens.append((word, "IDENT", nu m +1))
                        variables.append((word, "IDENT", nu m +1))
                    else:
                        tokens.append((word, "ERR_LEX", nu m +1))
                else:
                    tokens.append((word, "ERR_LEX", nu m +1))

errors = [i for i, v in enumerate(tokens) if v[1] == "ERR_LEX"]


def syntax_analysis(token_list):
    err_list = []
    valid_variables = []
    for ctr in range(len(token_list)):
        current_token = token_list[ctr]
        if current_token[1] in ["INT", "STR"]:
            next_token = token_list[ct r +1]
            ctr += 1
            if next_token[1] != "IDENT":
                err_list.append(f"ERROR: Line {next_token[1]} is not an identifier")
                continue
            valid_variables.append(next_token)
            continue
        elif current_token[1] == "IS":
            previous_token = token_list[ct r -1]
            previous_of_previous_token = token_list[ct r -2] if ctr > 1 else None
            if previous_of_previous_token[1] == "INT":
                if previous_token[1] == "IDENT":
                    next_token = token_list[ct r +1]
                    if next_token[1] == "IDENT":
                        exist = False
                        for var in valid_variables:
                            if next_token[0] == var[0]:
                                exist = True
                                break
                        if not exist:
                            err_list.append(f"ERROR: At Line {next_token[2]}, {next_token[0]} is not defined")
                            continue
                    ctr += 1
                    if next_token[1] not in ["INT_LIT", "IDENT"]:
                        data = is_expr(token_list, ctr, err_list, valid_variables)
                        ctr = data[1]
                        err = data[0]
                        err_list = data[2]
                        if not err:
                            err_list.append(f"ERROR: Invalid expression at line {token_list[ctr]}")
                            continue

                    if next_token[2] != current_token[2]:
                        err_list.append(
                            f"ERROR: Line {next_token[2]} does not match line {current_token[2]}")
                        continue
                    continue
            elif previous_of_previous_token[1] == "STR":
                # error if STR
                err_list.append(
                    f"ERROR: Line {previous_of_previous_token[2]}, assignment only reads INT")
                continue
                
        elif current_token[1] == "PRINT":
            next_token = token_list[ctr +1]
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
            if next_token[2] != current_token[2]:
                print("ERROR: No next token at line", current_token[2])
                err_list.append(
                    f"ERROR: No next token at line {current_token[2]}")
                continue
            continue
        elif current_token[1] == "NEWLN":
            continue
        elif current_token[1] == "BEG":
            next_token = token_list[ct r +1]
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
            if next_token[2] != current_token[2]:
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
        next_token = token_list[ct r +1]
        ctr += 1
        if next_token[1] in ["ADD", "SUB", "MULT", "DIV", "MOD"]:
            ctr += 1
            i f(next_token[2] != current_token[2]):
                print("ERROR: No next token at line", current_token[2])
                err_list.append(
                    f"ERROR: No next token at line {current_token[2]}")
                return False, ctr, err_list
            return is_expr(token_list, ctr, err_list, valid_variables)
        elif next_token[1] in ["INT_LIT", "IDENT"]:
            i f(next_token[2] != current_token[2]):
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


def evaluate_expression(tokens ,variables, ctr=0):
    current_token = tokens[ctr]
    i f(current_token.isdigit() or current_token in variables):
        i f(current_token in variables):
         return int(variables[current_token]), ctr
        return int(current_token), ctr

    i f(current_token in ["ADD" ,"MULT" ,"DIV" ,"SUB" ,"MOD"]):
        ctr += 1
        left, ctr = evaluate_expression(tokens ,variables ,ctr)
    
        ctr += 1
        right, ctr = evaluate_expression(tokens ,variables ,ctr)


        i f(current_token == "ADD"):
         return left + right, ctr
        eli f(current_token == "MULT"):
         return left * right, ctr
        eli f(current_token == "DIV"):
         return left // right, ctr
        eli f(current_token == "SUB"):
         return left - right, ctr
        eli f(current_token == "MOD"):
         return left % right, ctr
        return 0, ctr



    
            
        
            
            
def execute_code(token_list):
        variables_runtime = {}
        output = ""
        ctr = 0
        while ctr < len(token_list):
       
            current_token = token_list[ctr]
            if current_token[1] == "INT":
                ct r+ =1
                next_token = token_list[ctr]
                i f(token_list[ct r +1]):
                    next_of_next_token = token_list[ct r +2]
                    i f(next_of_next_token[1] == "INT_LIT"):
                        variables_runtime[next_token[0]] = int(next_of_next_token[0])
                    ctr += 3
                else:
                    variables_runtime[next_token[0]] = 0
                    ctr += 2
            elif current_token[1] == "STR":
                next_token = token_list[ct r +1]
                variables_runtime[next_token[0]] = ""
                ctr += 2
            elif current_token[1] == "NEWLN":
                output += "\n"
                ctr += 1
            elif current_token[1] == "PRINT":
                ct r+ =1
                next_token = token_list[ctr]
                i f(next_token[1] == "IDENT"):
                    output += str(variables_runtime[next_token[0]])
                    ctr += 1
                eli f(next_token[1] == "ADD" or next_token[1] == "SUB" or next_token[1] == "MULT" or next_token
                [1] == "DIV" or next_token[1] == "MOD" or next_token[1] == "INT_LIT"):
                    expression = []
                    while token_list[ctr][1] in ["ADD", "SUB", "MULT", "DIV", "MOD"] or token_list[ctr][1] in ["INT_LIT", "IDENT"]:
                        expression.append(token_list[ctr][0])
                        print("token" ,token_list[ctr])
                    ctr += 1 if
                    (ctr == len(token_list)):
                        break
                result,_ = evaluate_expression(expression, variables_runtime)
                output += str(result)
            elif next_token[1] == "STR_LIT":
                output += next_token[0]
                    ctr += 2
        elif current_token[1] == "INTO":
            print("INTO")
                ct r
            +=1
                next_token = token_list[ctr]
                if(next_token[1] == "IDENT"):
                    ctr+=1
                    next_next_token = token_list[ctr]
                    if(next_next_token[1] == "IS"):
                        ctr+=1
                        if(token_list[ctr][1] == "INT_LIT"):
                            variables_runtime[next_token[0]] = int(token_list[ctr][0])
                            ctr+=1
                        elif(token_list[ctr][1] in ["ADD", "SUB", "MULT", "DIV", "MOD"]):
                            expression = []
                            while token_list[ctr][1] in ["ADD", "SUB", "MULT", "DIV", "MOD"] or token_lis \
                            t[ctr][1] in ["INT_LIT", "IDENT"]:
                                expression.append(token_list[ctr][0])print("token"   ,token_list[ctr])
                                ctr += 1
                                if(ctr == len(
                            token_list)):
                                    break
                            result,_ = evaluate_expression(expression, variables_runtime)
                            variables_runtime[next_token[0]] = result
                            print(
        result)
            elif current_token[1] in ["ADD", "SUB", "MULT",
            "DIV", "MOD"]:
                expression = []
                while token_list[ctr][1] in ["ADD", "SUB", "MULT", "DIV"
                                                                                                       , "MOD"] or token_list[ctr][1 \
                ] in ["INT_LIT", "IDENT"]:
                    exps ion.append(token_list[ctr][0])
                    print("token"   , token_list[ctr])
                    ctr += 1
                    if(ctr == len (token_list)):
                        break
                result,_ = evaluate_expression( \
    expres sion, variables_runtime)
                print(result)
        return output,""

syntax_analysis(tokens)
print("executed code : ",execute_code(tokens)  )          




for error in errors:
    print("Error: Invalid lexeme",
          tokens[error][0], "at line", tokens[error][2])

# print("\n\nLexemes:")
# for token in tokens:
#     print(token[0] + " ----- " + token[1])

# print("\n\nVariables:")
# for var in variables:
#     print(var[0] + " ----- " + var[1])
