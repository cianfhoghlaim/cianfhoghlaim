import marimo

__generated_with = "0.10.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import json
    return mo, pd, json


@app.cell
def _(mo):
    mo.md(
        """
        # Analytics Dashboard

        This is an embedded marimo notebook serving as an interactive analytics dashboard.
        The notebook is accessed through an authenticated reverse proxy.
        """
    )
    return


@app.cell
def _(mo):
    # Interactive controls
    category = mo.ui.dropdown(
        options=["A", "B", "C", "D", "All"],
        value="All",
        label="Select Category"
    )

    sample_size = mo.ui.slider(
        start=10,
        stop=100,
        step=10,
        value=50,
        label="Sample Size"
    )

    mo.hstack([category, sample_size])
    return category, sample_size


@app.cell
def _(pd, category, sample_size):
    # Generate sample data
    import random
    random.seed(42)

    data = pd.DataFrame({
        "id": range(1, sample_size.value + 1),
        "value": [random.randint(10, 100) for _ in range(sample_size.value)],
        "category": [random.choice(["A", "B", "C", "D"]) for _ in range(sample_size.value)],
    })

    # Filter by category if selected
    if category.value != "All":
        filtered_data = data[data["category"] == category.value]
    else:
        filtered_data = data

    filtered_data
    return data, filtered_data, random


@app.cell
def _(filtered_data, mo):
    # Display statistics
    stats = filtered_data.describe()
    mo.md(f"""
    ## Statistics

    - **Count**: {len(filtered_data)}
    - **Mean Value**: {filtered_data['value'].mean():.2f}
    - **Max Value**: {filtered_data['value'].max()}
    - **Min Value**: {filtered_data['value'].min()}
    """)
    return stats,


@app.cell
def _(filtered_data, mo):
    # Create a simple visualization using marimo's built-in plotting
    import altair as alt

    chart = alt.Chart(filtered_data).mark_bar().encode(
        x=alt.X("category:N", title="Category"),
        y=alt.Y("mean(value):Q", title="Average Value"),
        color="category:N"
    ).properties(
        width=400,
        height=300,
        title="Average Value by Category"
    )

    mo.ui.altair_chart(chart)
    return alt, chart


@app.cell
def _(mo):
    # Access request metadata (useful for auth context)
    app_meta = mo.app_meta()
    mo.md(f"""
    ## Request Context

    This section shows metadata about the current request,
    which can be used for authentication context.

    ```
    {app_meta}
    ```
    """)
    return app_meta,


if __name__ == "__main__":
    app.run()
