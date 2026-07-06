// apps/web/src/components/MarimoEmbed.tsx
// The marimo notebook embedder.
// Per openspec/changes/cianfhoghlaim-website-rewrite/proposal.md
// — embeds the 8 NCCA subject marimo notebooks (notebooks/leaving_cert/{subject}.py)
// as interactive widgets inside a CF R2 iframe.
// Per iximiuz Labs "Provisioned in seconds" model.

import * as React from "react";
import { CiSemanticPill } from "@cianfhoghlaim/ui";

export interface MarimoEmbedProps {
  notebookPath: string;
  title: string;
  subject: string;
  /** Cloudflare R2 signed URL for the HTML export. */
  r2SignedUrl?: string;
  /** Whether to render the full notebook (true) or a preview (false). */
  full?: boolean;
}

export function MarimoEmbed({ notebookPath, title, subject, r2SignedUrl, full = true }: MarimoEmbedProps) {
  const heightClass = full ? "h-[800px]" : "h-[400px]";
  const fallback = r2SignedUrl ?? `/_notebooks/${notebookPath.split("/").pop()}`;

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center gap-2 text-sm">
        <CiSemanticPill kind="eiraic" label="marimo" />
        <code className="text-xs text-slate-500 font-mono">{notebookPath}</code>
      </div>
      <div className={`${heightClass} w-full rounded-lg border border-slate-700 overflow-hidden`}>
        <iframe
          src={fallback}
          title={title}
          className="w-full h-full bg-slate-950"
          loading="lazy"
        />
      </div>
    </div>
  );
}