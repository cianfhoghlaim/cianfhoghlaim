import { ExternalLink } from "lucide-react";

interface CrossLink {
  title: string;
  source: string;
  url: string;
  description: string;
}

const PLACEHOLDER_LINKS: CrossLink[] = [
  {
    title: "Leaving Cert Irish Curriculum Analysis",
    source: "oideachais/data_platform",
    url: "#",
    description: "Full coverage matrix of SEC exam papers 2014–2025 with BAML-extracted topic tags.",
  },
  {
    title: "Gaeilge Marking Scheme Rubric Patterns",
    source: "oideachais/data_platform",
    url: "#",
    description: "PCLM/SRPs analysis across Higher and Ordinary level Gaeilge papers.",
  },
  {
    title: "Irish-Language OCR Pipeline",
    source: "meaisínfhoghlaim/ocr",
    url: "#",
    description: "Fine-tuned TrOCR model for historical Irish-language curriculum documents (1920s–present).",
  },
  {
    title: "Bilingual RAG Embeddings",
    source: "meaisínfhoghlaim/rag",
    url: "#",
    description: "LanceDB + CocoIndex embeddings of curriculum texts in English and Gaeilge.",
  },
];

export function CrossLinksSection() {
  return (
    <section>
      <h2 className="text-2xl font-bold mb-6">Cross-Linked Outputs</h2>
      <div className="space-y-4">
        {PLACEHOLDER_LINKS.map((link, i) => (
          <div key={i} className="rounded-xl bg-card border border-border p-5">
            <div className="flex items-start justify-between mb-2">
              <h3 className="font-semibold">{link.title}</h3>
              <code className="text-xs bg-muted px-2 py-1 rounded shrink-0 ml-2">{link.source}</code>
            </div>
            <p className="text-muted-foreground text-sm mb-2">{link.description}</p>
            {link.url !== "#" && (
              <a
                href={link.url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-sm text-primary hover:underline"
              >
                <ExternalLink className="h-3 w-3" />
                Open
              </a>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
