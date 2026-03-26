// @ts-expect-error React import needed for classic JSX runtime
import React, { useState, useRef } from 'react';
import {
  SQLWorkbenchEmbedded,
  SQLWorkbenchProvider,
  useSQLWorkbench,
  type SQLWorkbenchEmbeddedRef,
  type Theme
} from '../index';
import './App.css';

function DemoContent() {
  const { isReady, error } = useSQLWorkbench();
  const [theme, setTheme] = useState<Theme>('auto');
  const [editable, setEditable] = useState(true);
  const workbenchRef = useRef<SQLWorkbenchEmbeddedRef>(null);

  const examples = [
    {
      title: 'Simple Series',
      code: 'SELECT * FROM generate_series(1, 10);'
    },
    {
      title: 'Date Range',
      code: `SELECT
  date,
  day_name
FROM generate_series(
  DATE '2024-01-01',
  DATE '2024-01-07',
  INTERVAL 1 DAY
) AS t(date)
CROSS JOIN (
  SELECT dayname(date) AS day_name
) AS d;`
    },
    {
      title: 'Aggregation',
      code: `WITH sales AS (
  SELECT
    unnest(['Electronics', 'Clothing', 'Food', 'Electronics', 'Food']) AS category,
    unnest([1200, 450, 890, 2100, 760]) AS amount
)
SELECT
  category,
  COUNT(*) AS transactions,
  SUM(amount) AS total_sales,
  AVG(amount) AS avg_sale
FROM sales
GROUP BY category
ORDER BY total_sales DESC;`
    }
  ];

  const [currentExample, setCurrentExample] = useState(examples[0].code);

  if (error) {
    return (
      <div className="error">
        <h2>Error Loading SQL Workbench</h2>
        <p>{error.message}</p>
      </div>
    );
  }

  if (!isReady) {
    return (
      <div className="loading">
        <h2>Loading SQL Workbench...</h2>
      </div>
    );
  }

  return (
    <div className="app">
      <header>
        <h1>React SQL Workbench Embedded</h1>
        <p>A React wrapper for sql-workbench-embedded with DuckDB WASM</p>
      </header>

      <div className="controls">
        <div className="control-group">
          <label htmlFor="theme-select">Theme:</label>
          <select
            id="theme-select"
            value={theme}
            onChange={(e) => setTheme(e.target.value as 'light' | 'dark' | 'auto')}
          >
            <option value="auto">Auto</option>
            <option value="light">Light</option>
            <option value="dark">Dark</option>
          </select>
        </div>

        <div className="control-group">
          <label htmlFor="editable-checkbox">
            <input
              id="editable-checkbox"
              type="checkbox"
              checked={editable}
              onChange={(e) => setEditable(e.target.checked)}
            />
            Editable
          </label>
        </div>

        <div className="control-group">
          <label htmlFor="example-select">Example:</label>
          <select
            id="example-select"
            onChange={(e) => {
              const example = examples.find(ex => ex.title === e.target.value);
              if (example) setCurrentExample(example.code);
            }}
          >
            {examples.map((ex) => (
              <option key={ex.title} value={ex.title}>
                {ex.title}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="workbench-container">
        <SQLWorkbenchEmbedded
          ref={workbenchRef}
          key={`${theme}-${editable}-${currentExample}`}
          initialCode={currentExample}
          theme={theme}
          editable={editable}
          showOpenButton={true}
          onReady={(instance) => {
            console.log('SQL Workbench instance ready:', instance);
          }}
          onError={(error) => {
            console.error('SQL Workbench error:', error);
          }}
        />
      </div>

      <footer>
        <p>
          Built with <a href="https://github.com/tobilg/sql-workbench-embedded" target="_blank" rel="noopener noreferrer">sql-workbench-embedded</a>
        </p>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <SQLWorkbenchProvider
      config={{
        theme: 'auto',
        editable: true,
        initQueries: [
          // You can add DuckDB initialization queries here
          // e.g., "INSTALL spatial", "LOAD spatial"
        ]
      }}
      onReady={() => {
        console.log('SQL Workbench provider ready');
      }}
      onError={(error) => {
        console.error('SQL Workbench provider error:', error);
      }}
    >
      <DemoContent />
    </SQLWorkbenchProvider>
  );
}
