---
name: pydantic
description: Expert assistance for data validation and settings management with Pydantic v2. Use when users need type-safe models, data parsing, validation, serialization, or structured LLM outputs with Python type hints.
---

# Pydantic - Data Validation with Python Type Hints

**Version:** 2.x | **Last Updated:** 2025-01

## Overview

Pydantic is the most widely used data validation library for Python, providing:

- **Type-Safe Models**: Define data structures with Python type hints
- **Automatic Validation**: Parse and validate data from any source
- **Serialization**: Convert models to/from JSON, dict, and other formats
- **Settings Management**: Type-safe configuration from environment variables
- **Performance**: Rust-powered core (pydantic-core) for speed

**Documentation**: https://docs.pydantic.dev

## When to Use This Skill

Activate when users need:

- "Validate API request/response data"
- "Create type-safe data models"
- "Parse JSON with validation"
- "Manage configuration from environment"
- "Serialize Python objects to JSON"
- "Define schemas for LLM structured outputs"

## Core Concepts

### 1. Basic Models

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class User(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=100)
    email: str
    created_at: datetime = Field(default_factory=datetime.now)
    bio: Optional[str] = None

# Create from dict
user = User(id=1, name="Alice", email="alice@example.com")

# Create from JSON
user = User.model_validate_json('{"id": 1, "name": "Alice", "email": "alice@example.com"}')

# Access fields
print(user.name)  # "Alice"
print(user.model_dump())  # dict representation
print(user.model_dump_json())  # JSON string
```

### 2. Field Types and Constraints

```python
from pydantic import BaseModel, Field, EmailStr, HttpUrl, constr, conint, confloat
from typing import Literal, Annotated
from datetime import date
from enum import Enum

class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

class Product(BaseModel):
    # Basic types with constraints
    id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=200)
    price: float = Field(..., ge=0, le=10000)
    quantity: int = Field(default=0, ge=0)

    # Constrained types
    sku: constr(pattern=r'^[A-Z]{3}-\d{4}$')  # e.g., "ABC-1234"
    rating: confloat(ge=0, le=5)

    # Special types
    email: EmailStr
    website: HttpUrl
    status: Status = Status.ACTIVE

    # Literal for fixed values
    currency: Literal["USD", "EUR", "GBP"] = "USD"

    # Date/time
    release_date: date
```

### 3. Nested Models

```python
from pydantic import BaseModel
from typing import List, Optional

class Address(BaseModel):
    street: str
    city: str
    country: str
    zip_code: Optional[str] = None

class Company(BaseModel):
    name: str
    address: Address
    employees: List["Employee"] = []

class Employee(BaseModel):
    id: int
    name: str
    email: str
    company: Optional[Company] = None

# Parse nested data
data = {
    "name": "Acme Corp",
    "address": {
        "street": "123 Main St",
        "city": "San Francisco",
        "country": "USA"
    },
    "employees": [
        {"id": 1, "name": "Alice", "email": "alice@acme.com"}
    ]
}
company = Company.model_validate(data)
```

### 4. Validators

```python
from pydantic import BaseModel, field_validator, model_validator, ValidationError
from typing import Self

class User(BaseModel):
    username: str
    email: str
    password: str
    password_confirm: str

    # Field validator - runs on single field
    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError('must be alphanumeric')
        return v.lower()

    @field_validator('email')
    @classmethod
    def email_valid(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('invalid email format')
        return v.lower()

    # Model validator - runs on entire model
    @model_validator(mode='after')
    def passwords_match(self) -> Self:
        if self.password != self.password_confirm:
            raise ValueError('passwords do not match')
        return self

# Validation with mode='before' - transform input
class NormalizedUser(BaseModel):
    name: str

    @field_validator('name', mode='before')
    @classmethod
    def normalize_name(cls, v):
        if isinstance(v, str):
            return v.strip().title()
        return v
```

### 5. Serialization Control

```python
from pydantic import BaseModel, Field, computed_field, field_serializer
from datetime import datetime

class Article(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    author_id: int = Field(..., exclude=True)  # Excluded from serialization

    # Computed field - calculated on access
    @computed_field
    @property
    def preview(self) -> str:
        return self.content[:100] + "..." if len(self.content) > 100 else self.content

    # Custom serializer
    @field_serializer('created_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()

# Control serialization
article = Article(id=1, title="Hello", content="Long content...", created_at=datetime.now(), author_id=42)

# Include/exclude specific fields
article.model_dump(include={'id', 'title'})
article.model_dump(exclude={'content'})

# Serialize to JSON with options
article.model_dump_json(indent=2)
```

### 6. Generic Models

```python
from pydantic import BaseModel
from typing import TypeVar, Generic, List

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    per_page: int

    @property
    def has_next(self) -> bool:
        return self.page * self.per_page < self.total

class User(BaseModel):
    id: int
    name: str

class Product(BaseModel):
    id: int
    name: str
    price: float

# Use with different types
user_response = PaginatedResponse[User](
    items=[User(id=1, name="Alice")],
    total=100,
    page=1,
    per_page=10
)

product_response = PaginatedResponse[Product](
    items=[Product(id=1, name="Widget", price=9.99)],
    total=50,
    page=1,
    per_page=10
)
```

### 7. Settings Management

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_prefix='APP_',  # Reads APP_DATABASE_URL, etc.
        case_sensitive=False,
        extra='ignore'
    )

    # Required settings
    database_url: str
    secret_key: SecretStr

    # Optional with defaults
    debug: bool = False
    log_level: str = "INFO"
    port: int = 8000

    # Nested settings with env prefix
    redis_host: str = "localhost"
    redis_port: int = 6379

# Usage
settings = Settings()
print(settings.database_url)
print(settings.secret_key.get_secret_value())  # Access secret
```

### 8. JSON Schema Generation

```python
from pydantic import BaseModel
from typing import List, Optional
import json

class Author(BaseModel):
    name: str
    email: str

class Book(BaseModel):
    title: str
    author: Author
    year: int
    tags: List[str] = []
    isbn: Optional[str] = None

# Generate JSON Schema
schema = Book.model_json_schema()
print(json.dumps(schema, indent=2))

# Output:
# {
#   "title": "Book",
#   "type": "object",
#   "properties": {
#     "title": {"type": "string"},
#     "author": {"$ref": "#/$defs/Author"},
#     "year": {"type": "integer"},
#     "tags": {"type": "array", "items": {"type": "string"}, "default": []},
#     "isbn": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": null}
#   },
#   "required": ["title", "author", "year"],
#   "$defs": {
#     "Author": {...}
#   }
# }
```

## Common Patterns

### 1. API Request/Response Models

```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

# Request model
class UserSearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
    sort_by: str = "created_at"
    sort_order: SortOrder = SortOrder.DESC
    filters: Optional[dict] = None

# Response model
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}  # Enable ORM mode

class UserSearchResponse(BaseModel):
    items: List[UserResponse]
    total: int
    page: int
    per_page: int
```

### 2. ORM Integration (SQLAlchemy)

```python
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase

# SQLAlchemy model
class Base(DeclarativeBase):
    pass

class UserORM(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)

# Pydantic model with ORM support
class UserSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str

# Convert ORM to Pydantic
user_orm = UserORM(id=1, name="Alice", email="alice@example.com")
user_schema = UserSchema.model_validate(user_orm)
```

### 3. Discriminated Unions

```python
from pydantic import BaseModel, Field
from typing import Literal, Union, Annotated

class Cat(BaseModel):
    pet_type: Literal["cat"]
    name: str
    meows: int

class Dog(BaseModel):
    pet_type: Literal["dog"]
    name: str
    barks: float

# Discriminated union - Pydantic uses pet_type to determine type
Pet = Annotated[Union[Cat, Dog], Field(discriminator='pet_type')]

class Owner(BaseModel):
    name: str
    pet: Pet

# Parsing
owner1 = Owner.model_validate({
    "name": "Alice",
    "pet": {"pet_type": "cat", "name": "Whiskers", "meows": 5}
})  # Creates Cat

owner2 = Owner.model_validate({
    "name": "Bob",
    "pet": {"pet_type": "dog", "name": "Buddy", "barks": 3.5}
})  # Creates Dog
```

### 4. Custom Types

```python
from pydantic import BaseModel, GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema
from typing import Annotated, Any

class PhoneNumber(str):
    """Custom phone number type with validation."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
        )

    @classmethod
    def _validate(cls, v: str) -> 'PhoneNumber':
        # Remove non-digits
        digits = ''.join(c for c in v if c.isdigit())
        if len(digits) < 10 or len(digits) > 15:
            raise ValueError('Invalid phone number length')
        return cls(digits)

class Contact(BaseModel):
    name: str
    phone: PhoneNumber

# Usage
contact = Contact(name="Alice", phone="+1 (555) 123-4567")
print(contact.phone)  # "15551234567"
```

### 5. LLM Structured Output

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class Entity(BaseModel):
    """Named entity extracted from text."""
    name: str = Field(..., description="The entity name")
    type: str = Field(..., description="Entity type: PERSON, ORG, LOCATION, etc.")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score")

class TextAnalysis(BaseModel):
    """Structured analysis of text for LLM output."""
    summary: str = Field(..., description="Brief summary in 1-2 sentences")
    sentiment: Sentiment = Field(..., description="Overall sentiment")
    entities: List[Entity] = Field(default_factory=list, description="Named entities")
    key_topics: List[str] = Field(..., description="Main topics discussed")
    language: str = Field(default="en", description="ISO language code")

# Generate schema for LLM prompt
schema = TextAnalysis.model_json_schema()

# Use with OpenAI
from openai import OpenAI
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": f"Analyze: {text}"}],
    response_format={"type": "json_object"},
    # Include schema in system prompt
)

# Parse response
analysis = TextAnalysis.model_validate_json(response.choices[0].message.content)
```

## Validation Modes

### Strict Mode

```python
from pydantic import BaseModel, ConfigDict

class StrictUser(BaseModel):
    model_config = ConfigDict(strict=True)

    id: int
    name: str

# Strict mode rejects type coercion
StrictUser(id=1, name="Alice")      # OK
StrictUser(id="1", name="Alice")    # ValidationError - "1" is str, not int

# Lax mode (default) allows coercion
class LaxUser(BaseModel):
    id: int
    name: str

LaxUser(id="1", name="Alice")       # OK - "1" coerced to 1
```

### Validation Methods

```python
from pydantic import BaseModel, ValidationError

class User(BaseModel):
    id: int
    name: str

# model_validate - from dict/object
user = User.model_validate({"id": 1, "name": "Alice"})

# model_validate_json - from JSON string
user = User.model_validate_json('{"id": 1, "name": "Alice"}')

# model_construct - skip validation (use with caution)
user = User.model_construct(id=1, name="Alice")

# Handle validation errors
try:
    user = User(id="not_an_int", name=123)
except ValidationError as e:
    print(e.error_count())  # Number of errors
    print(e.errors())       # List of error details
    print(e.json())         # JSON representation
```

## Performance Tips

### 1. Use model_construct for Trusted Data

```python
# Skip validation when data is already validated
user = User.model_construct(id=1, name="Alice")
```

### 2. Reuse Models with copy()

```python
user = User(id=1, name="Alice")
updated = user.model_copy(update={"name": "Bob"})
```

### 3. Use TypeAdapter for Non-Model Validation

```python
from pydantic import TypeAdapter
from typing import List

# Validate list of ints without creating model
adapter = TypeAdapter(List[int])
result = adapter.validate_python(["1", "2", "3"])  # [1, 2, 3]
```

### 4. Lazy Validators

```python
from pydantic import BaseModel, field_validator

class HeavyModel(BaseModel):
    data: str

    @field_validator('data')
    @classmethod
    def validate_data(cls, v: str) -> str:
        # Only runs when field is accessed/validated
        return v.upper()
```

## Integration Patterns

### FastAPI

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float

@app.post("/items/")
async def create_item(item: Item):
    return item
```

### BAML

```python
# Pydantic models work directly with BAML structured outputs
from baml_client.types import ExtractedEntity  # Generated Pydantic model
```

### Dagster

```python
from dagster import asset, Config
from pydantic import Field

class MyConfig(Config):
    threshold: float = Field(default=0.5, ge=0, le=1)

@asset
def my_asset(config: MyConfig):
    return process_with_threshold(config.threshold)
```

## Troubleshooting

### "ValidationError"
- Check field types match input data
- Use `strict=False` for lenient parsing
- Review error details with `e.errors()`

### "Field required"
- Add default value or `Optional[]`
- Use `Field(default=...)` for defaults

### "Extra fields not permitted"
- Set `model_config = ConfigDict(extra='allow')` or `'ignore'`

### Performance Issues
- Use `model_construct` for trusted data
- Avoid deep nesting where possible
- Use `TypeAdapter` for simple validations

## Resources

- **Documentation**: https://docs.pydantic.dev
- **GitHub**: https://github.com/pydantic/pydantic
- **Migration Guide (v1 to v2)**: https://docs.pydantic.dev/latest/migration/
- **pydantic-settings**: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
