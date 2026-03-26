// BAML Generator Configuration
// This configures code generation for TypeScript

generator target {
  // Generate TypeScript code
  output_type "typescript"

  // Output directory (relative to baml_src/)
  output_dir "../src/baml"

  // BAML package version
  version "0.206.1"

  // Default client mode
  default_client_mode async
}
