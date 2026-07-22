/// <reference types="vite/client" />

// Vite's `?url` import form — returns the public URL of an asset.
// Used by `apps/web/packages/lineage/PdfViewer.tsx` to resolve the
// PDF.js worker (`pdfjs-dist/build/pdf.worker.mjs`).
declare module "*?url" {
  const src: string;
  export default src;
}
