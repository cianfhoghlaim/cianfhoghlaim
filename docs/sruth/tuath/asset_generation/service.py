"""Celtic asset generation service using LiteLLM."""

import asyncio
import base64
import hashlib
import time
from typing import Optional
from pathlib import Path

import httpx
from pydantic import BaseModel

from .models import (
    AssetRequest,
    AssetResponse,
    AssetType,
    CelticStyle,
    GenerationModel,
    BatchAssetRequest,
    BatchAssetResponse,
)
from .prompts import CelticPromptGenerator


class LiteLLMConfig(BaseModel):
    """Configuration for LiteLLM gateway."""

    api_base: str = "http://localhost:4000"
    api_key: Optional[str] = None
    timeout: int = 120
    max_retries: int = 3


class AssetCache:
    """Simple in-memory cache for generated assets."""

    def __init__(self, max_size: int = 1000):
        self.cache: dict[str, AssetResponse] = {}
        self.max_size = max_size
        self.access_order: list[str] = []

    def get(self, key: str) -> Optional[AssetResponse]:
        """Get cached asset."""
        if key in self.cache:
            # Move to end of access order (LRU)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None

    def set(self, key: str, value: AssetResponse):
        """Cache an asset."""
        if len(self.cache) >= self.max_size:
            # Evict oldest
            oldest = self.access_order.pop(0)
            del self.cache[oldest]

        self.cache[key] = value
        self.access_order.append(key)

    def generate_key(self, request: AssetRequest) -> str:
        """Generate cache key from request."""
        key_data = f"{request.asset_type}:{request.style}:{request.model}:"
        key_data += f"{request.width}x{request.height}:"
        key_data += f"{request.item_name}:{request.item_type}:{request.rarity}:"
        key_data += f"{request.clan}:{request.seed}"
        return hashlib.md5(key_data.encode()).hexdigest()


class AssetGenerationService:
    """Service for generating Celtic game assets."""

    def __init__(
        self,
        config: Optional[LiteLLMConfig] = None,
        cache_enabled: bool = True,
    ):
        self.config = config or LiteLLMConfig()
        self.prompt_generator = CelticPromptGenerator()
        self.cache = AssetCache() if cache_enabled else None
        self.client = httpx.AsyncClient(
            base_url=self.config.api_base,
            timeout=self.config.timeout,
        )

        # Statistics
        self.total_generated = 0
        self.total_cached = 0
        self.total_errors = 0

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def generate(self, request: AssetRequest) -> AssetResponse:
        """Generate a single asset."""

        start_time = time.time()

        # Check cache
        if self.cache and request.use_cache:
            cache_key = request.cache_key or self.cache.generate_key(request)
            cached = self.cache.get(cache_key)
            if cached:
                self.total_cached += 1
                return cached

        try:
            # Generate prompt
            prompt = request.prompt_override or self.prompt_generator.generate_prompt(
                asset_type=request.asset_type,
                style=request.style,
                item_name=request.item_name,
                item_type=request.item_type,
                rarity=request.rarity,
                clan=request.clan,
                power_level=request.power_level,
            )

            negative_prompt = request.negative_prompt or self.prompt_generator.get_negative_prompt(
                request.asset_type
            )

            # Call LiteLLM image generation endpoint
            response = await self._call_litellm(
                model=request.model,
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=request.width,
                height=request.height,
                steps=request.steps,
                guidance_scale=request.guidance_scale,
                seed=request.seed,
            )

            generation_time = int((time.time() - start_time) * 1000)

            result = AssetResponse(
                success=True,
                asset_id=self._generate_asset_id(),
                image_base64=response.get("image_base64"),
                image_url=response.get("image_url"),
                prompt_used=prompt,
                model_used=request.model,
                generation_time_ms=generation_time,
                asset_type=request.asset_type,
                style=request.style,
                width=request.width,
                height=request.height,
            )

            # Cache result
            if self.cache and request.use_cache:
                cache_key = request.cache_key or self.cache.generate_key(request)
                self.cache.set(cache_key, result)

            self.total_generated += 1
            return result

        except Exception as e:
            self.total_errors += 1
            return AssetResponse(
                success=False,
                asset_id="",
                prompt_used=request.prompt_override or "",
                model_used=request.model,
                generation_time_ms=int((time.time() - start_time) * 1000),
                asset_type=request.asset_type,
                style=request.style,
                width=request.width,
                height=request.height,
                error=str(e),
            )

    async def generate_batch(
        self,
        batch_request: BatchAssetRequest,
    ) -> BatchAssetResponse:
        """Generate multiple assets in batch."""

        batch_id = self._generate_asset_id()

        # Run all generations concurrently
        tasks = [self.generate(req) for req in batch_request.requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        responses = []
        completed = 0
        failed = 0

        for result in results:
            if isinstance(result, Exception):
                failed += 1
                responses.append(
                    AssetResponse(
                        success=False,
                        asset_id="",
                        prompt_used="",
                        model_used="",
                        generation_time_ms=0,
                        asset_type=AssetType.ITEM_ICON,
                        style=CelticStyle.KNOTWORK,
                        width=512,
                        height=512,
                        error=str(result),
                    )
                )
            elif result.success:
                completed += 1
                responses.append(result)
            else:
                failed += 1
                responses.append(result)

        return BatchAssetResponse(
            batch_id=batch_id,
            total_requested=len(batch_request.requests),
            completed=completed,
            failed=failed,
            results=responses,
        )

    async def _call_litellm(
        self,
        model: str,
        prompt: str,
        negative_prompt: str,
        width: int,
        height: int,
        steps: int,
        guidance_scale: float,
        seed: Optional[int],
    ) -> dict:
        """Call LiteLLM image generation API."""

        headers = {}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        payload = {
            "model": model,
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "size": f"{width}x{height}",
            "n": 1,
            "response_format": "b64_json",
            "quality": "standard",
        }

        # Add optional parameters based on model
        if "flux" in model.lower() or "sdxl" in model.lower():
            payload["extra_body"] = {
                "num_inference_steps": steps,
                "guidance_scale": guidance_scale,
            }
            if seed is not None:
                payload["extra_body"]["seed"] = seed

        for attempt in range(self.config.max_retries):
            try:
                response = await self.client.post(
                    "/v1/images/generations",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()

                data = response.json()

                # Extract image from response
                if "data" in data and len(data["data"]) > 0:
                    image_data = data["data"][0]
                    return {
                        "image_base64": image_data.get("b64_json"),
                        "image_url": image_data.get("url"),
                    }

                raise ValueError("No image data in response")

            except httpx.HTTPStatusError as e:
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(2**attempt)  # Exponential backoff
            except Exception as e:
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(1)

        raise RuntimeError("Max retries exceeded")

    def _generate_asset_id(self) -> str:
        """Generate unique asset ID."""
        import uuid

        return f"asset_{uuid.uuid4().hex[:12]}"

    async def upload_to_ipfs(
        self,
        image_data: bytes,
        metadata: dict,
    ) -> Optional[str]:
        """Upload asset to IPFS (placeholder)."""
        # TODO: Implement IPFS upload via Pinata or similar
        return None

    async def upload_to_arweave(
        self,
        image_data: bytes,
        metadata: dict,
    ) -> Optional[str]:
        """Upload asset to Arweave (placeholder)."""
        # TODO: Implement Arweave upload
        return None

    def get_stats(self) -> dict:
        """Get service statistics."""
        return {
            "total_generated": self.total_generated,
            "total_cached": self.total_cached,
            "total_errors": self.total_errors,
            "cache_size": len(self.cache.cache) if self.cache else 0,
        }


# Convenience functions for common asset types
async def generate_item_icon(
    service: AssetGenerationService,
    item_name: str,
    item_type: str,
    style: CelticStyle = CelticStyle.KNOTWORK,
    rarity: str = "common",
) -> AssetResponse:
    """Generate an item icon."""
    from .models import ItemRarity

    return await service.generate(
        AssetRequest(
            asset_type=AssetType.ITEM_ICON,
            style=style,
            item_name=item_name,
            item_type=item_type,
            rarity=ItemRarity(rarity),
            width=256,
            height=256,
        )
    )


async def generate_character_portrait(
    service: AssetGenerationService,
    character_name: str,
    clan: Optional[str] = None,
    style: CelticStyle = CelticStyle.ILLUMINATED,
) -> AssetResponse:
    """Generate a character portrait."""
    from .models import ClanId

    return await service.generate(
        AssetRequest(
            asset_type=AssetType.CHARACTER_PORTRAIT,
            style=style,
            item_name=character_name,
            clan=ClanId(clan) if clan else None,
            width=512,
            height=512,
            model=GenerationModel.FLUX_DEV,  # Higher quality for portraits
        )
    )


async def generate_clan_heraldry(
    service: AssetGenerationService,
    clan: str,
    style: CelticStyle = CelticStyle.KNOTWORK,
) -> AssetResponse:
    """Generate clan heraldry/shield."""
    from .models import ClanId

    return await service.generate(
        AssetRequest(
            asset_type=AssetType.CLAN_HERALDRY,
            style=style,
            clan=ClanId(clan),
            width=512,
            height=512,
        )
    )
