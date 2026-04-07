"""Babylon.js asset exporter.

Generates:
- TypeScript ES modules for asset loading
- .babylon scene files (JSON format)
- WGSL shaders for WebGPU rendering
- Asset manifest for lazy loading
"""

import base64
import json
import time
from pathlib import Path
from typing import Any

from ..models import AssetType, CelticStyle, AssetResponse
from .base_exporter import (
    BaseExporter,
    ExportConfig,
    ExportResult,
    TargetEngine,
)


class BabylonExporter(BaseExporter):
    """Export assets for Babylon.js 7+.

    Generates:
    - TypeScript asset modules with full type safety
    - .babylon JSON scene files
    - WGSL shaders for WebGPU
    - Asset manifests for lazy loading
    """

    @property
    def engine_name(self) -> str:
        return "Babylon.js"

    @property
    def engine_version(self) -> str:
        return "7.0"

    def export_texture(
        self,
        asset: AssetResponse,
        image_data: bytes,
        name: str,
    ) -> ExportResult:
        """Export texture with TypeScript module."""
        start_time = time.time()
        warnings = self.validate_asset(asset)
        safe_name = self._sanitize_name(name)

        try:
            # Write the PNG image
            png_path = self.config.output_dir / f"{safe_name}.png"
            png_path.write_bytes(image_data)

            # Generate TypeScript module
            ts_path = self.config.output_dir / f"{safe_name}.ts"
            ts_content = self._generate_texture_module(safe_name, asset)
            ts_path.write_text(ts_content)

            # Generate asset manifest entry
            manifest_path = self.config.output_dir / f"{safe_name}.manifest.json"
            manifest = self._generate_texture_manifest(safe_name, asset)
            manifest_path.write_text(json.dumps(manifest, indent=2))

            elapsed_ms = int((time.time() - start_time) * 1000)

            return ExportResult(
                success=True,
                engine=TargetEngine.BABYLON,
                asset_type=asset.asset_type,
                primary_file=ts_path,
                additional_files=[png_path, manifest_path],
                export_time_ms=elapsed_ms,
                file_sizes={
                    str(png_path): len(image_data),
                    str(ts_path): ts_path.stat().st_size,
                },
                warnings=warnings,
                import_instructions=(
                    "1. Copy files to your project's assets folder\n"
                    "2. Import the TypeScript module:\n"
                    f"   import {{ load{self._pascal_case(safe_name)}Texture }} from './{safe_name}';\n"
                    "3. Call the loader function with your scene"
                ),
            )

        except Exception as e:
            return ExportResult(
                success=False,
                engine=TargetEngine.BABYLON,
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
        """Export material as TypeScript module + WGSL shader."""
        start_time = time.time()
        safe_name = self._sanitize_name(name)

        try:
            # Generate WGSL shader for Celtic effects
            shader_path = self.config.output_dir / f"{safe_name}.wgsl"
            shader_content = self._generate_wgsl_shader(style, properties)
            shader_path.write_text(shader_content)

            # Generate TypeScript material module
            ts_path = self.config.output_dir / f"{safe_name}Material.ts"
            ts_content = self._generate_material_module(safe_name, textures, style, properties)
            ts_path.write_text(ts_content)

            # Generate material manifest
            manifest_path = self.config.output_dir / f"{safe_name}Material.manifest.json"
            manifest = self._generate_material_manifest(safe_name, textures, style, properties)
            manifest_path.write_text(json.dumps(manifest, indent=2))

            elapsed_ms = int((time.time() - start_time) * 1000)

            return ExportResult(
                success=True,
                engine=TargetEngine.BABYLON,
                asset_type=AssetType.SPELL_EFFECT,
                primary_file=ts_path,
                additional_files=[shader_path, manifest_path],
                export_time_ms=elapsed_ms,
                file_sizes={
                    str(ts_path): ts_path.stat().st_size,
                    str(shader_path): shader_path.stat().st_size,
                },
                import_instructions=(
                    f"1. Import the material module:\n"
                    f"   import {{ create{self._pascal_case(safe_name)}Material }} from './{safe_name}Material';\n"
                    "2. Call with your scene to create the material"
                ),
            )

        except Exception as e:
            return ExportResult(
                success=False,
                engine=TargetEngine.BABYLON,
                asset_type=AssetType.SPELL_EFFECT,
                error=str(e),
            )

    def export_scene(
        self,
        name: str,
        assets: list[tuple[AssetResponse, dict[str, Any]]],
    ) -> ExportResult:
        """Export scene as .babylon file + TypeScript loader."""
        start_time = time.time()
        safe_name = self._sanitize_name(name)

        try:
            # Generate .babylon scene file
            babylon_path = self.config.output_dir / f"{safe_name}.babylon"
            babylon_content = self._generate_babylon_scene(safe_name, assets)
            babylon_path.write_text(json.dumps(babylon_content, indent=2))

            # Generate TypeScript scene loader module
            ts_path = self.config.output_dir / f"{safe_name}Scene.ts"
            ts_content = self._generate_scene_module(safe_name, assets)
            ts_path.write_text(ts_content)

            elapsed_ms = int((time.time() - start_time) * 1000)

            return ExportResult(
                success=True,
                engine=TargetEngine.BABYLON,
                asset_type=AssetType.TERRITORY_TILE,
                primary_file=babylon_path,
                additional_files=[ts_path],
                export_time_ms=elapsed_ms,
                file_sizes={
                    str(babylon_path): babylon_path.stat().st_size,
                    str(ts_path): ts_path.stat().st_size,
                },
                import_instructions=(
                    "Load using SceneLoader:\n"
                    f"  SceneLoader.Load('', '{safe_name}.babylon', engine);\n"
                    "Or use the TypeScript module for full control"
                ),
            )

        except Exception as e:
            return ExportResult(
                success=False,
                engine=TargetEngine.BABYLON,
                asset_type=AssetType.TERRITORY_TILE,
                error=str(e),
            )

    def get_file_extension(self, asset_type: AssetType) -> str:
        """Get Babylon.js file extension for asset type."""
        extensions = {
            AssetType.CHARACTER_PORTRAIT: "ts",
            AssetType.ITEM_ICON: "ts",
            AssetType.CLAN_HERALDRY: "ts",
            AssetType.TERRITORY_TILE: "babylon",
            AssetType.SPELL_EFFECT: "ts",
            AssetType.CREATURE: "babylon",
        }
        return extensions.get(asset_type, "ts")

    def _pascal_case(self, name: str) -> str:
        """Convert to PascalCase."""
        return "".join(word.capitalize() for word in name.split("_"))

    def _generate_texture_module(self, name: str, asset: AssetResponse) -> str:
        """Generate TypeScript texture loader module."""
        pascal_name = self._pascal_case(name)
        metadata = self.generate_metadata(asset) if self.config.include_metadata else {}

        return f'''/**
 * {pascal_name} Texture Loader
 * Generated by Cianfhoghlaim Asset Pipeline
 *
 * Asset Type: {asset.asset_type}
 * Celtic Style: {asset.style}
 * Dimensions: {asset.width}x{asset.height}
 */

import {{ Scene, Texture }} from "@babylonjs/core";

export interface {pascal_name}TextureMetadata {{
  assetId: string;
  assetType: string;
  celticStyle: string;
  width: number;
  height: number;
  modelUsed: string;
  prompt: string;
  ipfsCid?: string;
  arweaveId?: string;
}}

export const {name.upper()}_METADATA: {pascal_name}TextureMetadata = {json.dumps(metadata, indent=2)};

/**
 * Load the {pascal_name} texture into a Babylon.js scene.
 *
 * @param scene - The Babylon.js scene
 * @param basePath - Base path to texture file (default: current directory)
 * @returns Promise resolving to the loaded Texture
 */
export async function load{pascal_name}Texture(
  scene: Scene,
  basePath: string = "./"
): Promise<Texture> {{
  const texture = new Texture(
    `${{basePath}}{name}.png`,
    scene,
    {str(not self.config.generate_mipmaps).lower()},  // noMipmap
    false,  // invertY
    Texture.TRILINEAR_SAMPLINGMODE
  );

  // Wait for texture to load
  await new Promise<void>((resolve, reject) => {{
    texture.onLoadObservable.addOnce(() => resolve());
    texture.onErrorObservable.addOnce((error) => reject(error));
  }});

  return texture;
}}

/**
 * Create a sprite with this texture.
 */
export function create{pascal_name}Sprite(
  scene: Scene,
  texture: Texture,
  width: number = {asset.width / 100},
  height: number = {asset.height / 100}
) {{
  // Import dynamically to avoid bundling unused code
  const {{ SpriteManager, Sprite }} = require("@babylonjs/core");

  const manager = new SpriteManager(
    "{name}Manager",
    texture.url,
    1,
    {{ width: {asset.width}, height: {asset.height} }},
    scene
  );

  const sprite = new Sprite("{name}", manager);
  sprite.width = width;
  sprite.height = height;

  return {{ sprite, manager }};
}}
'''

    def _generate_texture_manifest(self, name: str, asset: AssetResponse) -> dict:
        """Generate texture manifest for lazy loading."""
        return {
            "name": name,
            "type": "texture",
            "file": f"{name}.png",
            "module": f"{name}.ts",
            "dimensions": {
                "width": asset.width,
                "height": asset.height,
            },
            "metadata": self.generate_metadata(asset) if self.config.include_metadata else {},
            "babylonOptions": {
                "samplingMode": "TRILINEAR_SAMPLINGMODE",
                "generateMipMaps": self.config.generate_mipmaps,
                "invertY": False,
            },
        }

    def _generate_material_module(
        self,
        name: str,
        textures: dict[str, Path],
        style: CelticStyle,
        properties: dict[str, Any],
    ) -> str:
        """Generate TypeScript material module."""
        pascal_name = self._pascal_case(name)
        primary = properties.get("primary_color", [0.8, 0.6, 0.2, 1.0])
        secondary = properties.get("secondary_color", [0.2, 0.5, 0.3, 1.0])
        speed = properties.get("animation_speed", 1.0)

        # Determine if we use ShaderMaterial or StandardMaterial
        use_shader = style in (CelticStyle.KNOTWORK, CelticStyle.SPIRAL)

        if use_shader:
            return f'''/**
 * {pascal_name} Celtic Material
 * Generated by Cianfhoghlaim Asset Pipeline
 *
 * Celtic Style: {style}
 * Uses WebGPU ShaderMaterial for procedural patterns
 */

import {{
  Scene,
  ShaderMaterial,
  Effect,
  Color3,
  Vector2
}} from "@babylonjs/core";

// Import WGSL shader
import shaderCode from "./{name}.wgsl?raw";

export interface {pascal_name}MaterialOptions {{
  primaryColor?: Color3;
  secondaryColor?: Color3;
  animationSpeed?: number;
  lineWidth?: number;
  patternScale?: number;
}}

const DEFAULT_OPTIONS: Required<{pascal_name}MaterialOptions> = {{
  primaryColor: new Color3({primary[0]}, {primary[1]}, {primary[2]}),
  secondaryColor: new Color3({secondary[0]}, {secondary[1]}, {secondary[2]}),
  animationSpeed: {speed},
  lineWidth: 0.05,
  patternScale: 5.0,
}};

/**
 * Create the {pascal_name} Celtic shader material.
 */
export function create{pascal_name}Material(
  scene: Scene,
  options: {pascal_name}MaterialOptions = {{}}
): ShaderMaterial {{
  const opts = {{ ...DEFAULT_OPTIONS, ...options }};

  // Register shader if not already registered
  if (!Effect.ShadersStore["{name}VertexShader"]) {{
    Effect.ShadersStore["{name}VertexShader"] = `
      precision highp float;
      attribute vec3 position;
      attribute vec2 uv;
      uniform mat4 worldViewProjection;
      varying vec2 vUV;
      void main() {{
        gl_Position = worldViewProjection * vec4(position, 1.0);
        vUV = uv;
      }}
    `;
    Effect.ShadersStore["{name}FragmentShader"] = shaderCode;
  }}

  const material = new ShaderMaterial(
    "{name}Material",
    scene,
    {{
      vertex: "{name}",
      fragment: "{name}",
    }},
    {{
      attributes: ["position", "uv"],
      uniforms: [
        "worldViewProjection",
        "time",
        "primaryColor",
        "secondaryColor",
        "animationSpeed",
        "lineWidth",
        "patternScale",
      ],
    }}
  );

  // Set uniforms
  material.setColor3("primaryColor", opts.primaryColor);
  material.setColor3("secondaryColor", opts.secondaryColor);
  material.setFloat("animationSpeed", opts.animationSpeed);
  material.setFloat("lineWidth", opts.lineWidth);
  material.setFloat("patternScale", opts.patternScale);

  // Animate time uniform
  scene.registerBeforeRender(() => {{
    material.setFloat("time", performance.now() / 1000);
  }});

  return material;
}}
'''
        else:
            return f'''/**
 * {pascal_name} Material
 * Generated by Cianfhoghlaim Asset Pipeline
 *
 * Celtic Style: {style}
 * Uses StandardMaterial with texture mapping
 */

import {{
  Scene,
  StandardMaterial,
  Texture,
  Color3
}} from "@babylonjs/core";

export interface {pascal_name}MaterialOptions {{
  diffuseColor?: Color3;
  specularColor?: Color3;
  emissiveColor?: Color3;
  metallic?: number;
  roughness?: number;
}}

const DEFAULT_OPTIONS: Required<{pascal_name}MaterialOptions> = {{
  diffuseColor: new Color3({primary[0]}, {primary[1]}, {primary[2]}),
  specularColor: new Color3(0.1, 0.1, 0.1),
  emissiveColor: new Color3(0, 0, 0),
  metallic: {properties.get("metallic", 0.0)},
  roughness: {properties.get("roughness", 0.5)},
}};

/**
 * Create the {pascal_name} material.
 */
export function create{pascal_name}Material(
  scene: Scene,
  textures: {{ [key: string]: Texture }} = {{}},
  options: {pascal_name}MaterialOptions = {{}}
): StandardMaterial {{
  const opts = {{ ...DEFAULT_OPTIONS, ...options }};

  const material = new StandardMaterial("{name}Material", scene);

  material.diffuseColor = opts.diffuseColor;
  material.specularColor = opts.specularColor;
  material.emissiveColor = opts.emissiveColor;

  // Apply textures
  if (textures.albedo) {{
    material.diffuseTexture = textures.albedo;
  }}
  if (textures.normal) {{
    material.bumpTexture = textures.normal;
  }}
  if (textures.emission) {{
    material.emissiveTexture = textures.emission;
  }}

  return material;
}}
'''

    def _generate_material_manifest(
        self,
        name: str,
        textures: dict[str, Path],
        style: CelticStyle,
        properties: dict[str, Any],
    ) -> dict:
        """Generate material manifest."""
        return {
            "name": f"{name}Material",
            "type": "material",
            "module": f"{name}Material.ts",
            "shader": f"{name}.wgsl" if style in (CelticStyle.KNOTWORK, CelticStyle.SPIRAL) else None,
            "celticStyle": style,
            "textures": {slot: str(path.name) for slot, path in textures.items()},
            "defaultParameters": {
                "primaryColor": properties.get("primary_color", [0.8, 0.6, 0.2, 1.0]),
                "secondaryColor": properties.get("secondary_color", [0.2, 0.5, 0.3, 1.0]),
                "animationSpeed": properties.get("animation_speed", 1.0),
            },
        }

    def _generate_wgsl_shader(self, style: CelticStyle, properties: dict[str, Any]) -> str:
        """Generate WGSL shader for Celtic effects."""
        if style == CelticStyle.KNOTWORK:
            return self._knotwork_wgsl()
        elif style == CelticStyle.SPIRAL:
            return self._spiral_wgsl()
        return self._default_wgsl()

    def _knotwork_wgsl(self) -> str:
        """Celtic knotwork WGSL shader."""
        return """// Celtic Knotwork Shader
// Generated by Cianfhoghlaim Asset Pipeline

precision highp float;

varying vec2 vUV;

uniform float time;
uniform vec3 primaryColor;
uniform vec3 secondaryColor;
uniform float animationSpeed;
uniform float lineWidth;
uniform float patternScale;

float knotSegment(vec2 p, float r, float w) {
    return abs(length(p) - r) - w;
}

float celticPattern(vec2 uv, float t) {
    vec2 id = floor(uv * patternScale);
    vec2 p = fract(uv * patternScale) - 0.5;

    float checker = mod(id.x + id.y, 2.0);

    float d1 = knotSegment(p - vec2(0.5, 0.0), 0.5, lineWidth);
    float d2 = knotSegment(p + vec2(0.5, 0.0), 0.5, lineWidth);

    float phase = sin(t * animationSpeed + id.x * 0.5 + id.y * 0.7) * 0.5 + 0.5;

    return mix(d1, d2, phase * checker + (1.0 - checker) * (1.0 - phase));
}

void main() {
    float pattern = celticPattern(vUV, time);

    // Anti-aliased edge
    float edge = smoothstep(0.0, fwidth(pattern) * 2.0, pattern);

    // Mix colors based on pattern
    vec3 color = mix(primaryColor, secondaryColor, edge);

    // Add subtle glow on lines
    float glow = exp(-abs(pattern) * 10.0) * 0.3;
    color += primaryColor * glow;

    gl_FragColor = vec4(color, 1.0);
}
"""

    def _spiral_wgsl(self) -> str:
        """Celtic spiral WGSL shader."""
        return """// Celtic Spiral/Triskele Shader
// Generated by Cianfhoghlaim Asset Pipeline

precision highp float;

varying vec2 vUV;

uniform float time;
uniform vec3 primaryColor;
uniform vec3 secondaryColor;
uniform float animationSpeed;

const float TAU = 6.28318530718;
const float NUM_ARMS = 3.0;
const float SPIRAL_TIGHTNESS = 3.0;

float spiral(vec2 p, float arms, float tightness, float rotation) {
    float angle = atan(p.y, p.x) + rotation;
    float radius = length(p);

    float spiralAngle = radius * tightness * TAU;
    float armAngle = angle * arms;

    float d = sin(armAngle - spiralAngle);
    return abs(d) - 0.1;
}

void main() {
    vec2 uv = vUV * 2.0 - 1.0;

    float s = spiral(uv, NUM_ARMS, SPIRAL_TIGHTNESS, time * animationSpeed);
    float pattern = smoothstep(0.0, fwidth(s) * 2.0, s);

    float dist = length(uv);
    vec3 color = mix(primaryColor, secondaryColor, pattern);

    // Glow effect
    float glow = exp(-abs(s) * 8.0) * 0.4;
    color += primaryColor * glow * (1.0 - dist);

    gl_FragColor = vec4(color, 1.0);
}
"""

    def _default_wgsl(self) -> str:
        """Default WGSL shader."""
        return """// Celtic Default Shader
// Generated by Cianfhoghlaim Asset Pipeline

precision highp float;

varying vec2 vUV;

uniform vec3 primaryColor;
uniform vec3 secondaryColor;
uniform sampler2D albedoTexture;

void main() {
    vec4 tex = texture2D(albedoTexture, vUV);
    vec3 color = mix(primaryColor, secondaryColor, tex.r);
    gl_FragColor = vec4(color * tex.rgb, tex.a);
}
"""

    def _generate_babylon_scene(
        self,
        name: str,
        assets: list[tuple[AssetResponse, dict[str, Any]]],
    ) -> dict:
        """Generate .babylon scene file."""
        meshes = []
        materials = []

        for i, (asset, transform) in enumerate(assets):
            safe_name = self._sanitize_name(asset.asset_id)
            pos = transform.get("position", [0, 0, 0])
            rot = transform.get("rotation", [0, 0, 0])
            scale = transform.get("scale", [1, 1, 1])

            # Create plane mesh for sprite
            mesh_id = f"mesh_{safe_name}"
            material_id = f"material_{safe_name}"

            meshes.append({
                "name": safe_name,
                "id": mesh_id,
                "type": "Plane",
                "position": pos,
                "rotation": rot,
                "scaling": scale,
                "materialId": material_id,
                "isEnabled": True,
                "isVisible": True,
                "billboardMode": 0,
            })

            materials.append({
                "name": material_id,
                "id": material_id,
                "diffuseTexture": {
                    "name": f"{safe_name}.png",
                    "level": 1,
                    "hasAlpha": True,
                },
                "diffuse": [1, 1, 1],
                "specular": [0, 0, 0],
                "emissive": [0, 0, 0],
                "backFaceCulling": False,
            })

        return {
            "producer": {
                "name": "Cianfhoghlaim Asset Pipeline",
                "version": "1.0",
                "exporter_version": "1.0",
            },
            "autoClear": True,
            "clearColor": [0.2, 0.2, 0.3],
            "ambientColor": [0.3, 0.3, 0.3],
            "gravity": [0, -9.81, 0],
            "cameras": [{
                "name": "MainCamera",
                "id": "camera_main",
                "type": "FreeCamera",
                "position": [0, 2, -10],
                "target": [0, 0, 0],
                "fov": 0.8,
                "minZ": 0.1,
                "maxZ": 1000,
            }],
            "lights": [{
                "name": "DirectionalLight",
                "id": "light_main",
                "type": 1,  # DirectionalLight
                "position": [0, 10, 0],
                "direction": [0, -1, 0.5],
                "intensity": 1,
                "diffuse": [1, 1, 1],
                "specular": [1, 1, 1],
            }],
            "materials": materials,
            "meshes": meshes,
        }

    def _generate_scene_module(
        self,
        name: str,
        assets: list[tuple[AssetResponse, dict[str, Any]]],
    ) -> str:
        """Generate TypeScript scene loader module."""
        pascal_name = self._pascal_case(name)

        asset_imports = []
        for asset, _ in assets:
            safe_name = self._sanitize_name(asset.asset_id)
            pascal_asset = self._pascal_case(safe_name)
            asset_imports.append(
                f"import {{ load{pascal_asset}Texture }} from './{safe_name}';"
            )

        return f'''/**
 * {pascal_name} Scene Loader
 * Generated by Cianfhoghlaim Asset Pipeline
 */

import {{
  Scene,
  Engine,
  FreeCamera,
  HemisphericLight,
  Vector3,
  MeshBuilder,
  StandardMaterial,
  SceneLoader,
}} from "@babylonjs/core";

{chr(10).join(asset_imports)}

export interface {pascal_name}SceneOptions {{
  basePath?: string;
  enablePhysics?: boolean;
}}

/**
 * Load the {pascal_name} scene from .babylon file.
 */
export async function load{pascal_name}Scene(
  engine: Engine,
  options: {pascal_name}SceneOptions = {{}}
): Promise<Scene> {{
  const basePath = options.basePath ?? "./";

  return new Promise((resolve, reject) => {{
    SceneLoader.Load(
      basePath,
      "{name}.babylon",
      engine,
      (scene) => {{
        // Post-load setup
        scene.createDefaultCameraOrLight(true, true, true);
        resolve(scene);
      }},
      undefined,
      (scene, message, exception) => {{
        reject(exception ?? new Error(message));
      }}
    );
  }});
}}

/**
 * Create the {pascal_name} scene programmatically.
 */
export async function create{pascal_name}Scene(
  engine: Engine,
  options: {pascal_name}SceneOptions = {{}}
): Promise<Scene> {{
  const basePath = options.basePath ?? "./";
  const scene = new Scene(engine);

  // Camera
  const camera = new FreeCamera("mainCamera", new Vector3(0, 2, -10), scene);
  camera.setTarget(Vector3.Zero());
  camera.attachControl(engine.getRenderingCanvas(), true);

  // Light
  const light = new HemisphericLight("mainLight", new Vector3(0, 1, 0), scene);
  light.intensity = 0.7;

  // Load textures and create sprites
  await Promise.all([
    // Add texture loading here
  ]);

  return scene;
}}

/**
 * Scene asset manifest for lazy loading.
 */
export const {name.upper()}_MANIFEST = {{
  name: "{name}",
  assets: {json.dumps([self._sanitize_name(a[0].asset_id) for a in assets])},
  sceneFile: "{name}.babylon",
}};
'''
