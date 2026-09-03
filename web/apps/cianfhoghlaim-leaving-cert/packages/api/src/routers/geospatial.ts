// @cianfhoghlaim/api — geospatial oRPC router
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md T4.14.
// Wired to cianfhoghlaim/tuatha/geospatial/{geoparquet_writer.py,hilbert_indexing.py}
// for the topic-frequency heatmap data layer.

import { os } from "@orpc/server";
import { z } from "zod";
import type { ApiContext } from "../context";

const SubjectSchema = z.enum([
  "mathematics", "applied_mathematics", "chemistry", "geography",
  "history", "english", "gaeilge", "computer_science",
]);

export const geospatialRouter = os.$context<ApiContext>().router({
  writeTopicFrequencyGeoParquet: os
    .input(z.object({
      subject: SubjectSchema,
      language: z.enum(["en", "ga"]),
    }))
    .handler(async ({ input }) => {
      // TODO: query MotherDuck for the topic-frequency rows + call
      // cianfhoghlaim.tuatha.geospatial.geoparquet_writer.write_geo_parquet(...)
      return {
        subject: input.subject,
        language: input.language,
        status: "queued",
        estimated_rows: 0,
        estimated_minutes: 3,
      };
    }),

  readHilbertSorted: os
    .input(z.object({
      subject: SubjectSchema,
      language: z.enum(["en", "ga"]),
      bbox: z.object({
        x_min: z.number(),
        y_min: z.number(),
        x_max: z.number(),
        y_max: z.number(),
      }).optional(),
    }))
    .handler(async ({ input }) => {
      // TODO: read the Hilbert-sorted GeoParquet + filter by bbox
      return {
        subject: input.subject,
        language: input.language,
        bbox: input.bbox,
        rows: [],
      };
    }),
});