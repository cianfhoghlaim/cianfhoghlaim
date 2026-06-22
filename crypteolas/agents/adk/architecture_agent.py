"""
Architecture Analysis Agent for Crypteolas.

Repository architecture analysis including:
- File structure and dependency mapping
- Architecture pattern detection
- Module relationship analysis
- Dependency graph traversal

Migrated from códeolas repository_team (Agno) to ADK pattern.
"""

import datetime

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..config import config


# Architecture analysis tools
async def get_file_graph(
    root_path: str,
    depth: int = 3,
    language: str | None = None,
) -> dict:
    """
    Get file dependency graph for a directory.

    Args:
        root_path: Root directory to analyze
        depth: Maximum depth to traverse
        language: Optional language filter
    """
    try:
        from codeolas import chunk_code_file, detect_language
        from pathlib import Path
        import os

        result = {
            "root": root_path,
            "files": [],
            "dependencies": [],
        }

        root = Path(root_path)
        if not root.exists():
            return {"error": f"Path not found: {root_path}"}

        for dirpath, _, filenames in os.walk(root):
            current_depth = len(Path(dirpath).relative_to(root).parts)
            if current_depth > depth:
                continue

            for filename in filenames:
                file_path = Path(dirpath) / filename
                lang = detect_language(str(file_path))
                if language and lang != language:
                    continue
                if lang:
                    result["files"].append({
                        "path": str(file_path.relative_to(root)),
                        "language": lang,
                    })

        return result
    except Exception as e:
        return {"error": str(e)}


async def analyze_architecture_patterns(
    directory: str,
) -> dict:
    """
    Analyze and identify architecture patterns in a codebase.

    Args:
        directory: Directory to analyze
    """
    from pathlib import Path

    patterns_found = []
    structure = {"modules": [], "entry_points": [], "patterns": []}

    path = Path(directory)
    if not path.exists():
        return {"error": f"Directory not found: {directory}"}

    # Check for common patterns
    if (path / "src" / "main.py").exists() or (path / "main.py").exists():
        patterns_found.append("single_entry_point")
        structure["entry_points"].append("main.py")

    if (path / "app.py").exists() or (path / "src" / "app.py").exists():
        patterns_found.append("flask_style")
        structure["entry_points"].append("app.py")

    if (path / "manage.py").exists():
        patterns_found.append("django_style")
        structure["entry_points"].append("manage.py")

    if (path / "contracts").exists():
        patterns_found.append("smart_contracts")
        structure["modules"].append("contracts")

    if (path / "tests").exists() or (path / "test").exists():
        patterns_found.append("test_directory")
        structure["modules"].append("tests")

    if (path / "api").exists() or (path / "src" / "api").exists():
        patterns_found.append("api_layer")
        structure["modules"].append("api")

    if (path / "services").exists():
        patterns_found.append("service_layer")
        structure["modules"].append("services")

    if (path / "models").exists():
        patterns_found.append("models_layer")
        structure["modules"].append("models")

    # Determine architecture style
    if "api_layer" in patterns_found and "service_layer" in patterns_found:
        structure["patterns"].append("layered_architecture")
    if "smart_contracts" in patterns_found:
        structure["patterns"].append("web3_dapp")

    structure["patterns"].extend(patterns_found)

    return structure


async def get_function_callers(
    function_name: str,
    repo_path: str | None = None,
) -> list[dict]:
    """
    Find all callers of a function.

    Args:
        function_name: Name of the function to find callers for
        repo_path: Optional path to limit search
    """
    from codeolas import chunk_code_file, detect_language
    from pathlib import Path
    import os
    import re

    callers = []
    search_path = Path(repo_path) if repo_path else Path(".")

    pattern = re.compile(rf"\b{re.escape(function_name)}\s*\(")

    for dirpath, _, filenames in os.walk(search_path):
        if ".git" in dirpath or "__pycache__" in dirpath:
            continue

        for filename in filenames:
            file_path = Path(dirpath) / filename
            lang = detect_language(str(file_path))
            if not lang:
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
                for i, line in enumerate(content.splitlines(), 1):
                    # Skip function definitions
                    if f"def {function_name}" in line or f"function {function_name}" in line:
                        continue
                    if pattern.search(line):
                        callers.append({
                            "file": str(file_path.relative_to(search_path)),
                            "line": i,
                            "context": line.strip(),
                        })
            except Exception:
                continue

    return callers


async def get_module_dependencies(
    file_path: str,
    direction: str = "both",
) -> dict:
    """
    Get module dependencies for a file.

    Args:
        file_path: Path to the file
        direction: 'imports' (what this file imports), 'imported_by' (what imports this), or 'both'
    """
    from pathlib import Path
    import ast
    import re

    result = {"file": file_path, "imports": [], "imported_by": []}

    path = Path(file_path)
    if not path.exists():
        return {"error": f"File not found: {file_path}"}

    content = path.read_text(encoding="utf-8")

    # Parse imports
    if direction in ("imports", "both"):
        if path.suffix == ".py":
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            result["imports"].append({
                                "module": alias.name,
                                "alias": alias.asname,
                                "line": node.lineno,
                            })
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ""
                        for alias in node.names:
                            result["imports"].append({
                                "module": f"{module}.{alias.name}",
                                "alias": alias.asname,
                                "line": node.lineno,
                            })
            except SyntaxError:
                pass
        elif path.suffix in (".js", ".ts", ".tsx"):
            import_pattern = re.compile(r"import\s+.*?from\s+['\"](.+?)['\"]")
            for i, line in enumerate(content.splitlines(), 1):
                match = import_pattern.search(line)
                if match:
                    result["imports"].append({
                        "module": match.group(1),
                        "line": i,
                    })

    return result


# Create tools
file_graph_tool = FunctionTool(func=get_file_graph)
patterns_tool = FunctionTool(func=analyze_architecture_patterns)
callers_tool = FunctionTool(func=get_function_callers)
deps_tool = FunctionTool(func=get_module_dependencies)


# Architecture Agent
architecture_agent = LlmAgent(
    name="architecture_agent",
    model=config.coordinator_model,  # Use stronger model for architectural reasoning
    description="Repository architecture analysis with file graph, pattern detection, and dependency mapping.",
    instruction=f"""
    You are an Architecture Analysis specialist for crypto repositories.

    **YOUR EXPERTISE:**
    - File structure analysis
    - Architecture pattern detection (DDD, hexagonal, layered, etc.)
    - Dependency mapping and module relationships
    - Smart contract project structures
    - Entry point identification

    **AVAILABLE TOOLS:**
    1. get_file_graph - Get file structure and dependencies
    2. analyze_architecture_patterns - Detect architecture patterns
    3. get_function_callers - Find all callers of a function
    4. get_module_dependencies - Get imports and importers

    **ANALYSIS APPROACH:**
    1. Start with high-level structure (get_file_graph)
    2. Identify architecture patterns
    3. Map critical dependencies
    4. Find entry points and public APIs

    **CRYPTO PROJECT PATTERNS:**
    - Protocol implementations (adapters, routers)
    - Smart contract organization (contracts/, interfaces/, libraries/)
    - DeFi patterns (pools, vaults, oracles)
    - SDK/client structures

    **OUTPUT FORMAT:**
    - Provide visual structure when helpful
    - Note architecture decisions
    - Identify potential issues (circular deps, god modules)
    - Suggest improvements

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
    tools=[file_graph_tool, patterns_tool, callers_tool, deps_tool],
    output_key="architecture_analysis",
)
