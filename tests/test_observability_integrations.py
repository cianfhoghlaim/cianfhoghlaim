"""
Integration tests for observability stack.

Tests connectivity and functionality of:
- Langfuse (LLM cost tracking)
- Datadog APM (tracing)
- Logfire (Pydantic observability)
- LiteLLM (unified LLM access)

Usage:
    pytest tests/test_observability_integrations.py -v
    python tests/test_observability_integrations.py  # Run directly
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project roots to path
sys.path.insert(0, str(Path(__file__).parent.parent / "sruth" / "códeolas"))
sys.path.insert(0, str(Path(__file__).parent.parent / "sruth" / "oideachais"))


class TestLangfuseIntegration:
    """Test Langfuse LLM observability integration."""

    def test_langfuse_client_init(self):
        """Test Langfuse client initialization."""
        try:
            from langfuse import Langfuse

            public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
            secret_key = os.getenv("LANGFUSE_SECRET_KEY", "")

            if not public_key or not secret_key:
                print("⚠️  Langfuse credentials not set (LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY)")
                return

            client = Langfuse(
                public_key=public_key,
                secret_key=secret_key,
                host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
            )

            # Create a test trace
            trace = client.trace(
                name="integration_test",
                metadata={"test": True},
                tags=["test", "integration"],
            )
            client.flush()

            print(f"✅ Langfuse connected - trace ID: {trace.id}")

        except ImportError:
            print("⚠️  Langfuse not installed: pip install langfuse")
        except Exception as e:
            print(f"❌ Langfuse error: {e}")

    def test_codeolas_observability(self):
        """Test códeolas observability module."""
        try:
            from sruth.codeolas.core.observability import get_observability

            obs = get_observability()
            with obs.trace_embedding("test-model", 1, 100):
                pass  # Simulate embedding operation

            summary = obs.get_session_summary()
            print(f"✅ Códeolas observability: {summary['embeddings']['count']} embeddings traced")

        except ImportError:
            print("⚠️  Códeolas not installed or not in path")
        except Exception as e:
            print(f"❌ Códeolas observability error: {e}")


class TestDatadogIntegration:
    """Test Datadog APM integration."""

    def test_datadog_tracer_init(self):
        """Test Datadog tracer initialization."""
        try:
            from ddtrace import tracer, patch_all

            # Check if tracer is enabled
            if not tracer.enabled:
                print("⚠️  Datadog tracer not enabled (DD_TRACE_ENABLED=false or no agent)")
                return

            # Create a test span
            with tracer.trace("integration_test", service="test-service") as span:
                span.set_tag("test", True)
                span.set_tag("integration", "observability")

            print(f"✅ Datadog tracer connected - service: {tracer._writer.api.hostname}")

        except ImportError:
            print("⚠️  ddtrace not installed: pip install ddtrace")
        except Exception as e:
            print(f"❌ Datadog error: {e}")

    def test_datadog_agent_connectivity(self):
        """Test connectivity to Datadog agent."""
        import socket

        dd_host = os.getenv("DD_AGENT_HOST", "localhost")
        dd_port = int(os.getenv("DD_TRACE_AGENT_PORT", "8126"))

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((dd_host, dd_port))
            sock.close()

            if result == 0:
                print(f"✅ Datadog agent reachable at {dd_host}:{dd_port}")
            else:
                print(f"⚠️  Datadog agent not reachable at {dd_host}:{dd_port}")

        except Exception as e:
            print(f"❌ Datadog agent connectivity error: {e}")


class TestLogfireIntegration:
    """Test Pydantic Logfire integration."""

    def test_logfire_init(self):
        """Test Logfire initialization."""
        try:
            import logfire

            token = os.getenv("LOGFIRE_TOKEN", "")
            if not token:
                print("⚠️  LOGFIRE_TOKEN not set")
                return

            logfire.configure(
                token=token,
                service_name=os.getenv("LOGFIRE_SERVICE_NAME", "integration-test"),
                send_to_logfire=True,
            )

            with logfire.span("integration_test"):
                logfire.info("Integration test span")

            print("✅ Logfire configured and connected")

        except ImportError:
            print("⚠️  Logfire not installed: pip install logfire")
        except Exception as e:
            print(f"❌ Logfire error: {e}")


class TestLiteLLMIntegration:
    """Test LiteLLM unified LLM access."""

    def test_litellm_providers(self):
        """Test LiteLLM provider configuration."""
        try:
            import litellm

            # Check available providers
            providers = []

            if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
                providers.append("gemini")

            if os.getenv("ANTHROPIC_API_KEY"):
                providers.append("anthropic")

            if os.getenv("OPENAI_API_KEY"):
                providers.append("openai")

            if os.getenv("GROQ_API_KEY"):
                providers.append("groq")

            if providers:
                print(f"✅ LiteLLM providers configured: {', '.join(providers)}")
            else:
                print("⚠️  No LLM API keys configured")

        except ImportError:
            print("⚠️  LiteLLM not installed: pip install litellm")
        except Exception as e:
            print(f"❌ LiteLLM error: {e}")

    async def test_litellm_completion(self):
        """Test LiteLLM completion (requires API key)."""
        try:
            import litellm

            # Use cheapest model for testing
            model = None
            if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
                model = "gemini/gemini-2.0-flash"
            elif os.getenv("GROQ_API_KEY"):
                model = "groq/llama-3.1-8b-instant"
            elif os.getenv("ANTHROPIC_API_KEY"):
                model = "claude-3-haiku-20240307"

            if not model:
                print("⚠️  No API keys available for completion test")
                return

            response = await litellm.acompletion(
                model=model,
                messages=[{"role": "user", "content": "Say 'test ok' in 2 words"}],
                max_tokens=10,
            )

            print(f"✅ LiteLLM completion ({model}): {response.choices[0].message.content[:50]}")

        except ImportError:
            print("⚠️  LiteLLM not installed")
        except Exception as e:
            print(f"❌ LiteLLM completion error: {e}")


class TestOCRObservability:
    """Test OCR observability from oideachais."""

    def test_ocr_observability_init(self):
        """Test OCR observability module."""
        try:
            from ocr.observability import get_ocr_observability

            obs = get_ocr_observability()

            with obs.trace_extraction("test-model", "test.png", page_count=1) as ctx:
                ctx.set_result("Test extraction", confidence=0.95)

            summary = obs.get_session_summary()
            print(f"✅ OCR observability: {summary['count']} extractions traced")

        except ImportError:
            print("⚠️  OCR observability not installed or not in path")
        except Exception as e:
            print(f"❌ OCR observability error: {e}")


def run_all_tests():
    """Run all integration tests."""
    print("\n" + "=" * 60)
    print("OBSERVABILITY INTEGRATION TESTS")
    print("=" * 60 + "\n")

    # Langfuse tests
    print("--- Langfuse ---")
    langfuse = TestLangfuseIntegration()
    langfuse.test_langfuse_client_init()
    langfuse.test_codeolas_observability()

    # Datadog tests
    print("\n--- Datadog ---")
    datadog = TestDatadogIntegration()
    datadog.test_datadog_agent_connectivity()
    datadog.test_datadog_tracer_init()

    # Logfire tests
    print("\n--- Logfire ---")
    logfire = TestLogfireIntegration()
    logfire.test_logfire_init()

    # LiteLLM tests
    print("\n--- LiteLLM ---")
    litellm = TestLiteLLMIntegration()
    litellm.test_litellm_providers()
    asyncio.run(litellm.test_litellm_completion())

    # OCR observability tests
    print("\n--- OCR Observability ---")
    ocr = TestOCRObservability()
    ocr.test_ocr_observability_init()

    print("\n" + "=" * 60)
    print("Tests complete")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_all_tests()
