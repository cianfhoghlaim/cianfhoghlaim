"use client"

import Image from "next/image";
import { useGenerateRecipe } from "../baml_client/react/hooks"
import { useEffect, useState } from "react";
import { type Recipe } from "@/baml_client";

export default function Home() {
  const [servingScale, setServingScale] = useState(1)
  const { data, error, streamData } = useGenerateRecipe()

  const [recipe, setRecipe] = useState<Recipe | undefined>(undefined)

  useEffect(() => {
    if (streamData) {
      setRecipe(streamData)
      streamData.ingredients.map((i) => {
        (i.quantity ?? 0) * (servingScale ?? 0)
      })
    }
  }, [streamData])

  if (!recipe) {
    return <div>Loading...</div>
  }

  return (
    <div>
      <h1>Recipe</h1>
      <p>{recipe.name}</p>
      <p>{recipe.servings}</p>
      <p>{recipe.ingredients.map((i) => <>
      <p>{i.name}</p><p>{i.quantity * servingScale}</p><p>{i.unit}</p></>)}</p>
      <p>{recipe.instructions.join(", ")}</p>
    </div>
  );
}
