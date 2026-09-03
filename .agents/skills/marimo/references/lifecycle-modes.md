# Marimo Lifecycle Modes (`edit` / `run` / `script`)

Marimo notebooks have 3 lifecycle modes. Use `mo.app_meta().mode`
and `mo.running_in_notebook()` to branch between them.

## The 3 modes

| Mode | When | Use case |
|:--|:--|:--|
| `edit` | `marimo edit notebook.py` | Interactive editing in the browser |
| `run` | `marimo run notebook.py` | Read-only interactive (no edit) |
| `script` | `uv run notebook.py` or `python notebook.py` | CLI / batch execution |

## `mo.app_meta().mode`

```python
@app.cell
def _():
    mode = mo.app_meta().mode
    if mode == "edit":
        # show edit hints
    elif mode == "run":
        # show the dashboard
    elif mode == "script":
        # run as a CLI
    return (mode,)
```

## `mo.running_in_notebook()`

Returns `True` when the notebook is running in the marimo
editor (edit or run mode), `False` when running as a script.

```python
@app.cell
def _():
    if not mo.running_in_notebook():
        # Don't show UI components when running headless
        result = do_batch_thing()
        print(result)
        sys.exit(0)
    return
```

## Combining with `argparse`

The canonical "notebook-as-CLI" pattern (`running_as_a_script/with_argparse.py`):

```python
import argparse
import sys


@app.setup
def _():
    if not mo.running_in_notebook():
        # Parse CLI args when running as a script
        parser = argparse.ArgumentParser()
        parser.add_argument("--query", required=True)
        parser.add_argument("--top-k", type=int, default=10)
        args = parser.parse_args()
        # Run the analysis headless
        result = run_analysis(args.query, args.top_k)
        print(result)
        sys.exit(0)
    return
```

## Marimo + Typer CLI

For more complex CLIs, use Typer (`typer-demo.py`):

```python
import typer

cli = typer.Typer()


@cli.command()
def main(query: str, top_k: int = 10):
    """Run the notebook headless."""
    result = run_analysis(query, top_k)
    print(result)


@app.cell
def _():
    if mo.app_meta().mode == "script":
        cli()
    return
```

## Marimo + FastMCP server in one file

For serving a notebook as an MCP server (`my-mcp.py`):

```python
import marimo as mo
from mcp.server.fastmcp import FastMCP

# Generate an app programmatically
app = marimo.App()


@app.setup
def setup_mcp():
    mcp = FastMCP("cianfhoghlaim-curriculum")
    return (mcp,)


@app.cell
def _():
    setup_mcp()
    # Register a tool
    @mcp.tool
    def query_curriculum(query: str) -> str:
        """Query the curriculum corpus."""
        return run_query(query)
    return


if __name__ == "__main__":
    if mo.app_meta().mode == "script":
        mcp.run()
    else:
        app.run()
```

## KCG conventions

- Notebooks intended to run as CLIs MUST use the
  `argparse` + `mo.running_in_notebook()` pattern
- Notebooks intended to serve as MCP servers MUST use the
  FastMCP + `@app.setup` pattern
- Notebooks intended to be edited interactively SHOULD
  default to `marimo edit` mode

## Resources

- Marimo lifecycle: <https://docs.marimo.io/guides/lifecycle/>
- Typer: <https://typer.tiangolo.com/>
- FastMCP: <https://github.com/jlowin/fastmcp>
