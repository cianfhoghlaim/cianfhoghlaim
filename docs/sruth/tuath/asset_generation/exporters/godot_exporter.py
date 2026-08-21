"""Godot 4 asset exporter.

Generates:
- .tres: Resource files (textures, materials)
- .tscn: Scene files (positioned assets)
- .gdshader: Shader files for Celtic effects
"""

import base64
import json
import time
from pathlib import Path
from typing import Any, Optional

from ..models import AssetType, CelticStyle, AssetResponse
from .base_exporter import (
    BaseExporter,
    ExportConfig,
    ExportResult,
    TargetEngine,
    TextureFormat,
)


class GodotExporter(BaseExporter):
    """Export assets for Godot 4.x.

    Supports:
    - Texture2D resources (.tres with external .png)
    - StandardMaterial3D / ShaderMaterial (.tres)
    - PackedScene files (.tscn)
    - Custom Celtic shaders (.gdshader)
    """

    @property
    def engine_name(self) -> str:
        return "Godot Engine"

    @property
    def engine_version(self) -> str:
        return "4.4"

    def export_texture(
        self,
        asset: AssetResponse,
        image_data: bytes,
        name: str,
    ) -> ExportResult:
        """Export texture as Godot resource."""
        start_time = time.time()
        warnings = self.validate_asset(asset)
        safe_name = self._sanitize_name(name)

        try:
            # Write the PNG image
            png_path = self.config.output_dir / f"{safe_name}.png"
            png_path.write_bytes(image_data)

            # Create .import file (Godot's import metadata)
            import_path = self.config.output_dir / f"{safe_name}.png.import"
            import_content = self._generate_import_file(safe_name, asset)
            import_path.write_text(import_content)

            # Generate .tres resource file
            tres_path = self.config.output_dir / f"{safe_name}.tres"
            tres_content = self._generate_texture_resource(safe_name, asset)
            tres_path.write_text(tres_content)

            elapsed_ms = int((time.time() - start_time) * 1000)

            return ExportResult(
                success=True,
                engine=TargetEngine.GODOT,
                asset_type=asset.asset_type,
                primary_file=tres_path,
                additional_files=[png_path, import_path],
                export_time_ms=elapsed_ms,
                file_sizes={
                    str(png_path): len(image_data),
                    str(tres_path): tres_path.stat().st_size,
                },
                warnings=warnings,
                import_instructions=(
                    "Place files in your Godot project's res:// directory. "
                    "Godot will auto-import on next editor load."
                ),
            )

        except Exception as e:
            return ExportResult(
                success=False,
                engine=TargetEngine.GODOT,
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
        """Export material as Godot resource."""
        start_time = time.time()
        safe_name = self._sanitize_name(name)

        try:
            # Determine material type based on style
            if style in (CelticStyle.KNOTWORK, CelticStyle.SPIRAL):
                # Use ShaderMaterial for procedural Celtic patterns
                material_content = self._generate_shader_material(
                    safe_name, textures, style, properties
                )
                # Also generate the shader file
                shader_path = self.config.output_dir / f"{safe_name}.gdshader"
                shader_content = self._generate_celtic_shader(style, properties)
                shader_path.write_text(shader_content)
            else:
                # Use StandardMaterial3D for regular textures
                material_content = self._generate_standard_material(safe_name, textures, properties)
                shader_path = None

            # Write material resource
            material_path = self.config.output_dir / f"{safe_name}.tres"
            material_path.write_text(material_content)

            elapsed_ms = int((time.time() - start_time) * 1000)

            additional = [shader_path] if shader_path else []

            return ExportResult(
                success=True,
                engine=TargetEngine.GODOT,
                asset_type=AssetType.SPELL_EFFECT,  # Materials are typically for effects
                primary_file=material_path,
                additional_files=additional,
                export_time_ms=elapsed_ms,
                file_sizes={str(material_path): material_path.stat().st_size},
            )

        except Exception as e:
            return ExportResult(
                success=False,
                engine=TargetEngine.GODOT,
                asset_type=AssetType.SPELL_EFFECT,
                error=str(e),
            )

    def export_scene(
        self,
        name: str,
        assets: list[tuple[AssetResponse, dict[str, Any]]],
    ) -> ExportResult:
        """Export scene as Godot PackedScene."""
        start_time = time.time()
        safe_name = self._sanitize_name(name)

        try:
            scene_content = self._generate_scene(safe_name, assets)
            scene_path = self.config.output_dir / f"{safe_name}.tscn"
            scene_path.write_text(scene_content)

            elapsed_ms = int((time.time() - start_time) * 1000)

            return ExportResult(
                success=True,
                engine=TargetEngine.GODOT,
                asset_type=AssetType.TERRITORY_TILE,  # Scenes are typically environments
                primary_file=scene_path,
                export_time_ms=elapsed_ms,
                file_sizes={str(scene_path): scene_path.stat().st_size},
                import_instructions=(
                    "Open the .tscn file in Godot Editor. "
                    "Ensure referenced textures are in the same directory."
                ),
            )

        except Exception as e:
            return ExportResult(
                success=False,
                engine=TargetEngine.GODOT,
                asset_type=AssetType.TERRITORY_TILE,
                error=str(e),
            )

    def get_file_extension(self, asset_type: AssetType) -> str:
        """Get Godot file extension for asset type."""
        extensions = {
            AssetType.CHARACTER_PORTRAIT: "tres",
            AssetType.ITEM_ICON: "tres",
            AssetType.CLAN_HERALDRY: "tres",
            AssetType.TERRITORY_TILE: "tscn",
            AssetType.SPELL_EFFECT: "tres",
            AssetType.CREATURE: "tscn",
        }
        return extensions.get(asset_type, "tres")

    def _generate_import_file(self, name: str, asset: AssetResponse) -> str:
        """Generate Godot .import file for texture."""
        return f"""[remap]

importer="texture"
type="CompressedTexture2D"
uid="uid://{self._generate_uid()}"
path="res://.godot/imported/{name}.ctex"

[deps]

source_file="res://{name}.png"
dest_files=["res://.godot/imported/{name}.ctex"]

[params]

compress/mode=0
compress/high_quality=true
compress/lossy_quality=0.7
compress/hdr_compression=1
compress/normal_map=0
compress/channel_pack=0
mipmaps/generate={str(self.config.generate_mipmaps).lower()}
mipmaps/limit=-1
roughness/mode=0
roughness/src_normal=""
process/fix_alpha_border=true
process/premult_alpha=false
process/normal_map_invert_y=false
process/hdr_as_srgb=false
process/hdr_clamp_exposure=false
process/size_limit={self.config.texture_max_size}
detect_3d/compress_to=1
"""

    def _generate_texture_resource(self, name: str, asset: AssetResponse) -> str:
        """Generate Godot .tres resource for texture reference."""
        metadata = self.generate_metadata(asset) if self.config.include_metadata else {}

        return f"""[gd_resource type="Texture2D" load_steps=2 format=3]

[ext_resource type="Texture2D" uid="uid://{self._generate_uid()}" path="res://{name}.png" id="1"]

[resource]
resource_name = "{name}"
{self._format_metadata(metadata)}
"""

    def _generate_standard_material(
        self,
        name: str,
        textures: dict[str, Path],
        properties: dict[str, Any],
    ) -> str:
        """Generate StandardMaterial3D resource."""
        albedo_color = properties.get("albedo_color", [1.0, 1.0, 1.0, 1.0])
        metallic = properties.get("metallic", 0.0)
        roughness = properties.get("roughness", 0.5)

        # Build external resources
        ext_resources = []
        for i, (slot, path) in enumerate(textures.items(), 1):
            ext_resources.append(
                f'[ext_resource type="Texture2D" path="res://{path.name}" id="{i}"]'
            )

        ext_section = "\n".join(ext_resources)

        # Map texture slots
        texture_params = []
        slot_mapping = {
            "albedo": "albedo_texture",
            "normal": "normal_texture",
            "roughness": "roughness_texture",
            "metallic": "metallic_texture",
            "emission": "emission_texture",
        }

        for i, (slot, _) in enumerate(textures.items(), 1):
            if slot in slot_mapping:
                texture_params.append(f'{slot_mapping[slot]} = ExtResource("{i}")')

        texture_section = "\n".join(texture_params)

        return f"""[gd_resource type="StandardMaterial3D" load_steps={len(textures) + 1} format=3]

{ext_section}

[resource]
resource_name = "{name}"
albedo_color = Color({albedo_color[0]}, {albedo_color[1]}, {albedo_color[2]}, {albedo_color[3]})
metallic = {metallic}
roughness = {roughness}
{texture_section}
"""

    def _generate_shader_material(
        self,
        name: str,
        textures: dict[str, Path],
        style: CelticStyle,
        properties: dict[str, Any],
    ) -> str:
        """Generate ShaderMaterial resource for Celtic effects."""
        return f"""[gd_resource type="ShaderMaterial" load_steps=2 format=3]

[ext_resource type="Shader" path="res://{name}.gdshader" id="1"]

[resource]
resource_name = "{name}"
shader = ExtResource("1")
shader_parameter/celtic_style = "{style}"
shader_parameter/primary_color = Color({properties.get("primary_color", [0.8, 0.6, 0.2, 1.0])[0]}, {properties.get("primary_color", [0.8, 0.6, 0.2, 1.0])[1]}, {properties.get("primary_color", [0.8, 0.6, 0.2, 1.0])[2]}, 1.0)
shader_parameter/secondary_color = Color({properties.get("secondary_color", [0.2, 0.5, 0.3, 1.0])[0]}, {properties.get("secondary_color", [0.2, 0.5, 0.3, 1.0])[1]}, {properties.get("secondary_color", [0.2, 0.5, 0.3, 1.0])[2]}, 1.0)
shader_parameter/animation_speed = {properties.get("animation_speed", 1.0)}
"""

    def _generate_celtic_shader(
        self,
        style: CelticStyle,
        properties: dict[str, Any],
    ) -> str:
        """Generate GLSL shader for Celtic patterns."""
        if style == CelticStyle.KNOTWORK:
            return self._knotwork_shader()
        elif style == CelticStyle.SPIRAL:
            return self._spiral_shader()
        else:
            return self._default_shader()

    def _knotwork_shader(self) -> str:
        """Celtic knotwork shader (SDF-based interlacing)."""
        return """shader_type spatial;

uniform vec4 primary_color : source_color = vec4(0.8, 0.6, 0.2, 1.0);
uniform vec4 secondary_color : source_color = vec4(0.2, 0.5, 0.3, 1.0);
uniform float animation_speed : hint_range(0.0, 5.0) = 1.0;
uniform float line_width : hint_range(0.01, 0.2) = 0.05;
uniform float pattern_scale : hint_range(1.0, 20.0) = 5.0;

// SDF for a single Celtic knot segment
float knot_segment(vec2 p, float r, float w) {
    float d = abs(length(p) - r) - w;
    return d;
}

// Interlacing pattern
float celtic_pattern(vec2 uv, float time) {
    vec2 id = floor(uv * pattern_scale);
    vec2 p = fract(uv * pattern_scale) - 0.5;

    // Alternate pattern based on cell
    float checker = mod(id.x + id.y, 2.0);

    // Create overlapping arcs
    float d1 = knot_segment(p - vec2(0.5, 0.0), 0.5, line_width);
    float d2 = knot_segment(p + vec2(0.5, 0.0), 0.5, line_width);

    // Animate interweaving
    float phase = sin(time * animation_speed + id.x * 0.5 + id.y * 0.7) * 0.5 + 0.5;

    return mix(d1, d2, phase * checker + (1.0 - checker) * (1.0 - phase));
}

void fragment() {
    vec2 uv = UV;
    float time = TIME;

    float pattern = celtic_pattern(uv, time);

    // Anti-aliased edge
    float edge = smoothstep(0.0, fwidth(pattern) * 2.0, pattern);

    // Mix colors based on pattern
    vec3 color = mix(primary_color.rgb, secondary_color.rgb, edge);

    // Add subtle glow on lines
    float glow = exp(-abs(pattern) * 10.0) * 0.3;
    color += primary_color.rgb * glow;

    ALBEDO = color;
    EMISSION = color * glow * 2.0;
}
"""

    def _spiral_shader(self) -> str:
        """Celtic spiral/triskele shader."""
        return """shader_type spatial;

uniform vec4 primary_color : source_color = vec4(0.8, 0.6, 0.2, 1.0);
uniform vec4 secondary_color : source_color = vec4(0.2, 0.5, 0.3, 1.0);
uniform float animation_speed : hint_range(0.0, 5.0) = 1.0;
uniform int num_arms : hint_range(2, 6) = 3;
uniform float spiral_tightness : hint_range(1.0, 10.0) = 3.0;

float spiral(vec2 p, float arms, float tightness, float rotation) {
    float angle = atan(p.y, p.x) + rotation;
    float radius = length(p);

    // Archimedean spiral
    float spiral_angle = radius * tightness * TAU;
    float arm_angle = angle * float(arms);

    float d = sin(arm_angle - spiral_angle);
    return abs(d) - 0.1;
}

void fragment() {
    vec2 uv = UV * 2.0 - 1.0;
    float time = TIME * animation_speed;

    // Create triskele with rotating arms
    float s = spiral(uv, float(num_arms), spiral_tightness, time);

    // Smooth edges
    float pattern = smoothstep(0.0, fwidth(s) * 2.0, s);

    // Color gradient from center
    float dist = length(uv);
    vec3 color = mix(primary_color.rgb, secondary_color.rgb, pattern);

    // Glow effect
    float glow = exp(-abs(s) * 8.0) * 0.4;
    color += primary_color.rgb * glow * (1.0 - dist);

    ALBEDO = color;
    EMISSION = color * glow * 1.5;
}
"""

    def _default_shader(self) -> str:
        """Default Celtic-themed shader."""
        return """shader_type spatial;

uniform vec4 primary_color : source_color = vec4(0.8, 0.6, 0.2, 1.0);
uniform vec4 secondary_color : source_color = vec4(0.2, 0.5, 0.3, 1.0);
uniform sampler2D albedo_texture : source_color;

void fragment() {
    vec4 tex = texture(albedo_texture, UV);
    vec3 color = mix(primary_color.rgb, secondary_color.rgb, tex.r);
    ALBEDO = color * tex.rgb;
    ALPHA = tex.a;
}
"""

    def _generate_scene(
        self,
        name: str,
        assets: list[tuple[AssetResponse, dict[str, Any]]],
    ) -> str:
        """Generate PackedScene (.tscn) file."""
        # Build external resources
        ext_resources = []
        for i, (asset, _) in enumerate(assets, 1):
            safe_asset_name = self._sanitize_name(asset.asset_id)
            ext_resources.append(
                f'[ext_resource type="Texture2D" path="res://{safe_asset_name}.png" id="{i}"]'
            )

        ext_section = "\n".join(ext_resources)

        # Build node tree
        nodes = [f'[node name="{name}" type="Node3D"]']

        for i, (asset, transform) in enumerate(assets, 1):
            safe_asset_name = self._sanitize_name(asset.asset_id)
            pos = transform.get("position", [0, 0, 0])
            rot = transform.get("rotation", [0, 0, 0])
            scale = transform.get("scale", [1, 1, 1])

            nodes.append(f"""
[node name="{safe_asset_name}" type="Sprite3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {pos[0]}, {pos[1]}, {pos[2]})
texture = ExtResource("{i}")
""")

        nodes_section = "\n".join(nodes)

        return f"""[gd_scene load_steps={len(assets) + 1} format=3]

{ext_section}

{nodes_section}
"""

    def _generate_uid(self) -> str:
        """Generate a unique ID for Godot resources."""
        import random
        import string

        chars = string.ascii_lowercase + string.digits
        return "".join(random.choices(chars, k=12))

    def _format_metadata(self, metadata: dict[str, Any]) -> str:
        """Format metadata as Godot resource properties."""
        if not metadata:
            return ""

        lines = ["metadata = {"]
        for key, value in metadata.items():
            if isinstance(value, str):
                lines.append(f'    "{key}": "{value}",')
            elif isinstance(value, dict):
                lines.append(f'    "{key}": {json.dumps(value)},')
            else:
                lines.append(f'    "{key}": {value},')
        lines.append("}")

        return "\n".join(lines)
