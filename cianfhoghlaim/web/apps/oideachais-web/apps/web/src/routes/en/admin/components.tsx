// /en/admin/components — Component Catalog (Cianfhoghlaim Oideachais)
// Reads from the LanceDB ui_component_suggestions table (populated by the nightly
// baml.SuggestUIComponents Dagster asset).
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/en/admin/components")({
  component: ComponentCatalogComponent,
});

function ComponentCatalogComponent() {
  return (
    <div className="max-w-4xl mx-auto flex flex-col gap-6">
      <h1 className="font-cinzel text-2xl font-bold text-slate-100">
        Component Catalog
      </h1>
      <p className="text-slate-400">
        Admin route. Reads from the `ui_component_suggestions` LanceDB table,
        populated nightly by the `baml.SuggestUIComponents` Dagster asset.
        Shows 28 possible UIComponentKind values with priority 1-5.
      </p>
      <div className="bg-slate-800 border border-slate-700 rounded-lg p-4 text-center text-slate-500">
        LanceDB query endpoint not connected yet. The nightly Dagster asset
        writes to LanceDB `ui_component_suggestions`; this page will read from it.
      </div>
    </div>
  );
}
