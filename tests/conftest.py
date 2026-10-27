import sys
from pathlib import Path

sys.dont_write_bytecode = True

# These files verify the optional plugin SDK/engine and remain intact for main.
# Do not collect them when this edition has removed their production sources.
PLUGIN_TESTS = {
    'test_capability_scan.py', 'test_class_alias_bridge.py',
    'test_dynamic_proxy_shape.py', 'test_elyx_archive.py',
    'test_java_call_shape.py', 'test_java_refs.py',
    'test_native_plugin_compat.py', 'test_plugin_parse.py',
    'test_plugin_settings_types.py', 'test_python_runtime.py',
    'test_python_sdk_signatures.py', 'test_reference_parity.py',
    'test_reflection_gate.py', 'test_regressions.py', 'test_sdk_nx_port.py',
    'test_sdk_surface.py', 'test_shim_surface.py', 'test_storage_gate.py',
}
PLUGIN_ENGINE_PRESENT = (Path(__file__).resolve().parents[1] /
                         'TMessagesProj/src/main/python/base_plugin.py').is_file()


def pytest_ignore_collect(collection_path, config):
    return not PLUGIN_ENGINE_PRESENT and collection_path.name in PLUGIN_TESTS


def pytest_report_header(config):
    if not PLUGIN_ENGINE_PRESENT:
        return f'no-plugins edition: {len(PLUGIN_TESTS)} plugin-engine test modules are not applicable (preserved for main)'
