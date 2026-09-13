# provider/ssml.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping
from xml.sax.saxutils import escape

from .common import normalize_whitespace

DEFAULT_LANGUAGE = "de-DE"
DEFAULT_VOICE = "de-DE-KatjaNeural"


@dataclass(frozen=True)
class SSMLSettings:
    language: str = DEFAULT_LANGUAGE
    voice: str = DEFAULT_VOICE
    rate: str = "0%"
    pitch: str = "0%"
    volume: str = "0%"
    style: str | None = None
    style_degree: str | None = None
    substitutions: Mapping[str, str] = field(default_factory=dict)


class AzureSSMLBuilder:
    """
    Build Azure Speech SSML payloads.

    The builder is intentionally small and explicit so it can later be extended
    with:
    - voice styles
    - prosody controls
    - custom substitutions for technical terms
    - per-profile speech personalities
    """

    def __init__(self, settings: SSMLSettings | None = None) -> None:
        self.settings = settings or SSMLSettings()

    @staticmethod
    def _apply_substitutions(text: str, substitutions: Mapping[str, str]) -> str:
        """
        Replace technical terms with explicit SSML sub tags.

        Example:
          "Azure AI Foundry" -> '<sub alias="Azure A I Foundry">Azure AI Foundry</sub>'
        """
        result = text
        placeholder_map: dict[str, str] = {}

        # Longer keys first to avoid partial overlaps.
        for index, source in enumerate(
            sorted(substitutions.keys(), key=len, reverse=True),
            start=1,
        ):
            target = substitutions[source]
            if not source or not target:
                continue

            placeholder = f"__SSML_SUB_{index}__"
            placeholder_map[placeholder] = (
                f'<sub alias="{escape(target)}">{escape(source)}</sub>'
            )
            result = result.replace(source, placeholder)

        escaped = escape(result, {'"': '&quot;'})
        for placeholder, markup in placeholder_map.items():
            escaped = escaped.replace(placeholder, markup)

        return escaped

    @staticmethod
    def _wrap_style(text: str, style: str | None, style_degree: str | None) -> str:
        if not style:
            return text
        attrs = [f'style="{escape(style)}"']
        if style_degree:
            attrs.append(f'styledegree="{escape(style_degree)}"')
        attr_str = " ".join(attrs)
        return f"<mstts:express-as {attr_str}>{text}</mstts:express-as>"

    @staticmethod
    def _wrap_prosody(text: str, rate: str, pitch: str, volume: str) -> str:
        return (
            f'<prosody rate="{escape(rate)}" '
            f'pitch="{escape(pitch)}" '
            f'volume="{escape(volume)}">{text}</prosody>'
        )

    @staticmethod
    def _wrap_voice(text: str, voice: str) -> str:
        return f'<voice name="{escape(voice)}">{text}</voice>'

    @staticmethod
    def _wrap_speak(text: str, language: str) -> str:
        return (
            f'<speak version="1.0" '
            f'xmlns="http://www.w3.org/2001/10/synthesis" '
            f'xmlns:mstts="http://www.w3.org/2001/mstts" '
            f'xml:lang="{escape(language)}">{text}</speak>'
        )

    @staticmethod
    def _insert_light_pauses(text: str) -> str:
        """
        Add a few gentle pauses after short rhetorical breaks.
        This is intentionally conservative to keep the delivery natural.
        """
        normalized = normalize_whitespace(text)

        replacements = {
            " ... ": ' <break time="250ms"/> ',
            "…": ' <break time="250ms"/> ',
            " — ": ' <break time="180ms"/> ',
            " - ": ' <break time="180ms"/> ',
        }

        for source, target in replacements.items():
            normalized = normalized.replace(source, target)

        return normalized

    def build(self, text: str) -> str:
        """
        Build complete SSML from plain text.
        """
        cleaned = normalize_whitespace(text)
        cleaned = self._insert_light_pauses(cleaned)
        cleaned = self._apply_substitutions(cleaned, self.settings.substitutions)

        wrapped = self._wrap_prosody(
            cleaned,
            rate=self.settings.rate,
            pitch=self.settings.pitch,
            volume=self.settings.volume,
        )

        wrapped = self._wrap_style(
            wrapped,
            style=self.settings.style,
            style_degree=self.settings.style_degree,
        )

        wrapped = self._wrap_voice(wrapped, self.settings.voice)
        return self._wrap_speak(wrapped, self.settings.language)


def build_ssml(
    text: str,
    *,
    language: str = DEFAULT_LANGUAGE,
    voice: str = DEFAULT_VOICE,
    rate: str = "0%",
    pitch: str = "0%",
    volume: str = "0%",
    style: str | None = None,
    style_degree: str | None = None,
    substitutions: Mapping[str, str] | None = None,
) -> str:
    """
    Convenience wrapper for quick SSML generation.
    """
    builder = AzureSSMLBuilder(
        SSMLSettings(
            language=language,
            voice=voice,
            rate=rate,
            pitch=pitch,
            volume=volume,
            style=style,
            style_degree=style_degree,
            substitutions=substitutions or {},
        )
    )
    return builder.build(text)