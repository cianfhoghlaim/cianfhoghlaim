def get_ingredients(index,ingredients,data):
  answer = []
  for i in range(500):
    if data[index][i] == 1: 
      answer.append(ingredients[i])
  return answer
