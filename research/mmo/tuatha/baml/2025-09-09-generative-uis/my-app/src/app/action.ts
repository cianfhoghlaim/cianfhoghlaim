import { b } from "../baml_client"

export const generateRecipe = async (recipe: string) => {
  const stream = b.stream.GenerateRecipe(recipe)  
  for await (const chunk of stream) {
    chunk.ingredients.map((i) => {
      i.quantity * chunk.servings
    })
  }
}
