"""Asset processors for texture, mesh, and shader operations.

Provides:
- TextureProcessor: Resize, compress, atlas generation
- (Future) MeshProcessor: LOD generation, decimation
- (Future) ShaderCompiler: Cross-platform shader compilation
"""

from .texture_processor import TextureProcessingConfig, TextureProcessor

__all__ = [
    "TextureProcessingConfig",
    "TextureProcessor",
]
