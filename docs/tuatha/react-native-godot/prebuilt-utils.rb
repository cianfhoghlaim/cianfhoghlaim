require "json"
require "fileutils"

# ----------------------------------------------------------------------
# Helper: Returns the relative path to the pre‑built library directory.
#
# Parameters:
#   lib_name (String) – The `name` field from an entry in the
#                        `prebuiltFiles` array of package.json.
#
# Returns:
#   String – Relative path to the directory that contains the
#            pre‑built framework for the given library, i.e.:
#            <destination_base_dir>/<name>/<version>
#
# The function looks up the matching entry in `prebuiltFiles` and
# builds the path using its `destination_base_dir` and `version`.
# ----------------------------------------------------------------------
def prebuilt_path(lib_name)
  # Load package.json (assumes this file lives in the same directory as the podspec)
  package_path = File.join(__dir__, "package.json")
  unless File.file?(package_path)
    raise "Unable to locate package.json at #{package_path}"
  end

  package = JSON.parse(File.read(package_path))

  entry = package["prebuiltFiles"]&.find { |e| e["name"] == lib_name }

  unless entry
    raise "Prebuilt entry not found for library '#{lib_name}'. Ensure it exists in package.json."
  end

  # Build the relative path: <destination_base_dir>/<name>/<version>
  File.join(entry["destination_base_dir"], lib_name, entry["version"])
end
