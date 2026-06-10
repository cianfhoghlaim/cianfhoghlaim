import marimo

__generated_with = "0.13.11"
app = marimo.App(width="columns")


@app.cell
def _():
    import marimo as mo
    return (mo,)

@app.cell
def _(mo):
    _df = mo.sql(
        f"""
        INSTALL httpfs;
        LOAD httpfs;
        INSTALL iceberg;
        LOAD iceberg;

        -- Define R2 Credentials
        CREATE SECRET r2_secret (
            TYPE R2,
            KEY_ID 'your_r2_access_key_id',
            SECRET 'your_r2_secret_access_key',
            ACCOUNT_ID 'your_cloudflare_account_id'
        );

        -- Attach the R2 REST Catalog
        -- This turns the R2 bucket into a queryable database schema
        ATTACH 'r2_catalog' (
            TYPE ICEBERG,
            CONNECTION_URL 'https://<account_id>.r2.cloudflarestorage.com/v1/iceberg/catalog',
            TOKEN 'your_bearer_token' -- If using token-based auth for the catalog
        );
        """
    )
    return





@app.cell
def _(mo):
    _df = mo.sql(
        f"""
        INSTALL ducklake;
        ATTACH 'ducklake:metadata.ducklake' AS myducklake;
        """
    )
    return


if __name__ == "__main__":
    app.run()
