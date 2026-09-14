import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))


def _load_provider_exports():
    from provider import AzureSTTProvider, AzureTTSProvider, register

    return AzureSTTProvider, AzureTTSProvider, register


AzureSTTProvider, AzureTTSProvider, register = _load_provider_exports()

__all__ = [
    "AzureTTSProvider",
    "AzureSTTProvider",
    "register",
]
