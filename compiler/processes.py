from utils.CustomErrors import InvalidLexemeError, InvalidProdFileError, InvalidParseTableError


def lexical_analysis(lines: list[str]):
    tokens = []
    variables = []
    errors = []
    keywords = ["ADD", "SUB", "MULT", "DIV", "MOD", "INTO", "IS", "BEG", "PRINT", "INT", "STR", "DEFINE", "NEWLN"]

    # TODO: Add comments
    for idx, line in enumerate(lines, start=1):
        lexemes = line.split(" ")
        if line == "":
            continue
        if line == "IOL" or line == "LOI":
            continue
        for word in lexemes:
            if word in keywords:
                tokens.append((word, word, idx))
            elif word.isnumeric():
                tokens.append((word, "INT_LIT", idx))
            elif word[0].isalpha() and word.isalnum():
                variables.append((word, "IDENT", idx))
            else:
                tokens.append((word, "ERR_LEX", idx))
                errors.append((word, idx))

    # If errors were found then return the error list only
    if len(errors) > 1:
        raise InvalidLexemeError(errors)

    return {
        "tokens": tokens,
        "vars": variables,
    }


def syntax_analysis(prod_table: list, parse_table: list, input_buffer: list):
    # Non-recursive predictive parsing
    rules = []

    prod = __format_prod_table(prod_table)

    nt_symbols = parse_table[0]

    for line in parse_table[1:]:
        for ctr, char in enumerate(line[1:], 1):
            if char:
                rules.append((line[0], nt_symbols[ctr], char))

    output = ''
    rule_num = ''
    stack = []
    buffer = ''
    line = ''
    input_buffer.append("$")
    stack.append("$")
    error = False
    error_idx = None

    for ctr, inp in enumerate(input_buffer):
        if stack[-1] == "$":
            for item in rules:
                if item[1] == inp:
                    stack.append(item[0])
                    break
            for item in range(ctr, len(input_buffer)):
                buffer = f"{buffer}{input_buffer[item]} "
            line += f"{' '.join(reversed(stack))} {buffer}\n"

        while stack:
            buffer = ''
            for item in range(ctr, len(input_buffer)):
                buffer = f"{buffer}{input_buffer[item]} "

            if stack[-1] not in nt_symbols and stack[-1] != 'e':

                non_terminal = stack.pop()
                for item in rules:
                    if item[0] == non_terminal and item[1] == input_buffer[ctr]:
                        rule_num = item[2]
                        break
                    rule_num = False
                if rule_num:
                    production = prod[(rule_num, non_terminal)].split(" ")
                    for item in reversed(production):
                        stack.append(item)
                    if stack[-1] == 'e':
                        stack.pop()
                    line += ' '.join(reversed(stack)) + ","
                    product = f"{non_terminal} > {' '.join(production)}"
                    line += f"{buffer}, Output {product}\n"
                else:
                    error = True
                    line += ' '.join(reversed(stack)) + ","
                    line += f"{buffer}, Parsing ERROR\n"
                    break
            else:
                if stack[-1] == input_buffer[ctr]:
                    ch = stack.pop()
                    line += ' '.join(reversed(stack)) + ","
                    line += f"{buffer}, Match {ch}\n"
                    output += ch
                    break
                else:
                    error = True
                    line += ' '.join(reversed(stack)) + ","
                    line += f"{buffer}, PARSING ERROR\n"
                    break
        if error:
            error_idx = ctr
            InvalidParseTableError("Parsed file", ctr)
            break

    if stack:
        InvalidParseTableError("Parsed file", error_idx)

    return line


def __format_prod_table(prod_table: list):
    return {tuple([line[0], line[1]]): line[2].strip() for line in prod_table}


def check_and_clean_prod(lines: list, filename):
    curr_idx = 0
    try:
        cleaned_prod_file = []
        for idx, line in enumerate(lines):
            curr_idx = idx
            line = line.split(",")

            if len(line) != 3:
                raise InvalidProdFileError(filename, idx)

            if int(line[0]) != idx + 1:
                raise InvalidProdFileError(filename, idx)

            new_line = [val.strip() for val in line]
            cleaned_prod_file.append(new_line)
        return cleaned_prod_file
    except InvalidProdFileError:
        raise

    except IndexError:
        raise InvalidProdFileError(filename, curr_idx)


def check_and_clean_parse(lines: list, filename):
    curr_idx = 0

    try:
        cleaned_parse_table = []

        symbols = lines[0].split(",")
        symbols = [val.strip() for val in symbols]
        if symbols[0] != "":
            raise InvalidParseTableError(filename, 0)
        cleaned_parse_table.append(symbols)

        lines = lines[1:]

        expected_length = len(symbols)

        for idx, line in enumerate(lines):
            curr_idx = idx
            line = line.split(",")

            if len(line) != expected_length:
                raise InvalidParseTableError(filename, idx)

            if line[0] == "":
                raise InvalidParseTableError(filename, idx)

            new_line = [val.strip() for val in line]
            cleaned_parse_table.append(new_line)
        return cleaned_parse_table
    except InvalidParseTableError:
        raise

    except IndexError:
        raise InvalidParseTableError(filename, curr_idx)
