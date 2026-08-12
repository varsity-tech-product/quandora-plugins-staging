import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MACOS_HELPER = ROOT / "plugins/quandora-staging/scripts/workbuddy-mcp-login-macos.sh"
WINDOWS_HELPER = ROOT / "plugins/quandora-staging/scripts/workbuddy-mcp-login-windows.ps1"
EXPECTED_VERSION = "1.0.8-staging.41"


def test_workbuddy_oauth_readiness_is_not_pinned_to_backend_tool_count():
    macos = MACOS_HELPER.read_text()
    windows = WINDOWS_HELPER.read_text()

    assert "-eq 27" not in macos
    assert "-eq 27" not in windows
    assert "-ToolsCount 27" not in windows
    assert not re.search(r'"\$tools_count"\s+-(?:eq|ne|gt|ge|lt|le)\b', macos)
    assert not re.search(r"\$state\.toolsCount\s+-(?:eq|ne|gt|ge|lt|le)\b", windows)
    assert '"$connection_status" = \'connected\'' in macos
    assert '"$needs_auth" = \'false\'' in macos
    assert "$state.status -eq 'connected'" in windows
    assert "-not $state.needsAuth" in windows


def test_followup_release_has_one_version_across_all_manifests():
    version_values = []
    for path in ROOT.rglob("*.json"):
        payload = json.loads(path.read_text())
        if path == ROOT / ".claude-plugin/marketplace.json":
            version_values.extend(
                [payload["version"], payload["plugins"][0]["version"]]
            )
        elif path == ROOT / ".codebuddy-plugin/marketplace.json":
            version_values.extend(
                [payload["version"], payload["plugins"][0]["version"]]
            )
        elif path.name in {"plugin.json", "kimi.plugin.json"} and "version" in payload:
            version_values.append(payload["version"])

    assert len(version_values) == 9
    assert set(version_values) == {EXPECTED_VERSION}
