# Migration Guide: Project to Hermes Speech Provider Model

This guide explains how to migrate an existing project from a more generic or ad hoc architecture to a Hermes-compatible speech provider / extension model.

---

## Ziel der Migration

The previous project structure was useful for development, but it did not yet clearly match the Hermes model. The target state is:

- clean provider-oriented architecture
- clear separation between Hermes orchestration and Azure Speech logic
- testable STT/TTS backend abstraction
- secure configuration and runtime behavior
- easier public or plugin-style reuse

The final target is not a generic “skill”, but a Hermes-compatible speech provider backend.

---

## Ausgangssituation

Die bisherige Struktur kann typischerweise folgende Merkmale haben:

- Scripts, CLI-Bridge oder ad hoc Python helpers
- direkte Azure SDK calls in multiple places
- configuration spread across runtime code
- missing or weak provider contract
- unclear separation between orchestration and backend logic
- no explicit security or timeout handling

This is usually enough for a prototype, but it is not robust enough for a reusable Hermes provider model.

---

## Zielarchitektur

The target architecture is:

1. Hermes host or agent runtime
2. provider / bridge layer
3. provider package with STT/TTS logic
4. Azure Speech SDK integration behind the provider
5. config, exceptions, and helpers in dedicated modules

Conceptually:

```text
Hermes Agent
   -> provider bridge / wrapper
      -> provider package
         -> Azure Speech SDK
```

The important change is: the backend becomes a provider layer, not a task or skill implementation.

---

## Migration Steps

### Step 1: Inventory the current project

List all existing runtime components and classify them:

- direct Azure SDK code
- STT logic
- TTS logic
- config loading
- temp-file helpers
- shell scripts or wrappers
- example or test logic

At this point, identify what belongs in the provider package and what should remain in the Hermes host layer.

---

### Step 2: Split responsibilities

Move the code into the following layers:

- `provider/config.py`: configuration and `.env` loading
- `provider/tts.py`: TTS synthesis logic
- `provider/stt.py`: speech-to-text logic
- `provider/ssml.py`: SSML generation
- `provider/exceptions.py`: structured errors
- `provider/common.py`: file and temp helpers
- `provider/hermes.py`: Hermes-facing provider wrappers

This creates a real backend boundary and keeps the host responsibilities separate.

---

### Step 3: Introduce a provider contract

The project should expose a consistent interface for the Hermes backend:

- `HermesSpeechProvider`
- `HermesTTSProvider`
- `HermesSTTProvider`

These wrappers should validate config and provide a stable provider entry point for Hermes integration.

This replaces “just calling Python functions” with a clear provider contract.

---

### Step 4: Move configuration handling into a secure contract

Any project-specific config should be normalized into a single object such as:

- `AzureSpeechConfig`

Requirements:

- load from environment or `.env`
- validate required values
- redact secrets in `repr()` and `as_dict()`
- keep secret handling out of logs and exceptions

This is a foundational migration requirement.

---

### Step 5: Add runtime protection

Before the project is considered provider-ready, add protections for:

- missing Azure SDK dependency
- missing config values
- timeout handling for STT/TTS
- temp-file cleanup on failure
- explicit cancellation and synthesis errors

This is essential for public or Hermes-hosted use.

---

### Step 6: Replace ad hoc scripts with bridge wrappers

If the project previously used directly embedded scripts or one-off calls, replace them with bridge-layer wrappers such as:

- `scripts/azure_speech_tts.py`
- `scripts/azure_speech_stt.py`

These wrappers should:

- add the project root to the Python path
- call the provider package cleanly
- keep runtime arguments explicit
- return stable output values or files

---

### Step 7: Add tests for the migration boundary

The migration should be validated with behavior tests, not just structure checks.

Minimum tests:

- config loads from `.env`
- config redacts secrets
- missing dependency raises provider error
- TTS handles timeout gracefully
- STT handles missing file and empty transcript
- Hermes provider wrappers validate config correctly

This prevents a migration from becoming a silent behavior change.

---

### Step 8: Update documentation

After the migration, document:

- what the project is (provider backend, not skill)
- how it integrates with Hermes
- environment variables and `.env` requirements
- example usage
- operational and security requirements

This should include a migration note explaining the old vs new model.

---

## Recommended Migration Checklist

Before declaring the migration complete, validate:

- [ ] provider package structure is clean and separated
- [ ] config values are validated centrally
- [ ] secrets are redacted everywhere relevant
- [ ] timeouts exist for all speech operations
- [ ] poor dependency state fails explicitly and safely
- [ ] output files are cleaned on failure
- [ ] Hermes wrapper contract is in place
- [ ] tests cover provider and bridge behavior
- [ ] docs explain Hermes integration clearly
- [ ] project is framed as provider/extension, not generic skill

---

## Rollback Strategy

If the migration does not work as intended, the rollback should be careful and limited:

1. preserve the old wrapper scripts temporarily
2. keep a feature freeze for the migrated branch
3. revert only the provider boundary changes first
4. reintroduce the old direct-integration code only as a temporary fallback
5. re-run the migration after isolating the exact breakage

The goal is not a full rewrite, but a controlled transition of behavior and responsibilities.

---

## Minimal Migration Outcome

A successfully migrated project should be able to do all of the following:

- load Azure settings from environment or `.env`
- validate config centrally
- call STT/TTS through provider APIs
- use Hermes-facing provider wrappers
- emit structured errors instead of raw runtime crashes
- be testable without relying on the Hermes host itself

---

## Final Principle

The migration is complete when the project is clearly no longer a loose set of scripts, but a reusable Hermes speech provider backend with explicit boundaries, secure config handling, and stable runtime behavior.
