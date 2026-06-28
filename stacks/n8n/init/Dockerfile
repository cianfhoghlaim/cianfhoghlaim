FROM oven/bun:1.3.14-alpine
LABEL org.opencontainers.image.source="https://github.com/cianfhoghlaim/kings_college_galway"
LABEL org.opencontainers.image.description="n8n-init: one-shot seeder for n8n workflow JSONs"
WORKDIR /app
COPY seed.ts /app/seed.ts
USER 65532:65532
ENTRYPOINT ["bun", "run", "/app/seed.ts"]
