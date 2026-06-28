// Type shims for Vite ?url imports
declare module "*.css?url" {
  const url: string;
  export default url;
}

declare module "*.css" {
  const content: string;
  export default content;
}
