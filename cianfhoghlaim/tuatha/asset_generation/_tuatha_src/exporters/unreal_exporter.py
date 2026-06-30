"""Unreal Engine 5 asset exporter.

Generates:
- .json: Asset manifests for Python import
- .py: Unreal Python import scripts
- .usf: HLSL shader files
- Raw textures for import

Note: .uasset is binary and must be created within Unreal Editor.
This exporter generates import-ready assets and automation scripts.
"""

import json
import time
from pathlib import Path
from typing import Any

from ..models import AssetResponse, AssetType, CelticStyle
from .base_exporter import (
    BaseExporter,
    ExportResult,
    TargetEngine,
)


class UnrealExporter(BaseExporter):
    """Export assets for Unreal Engine 5.

    Generates:
    - Raw textures (PNG/TGA) with import manifests
    - Unreal Python scripts for automated import
    - Material HLSL shaders (.usf)
    - DataAsset JSON for blueprint integration
    """

    @property
    def engine_name(self) -> str:
        return "Unreal Engine"

    @property
    def engine_version(self) -> str:
        return "5.4"

    def export_texture(
        self,
        asset: AssetResponse,
        image_data: bytes,
        name: str,
    ) -> ExportResult:
        """Export texture with Unreal import manifest."""
        start_time = time.time()
        warnings = self.validate_asset(asset)
        safe_name = self._sanitize_name(name)

        try:
            # Write the PNG image
            png_path = self.config.output_dir / f"{safe_name}.png"
            png_path.write_bytes(image_data)

            # Generate import manifest
            manifest_path = self.config.output_dir / f"{safe_name}.json"
            manifest = self._generate_texture_manifest(safe_name, asset)
            manifest_path.write_text(json.dumps(manifest, indent=2))

            # Generate Python import script
            script_path = self.config.output_dir / f"import_{safe_name}.py"
            script_content = self._generate_import_script(safe_name, asset, "texture")
            script_path.write_text(script_content)

            elapsed_ms = int((time.time() - start_time) * 1000)

            return ExportResult(
                success=True,
                engine=TargetEngine.UNREAL,
                asset_type=asset.asset_type,
                primary_file=png_path,
                additional_files=[manifest_path, script_path],
                export_time_ms=elapsed_ms,
                file_sizes={
                    str(png_path): len(image_data),
                    str(manifest_path): manifest_path.stat().st_size,
                },
                warnings=warnings,
                import_instructions=(
                    "1. Copy files to your Unreal project's Content folder\n"
                    "2. Open Unreal Editor and enable Python plugin\n"
                    f"3. Run the import script: py import_{safe_name}.py\n"
                    "Or manually import the PNG through Content Browser"
                ),
            )

        except Exception as e:
            return ExportResult(
                success=False,
                engine=TargetEngine.UNREAL,
                asset_type=asset.asset_type,
                error=str(e),
                warnings=warnings,
            )

    def export_material(
        self,
        name: str,
        textures: dict[str, Path],
        style: CelticStyle,
        properties: dict[str, Any],
    ) -> ExportResult:
        """Export material as HLSL shader + manifest."""
        start_time = time.time()
        safe_name = self._sanitize_name(name)

        try:
            # Generate HLSL shader
            shader_path = self.config.output_dir / f"MF_{safe_name}.usf"
            shader_content = self._generate_material_function(style, properties)
            shader_path.write_text(shader_content)

            # Generate material manifest
            manifest_path = self.config.output_dir / f"{safe_name}_material.json"
            manifest = self._generate_material_manifest(safe_name, textures, style, properties)
            manifest_path.write_text(json.dumps(manifest, indent=2))

            # Generate Python import script
            script_path = self.config.output_dir / f"import_{safe_name}_material.py"
            script_content = self._generate_material_script(safe_name, textures, style, properties)
            script_path.write_text(script_content)

            elapsed_ms = int((time.time() - start_time) * 1000)

            return ExportResult(
                success=True,
                engine=TargetEngine.UNREAL,
                asset_type=AssetType.SPELL_EFFECT,
                primary_file=manifest_path,
                additional_files=[shader_path, script_path],
                export_time_ms=elapsed_ms,
                file_sizes={
                    str(shader_path): shader_path.stat().st_size,
                    str(manifest_path): manifest_path.stat().st_size,
                },
                import_instructions=(
                    "1. Copy .usf file to your project's Shaders folder\n"
                    "2. Run the import script to create the Material\n"
                    "3. Or manually create Material and add Custom node with HLSL code"
                ),
            )

        except Exception as e:
            return ExportResult(
                success=False,
                engine=TargetEngine.UNREAL,
                asset_type=AssetType.SPELL_EFFECT,
                error=str(e),
            )

    def export_scene(
        self,
        name: str,
        assets: list[tuple[AssetResponse, dict[str, Any]]],
    ) -> ExportResult:
        """Export scene as DataAsset + import script."""
        start_time = time.time()
        safe_name = self._sanitize_name(name)

        try:
            # Generate scene manifest as DataAsset JSON
            manifest_path = self.config.output_dir / f"DA_{safe_name}.json"
            manifest = self._generate_scene_manifest(safe_name, assets)
            manifest_path.write_text(json.dumps(manifest, indent=2))

            # Generate Python spawn script
            script_path = self.config.output_dir / f"spawn_{safe_name}.py"
            script_content = self._generate_spawn_script(safe_name, assets)
            script_path.write_text(script_content)

            elapsed_ms = int((time.time() - start_time) * 1000)

            return ExportResult(
                success=True,
                engine=TargetEngine.UNREAL,
                asset_type=AssetType.TERRITORY_TILE,
                primary_file=manifest_path,
                additional_files=[script_path],
                export_time_ms=elapsed_ms,
                file_sizes={str(manifest_path): manifest_path.stat().st_size},
                import_instructions=(
                    "1. Create a DataAsset in Unreal based on the JSON structure\n"
                    "2. Run the spawn script to instantiate actors in the level\n"
                    "3. Or use the JSON to drive a Blueprint spawning system"
                ),
            )

        except Exception as e:
            return ExportResult(
                success=False,
                engine=TargetEngine.UNREAL,
                asset_type=AssetType.TERRITORY_TILE,
                error=str(e),
            )

    def get_file_extension(self, asset_type: AssetType) -> str:
        """Get Unreal file extension for asset type."""
        extensions = {
            AssetType.CHARACTER_PORTRAIT: "png",
            AssetType.ITEM_ICON: "png",
            AssetType.CLAN_HERALDRY: "png",
            AssetType.TERRITORY_TILE: "json",
            AssetType.SPELL_EFFECT: "usf",
            AssetType.CREATURE: "json",
        }
        return extensions.get(asset_type, "json")

    def _generate_texture_manifest(self, name: str, asset: AssetResponse) -> dict:
        """Generate texture import manifest."""
        # Determine texture group based on asset type
        texture_group = {
            AssetType.CHARACTER_PORTRAIT: "UI",
            AssetType.ITEM_ICON: "UI",
            AssetType.CLAN_HERALDRY: "UI",
            AssetType.TERRITORY_TILE: "World",
            AssetType.SPELL_EFFECT: "Effects",
            AssetType.CREATURE: "Character",
        }.get(asset.asset_type, "World")

        return {
            "asset_type": "Texture2D",
            "name": f"T_{name}",
            "source_file": f"{name}.png",
            "import_settings": {
                "texture_group": texture_group,
                "compression_settings": "TC_Default",
                "mip_gen_settings": "TMGS_FromTextureGroup" if self.config.generate_mipmaps else "TMGS_NoMipmaps",
                "srgb": True,
                "filter": "TF_Default",
                "max_texture_size": self.config.texture_max_size,
            },
            "metadata": self.generate_metadata(asset) if self.config.include_metadata else {},
            "dimensions": {
                "width": asset.width,
                "height": asset.height,
            },
        }

    def _generate_material_manifest(
        self,
        name: str,
        textures: dict[str, Path],
        style: CelticStyle,
        properties: dict[str, Any],
    ) -> dict:
        """Generate material manifest."""
        return {
            "asset_type": "Material",
            "name": f"M_{name}",
            "shading_model": "MSM_DefaultLit",
            "blend_mode": "BLEND_Opaque",
            "celtic_style": style,
            "shader_file": f"MF_{name}.usf",
            "textures": {slot: str(path) for slot, path in textures.items()},
            "parameters": {
                "primary_color": properties.get("primary_color", [0.8, 0.6, 0.2, 1.0]),
                "secondary_color": properties.get("secondary_color", [0.2, 0.5, 0.3, 1.0]),
                "animation_speed": properties.get("animation_speed", 1.0),
                "metallic": properties.get("metallic", 0.0),
                "roughness": properties.get("roughness", 0.5),
            },
        }

    def _generate_scene_manifest(
        self,
        name: str,
        assets: list[tuple[AssetResponse, dict[str, Any]]],
    ) -> dict:
        """Generate scene DataAsset manifest."""
        actors = []
        for asset, transform in assets:
            safe_asset_name = self._sanitize_name(asset.asset_id)
            actors.append({
                "name": safe_asset_name,
                "asset_reference": f"/Game/CelticAssets/T_{safe_asset_name}",
                "transform": {
                    "location": transform.get("position", [0, 0, 0]),
                    "rotation": transform.get("rotation", [0, 0, 0]),
                    "scale": transform.get("scale", [1, 1, 1]),
                },
                "asset_type": asset.asset_type,
                "celtic_style": asset.style,
            })

        return {
            "asset_type": "DataAsset",
            "name": f"DA_{name}",
            "class": "CelticSceneData",
            "actors": actors,
            "metadata": {
                "generator": "cianfhoghlaim-asset-pipeline",
                "scene_name": name,
                "actor_count": len(actors),
            },
        }

    def _generate_import_script(self, name: str, asset: AssetResponse, asset_type: str) -> str:
        """Generate Unreal Python import script."""
        return f'''"""
Unreal Engine Python import script for {name}.
Generated by Cianfhoghlaim Asset Pipeline.

Run in Unreal Editor: Execute Python Script
"""

import unreal

def import_texture():
    """Import texture asset."""
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    # Import task
    task = unreal.AssetImportTask()
    task.set_editor_property('filename', '{name}.png')
    task.set_editor_property('destination_path', '/Game/CelticAssets')
    task.set_editor_property('destination_name', 'T_{name}')
    task.set_editor_property('replace_existing', True)
    task.set_editor_property('automated', True)
    task.set_editor_property('save', True)

    # Texture import options
    options = unreal.FbxImportUI()
    task.set_editor_property('options', options)

    # Execute import
    asset_tools.import_asset_tasks([task])

    # Get imported asset
    asset_path = '/Game/CelticAssets/T_{name}'
    texture = unreal.EditorAssetLibrary.load_asset(asset_path)

    if texture:
        # Set texture properties
        texture.set_editor_property('srgb', True)
        texture.set_editor_property('compression_settings',
            unreal.TextureCompressionSettings.TC_DEFAULT)

        unreal.log(f'Successfully imported: {{asset_path}}')
        return texture
    else:
        unreal.log_warning(f'Failed to import: {{asset_path}}')
        return None


if __name__ == '__main__':
    import_texture()
'''

    def _generate_material_script(
        self,
        name: str,
        textures: dict[str, Path],
        style: CelticStyle,
        properties: dict[str, Any],
    ) -> str:
        """Generate Unreal Python material creation script."""
        primary = properties.get("primary_color", [0.8, 0.6, 0.2, 1.0])
        secondary = properties.get("secondary_color", [0.2, 0.5, 0.3, 1.0])

        return f'''"""
Unreal Engine Python material creation script for {name}.
Generated by Cianfhoghlaim Asset Pipeline.

Run in Unreal Editor: Execute Python Script
"""

import unreal

def create_celtic_material():
    """Create Celtic-themed material."""
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    material_factory = unreal.MaterialFactoryNew()

    # Create material asset
    material_path = '/Game/CelticAssets/Materials'
    material_name = 'M_{name}'

    material = asset_tools.create_asset(
        material_name,
        material_path,
        unreal.Material,
        material_factory
    )

    if not material:
        unreal.log_warning('Failed to create material')
        return None

    # Create material expression nodes
    mel = unreal.MaterialEditingLibrary

    # Base Color parameter
    base_color = mel.create_material_expression(
        material,
        unreal.MaterialExpressionVectorParameter,
        -400, 0
    )
    base_color.set_editor_property('parameter_name', 'PrimaryColor')
    base_color.set_editor_property('default_value',
        unreal.LinearColor({primary[0]}, {primary[1]}, {primary[2]}, {primary[3]}))

    # Secondary color parameter
    secondary_color = mel.create_material_expression(
        material,
        unreal.MaterialExpressionVectorParameter,
        -400, 200
    )
    secondary_color.set_editor_property('parameter_name', 'SecondaryColor')
    secondary_color.set_editor_property('default_value',
        unreal.LinearColor({secondary[0]}, {secondary[1]}, {secondary[2]}, {secondary[3]}))

    # Custom HLSL node for Celtic pattern
    custom = mel.create_material_expression(
        material,
        unreal.MaterialExpressionCustom,
        -200, 100
    )
    custom.set_editor_property('code', """
// Celtic {style} pattern
float2 uv = Parameters.TexCoords[0].xy;
float pattern = sin(uv.x * 10.0 + View.RealTime) * sin(uv.y * 10.0);
return lerp(PrimaryColor, SecondaryColor, saturate(pattern * 0.5 + 0.5));
""")
    custom.set_editor_property('output_type', unreal.CustomMaterialOutputType.CMOT_FLOAT3)

    # Connect to base color
    mel.connect_material_property(
        custom, '',
        unreal.MaterialProperty.MP_BASE_COLOR
    )

    # Compile and save
    unreal.MaterialEditingLibrary.recompile_material(material)
    unreal.EditorAssetLibrary.save_asset(f'{{material_path}}/{{material_name}}')

    unreal.log(f'Created material: {{material_path}}/{{material_name}}')
    return material


if __name__ == '__main__':
    create_celtic_material()
'''

    def _generate_spawn_script(
        self,
        name: str,
        assets: list[tuple[AssetResponse, dict[str, Any]]],
    ) -> str:
        """Generate Unreal Python actor spawning script."""
        actor_spawns = []
        for i, (asset, transform) in enumerate(assets):
            safe_name = self._sanitize_name(asset.asset_id)
            pos = transform.get("position", [0, 0, 0])
            rot = transform.get("rotation", [0, 0, 0])
            scale = transform.get("scale", [1, 1, 1])

            actor_spawns.append(f"""
    # Spawn actor {i}: {safe_name}
    spawn_actor(
        '/Game/CelticAssets/T_{safe_name}',
        unreal.Vector({pos[0]}, {pos[1]}, {pos[2]}),
        unreal.Rotator({rot[0]}, {rot[1]}, {rot[2]}),
        unreal.Vector({scale[0]}, {scale[1]}, {scale[2]})
    )""")

        return f'''"""
Unreal Engine Python scene spawning script for {name}.
Generated by Cianfhoghlaim Asset Pipeline.

Run in Unreal Editor: Execute Python Script
"""

import unreal

def spawn_actor(texture_path, location, rotation, scale):
    """Spawn a sprite actor with the given texture."""
    world = unreal.EditorLevelLibrary.get_editor_world()

    # Create a Billboard Component Actor
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.Actor,
        location,
        rotation
    )

    if actor:
        # Add sprite component
        sprite = actor.add_component_by_class(
            unreal.BillboardComponent,
            False,
            unreal.Transform(),
            False
        )

        # Load and set texture
        texture = unreal.EditorAssetLibrary.load_asset(texture_path)
        if texture:
            sprite.set_sprite(texture)
            sprite.set_world_scale_3d(scale)

        actor.set_actor_label(texture_path.split('/')[-1])

    return actor


def spawn_scene():
    """Spawn all actors in the {name} scene."""
    unreal.log('Spawning {name} scene...')
{"".join(actor_spawns)}
    unreal.log('Scene spawning complete!')


if __name__ == '__main__':
    spawn_scene()
'''

    def _generate_material_function(self, style: CelticStyle, properties: dict[str, Any]) -> str:
        """Generate HLSL Material Function for Celtic effects."""
        if style == CelticStyle.KNOTWORK:
            return self._knotwork_hlsl()
        elif style == CelticStyle.SPIRAL:
            return self._spiral_hlsl()
        return self._default_hlsl()

    def _knotwork_hlsl(self) -> str:
        """Celtic knotwork HLSL shader."""
        return """// Celtic Knotwork Material Function
// Generated by Cianfhoghlaim Asset Pipeline

// Inputs: UV, PrimaryColor, SecondaryColor, Time, LineWidth, PatternScale

float KnotSegment(float2 p, float r, float w)
{
    return abs(length(p) - r) - w;
}

float3 CelticKnotwork(
    float2 UV,
    float3 PrimaryColor,
    float3 SecondaryColor,
    float Time,
    float LineWidth,
    float PatternScale
)
{
    float2 id = floor(UV * PatternScale);
    float2 p = frac(UV * PatternScale) - 0.5;

    float checker = fmod(id.x + id.y, 2.0);

    float d1 = KnotSegment(p - float2(0.5, 0.0), 0.5, LineWidth);
    float d2 = KnotSegment(p + float2(0.5, 0.0), 0.5, LineWidth);

    float phase = sin(Time + id.x * 0.5 + id.y * 0.7) * 0.5 + 0.5;
    float pattern = lerp(d1, d2, phase * checker + (1.0 - checker) * (1.0 - phase));

    // Anti-aliased edge
    float edge = smoothstep(0.0, fwidth(pattern) * 2.0, pattern);

    // Mix colors based on pattern
    float3 color = lerp(PrimaryColor, SecondaryColor, edge);

    // Add subtle glow on lines
    float glow = exp(-abs(pattern) * 10.0) * 0.3;
    color += PrimaryColor * glow;

    return color;
}
"""

    def _spiral_hlsl(self) -> str:
        """Celtic spiral HLSL shader."""
        return """// Celtic Spiral/Triskele Material Function
// Generated by Cianfhoghlaim Asset Pipeline

// Inputs: UV, PrimaryColor, SecondaryColor, Time, NumArms, SpiralTightness

#define TAU 6.28318530718

float Spiral(float2 p, float arms, float tightness, float rotation)
{
    float angle = atan2(p.y, p.x) + rotation;
    float radius = length(p);

    float spiralAngle = radius * tightness * TAU;
    float armAngle = angle * arms;

    float d = sin(armAngle - spiralAngle);
    return abs(d) - 0.1;
}

float3 CelticSpiral(
    float2 UV,
    float3 PrimaryColor,
    float3 SecondaryColor,
    float Time,
    float NumArms,
    float SpiralTightness
)
{
    float2 uv = UV * 2.0 - 1.0;

    float s = Spiral(uv, NumArms, SpiralTightness, Time);
    float pattern = smoothstep(0.0, fwidth(s) * 2.0, s);

    float dist = length(uv);
    float3 color = lerp(PrimaryColor, SecondaryColor, pattern);

    // Glow effect
    float glow = exp(-abs(s) * 8.0) * 0.4;
    color += PrimaryColor * glow * (1.0 - dist);

    return color;
}
"""

    def _default_hlsl(self) -> str:
        """Default Celtic HLSL shader."""
        return """// Celtic Default Material Function
// Generated by Cianfhoghlaim Asset Pipeline

float3 CelticDefault(
    float2 UV,
    float3 PrimaryColor,
    float3 SecondaryColor,
    Texture2D AlbedoTexture,
    SamplerState AlbedoSampler
)
{
    float4 tex = AlbedoTexture.Sample(AlbedoSampler, UV);
    float3 color = lerp(PrimaryColor, SecondaryColor, tex.r);
    return color * tex.rgb;
}
"""
