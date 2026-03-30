import { createFileRoute } from "@tanstack/react-router";
import guitars from "@/data/example-guitars";

export const Route = createFileRoute("/iframe-guitar/$guitarId")({
  component: RouteComponent,
  loader: async ({ params }) => {
    const guitar = guitars.find((guitar) => guitar.id === +params.guitarId);
    if (!guitar) {
      throw new Error("Guitar not found");
    }
    return guitar;
  },
});

function RouteComponent() {
  const guitar = Route.useLoaderData();

  return (
    <div className="max-w-sm mx-auto bg-gray-900 text-white rounded-2xl shadow-lg overflow-hidden border border-gray-800 flex flex-col items-center p-6">
      <div className="w-full h-48 mb-4 rounded-xl overflow-hidden border border-gray-800">
        <img
          src={guitar.image}
          alt={guitar.name}
          className="w-full h-full object-cover"
        />
      </div>
      <h1 className="text-2xl font-bold mb-2 text-emerald-400 text-center">
        {guitar.name}
      </h1>
      <p className="text-gray-300 mb-4 text-center">{guitar.description}</p>
      <div className="flex items-center justify-between w-full mt-auto">
        <span className="text-xl font-semibold text-emerald-300">
          ${guitar.price}
        </span>
        <button className="ml-auto bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-lg transition-colors text-sm font-medium shadow">
          Add to Cart
        </button>
      </div>
    </div>
  );
}
