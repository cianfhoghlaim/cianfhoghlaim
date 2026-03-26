# Data Unified - Documentation Index

Welcome to the Data Unified project! This index will help you find the information you need.

## 📚 Documentation Files

### Getting Started

- **[QUICKSTART.md](./QUICKSTART.md)** - Get up and running in 5 minutes
  - Installation steps
  - First API calls
  - Common commands
  - Troubleshooting

### Core Documentation

- **[README.md](./README.md)** - Main project documentation
  - Overview and features
  - Installation guide
  - API reference
  - Project structure
  - Performance considerations

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Architecture and design
  - System architecture
  - Component details
  - Data flow examples
  - Design patterns
  - Scalability considerations

### Examples & Usage

- **[EXAMPLES.md](./EXAMPLES.md)** - Detailed usage examples
  - Basic operations
  - Analytics queries
  - Caching patterns
  - Advanced use cases
  - Performance testing

### Reference

- **[STRUCTURE.txt](./STRUCTURE.txt)** - Project structure reference
  - Directory layout
  - File descriptions
  - Feature checklist

## 🚀 Quick Links

### For First-Time Users
1. Start with [QUICKSTART.md](./QUICKSTART.md)
2. Run the setup script: `./scripts/setup.sh`
3. Try the examples in [EXAMPLES.md](./EXAMPLES.md)

### For Developers
1. Read [ARCHITECTURE.md](./ARCHITECTURE.md) for design patterns
2. Check [README.md](./README.md) for API reference
3. Review source code in `src/`

### For Integration
1. Study the caching patterns in `src/cache/patterns.ts`
2. Review DuckDB queries in `src/duckdb/queries.ts`
3. Explore BAML schemas in `baml_src/main.baml`

## 📁 Source Code Organization

```
src/
├── index.ts              # Main application entry point
├── duckdb/
│   ├── client.ts         # DuckDB connection management
│   └── queries.ts        # Analytical query functions
├── cache/
│   ├── redis.ts          # Redis client and utilities
│   └── patterns.ts       # Caching pattern implementations
└── baml/
    └── schemas.ts        # BAML schema type definitions

baml_src/
├── main.baml             # BAML schema and function definitions
└── generators.baml       # Code generation configuration
```

## 🛠️ Key Features by File

### DuckDB Features
- **client.ts**: Connection, initialization, extensions
- **queries.ts**: Analytics, time series, cohort analysis

### Cache Features
- **redis.ts**: Client, basic ops, hash ops
- **patterns.ts**: Cache-aside, write-through, stale-while-revalidate

### BAML Features
- **main.baml**: Schemas, LLM clients, functions
- **schemas.ts**: TypeScript types, validators

### API Features
- **index.ts**: REST endpoints, validation, error handling

## 📖 Learning Path

### Beginner
1. Run quickstart
2. Try basic examples
3. Understand caching patterns

### Intermediate
1. Study architecture
2. Explore query patterns
3. Customize endpoints

### Advanced
1. Optimize queries
2. Implement new patterns
3. Extend BAML schemas

## 🔗 External Resources

- [DuckDB Documentation](https://duckdb.org/docs/)
- [Dragonfly Documentation](https://www.dragonflydb.io/docs)
- [BAML Documentation](https://docs.boundaryml.com)
- [Hono Documentation](https://hono.dev/)
- [Zod Documentation](https://zod.dev/)

## 📊 Stats

- **Total Lines of Code**: ~1,864
- **Source Files**: 8 TypeScript files, 2 BAML files
- **Documentation**: 5 markdown files
- **Scripts**: 2 utility scripts

## 🎯 Common Tasks

| Task | Documentation | Command |
|------|--------------|---------|
| Setup project | QUICKSTART.md | `./scripts/setup.sh` |
| Start server | QUICKSTART.md | `npm run dev` |
| Test API | EXAMPLES.md | `./scripts/test-api.sh` |
| Create data | EXAMPLES.md | `curl -X POST /seed` |
| View cache | EXAMPLES.md | `curl /cache/info` |
| Custom query | EXAMPLES.md | `curl -X POST /analytics/query` |

## 💡 Tips

- Use QUICKSTART.md for your first setup
- Reference EXAMPLES.md when implementing features
- Consult ARCHITECTURE.md when scaling or optimizing
- Keep README.md handy for API reference

## 🤝 Contributing

This is a reference implementation. Feel free to:
- Adapt patterns for your use case
- Extend with new features
- Share improvements

---

**Need help?** Start with QUICKSTART.md or check the specific documentation file for your topic.
