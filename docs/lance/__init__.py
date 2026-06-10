# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright The Lance Authors

"""
Lance Namespace Implementations.

This package provides third-party catalog implementations for Lance Namespace:

- IcebergNamespace: Apache Iceberg REST Catalog
"""

from lance.iceberg import UnityNamespace

__all__ = [ "IcebergNamespace"]
