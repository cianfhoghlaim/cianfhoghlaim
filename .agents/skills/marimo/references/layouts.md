# Marimo Layouts (multi-column, sidebar, grid)

The canonical marimo layout patterns for the Cianfhoghlaim
platform. All dashboards use `width="full"` + multi-column
`@app.cell(column=N)` + (optionally) `layout_file="grid.json"`
for persistent layouts.

## Pattern 1: Multi-column header + body

```python
app = marimo.App(width="full")


@app.cell
def _():
    mo.md("# My Dashboard")
    return


@app.cell(column=1)
def _():
    mo.md("## Sidebar")
    mo.ui.dropdown(options=[...])
    return
```

## Pattern 2: Full sidebar

```python
app = marimo.App(width="full")


@app.cell
def _():
    mo.sidebar([
        mo.md("## Filters"),
        mo.ui.dropdown(options=[...]),
        mo.ui.slider(0, 100, value=50),
        mo.ui.date_range(),
    ], footer=[
        mo.md("---"),
        mo.md("Built with marimo"),
    ])
    return
```

## Pattern 3: Grid layout with persistent layout file

```python
app = marimo.App(width="full", layout_file="grid.json")
```

The user arranges cells in the editor; the layout is saved
to `grid.json` and restored on next load.

## Pattern 4: Tabs

```python
@app.cell
def _():
    mo.ui.tabs({
        "Overview": mo.md("..."),
        "Details": mo.ui.table(df),
        "Charts": mo.ui.altair_chart(chart),
    })
    return
```

## Pattern 5: Auto-refresh

```python
@app.cell
def _():
    interval = mo.ui.refresh(options=["1s", "3s", "5s", "off"])
    return (interval,)


@app.cell
def _():
    interval = _
    if interval.value != "off":
        import time
        time.sleep(int(interval.value[:-1]))
    df = fetch_live_data()
    return (df,)
```

## Pattern 6: Icons (lucide / material)

```python
@app.cell
def _():
    mo.icon("lucide:database")
    mo.icon("material:analytics")
    return
```

## Pattern 7: `mo.ui.altair_chart` with selection

```python
@app.cell
def _():
    import altair as alt
    chart = alt.Chart(df).mark_point().encode(x="x", y="y", color="category")
    mo.ui.altair_chart(chart, legend_selection=True, label="Select points")
    return
```

## KCG conventions

- All production dashboards use `width="full"` + multi-column
  layout
- The sidebar is the canonical place for filters (dropdown,
  slider, date range, multi-select)
- The footer of the sidebar is reserved for the "Built with
  marimo" credit (or a project-specific footer)
- Layouts persist via `layout_file=".../grid.json"` for any
  dashboard the user customises

## Resources

- Marimo layouts: <https://docs.marimo.io/guides/layouts/>
- Marimo UI components: <https://docs.marimo.io/api/ui/>
- Marimo sidebar: <https://docs.marimo.io/api/ui/sidebar/>
