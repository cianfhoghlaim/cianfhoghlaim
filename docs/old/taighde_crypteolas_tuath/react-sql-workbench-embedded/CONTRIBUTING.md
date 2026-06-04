# Contributing to react-sql-workbench-embedded

Thank you for your interest in contributing to react-sql-workbench-embedded!

## Development Setup

### Prerequisites

- Node.js 18+
- npm or yarn
- Git

### Getting Started

1. Fork and clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/react-sql-workbench-embedded.git
cd react-sql-workbench-embedded
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

This will start Vite's dev server with the demo application at http://localhost:5173 (or another port if 5173 is in use).

## Project Structure

```
react-sql-workbench-embedded/
├── src/
│   ├── components/           # React components
│   │   ├── SQLWorkbenchEmbedded.tsx
│   │   ├── SQLWorkbenchProvider.tsx
│   │   └── __tests__/        # Component tests
│   ├── demo/                 # Demo application
│   │   ├── App.tsx
│   │   ├── App.css
│   │   └── main.tsx
│   ├── test/                 # Test utilities
│   │   └── setup.ts
│   ├── types.ts              # TypeScript types
│   └── index.ts              # Main entry point
├── dist/                     # Build output (generated)
├── vite.config.ts           # Vite configuration
├── vitest.config.ts         # Vitest configuration
├── tsconfig.json            # TypeScript config (dev)
└── tsconfig.build.json      # TypeScript config (build)
```

## Development Workflow

### Running Tests

```bash
# Run tests in watch mode
npm test

# Run tests once
npm test -- --run

# Run tests with UI
npm run test:ui

# Run tests with coverage
npm run test:coverage
```

### Building

```bash
# Build the library
npm run build
```

This will:
1. Run TypeScript compiler to generate type declarations
2. Run Vite to bundle the library

Output goes to the `dist/` directory.

### Linting

```bash
npm run lint
```

### Preview Build

```bash
# Build and preview
npm run build
npm run preview
```

## Making Changes

### Adding a New Feature

1. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes in the `src/` directory

3. Add tests for your changes in `src/components/__tests__/`

4. Update documentation in README.md if needed

5. Run tests to ensure everything passes:
```bash
npm test -- --run
```

6. Build to ensure no build errors:
```bash
npm run build
```

7. Commit your changes:
```bash
git add .
git commit -m "feat: add your feature description"
```

### Bug Fixes

1. Create a new branch:
```bash
git checkout -b fix/bug-description
```

2. Fix the bug in the relevant component

3. Add a test that would have caught the bug

4. Run tests and build

5. Commit with a descriptive message:
```bash
git commit -m "fix: describe what was fixed"
```

## Testing Guidelines

- Write tests for all new components and features
- Ensure existing tests still pass
- Aim for high test coverage
- Use descriptive test names
- Mock external dependencies (like sql-workbench-embedded)

### Example Test

```tsx
import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { SQLWorkbenchEmbedded } from '../SQLWorkbenchEmbedded';

describe('SQLWorkbenchEmbedded', () => {
  it('renders with initial code', () => {
    const initialCode = 'SELECT 1;';
    const { container } = render(
      <SQLWorkbenchEmbedded initialCode={initialCode} />
    );

    expect(container.textContent).toContain(initialCode);
  });
});
```

## Code Style

- Use TypeScript for all new code
- Follow existing code style and conventions
- Use meaningful variable and function names
- Add JSDoc comments for public APIs
- Keep components focused and single-purpose

### TypeScript Guidelines

- Always define proper types for props and state
- Export types that consumers might need
- Use type inference where it makes code clearer
- Avoid `any` - use `unknown` if type is truly unknown

## Documentation

When adding new features:

1. Update README.md with usage examples
2. Add JSDoc comments to public APIs
3. Update USAGE.md if adding common patterns
4. Add TypeScript types with descriptions

## Commit Message Format

We follow conventional commits:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test changes
- `refactor:` - Code refactoring
- `chore:` - Build process or tooling changes

Examples:
```
feat: add support for custom themes
fix: resolve memory leak in workbench cleanup
docs: update API reference for new props
test: add tests for SQLWorkbenchProvider
```

## Pull Request Process

1. Update documentation for any public API changes
2. Add tests for new functionality
3. Ensure all tests pass: `npm test -- --run`
4. Ensure build succeeds: `npm run build`
5. Update README.md with any new features
6. Create a pull request with a clear description

### PR Description Template

```markdown
## Description
Brief description of what this PR does

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe how you tested your changes

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Tests pass locally
- [ ] Build succeeds
- [ ] Documentation updated
- [ ] Types are properly defined
```

## Questions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Questions about development
- Suggestions for improvements

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
