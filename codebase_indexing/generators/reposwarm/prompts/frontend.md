version=2
Act as a frontend component architect. Analyze the component structure and design patterns in this frontend application.

## Repository Structure and Files

{repo_structure}

---

**Special Instruction**: Only document components and design patterns that are ACTUALLY implemented in the codebase.

### Component Organization
1. **Directory Structure:** How components are organized
2. **Naming Conventions:** Component naming patterns
3. **Atomic Design:** Atoms, molecules, organisms, templates, pages

### Core Components
1. **Layout Components:** Header, Footer, Sidebar, Navigation
2. **Form Components:** Input, Select, Checkbox, etc.
3. **Display Components:** Card, Modal, Table, List
4. **Feedback Components:** Alert, Toast, Loading, Error

### Component Patterns
1. **Component Types:** Presentational vs Container
2. **Composition:** HOCs, render props, compound components
3. **Hooks/Composables:** Custom hooks for shared logic
4. **State Lifting:** How state is shared between components

### State Management
1. **State Library:** Redux, Zustand, Pinia, Context, etc.
2. **State Shape:** How state is structured
3. **Actions/Mutations:** How state changes
4. **Selectors:** How state is accessed

### Data Fetching
1. **Fetch Strategy:** REST, GraphQL, tRPC
2. **Data Libraries:** React Query, SWR, Apollo
3. **Caching:** Client-side caching strategies
4. **Error Handling:** How fetch errors are handled

### Styling
1. **CSS Strategy:** CSS-in-JS, Tailwind, CSS Modules
2. **Theme System:** Design tokens, theming
3. **Responsive Design:** Breakpoints, mobile-first

### Performance
1. **Code Splitting:** Lazy loading, dynamic imports
2. **Memoization:** React.memo, useMemo, computed
3. **Virtual Lists:** For long lists
4. **Image Optimization:** Lazy loading, responsive images

Format the output clearly using markdown.
