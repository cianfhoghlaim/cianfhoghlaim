function GenerateRecipe(recipe: string) -> Recipe {
  client "openai/gpt-4o"
  prompt #"
    Generate a recipe for the following ingredients:
    {{ recipe }}

    {{ ctx.output_format }}
  "#
}

class Recipe {
  name string @stream.not_null
  servings int @stream.not_null
  ingredients (Ingredient @stream.done)[]
  instructions string[]
}

class Ingredient {
  name string
  quantity int
  unit string
}

test TestName {
  functions [GenerateRecipe]
  args {
    recipe #"
      saag paneer
    "#
  }
}
