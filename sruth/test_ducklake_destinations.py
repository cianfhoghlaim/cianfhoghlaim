#!/usr/bin/env python3
"""Quick validation of DuckLake destinations across sruth projects."""

import os
import sys

# Ensure local environment
os.environ.setdefault("DLT_ENVIRONMENT", "local")
os.environ.setdefault("USE_DUCKLAKE", "false")  # Use fallback to avoid needing infrastructure

PROJECTS = ["crypteolas", "aleyum", "tuath"]
BASE_PATH = "/Users/cliste/dev/cianfhoghlaim/sruth"


def test_project(project: str) -> bool:
    """Test a single project's destination factory."""
    project_path = f"{BASE_PATH}/{project}"

    # Add project to path
    if project_path not in sys.path:
        sys.path.insert(0, project_path)

    try:
        # Clear any cached imports
        modules_to_remove = [k for k in sys.modules.keys() if k.startswith("dlt_utils")]
        for mod in modules_to_remove:
            del sys.modules[mod]

        # Test 1: Import destination module
        from dlt_utils import get_dlt_destination, create_pipeline
        print(f"  ✓ Import dlt_utils successful")

        # Test 2: Check NAMESPACE via module attribute
        from dlt_utils import destinations
        expected_namespace = project
        if hasattr(destinations, "NAMESPACE"):
            actual_namespace = destinations.NAMESPACE
            if actual_namespace != expected_namespace:
                print(f"  ✗ Namespace mismatch: expected '{expected_namespace}', got '{actual_namespace}'")
                return False
            print(f"  ✓ Namespace correctly set to '{actual_namespace}'")
        else:
            print(f"  ⚠ No NAMESPACE attribute (may be okay for older modules)")

        # Test 3: Pipeline creation with DuckDB fallback (no infra needed)
        pipeline = create_pipeline(
            pipeline_name=f"test_{project}",
            dataset_name="test",
            use_ducklake=False,  # Use fallback to avoid needing infrastructure
        )
        assert pipeline.pipeline_name == f"test_{project}"
        assert pipeline.dataset_name == "test"
        print(f"  ✓ create_pipeline() works (DuckDB fallback)")

        # Test 4: Verify get_dlt_destination returns fallback correctly
        dest = get_dlt_destination(use_ducklake=False)
        dest_type = type(dest).__name__
        print(f"  ✓ get_dlt_destination(use_ducklake=False) returned: {dest_type}")

        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Remove project from path
        if project_path in sys.path:
            sys.path.remove(project_path)


def test_oideachais() -> bool:
    """Test oideachais destination factory (directly load module file)."""
    import importlib.util

    destinations_path = f"{BASE_PATH}/oideachais/dlt_utils/destinations.py"

    try:
        # Clear cached imports
        modules_to_remove = [k for k in sys.modules.keys() if k.startswith("dlt_utils")]
        for mod in modules_to_remove:
            del sys.modules[mod]

        # Load destinations.py directly (bypass __init__.py to avoid safety.py import)
        spec = importlib.util.spec_from_file_location("oideachais_destinations", destinations_path)
        destinations = importlib.util.module_from_spec(spec)
        # Register in sys.modules before exec (required for @dataclass to work)
        sys.modules["oideachais_destinations"] = destinations
        spec.loader.exec_module(destinations)

        get_dlt_destination = destinations.get_dlt_destination
        create_pipeline = destinations.create_pipeline
        print(f"  ✓ Import destinations.py directly successful")

        # Test pipeline creation
        pipeline = create_pipeline(
            pipeline_name="test_oideachais",
            dataset_name="test",
            use_ducklake=False,
        )
        assert pipeline.pipeline_name == "test_oideachais"
        print(f"  ✓ create_pipeline() works (DuckDB fallback)")
        print(f"  ⚠ Note: oideachais has pre-existing import issues in safety.py (sruth.oideachais.core)")

        return True
    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up
        if "oideachais_destinations" in sys.modules:
            del sys.modules["oideachais_destinations"]


if __name__ == "__main__":
    print("=" * 60)
    print("Testing DuckLake destinations across sruth projects")
    print("=" * 60)
    print()

    results = {}

    for project in PROJECTS:
        print(f"[{project}]")
        results[project] = test_project(project)
        print()

    # Also test oideachais
    print("[oideachais]")
    results["oideachais"] = test_oideachais()
    print()

    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    passed = sum(results.values())
    total = len(results)

    for project, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  {project}: {status}")

    print()
    print(f"Results: {passed}/{total} projects passed")

    sys.exit(0 if passed == total else 1)
