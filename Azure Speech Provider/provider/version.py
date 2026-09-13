# provider/version.py

"""
Version information for the Azure Speech Hermes Provider.

Keep this file as the single source of truth for the provider version.
"""

from __future__ import annotations

TITLE = "hermes-provider-azure-speech"
DESCRIPTION = "Azure Speech STT/TTS provider for Hermes"
AUTHOR = "Ralf Rottmann"
LICENSE = "MIT"

VERSION = (0, 1, 0)

__version__ = ".".join(map(str, VERSION))
