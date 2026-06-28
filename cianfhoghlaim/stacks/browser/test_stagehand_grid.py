"""Test Stagehand backend integration with Stealth Grid and stagehand-proxy.

Architecture:
  Browser Grid (Patchright) → CDP → Stagehand SEA → /v1/responses → localhost:4005 → OpenCode Go

Prerequisites:
  1. Browser grid running: docker compose up browser-grid -d
  2. Stagehand proxy running: python stagehand_proxy.py
  3. CDP accessible: curl http://127.0.0.1:9223/json/version

Environment:
  OPENCODE_GO_API - Required. OpenCode Go API key for LLM calls.
  BROWSER_CDP_URL - CDP endpoint (default: http://127.0.0.1:9223)
  STAGEHAND_MODEL - Model name (default: openai/deepseek-v4-pro)
  STAGEHAND_PROXY_HOST - Proxy host (default: 127.0.0.1)
  STAGEHAND_PROXY_PORT - Proxy port (default: 4005)
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from sruth_browser.backends.selfhosted.stagehand_backend import StagehandBackend


async def main():
    proxy_host = os.environ.get("STAGEHAND_PROXY_HOST", "127.0.0.1")
    proxy_port = os.environ.get("STAGEHAND_PROXY_PORT", "4005")
    model = os.environ.get("STAGEHAND_MODEL", "openai/deepseek-v4-pro")

    print(f"=== Stagehand Backend Integration Test ===")
    print(f"CDP URL:    {os.environ.get('BROWSER_CDP_URL', 'http://127.0.0.1:9223')}")
    print(f"Proxy:      http://{proxy_host}:{proxy_port}/v1")
    print(f"Model:      {model}")
    print()

    backend = StagehandBackend()

    try:
        print("[1/5] Initializing backend...")
        await backend.initialize()
        print(f"  ✓ Initialized (session: {backend._session.id})")

        print("[2/5] Navigating to example.com...")
        nav = await backend.navigate("https://example.com")
        print(f"  ✓ Navigation: {nav.success} - {nav.title}")

        if not nav.success:
            print(f"  ✗ Navigation failed: {nav.error}")
            return

        print("[3/5] Extracting page content...")
        try:
            result = await backend.extract(
                "https://example.com",
                prompt="Extract the main heading and first paragraph text",
            )
            print(f"  ✓ Extraction: success={result.success}")
            if result.success and result.content:
                extracted = result.content.get("extracted", result.content)
                preview = str(extracted)[:300]
                print(f"  Content preview: {preview}...")
        except Exception as e:
            print(f"  ✗ Extraction failed: {e}")

        print("[4/5] Observing page elements...")
        try:
            obs = await backend.observe("Find all the links on this page")
            print(f"  ✓ Observations: {len(obs)} items found")
            if obs:
                for item in obs[:3]:
                    print(f"    - {item}")
        except Exception as e:
            print(f"  ✗ Observation failed: {e}")

        print("[5/5] Acting on page...")
        try:
            act = await backend.interact("Find and describe any links on the page")
            print(f"  ✓ Act: success={act.success}")
        except Exception as e:
            print(f"  ✗ Action failed: {e}")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nClosing backend...")
        await backend.close()
        print("Done.")


if __name__ == "__main__":
    if not os.environ.get("OPENCODE_GO_API"):
        print("ERROR: OPENCODE_GO_API environment variable is required.")
        print("Set it to your OpenCode Go API key.")
        sys.exit(1)

    os.environ.setdefault("BROWSER_CDP_URL", "http://127.0.0.1:9223")
    os.environ.setdefault("STAGEHAND_MODEL", "openai/deepseek-v4-pro")

    asyncio.run(main())