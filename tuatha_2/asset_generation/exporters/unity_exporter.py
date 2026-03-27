"""Unity asset exporter.

Generates:
- .prefab: Prefab files for GameObjects
- .asset: ScriptableObject assets
- .mat: Material files
- .meta: Unity metadata files
"""

import hashlib
import time
import uuid
from pathlib import Path
from typing import Any

from ..models import AssetType, CelticStyle, AssetResponse
from .base_exporter import (
    BaseExporter,
    ExportConfig,
    ExportResult,
    TargetEngine,
)


class UnityExporter(BaseExporter):
    """Export assets for Unity 2022+.

    Supports:
    - Texture2D assets with import settings
    - Standard/URP/HDRP materials
    - Prefabs with positioned sprites/meshes
    - Custom Celtic shader materials
    """

    @property
    def engine_name(self) -> str:
        return "Unity"

    @property
    def engine_version(self) -> str:
        return "2022.3 LTS"

    def export_texture(
        self,
        asset: AssetResponse,
        image_data: bytes,
        name: str,
    ) -> ExportResult:
        """Export texture with Unity metadata."""
        start_time = time.time()
        warnings = self.validate_asset(asset)
        safe_name = self._sanitize_name(name)

        try:
            # Write the PNG image
            png_path = self.config.output_dir / f"{safe_name}.png"
            png_path.write_bytes(image_data)

            # Generate GUID for asset
            guid = self._generate_guid(safe_name)

            # Create .meta file
            meta_path = self.config.output_dir / f"{safe_name}.png.meta"
            meta_content = self._generate_texture_meta(guid, asset)
            meta_path.write_text(meta_content)

            elapsed_ms = int((time.time() - start_time) * 1000)

            return ExportResult(
                success=True,
                engine=TargetEngine.UNITY,
                asset_type=asset.asset_type,
                primary_file=png_path,
                additional_files=[meta_path],
                export_time_ms=elapsed_ms,
                file_sizes={
                    str(png_path): len(image_data),
                    str(meta_path): meta_path.stat().st_size,
                },
                warnings=warnings,
                import_instructions=(
                    "Place files in your Unity project's Assets folder. "
                    "Keep the .meta file alongside the texture. "
                    "Unity will auto-import on editor focus."
                ),
            )

        except Exception as e:
            return ExportResult(
                success=False,
                engine=TargetEngine.UNITY,
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
        """Export material as Unity .mat file."""
        start_time = time.time()
        safe_name = self._sanitize_name(name)

        try:
            guid = self._generate_guid(safe_name)

            # Determine shader based on style
            if style in (CelticStyle.KNOTWORK, CelticStyle.SPIRAL):
                shader_name = f"Cianfhoghlaim/Celtic{style.title()}"
                material_content = self._generate_celtic_material(
                    safe_name, textures, style, properties
                )
                # Also export the shader
                shader_path = self.config.output_dir / f"Celtic{style.title()}.shader"
                shader_content = self._generate_celtic_shader(style)
                shader_path.write_text(shader_content)

                shader_meta_path = self.config.output_dir / f"Celtic{style.title()}.shader.meta"
                shader_meta = self._generate_shader_meta(self._generate_guid(f"shader_{style}"))
                shader_meta_path.write_text(shader_meta)
            else:
                shader_name = "Universal Render Pipeline/Lit"
                material_content = self._generate_urp_material(
                    safe_name, textures, properties
                )
                shader_path = None
                shader_meta_path = None

            # Write material
            material_path = self.config.output_dir / f"{safe_name}.mat"
            material_path.write_text(material_content)

            # Write material meta
            material_meta_path = self.config.output_dir / f"{safe_name}.mat.meta"
            material_meta = self._generate_material_meta(guid)
            material_meta_path.write_text(material_meta)

            elapsed_ms = int((time.time() - start_time) * 1000)

            additional = [material_meta_path]
            if shader_path:
                additional.extend([shader_path, shader_meta_path])

            return ExportResult(
                success=True,
                engine=TargetEngine.UNITY,
                asset_type=AssetType.SPELL_EFFECT,
                primary_file=material_path,
                additional_files=additional,
                export_time_ms=elapsed_ms,
                file_sizes={str(material_path): material_path.stat().st_size},
            )

        except Exception as e:
            return ExportResult(
                success=False,
                engine=TargetEngine.UNITY,
                asset_type=AssetType.SPELL_EFFECT,
                error=str(e),
            )

    def export_scene(
        self,
        name: str,
        assets: list[tuple[AssetResponse, dict[str, Any]]],
    ) -> ExportResult:
        """Export scene as Unity prefab."""
        start_time = time.time()
        safe_name = self._sanitize_name(name)

        try:
            guid = self._generate_guid(safe_name)

            prefab_content = self._generate_prefab(safe_name, assets)
            prefab_path = self.config.output_dir / f"{safe_name}.prefab"
            prefab_path.write_text(prefab_content)

            prefab_meta_path = self.config.output_dir / f"{safe_name}.prefab.meta"
            prefab_meta = self._generate_prefab_meta(guid)
            prefab_meta_path.write_text(prefab_meta)

            elapsed_ms = int((time.time() - start_time) * 1000)

            return ExportResult(
                success=True,
                engine=TargetEngine.UNITY,
                asset_type=AssetType.TERRITORY_TILE,
                primary_file=prefab_path,
                additional_files=[prefab_meta_path],
                export_time_ms=elapsed_ms,
                file_sizes={str(prefab_path): prefab_path.stat().st_size},
                import_instructions=(
                    "Place the .prefab and .prefab.meta in your Assets folder. "
                    "Ensure referenced textures are imported first. "
                    "Drag the prefab into your scene hierarchy."
                ),
            )

        except Exception as e:
            return ExportResult(
                success=False,
                engine=TargetEngine.UNITY,
                asset_type=AssetType.TERRITORY_TILE,
                error=str(e),
            )

    def get_file_extension(self, asset_type: AssetType) -> str:
        """Get Unity file extension for asset type."""
        extensions = {
            AssetType.CHARACTER_PORTRAIT: "png",
            AssetType.ITEM_ICON: "png",
            AssetType.CLAN_HERALDRY: "png",
            AssetType.TERRITORY_TILE: "prefab",
            AssetType.SPELL_EFFECT: "mat",
            AssetType.CREATURE: "prefab",
        }
        return extensions.get(asset_type, "asset")

    def _generate_guid(self, name: str) -> str:
        """Generate deterministic GUID from name."""
        hash_bytes = hashlib.md5(name.encode()).hexdigest()
        return hash_bytes[:32]

    def _generate_file_id(self) -> int:
        """Generate Unity file ID."""
        return abs(hash(uuid.uuid4())) % (2**31)

    def _generate_texture_meta(self, guid: str, asset: AssetResponse) -> str:
        """Generate Unity texture import settings."""
        is_sprite = asset.asset_type in (
            AssetType.CHARACTER_PORTRAIT,
            AssetType.ITEM_ICON,
            AssetType.CLAN_HERALDRY,
        )

        texture_type = "8" if is_sprite else "0"  # 8 = Sprite, 0 = Default
        sprite_mode = "1" if is_sprite else "0"  # 1 = Single, 0 = None

        return f"""fileFormatVersion: 2
guid: {guid}
TextureImporter:
  internalIDToNameTable: []
  externalObjects: {{}}
  serializedVersion: 12
  mipmaps:
    mipMapMode: 0
    enableMipMap: {1 if self.config.generate_mipmaps else 0}
    sRGBTexture: 1
    linearTexture: 0
    fadeOut: 0
    borderMipMap: 0
    mipMapsPreserveCoverage: 0
    alphaTestReferenceValue: 0.5
    mipMapFadeDistanceStart: 1
    mipMapFadeDistanceEnd: 3
  bumpmap:
    convertToNormalMap: 0
    externalNormalMap: 0
    heightScale: 0.25
    normalMapFilter: 0
  isReadable: 0
  streamingMipmaps: 0
  streamingMipmapsPriority: 0
  vTOnly: 0
  grayScaleToAlpha: 0
  generateCubemap: 6
  cubemapConvolution: 0
  seamlessCubemap: 0
  textureFormat: 1
  maxTextureSize: {self.config.texture_max_size}
  textureSettings:
    serializedVersion: 2
    filterMode: 1
    aniso: 1
    mipBias: 0
    wrapU: 1
    wrapV: 1
    wrapW: 0
  nPOTScale: 0
  lightmap: 0
  compressionQuality: 50
  spriteMode: {sprite_mode}
  spriteExtrude: 1
  spriteMeshType: 1
  alignment: 0
  spritePivot: {{x: 0.5, y: 0.5}}
  spritePixelsToUnits: 100
  spriteBorder: {{x: 0, y: 0, z: 0, w: 0}}
  spriteGenerateFallbackPhysicsShape: 1
  alphaUsage: 1
  alphaIsTransparency: 1
  spriteTessellationDetail: -1
  textureType: {texture_type}
  textureShape: 1
  singleChannelComponent: 0
  flipbookRows: 1
  flipbookColumns: 1
  maxTextureSizeSet: 0
  compressionQualitySet: 0
  textureFormatSet: 0
  ignorePngGamma: 0
  applyGammaDecoding: 0
  swizzle: 50462976
  platformSettings:
  - serializedVersion: 3
    buildTarget: DefaultTexturePlatform
    maxTextureSize: {self.config.texture_max_size}
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 1
    compressionQuality: 50
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  spriteSheet:
    serializedVersion: 2
    sprites: []
    outline: []
    physicsShape: []
    bones: []
    spriteID: {self._generate_guid('sprite_' + guid)[:8]}
    internalID: 0
    vertices: []
    indices:
    edges: []
    weights: []
    secondaryTextures: []
  spritePackingTag:
  pSDRemoveMatte: 0
  userData:
  assetBundleName:
  assetBundleVariant:
"""

    def _generate_material_meta(self, guid: str) -> str:
        """Generate Unity material meta file."""
        return f"""fileFormatVersion: 2
guid: {guid}
NativeFormatImporter:
  externalObjects: {{}}
  mainObjectFileID: 2100000
  userData:
  assetBundleName:
  assetBundleVariant:
"""

    def _generate_shader_meta(self, guid: str) -> str:
        """Generate Unity shader meta file."""
        return f"""fileFormatVersion: 2
guid: {guid}
ShaderImporter:
  externalObjects: {{}}
  defaultTextures: []
  nonModifiableTextures: []
  userData:
  assetBundleName:
  assetBundleVariant:
"""

    def _generate_prefab_meta(self, guid: str) -> str:
        """Generate Unity prefab meta file."""
        return f"""fileFormatVersion: 2
guid: {guid}
PrefabImporter:
  externalObjects: {{}}
  userData:
  assetBundleName:
  assetBundleVariant:
"""

    def _generate_urp_material(
        self,
        name: str,
        textures: dict[str, Path],
        properties: dict[str, Any],
    ) -> str:
        """Generate URP Lit material."""
        base_color = properties.get("albedo_color", [1, 1, 1, 1])
        metallic = properties.get("metallic", 0.0)
        smoothness = 1.0 - properties.get("roughness", 0.5)

        # Generate texture references
        texture_refs = ""
        if "albedo" in textures:
            texture_refs += f"""    - _BaseMap:
        m_Texture: {{fileID: 2800000, guid: {self._generate_guid(textures['albedo'].stem)}, type: 3}}
        m_Scale: {{x: 1, y: 1}}
        m_Offset: {{x: 0, y: 0}}
"""

        return f"""%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!21 &2100000
Material:
  serializedVersion: 8
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_Name: {name}
  m_Shader: {{fileID: 4800000, guid: 933532a4fcc9baf4fa0491de14d08ed7, type: 3}}
  m_ValidKeywords: []
  m_InvalidKeywords: []
  m_LightmapFlags: 4
  m_EnableInstancingVariants: 0
  m_DoubleSidedGI: 0
  m_CustomRenderQueue: -1
  stringTagMap: {{}}
  disabledShaderPasses: []
  m_SavedProperties:
    serializedVersion: 3
    m_TexEnvs:
{texture_refs}
    m_Floats:
    - _Metallic: {metallic}
    - _Smoothness: {smoothness}
    - _Surface: 0
    - _Blend: 0
    - _Cull: 2
    - _ZWrite: 1
    m_Colors:
    - _BaseColor: {{r: {base_color[0]}, g: {base_color[1]}, b: {base_color[2]}, a: {base_color[3]}}}
  m_BuildTextureStacks: []
"""

    def _generate_celtic_material(
        self,
        name: str,
        textures: dict[str, Path],
        style: CelticStyle,
        properties: dict[str, Any],
    ) -> str:
        """Generate Celtic shader material."""
        primary = properties.get("primary_color", [0.8, 0.6, 0.2, 1.0])
        secondary = properties.get("secondary_color", [0.2, 0.5, 0.3, 1.0])
        speed = properties.get("animation_speed", 1.0)

        return f"""%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!21 &2100000
Material:
  serializedVersion: 8
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_Name: {name}
  m_Shader: {{fileID: 4800000, guid: {self._generate_guid(f'shader_{style}')}, type: 3}}
  m_ValidKeywords: []
  m_InvalidKeywords: []
  m_LightmapFlags: 4
  m_EnableInstancingVariants: 0
  m_DoubleSidedGI: 0
  m_CustomRenderQueue: 3000
  stringTagMap:
    RenderType: Transparent
  disabledShaderPasses: []
  m_SavedProperties:
    serializedVersion: 3
    m_TexEnvs: []
    m_Floats:
    - _AnimationSpeed: {speed}
    - _LineWidth: 0.05
    - _PatternScale: 5.0
    m_Colors:
    - _PrimaryColor: {{r: {primary[0]}, g: {primary[1]}, b: {primary[2]}, a: {primary[3]}}}
    - _SecondaryColor: {{r: {secondary[0]}, g: {secondary[1]}, b: {secondary[2]}, a: {secondary[3]}}}
  m_BuildTextureStacks: []
"""

    def _generate_celtic_shader(self, style: CelticStyle) -> str:
        """Generate Unity shader for Celtic patterns."""
        if style == CelticStyle.KNOTWORK:
            return self._knotwork_shader()
        elif style == CelticStyle.SPIRAL:
            return self._spiral_shader()
        return self._default_shader()

    def _knotwork_shader(self) -> str:
        """Celtic knotwork shader for Unity."""
        return """Shader "Cianfhoghlaim/CelticKnotwork"
{
    Properties
    {
        _PrimaryColor ("Primary Color", Color) = (0.8, 0.6, 0.2, 1)
        _SecondaryColor ("Secondary Color", Color) = (0.2, 0.5, 0.3, 1)
        _AnimationSpeed ("Animation Speed", Range(0, 5)) = 1
        _LineWidth ("Line Width", Range(0.01, 0.2)) = 0.05
        _PatternScale ("Pattern Scale", Range(1, 20)) = 5
    }

    SubShader
    {
        Tags { "RenderType"="Transparent" "Queue"="Transparent" }
        LOD 100
        Blend SrcAlpha OneMinusSrcAlpha

        Pass
        {
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #pragma multi_compile_fog

            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex : POSITION;
                float2 uv : TEXCOORD0;
            };

            struct v2f
            {
                float2 uv : TEXCOORD0;
                UNITY_FOG_COORDS(1)
                float4 vertex : SV_POSITION;
            };

            float4 _PrimaryColor;
            float4 _SecondaryColor;
            float _AnimationSpeed;
            float _LineWidth;
            float _PatternScale;

            float knotSegment(float2 p, float r, float w)
            {
                return abs(length(p) - r) - w;
            }

            float celticPattern(float2 uv, float time)
            {
                float2 id = floor(uv * _PatternScale);
                float2 p = frac(uv * _PatternScale) - 0.5;

                float checker = fmod(id.x + id.y, 2.0);

                float d1 = knotSegment(p - float2(0.5, 0.0), 0.5, _LineWidth);
                float d2 = knotSegment(p + float2(0.5, 0.0), 0.5, _LineWidth);

                float phase = sin(time * _AnimationSpeed + id.x * 0.5 + id.y * 0.7) * 0.5 + 0.5;

                return lerp(d1, d2, phase * checker + (1.0 - checker) * (1.0 - phase));
            }

            v2f vert (appdata v)
            {
                v2f o;
                o.vertex = UnityObjectToClipPos(v.vertex);
                o.uv = v.uv;
                UNITY_TRANSFER_FOG(o,o.vertex);
                return o;
            }

            fixed4 frag (v2f i) : SV_Target
            {
                float pattern = celticPattern(i.uv, _Time.y);
                float edge = smoothstep(0.0, fwidth(pattern) * 2.0, pattern);

                float3 color = lerp(_PrimaryColor.rgb, _SecondaryColor.rgb, edge);

                float glow = exp(-abs(pattern) * 10.0) * 0.3;
                color += _PrimaryColor.rgb * glow;

                fixed4 col = fixed4(color, 1.0 - edge * 0.5);
                UNITY_APPLY_FOG(i.fogCoord, col);
                return col;
            }
            ENDHLSL
        }
    }
}
"""

    def _spiral_shader(self) -> str:
        """Celtic spiral shader for Unity."""
        return """Shader "Cianfhoghlaim/CelticSpiral"
{
    Properties
    {
        _PrimaryColor ("Primary Color", Color) = (0.8, 0.6, 0.2, 1)
        _SecondaryColor ("Secondary Color", Color) = (0.2, 0.5, 0.3, 1)
        _AnimationSpeed ("Animation Speed", Range(0, 5)) = 1
        _NumArms ("Number of Arms", Range(2, 6)) = 3
        _SpiralTightness ("Spiral Tightness", Range(1, 10)) = 3
    }

    SubShader
    {
        Tags { "RenderType"="Transparent" "Queue"="Transparent" }
        LOD 100
        Blend SrcAlpha OneMinusSrcAlpha

        Pass
        {
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag

            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex : POSITION;
                float2 uv : TEXCOORD0;
            };

            struct v2f
            {
                float2 uv : TEXCOORD0;
                float4 vertex : SV_POSITION;
            };

            float4 _PrimaryColor;
            float4 _SecondaryColor;
            float _AnimationSpeed;
            float _NumArms;
            float _SpiralTightness;

            #define TAU 6.28318530718

            float spiral(float2 p, float arms, float tightness, float rotation)
            {
                float angle = atan2(p.y, p.x) + rotation;
                float radius = length(p);

                float spiralAngle = radius * tightness * TAU;
                float armAngle = angle * arms;

                float d = sin(armAngle - spiralAngle);
                return abs(d) - 0.1;
            }

            v2f vert (appdata v)
            {
                v2f o;
                o.vertex = UnityObjectToClipPos(v.vertex);
                o.uv = v.uv;
                return o;
            }

            fixed4 frag (v2f i) : SV_Target
            {
                float2 uv = i.uv * 2.0 - 1.0;
                float time = _Time.y * _AnimationSpeed;

                float s = spiral(uv, _NumArms, _SpiralTightness, time);
                float pattern = smoothstep(0.0, fwidth(s) * 2.0, s);

                float dist = length(uv);
                float3 color = lerp(_PrimaryColor.rgb, _SecondaryColor.rgb, pattern);

                float glow = exp(-abs(s) * 8.0) * 0.4;
                color += _PrimaryColor.rgb * glow * (1.0 - dist);

                return fixed4(color, 1.0 - pattern * 0.3);
            }
            ENDHLSL
        }
    }
}
"""

    def _default_shader(self) -> str:
        """Default Celtic shader."""
        return """Shader "Cianfhoghlaim/CelticDefault"
{
    Properties
    {
        _MainTex ("Texture", 2D) = "white" {}
        _PrimaryColor ("Primary Color", Color) = (0.8, 0.6, 0.2, 1)
        _SecondaryColor ("Secondary Color", Color) = (0.2, 0.5, 0.3, 1)
    }

    SubShader
    {
        Tags { "RenderType"="Opaque" }
        LOD 100

        Pass
        {
            HLSLPROGRAM
            #pragma vertex vert
            #pragma fragment frag

            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex : POSITION;
                float2 uv : TEXCOORD0;
            };

            struct v2f
            {
                float2 uv : TEXCOORD0;
                float4 vertex : SV_POSITION;
            };

            sampler2D _MainTex;
            float4 _MainTex_ST;
            float4 _PrimaryColor;
            float4 _SecondaryColor;

            v2f vert (appdata v)
            {
                v2f o;
                o.vertex = UnityObjectToClipPos(v.vertex);
                o.uv = TRANSFORM_TEX(v.uv, _MainTex);
                return o;
            }

            fixed4 frag (v2f i) : SV_Target
            {
                fixed4 tex = tex2D(_MainTex, i.uv);
                float3 color = lerp(_PrimaryColor.rgb, _SecondaryColor.rgb, tex.r);
                return fixed4(color * tex.rgb, tex.a);
            }
            ENDHLSL
        }
    }
}
"""

    def _generate_prefab(
        self,
        name: str,
        assets: list[tuple[AssetResponse, dict[str, Any]]],
    ) -> str:
        """Generate Unity prefab file."""
        file_id = self._generate_file_id()

        # Build child GameObjects
        children = []
        for i, (asset, transform) in enumerate(assets):
            child_id = self._generate_file_id()
            safe_asset_name = self._sanitize_name(asset.asset_id)
            pos = transform.get("position", [0, 0, 0])
            rot = transform.get("rotation", [0, 0, 0, 1])  # Quaternion
            scale = transform.get("scale", [1, 1, 1])

            children.append(f"""--- !u!1 &{child_id}
GameObject:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  serializedVersion: 6
  m_Component:
  - component: {{fileID: {child_id + 1}}}
  - component: {{fileID: {child_id + 2}}}
  m_Layer: 0
  m_Name: {safe_asset_name}
  m_TagString: Untagged
  m_Icon: {{fileID: 0}}
  m_NavMeshLayer: 0
  m_StaticEditorFlags: 0
  m_IsActive: 1
--- !u!4 &{child_id + 1}
Transform:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {child_id}}}
  m_LocalRotation: {{x: {rot[0] if len(rot) > 3 else 0}, y: {rot[1] if len(rot) > 3 else 0}, z: {rot[2] if len(rot) > 3 else 0}, w: {rot[3] if len(rot) > 3 else 1}}}
  m_LocalPosition: {{x: {pos[0]}, y: {pos[1]}, z: {pos[2]}}}
  m_LocalScale: {{x: {scale[0]}, y: {scale[1]}, z: {scale[2]}}}
  m_Children: []
  m_Father: {{fileID: {file_id + 1}}}
  m_RootOrder: {i}
  m_LocalEulerAnglesHint: {{x: 0, y: 0, z: 0}}
--- !u!212 &{child_id + 2}
SpriteRenderer:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {child_id}}}
  m_Enabled: 1
  m_CastShadows: 0
  m_ReceiveShadows: 0
  m_DynamicOccludee: 1
  m_StaticShadowCaster: 0
  m_MotionVectors: 1
  m_LightProbeUsage: 1
  m_ReflectionProbeUsage: 1
  m_RayTracingMode: 0
  m_RayTraceProcedural: 0
  m_RenderingLayerMask: 1
  m_RendererPriority: 0
  m_Materials:
  - {{fileID: 10754, guid: 0000000000000000f000000000000000, type: 0}}
  m_Sprite: {{fileID: 21300000, guid: {self._generate_guid(safe_asset_name)}, type: 3}}
  m_Color: {{r: 1, g: 1, b: 1, a: 1}}
  m_FlipX: 0
  m_FlipY: 0
  m_DrawMode: 0
  m_Size: {{x: 1, y: 1}}
  m_SortingLayerID: 0
  m_SortingLayer: 0
  m_SortingOrder: 0
  m_SpriteTileMode: 0
  m_WasSpriteAssigned: 1
  m_MaskInteraction: 0
  m_SpriteSortPoint: 0
""")

        children_refs = "\n  ".join([f"- {{fileID: {self._generate_file_id() + i * 3 + 1}}}" for i in range(len(assets))])

        return f"""%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!1 &{file_id}
GameObject:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  serializedVersion: 6
  m_Component:
  - component: {{fileID: {file_id + 1}}}
  m_Layer: 0
  m_Name: {name}
  m_TagString: Untagged
  m_Icon: {{fileID: 0}}
  m_NavMeshLayer: 0
  m_StaticEditorFlags: 0
  m_IsActive: 1
--- !u!4 &{file_id + 1}
Transform:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {file_id}}}
  m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
  m_LocalPosition: {{x: 0, y: 0, z: 0}}
  m_LocalScale: {{x: 1, y: 1, z: 1}}
  m_Children:
  {children_refs}
  m_Father: {{fileID: 0}}
  m_RootOrder: 0
  m_LocalEulerAnglesHint: {{x: 0, y: 0, z: 0}}
{"".join(children)}
"""
