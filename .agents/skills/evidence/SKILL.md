---
name: evidence
description: Expert assistance for Evidence.dev BI dashboards. Use when users need SQL-driven analytics, markdown-based reports, data visualization components, or business intelligence as code.
---

# Evidence - BI as Code

**Version:** latest | **Last Updated:** 2025-01

## Overview

Evidence.dev is a framework for building data products with SQL and markdown:

- **Markdown-First**: Write reports in markdown
- **SQL-Driven**: Queries power visualizations
- **Rich Components**: Charts, tables, KPIs, inputs
- **Browser Execution**: DuckDB WebAssembly for fast queries
- **Version Control**: Dashboards as code

**Documentation**: https://docs.evidence.dev

## When to Use This Skill

Activate when users need:

- "Build analytics dashboards with SQL"
- "Create interactive reports"
- "Set up business intelligence as code"
- "Add charts and visualizations to markdown"
- "Build data-driven web applications"

## Core Concepts

### 1. Project Structure

```
my-project/
├── pages/                    # Markdown pages (routes)
│   ├── index.md             # Home page (/)
│   ├── sales.md             # /sales
│   └── customers/
│       ├── index.md         # /customers
│       └── [customer].md    # /customers/:customer
├── sources/                  # Data source queries
│   └── my_database/
│       └── orders.sql
├── queries/                  # Reusable SQL files
├── partials/                 # Reusable markdown
├── components/               # Custom Svelte components
├── evidence.config.yaml      # Configuration
└── package.json
```

### 2. Basic Dashboard Page

```markdown
---
title: Sales Dashboard
---

# Sales Dashboard

```sql total_sales
SELECT
    SUM(amount) as total,
    COUNT(*) as orders,
    COUNT(DISTINCT customer_id) as customers
FROM orders
WHERE order_date >= '2024-01-01'
```

<Grid cols=3>
    <BigValue data={total_sales} value=total fmt=usd0 title="Total Revenue" />
    <BigValue data={total_sales} value=orders title="Orders" />
    <BigValue data={total_sales} value=customers title="Customers" />
</Grid>

## Monthly Trend

```sql monthly_sales
SELECT
    date_trunc('month', order_date) as month,
    SUM(amount) as revenue
FROM orders
GROUP BY 1
ORDER BY 1
```

<LineChart
    data={monthly_sales}
    x=month
    y=revenue
    yFmt=usd0
    title="Revenue by Month"
/>
```

### 3. Interactive Filtering

```markdown
```sql categories
SELECT DISTINCT category FROM products ORDER BY 1
```

<Dropdown
    name=category_filter
    data={categories}
    value=category
    title="Category"
    defaultValue="All"
>
    <DropdownOption value="All" valueLabel="All Categories" />
</Dropdown>

```sql filtered_sales
SELECT * FROM sales
WHERE
    CASE WHEN '${inputs.category_filter.value}' = 'All'
         THEN TRUE
         ELSE category = '${inputs.category_filter.value}'
    END
```

<DataTable data={filtered_sales} search=true />
```

### 4. Query Chaining

```markdown
```sql base_orders
SELECT * FROM orders WHERE status = 'completed'
```

```sql order_summary
SELECT
    category,
    SUM(amount) as total,
    COUNT(*) as count
FROM ${base_orders}
GROUP BY 1
ORDER BY total DESC
```

<BarChart data={order_summary} x=category y=total />
```

### 5. Component Reference

**Data Components**
```markdown
<!-- Inline value -->
Total: <Value data={sales} column=total fmt=usd0 />

<!-- KPI Card -->
<BigValue
    data={metrics}
    value=revenue
    fmt=usd0
    title="Revenue"
    comparison=prev_revenue
    comparisonFmt=pct1
    comparisonTitle="vs Last Month"
/>

<!-- Delta indicator -->
<Delta data={metrics} column=change fmt=pct1 />
```

**Charts**
```markdown
<!-- Line Chart -->
<LineChart
    data={trend}
    x=date
    y=value
    series=category
    yFmt=num0
/>

<!-- Bar Chart -->
<BarChart
    data={breakdown}
    x=category
    y=amount
    yFmt=usd0
    swapXY=true
/>

<!-- Area Chart -->
<AreaChart
    data={stacked}
    x=month
    y=value
    series=region
/>

<!-- Scatter Plot -->
<ScatterPlot
    data={correlation}
    x=revenue
    y=customers
    series=segment
/>
```

**Tables**
```markdown
<DataTable
    data={orders}
    search=true
    rows=20
    link=detail_link
>
    <Column id=order_id title="Order" />
    <Column id=amount fmt=usd2 title="Amount" />
    <Column id=date fmt=shortdate title="Date" />
    <Column id=status title="Status" />
</DataTable>
```

**Inputs**
```markdown
<!-- Dropdown -->
<Dropdown name=region data={regions} value=region_name />

<!-- Multi-select -->
<Dropdown name=categories data={cats} value=category multiple=true />

<!-- Date Range -->
<DateRange
    name=date_range
    start="2024-01-01"
    end="2024-12-31"
/>

<!-- Slider -->
<Slider name=threshold min=0 max=100 step=10 />

<!-- Text Input -->
<TextInput name=search placeholder="Search..." />

<!-- Button Group -->
<ButtonGroup name=view>
    <ButtonGroupItem value="day" valueLabel="Daily" />
    <ButtonGroupItem value="week" valueLabel="Weekly" />
    <ButtonGroupItem value="month" valueLabel="Monthly" default />
</ButtonGroup>
```

### 6. Templated Pages

```markdown
<!-- pages/customers/[customer].md -->
---
title: Customer Details
---

# Customer: {params.customer}

```sql customer_data
SELECT * FROM customers WHERE customer_name = '${params.customer}'
```

```sql customer_orders
SELECT * FROM orders WHERE customer_id = (
    SELECT customer_id FROM customers
    WHERE customer_name = '${params.customer}'
)
ORDER BY order_date DESC
```

<DataTable data={customer_orders} />
```

```markdown
<!-- Link to templated page -->
```sql customers
SELECT
    customer_name,
    '/customers/' || customer_name as customer_link,
    SUM(amount) as total
FROM orders
JOIN customers USING (customer_id)
GROUP BY 1, 2
```

<DataTable data={customers} link=customer_link />
```

### 7. Formatting

```markdown
<!-- Built-in formats -->
<Value value=1234567 fmt=num0 />       <!-- 1,234,567 -->
<Value value=1234567 fmt=num0k />      <!-- 1,235K -->
<Value value=1234.56 fmt=usd2 />       <!-- $1,234.56 -->
<Value value=0.1234 fmt=pct1 />        <!-- 12.3% -->

<!-- In SQL (suffix convention) -->
```sql formatted
SELECT
    revenue as revenue_usd0,
    growth as growth_pct1,
    order_date as order_date_shortdate
FROM summary
```

<!-- Using fmt function -->
Revenue: {fmt(data[0].revenue, 'usd0')}
```

### 8. Layout Components

```markdown
<!-- Grid -->
<Grid cols=4>
    <BigValue ... />
    <BigValue ... />
    <BigValue ... />
    <BigValue ... />
</Grid>

<!-- Tabs -->
<Tabs>
    <Tab label="Overview">
        Content for overview tab
    </Tab>
    <Tab label="Details">
        Content for details tab
    </Tab>
</Tabs>

<!-- Accordion -->
<Accordion>
    <AccordionItem title="Section 1">
        Expandable content
    </AccordionItem>
</Accordion>
```

### 9. Conditional Rendering

```markdown
{#if data.length > 0}
    <DataTable data={data} />
{:else}
    <Alert status=info>No data available</Alert>
{/if}

{#each customers as customer}
    - {customer.name}: {fmt(customer.revenue, 'usd0')}
{/each}
```

### 10. Data Sources

```yaml
# sources/postgres_db/connection.yaml
name: postgres_db
type: postgres
options:
  host: localhost
  port: 5432
  database: analytics
  user: ${POSTGRES_USER}
  password: ${POSTGRES_PASSWORD}
```

```sql
-- sources/postgres_db/daily_sales.sql
SELECT
    date_trunc('day', order_date) as date,
    SUM(amount) as revenue
FROM orders
GROUP BY 1
ORDER BY 1
```

```markdown
<!-- Reference in pages -->
```sql sales
SELECT * FROM postgres_db.daily_sales
```
```

## CLI Commands

```bash
# Development
npm run dev              # Start dev server
npm run sources          # Run source queries

# Production
npm run build            # Build for production
npm run build:strict     # Strict mode (fail on errors)

# Preview
npm run preview          # Preview production build
```

## Best Practices

1. **Name Queries**: Always provide query names
2. **Format Values**: Use fmt on all numbers/dates
3. **Handle Empty Data**: Add conditional rendering
4. **Use Grid**: For responsive layouts
5. **Pre-aggregate**: Aggregate in source queries
6. **Limit Rows**: Keep page queries under 100K rows
7. **Add Titles**: Label all charts and KPIs

## Troubleshooting

### Query Not Working
1. Check query has a name
2. Verify SQL syntax
3. Run `npm run sources` to refresh data

### Component Not Rendering
1. Verify `data={query_name}` binding
2. Check column names match
3. Ensure query returns data

### Filtering Not Working
1. Check `inputs.name.value` syntax
2. Verify quotes in SQL
3. Add default value handling

### Performance Issues
1. Pre-aggregate in sources
2. Limit row counts
3. Use pagination for large tables

## Resources

- **Documentation**: https://docs.evidence.dev
- **Components**: https://docs.evidence.dev/components/
- **Examples**: https://evidence.dev/examples
- **GitHub**: https://github.com/evidence-dev/evidence
- **Slack**: https://slack.evidence.dev
