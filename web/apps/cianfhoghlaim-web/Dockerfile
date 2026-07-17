# =============================================================================
# Oideachais Web — TanStack Start monorepo image
# =============================================================================
# Build context: REPO ROOT (so we can reach the sibling croilar monorepo for
# the @croilar/ui cross-workspace dependency).
#
# Uses bun (the monorepo's package manager — apps use `workspace:*` protocol
# which npm rejects but bun supports natively).
# =============================================================================

FROM oven/bun:1-alpine

WORKDIR /app/oideachais/web

# -----------------------------------------------------------------------------
# 1. Install oideachais/web dependencies via bun
# -----------------------------------------------------------------------------
# Copy manifests first so the install layer caches correctly.
COPY oideachais/web/package.json oideachais/web/bun.lock* oideachais/web/turbo.json ./
COPY oideachais/web/apps/web/package.json apps/web/
COPY oideachais/web/packages/ packages/

# Sibling croilar monorepo (provides @croilar/ui). The Dockerfile is invoked
# from the repo root; we place it at ../../croilar/packages so the
# workspaces glob `../../croilar/packages/*` (added to package.json
# in the next step) can find it.
COPY croilar/packages/ ../../croilar/packages/

# Patch oideachais/web/package.json to include croilar packages in the
# workspace glob. This is needed because @croilar/ui is imported by
# apps/web/src/components/leaving-cert/LeavingCertLayout.tsx and was
# previously silently broken at runtime (vite: Cannot find module
# '@croilar/ui'). The patch is idempotent.
RUN if ! grep -q '../../croilar/packages' package.json; then \
      sed -i.bak 's|"packages/\*"|"packages/*",\n    "../../croilar/packages/*"|' package.json; \
    fi

RUN bun install

# -----------------------------------------------------------------------------
# 2. Copy source
# -----------------------------------------------------------------------------
WORKDIR /app
COPY oideachais/web/ /app/oideachais/web/
COPY croilar/packages/ /app/croilar/packages/

# 2a. Symlink oideachais/web/node_modules into every croilar package
#     so vite can resolve transitive deps (clsx, tailwind-merge, etc.)
#     from inside @croilar/ui's source files. Bun hoists everything to
#     /app/oideachais/web/node_modules, so a symlink is the cheapest fix.
RUN for d in /app/croilar/packages/*/; do \
      ln -sf /app/oideachais/web/node_modules "$d/node_modules"; \
    done

# -----------------------------------------------------------------------------
# 3. Expose + run
# -----------------------------------------------------------------------------
EXPOSE 80 3000

WORKDIR /app/oideachais/web/apps/web
CMD ["bunx", "vite", "dev", "--host", "0.0.0.0", "--port", "3000"]
