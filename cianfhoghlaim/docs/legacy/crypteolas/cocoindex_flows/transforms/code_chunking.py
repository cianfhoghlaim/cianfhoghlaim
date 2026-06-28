"""
Code Chunking Transforms for Crypteolas.

Provides semantic code chunking using tree-sitter for
language-aware splitting of code into meaningful units.
"""

from dataclasses import dataclass
from typing import Iterator


@dataclass
class CodeChunk:
    """A chunk of code with metadata."""

    text: str
    start_line: int
    end_line: int
    chunk_type: str  # function, class, method, module, block
    name: str | None = None
    language: str | None = None


def chunk_python(code: str, max_chunk_size: int = 1000) -> Iterator[CodeChunk]:
    """
    Chunk Python code by semantic units.

    Splits on:
    - Function definitions
    - Class definitions
    - Method definitions
    - Module-level blocks
    """
    try:
        import tree_sitter_python as tspython
        from tree_sitter import Language, Parser

        PY_LANGUAGE = Language(tspython.language())
        parser = Parser(PY_LANGUAGE)

        tree = parser.parse(bytes(code, "utf-8"))
        root = tree.root_node

        for child in root.children:
            if child.type in ("function_definition", "class_definition"):
                chunk_text = code[child.start_byte : child.end_byte]

                # Extract name
                name = None
                for subchild in child.children:
                    if subchild.type == "identifier":
                        name = code[subchild.start_byte : subchild.end_byte]
                        break

                # If chunk is too large, split by methods
                if len(chunk_text) > max_chunk_size and child.type == "class_definition":
                    # First yield the class signature
                    body_start = None
                    for subchild in child.children:
                        if subchild.type == "block":
                            body_start = subchild.start_byte
                            break

                    if body_start:
                        yield CodeChunk(
                            text=code[child.start_byte : body_start],
                            start_line=child.start_point[0] + 1,
                            end_line=child.start_point[0] + 1,
                            chunk_type="class_signature",
                            name=name,
                            language="python",
                        )

                    # Then yield each method
                    for subchild in child.children:
                        if subchild.type == "block":
                            for block_child in subchild.children:
                                if block_child.type == "function_definition":
                                    method_text = code[
                                        block_child.start_byte : block_child.end_byte
                                    ]
                                    method_name = None
                                    for mc in block_child.children:
                                        if mc.type == "identifier":
                                            method_name = code[mc.start_byte : mc.end_byte]
                                            break
                                    yield CodeChunk(
                                        text=method_text,
                                        start_line=block_child.start_point[0] + 1,
                                        end_line=block_child.end_point[0] + 1,
                                        chunk_type="method",
                                        name=f"{name}.{method_name}" if name and method_name else method_name,
                                        language="python",
                                    )
                else:
                    yield CodeChunk(
                        text=chunk_text,
                        start_line=child.start_point[0] + 1,
                        end_line=child.end_point[0] + 1,
                        chunk_type="function" if child.type == "function_definition" else "class",
                        name=name,
                        language="python",
                    )

    except ImportError:
        # Fallback to simple line-based chunking
        lines = code.split("\n")
        current_chunk: list[str] = []
        start_line = 1

        for i, line in enumerate(lines, 1):
            current_chunk.append(line)

            # Split on function/class definitions
            if line.strip().startswith(("def ", "class ", "async def ")):
                if len(current_chunk) > 1:
                    yield CodeChunk(
                        text="\n".join(current_chunk[:-1]),
                        start_line=start_line,
                        end_line=i - 1,
                        chunk_type="block",
                        language="python",
                    )
                    current_chunk = [line]
                    start_line = i

            # Also split if chunk gets too large
            if len("\n".join(current_chunk)) > max_chunk_size:
                yield CodeChunk(
                    text="\n".join(current_chunk),
                    start_line=start_line,
                    end_line=i,
                    chunk_type="block",
                    language="python",
                )
                current_chunk = []
                start_line = i + 1

        if current_chunk:
            yield CodeChunk(
                text="\n".join(current_chunk),
                start_line=start_line,
                end_line=len(lines),
                chunk_type="block",
                language="python",
            )


def chunk_javascript(code: str, max_chunk_size: int = 1000) -> Iterator[CodeChunk]:
    """
    Chunk JavaScript/TypeScript code by semantic units.

    Splits on:
    - Function declarations
    - Class declarations
    - Arrow function assignments
    - Export statements
    """
    try:
        import tree_sitter_javascript as tsjs
        from tree_sitter import Language, Parser

        JS_LANGUAGE = Language(tsjs.language())
        parser = Parser(JS_LANGUAGE)

        tree = parser.parse(bytes(code, "utf-8"))
        root = tree.root_node

        for child in root.children:
            if child.type in (
                "function_declaration",
                "class_declaration",
                "lexical_declaration",
                "export_statement",
            ):
                chunk_text = code[child.start_byte : child.end_byte]

                if len(chunk_text) <= max_chunk_size:
                    yield CodeChunk(
                        text=chunk_text,
                        start_line=child.start_point[0] + 1,
                        end_line=child.end_point[0] + 1,
                        chunk_type=child.type.replace("_", " "),
                        language="javascript",
                    )

    except ImportError:
        # Fallback to simple chunking
        lines = code.split("\n")
        current_chunk: list[str] = []
        start_line = 1

        for i, line in enumerate(lines, 1):
            current_chunk.append(line)

            if len("\n".join(current_chunk)) > max_chunk_size:
                yield CodeChunk(
                    text="\n".join(current_chunk),
                    start_line=start_line,
                    end_line=i,
                    chunk_type="block",
                    language="javascript",
                )
                current_chunk = []
                start_line = i + 1

        if current_chunk:
            yield CodeChunk(
                text="\n".join(current_chunk),
                start_line=start_line,
                end_line=len(lines),
                chunk_type="block",
                language="javascript",
            )


def chunk_solidity(code: str, max_chunk_size: int = 1000) -> Iterator[CodeChunk]:
    """
    Chunk Solidity code by semantic units.

    Splits on:
    - Contract definitions
    - Interface definitions
    - Function definitions
    - Event definitions
    """
    # Simple regex-based chunking for Solidity
    import re

    # Find contract/interface boundaries
    contract_pattern = re.compile(
        r"(contract|interface|library)\s+(\w+).*?\{",
        re.DOTALL,
    )

    matches = list(contract_pattern.finditer(code))

    if not matches:
        yield CodeChunk(
            text=code,
            start_line=1,
            end_line=code.count("\n") + 1,
            chunk_type="module",
            language="solidity",
        )
        return

    for i, match in enumerate(matches):
        # Find the end of this contract (matching brace)
        start = match.start()
        brace_count = 0
        end = start

        for j, char in enumerate(code[start:]):
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1
                if brace_count == 0:
                    end = start + j + 1
                    break

        chunk_text = code[start:end]
        start_line = code[:start].count("\n") + 1
        end_line = code[:end].count("\n") + 1

        yield CodeChunk(
            text=chunk_text,
            start_line=start_line,
            end_line=end_line,
            chunk_type=match.group(1),
            name=match.group(2),
            language="solidity",
        )


def chunk_rust(code: str, max_chunk_size: int = 1000) -> Iterator[CodeChunk]:
    """
    Chunk Rust code by semantic units.

    Splits on:
    - Function definitions (fn)
    - Struct definitions
    - Impl blocks
    - Trait definitions
    - Module definitions
    """
    try:
        import tree_sitter_rust as tsrust
        from tree_sitter import Language, Parser

        RUST_LANGUAGE = Language(tsrust.language())
        parser = Parser(RUST_LANGUAGE)

        tree = parser.parse(bytes(code, "utf-8"))
        root = tree.root_node

        for child in root.children:
            if child.type in (
                "function_item",
                "struct_item",
                "impl_item",
                "trait_item",
                "mod_item",
                "enum_item",
            ):
                chunk_text = code[child.start_byte : child.end_byte]

                # Extract name
                name = None
                for subchild in child.children:
                    if subchild.type in ("identifier", "type_identifier"):
                        name = code[subchild.start_byte : subchild.end_byte]
                        break

                if len(chunk_text) <= max_chunk_size:
                    yield CodeChunk(
                        text=chunk_text,
                        start_line=child.start_point[0] + 1,
                        end_line=child.end_point[0] + 1,
                        chunk_type=child.type.replace("_item", "").replace("_", " "),
                        name=name,
                        language="rust",
                    )
                else:
                    # Split large impl blocks by methods
                    if child.type == "impl_item":
                        for subchild in child.children:
                            if subchild.type == "declaration_list":
                                for method in subchild.children:
                                    if method.type == "function_item":
                                        method_text = code[method.start_byte : method.end_byte]
                                        method_name = None
                                        for mc in method.children:
                                            if mc.type == "identifier":
                                                method_name = code[mc.start_byte : mc.end_byte]
                                                break
                                        yield CodeChunk(
                                            text=method_text,
                                            start_line=method.start_point[0] + 1,
                                            end_line=method.end_point[0] + 1,
                                            chunk_type="method",
                                            name=f"{name}::{method_name}" if name else method_name,
                                            language="rust",
                                        )
                    else:
                        yield CodeChunk(
                            text=chunk_text,
                            start_line=child.start_point[0] + 1,
                            end_line=child.end_point[0] + 1,
                            chunk_type=child.type.replace("_item", ""),
                            name=name,
                            language="rust",
                        )

    except ImportError:
        # Fallback to simple chunking
        import re

        fn_pattern = re.compile(r"^(?:pub\s+)?(?:async\s+)?fn\s+(\w+)", re.MULTILINE)
        struct_pattern = re.compile(r"^(?:pub\s+)?struct\s+(\w+)", re.MULTILINE)
        impl_pattern = re.compile(r"^impl(?:<[^>]+>)?\s+(\w+)", re.MULTILINE)

        lines = code.split("\n")
        current_chunk: list[str] = []
        start_line = 1

        for i, line in enumerate(lines, 1):
            current_chunk.append(line)

            if fn_pattern.match(line.strip()) or struct_pattern.match(line.strip()) or impl_pattern.match(line.strip()):
                if len(current_chunk) > 1:
                    yield CodeChunk(
                        text="\n".join(current_chunk[:-1]),
                        start_line=start_line,
                        end_line=i - 1,
                        chunk_type="block",
                        language="rust",
                    )
                    current_chunk = [line]
                    start_line = i

            if len("\n".join(current_chunk)) > max_chunk_size:
                yield CodeChunk(
                    text="\n".join(current_chunk),
                    start_line=start_line,
                    end_line=i,
                    chunk_type="block",
                    language="rust",
                )
                current_chunk = []
                start_line = i + 1

        if current_chunk:
            yield CodeChunk(
                text="\n".join(current_chunk),
                start_line=start_line,
                end_line=len(lines),
                chunk_type="block",
                language="rust",
            )


def chunk_go(code: str, max_chunk_size: int = 1000) -> Iterator[CodeChunk]:
    """
    Chunk Go code by semantic units.

    Splits on:
    - Function declarations
    - Method declarations
    - Type declarations (struct, interface)
    - Package-level variables
    """
    try:
        import tree_sitter_go as tsgo
        from tree_sitter import Language, Parser

        GO_LANGUAGE = Language(tsgo.language())
        parser = Parser(GO_LANGUAGE)

        tree = parser.parse(bytes(code, "utf-8"))
        root = tree.root_node

        for child in root.children:
            if child.type in (
                "function_declaration",
                "method_declaration",
                "type_declaration",
                "var_declaration",
                "const_declaration",
            ):
                chunk_text = code[child.start_byte : child.end_byte]

                # Extract name
                name = None
                for subchild in child.children:
                    if subchild.type == "identifier":
                        name = code[subchild.start_byte : subchild.end_byte]
                        break
                    elif subchild.type == "type_spec":
                        for tsc in subchild.children:
                            if tsc.type == "type_identifier":
                                name = code[tsc.start_byte : tsc.end_byte]
                                break

                if len(chunk_text) <= max_chunk_size:
                    yield CodeChunk(
                        text=chunk_text,
                        start_line=child.start_point[0] + 1,
                        end_line=child.end_point[0] + 1,
                        chunk_type=child.type.replace("_declaration", "").replace("_", " "),
                        name=name,
                        language="go",
                    )

    except ImportError:
        # Fallback to simple chunking
        import re

        func_pattern = re.compile(r"^func\s+(?:\([^)]+\)\s+)?(\w+)", re.MULTILINE)
        type_pattern = re.compile(r"^type\s+(\w+)", re.MULTILINE)

        lines = code.split("\n")
        current_chunk: list[str] = []
        start_line = 1

        for i, line in enumerate(lines, 1):
            current_chunk.append(line)

            if func_pattern.match(line.strip()) or type_pattern.match(line.strip()):
                if len(current_chunk) > 1:
                    yield CodeChunk(
                        text="\n".join(current_chunk[:-1]),
                        start_line=start_line,
                        end_line=i - 1,
                        chunk_type="block",
                        language="go",
                    )
                    current_chunk = [line]
                    start_line = i

            if len("\n".join(current_chunk)) > max_chunk_size:
                yield CodeChunk(
                    text="\n".join(current_chunk),
                    start_line=start_line,
                    end_line=i,
                    chunk_type="block",
                    language="go",
                )
                current_chunk = []
                start_line = i + 1

        if current_chunk:
            yield CodeChunk(
                text="\n".join(current_chunk),
                start_line=start_line,
                end_line=len(lines),
                chunk_type="block",
                language="go",
            )


# Supported languages with Tree-sitter
TREE_SITTER_LANGUAGES = {
    "python": "tree_sitter_python",
    "javascript": "tree_sitter_javascript",
    "typescript": "tree_sitter_typescript",
    "rust": "tree_sitter_rust",
    "go": "tree_sitter_go",
    "solidity": "tree_sitter_solidity",
}


def chunk_code(
    code: str,
    language: str,
    max_chunk_size: int = 1000,
) -> Iterator[CodeChunk]:
    """
    Chunk code based on detected language.

    Parameters:
        code: Source code string
        language: Programming language
        max_chunk_size: Maximum characters per chunk

    Yields:
        CodeChunk objects
    """
    chunkers = {
        "python": chunk_python,
        "javascript": chunk_javascript,
        "typescript": chunk_javascript,
        "solidity": chunk_solidity,
        "rust": chunk_rust,
        "go": chunk_go,
    }

    chunker = chunkers.get(language)
    if chunker:
        yield from chunker(code, max_chunk_size)
    else:
        # Generic line-based fallback
        lines = code.split("\n")
        current_chunk: list[str] = []
        start_line = 1

        for i, line in enumerate(lines, 1):
            current_chunk.append(line)

            if len("\n".join(current_chunk)) > max_chunk_size:
                yield CodeChunk(
                    text="\n".join(current_chunk),
                    start_line=start_line,
                    end_line=i,
                    chunk_type="block",
                    language=language,
                )
                current_chunk = []
                start_line = i + 1

        if current_chunk:
            yield CodeChunk(
                text="\n".join(current_chunk),
                start_line=start_line,
                end_line=len(lines),
                chunk_type="block",
                language=language,
            )
