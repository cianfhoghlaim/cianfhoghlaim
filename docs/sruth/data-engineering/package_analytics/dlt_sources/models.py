from pydantic import BaseModel, Field
from typing import List, Union, Annotated, Type
from pydantic import BaseModel, ValidationError
from datetime import datetime
from typing import Optional, Dict
import pyarrow as pa

DUCKDB_EXTENSION = ["aws", "httpfs"]


class File(BaseModel):
    filename: Optional[str]
    project: Optional[str]
    version: Optional[str]
    type: Optional[str]


class Libc(BaseModel):
    lib: Optional[str]
    version: Optional[str]


class Distro(BaseModel):
    name: Optional[str]
    version: Optional[str]
    id: Optional[str]
    libc: Optional[Libc]


class Implementation(BaseModel):
    name: Optional[str]
    version: Optional[str]


class Installer(BaseModel):
    name: Optional[str]
    version: Optional[str]


class System(BaseModel):
    name: Optional[str]
    release: Optional[str]


class Details(BaseModel):
    installer: Optional[Installer]
    python: Optional[str]
    implementation: Optional[Implementation]
    distro: Optional[Distro]
    system: Optional[System]
    cpu: Optional[str]
    openssl_version: Optional[str]
    setuptools_version: Optional[str]
    rustc_version: Optional[str]
    ci: Optional[bool]


class FileDownloads(BaseModel):
    timestamp: Optional[datetime] = None
    country_code: Optional[str] = None
    url: Optional[str] = None
    project: Optional[str] = None
    file: Optional[File] = None
    details: Optional[Details] = None
    tls_protocol: Optional[str] = None
    tls_cipher: Optional[str] = None


class PypiJobParameters(BaseModel):
    start_date: str = "2019-04-01"
    end_date: str = "2023-11-30"
    pypi_project: str = "duckdb"
    gcp_project: str
    destination: Annotated[Union[List[str], str], Field(default=["local"])]  # local, s3, md


class TableValidationError(Exception):
    """Custom exception for Table validation errors."""

    pass


def validate_table(table: pa.Table, model: Type[BaseModel]):
    """
    Validates each row of a PyArrow Table against a Pydantic model.
    Raises TableValidationError if any row fails validation.

    :param table: PyArrow Table to validate.
    :param model: Pydantic model to validate against.
    :raises: TableValidationError
    """
    errors = []

    for i in range(table.num_rows):
        row = {column: table[column][i].as_py() for column in table.column_names}
        try:
            model(**row)
        except ValidationError as e:
            errors.append(f"Row {i} failed validation: {e}")

    if errors:
        error_message = "\n".join(errors)
        raise TableValidationError(
            f"Table validation failed with the following errors:\n{error_message}"
        )
