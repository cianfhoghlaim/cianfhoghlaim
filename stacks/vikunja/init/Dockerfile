FROM oven/bun:1.3.14-alpine
LABEL org.opencontainers.image.source="https://github.com/cianfhoghlaim/kings_college_galway"
LABEL org.opencontainers.image.description="vikunja-seed: one-shot seeder for Vikunja team + 6 projects"
WORKDIR /app
COPY seed.ts /app/seed.ts
USER 65532:65532
ENTRYPOINT ["bun", "run", "/app/seed.ts"]
