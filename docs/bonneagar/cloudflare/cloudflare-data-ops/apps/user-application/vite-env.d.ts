interface ImportMetaEnv {
  readonly VITE_BACKEND_HOST: string;
  readonly VITE_BASE_HOST: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
