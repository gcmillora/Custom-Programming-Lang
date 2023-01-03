def evaluate_expression(tokens,variables, ctr=0):
  
  current_token = tokens[ctr]
  

  if(current_token.isdigit() or current_token in variables):
    if(current_token in variables):
      return int(variables[current_token]), ctr
    return int(current_token), ctr
  
  if(current_token in ["ADD","MULT","DIV","SUB","MOD"]):
    ctr += 1
    left, ctr = evaluate_expression(tokens,variables,ctr)
  
    ctr += 1
    right, ctr = evaluate_expression(tokens,variables,ctr)

    if(current_token == "ADD"):
      return left + right, ctr
    elif(current_token == "MULT"):
      return left * right, ctr
    elif(current_token == "DIV"):
      return left / right, ctr
    elif(current_token == "SUB"):
      return left - right, ctr
    elif(current_token == "MOD"):
      return left % right, ctr
    return 0, ctr


  
    
variables ={
  "x":"5",
  "y":"6"
}
#ADD 5 MULT DIV 5 10 5
result = evaluate_expression(["ADD", "5","MULT","DIV","5","10","5"],variables)
print(result)