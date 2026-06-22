version=2
Act as a backend architect. Analyze this backend service.

## Repository Structure and Files

{repo_structure}

---

## Dependencies

{repo_deps}

---

Document the backend architecture:

### API Layer
1. **API Style:** REST, GraphQL, gRPC, or hybrid
2. **Endpoints:** Main API endpoints and their purposes
3. **Request Handling:** Middleware, validation, serialization
4. **Error Handling:** Error response patterns, status codes

### Service Layer
1. **Core Services:** Main business logic services
2. **Service Patterns:** Dependency injection, service locator
3. **Cross-Cutting Concerns:** Logging, caching, metrics

### Data Layer
1. **Database:** Type (SQL/NoSQL), ORM/ODM usage
2. **Data Models:** Core entities and relationships
3. **Data Access:** Repository patterns, query builders
4. **Caching:** Cache strategies and invalidation

### Events & Messaging
1. **Event System:** Event bus, message queues
2. **Async Processing:** Background jobs, workers
3. **Communication:** Internal service communication

### Security
1. **Authentication:** Auth mechanisms (JWT, OAuth, sessions)
2. **Authorization:** Permission systems, role-based access
3. **Data Protection:** Encryption, PII handling

**Special Instruction**: Only document components that are ACTUALLY present in the codebase.

Format the output clearly using markdown.
