from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from .common import write_text_file
from .hermes import HermesSTTProvider, HermesTTSProvider


def _build_tts_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    return parser


def _build_stt_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    return parser


def tts_main(argv: Sequence[str] | None = None) -> int:
    args = _build_tts_parser().parse_args(argv)
    text = Path(args.input).read_text(encoding="utf-8")
    provider = HermesTTSProvider.from_env()
    provider.synthesize(text, args.output)
    return 0


def stt_main(argv: Sequence[str] | None = None) -> int:
    args = _build_stt_parser().parse_args(argv)
    provider = HermesSTTProvider.from_env()
    transcript = provider.transcribe(args.input)
    write_text_file(args.output, transcript)
    return 0