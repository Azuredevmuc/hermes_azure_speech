# Hermes Azure Speech Provider — Phasenplan

## Ziel

Aus dem aktuellen Azure Speech Backend ein sicher nutzbares, testbares und für Hermes-Integrationen vorbereitbares Provider-Extension zu machen. Der Fokus liegt auf:

- Stabilität und Wiederverwendbarkeit
- Sicherheit von Konfigurationen und Logs
- Hermes-Integration nach Provider-/Extension-Modell
- öffentlich nutzbare Paketstruktur
- verlässlicher Testabdeckung

---

## Phase 1 — Stabilität und Baseline sichern

### Ziel
Die Grundlage so stabilisieren, dass das Projekt ohne Importfehler, unsichere Konfigurationen oder fragile Laufzeitannahmen nutzbar ist.

### Phase-1-Compliance-Anforderung
Dieses Projekt muss die Hermes-kompatible Provider-Positionierung ausdrücklich beibehalten und darf keine Platzhalter- oder falschen Public-Metadata-Daten enthalten, die ein Paket als unreif oder nicht-öffentlich erscheinen lassen.

### Aufgaben
- Importpfad und optionales Azure SDK sauber behandeln
- Laufzeitfehler für fehlende Abhängigkeiten klar und sauber abfangen
- Konfiguration validieren und standardisierte Fehlermeldungen definieren
- Secrets nicht in Logs oder Debug-Ausgaben weiterreichen
- kleine, reproduzierbare Tests für Kernfunktionen ergänzen

### Konkrete Anforderungen
- `AzureSpeechConfig.from_env()` darf bei fehlenden Variablen sauber fehlschlagen
- fehlendes Azure SDK darf keine Importzeit-Katastrophe verursachen
- `as_dict()` redigiert sensible Werte und darf keine Roh-Keys ausgeben
- der Provider darf bei ungültiger Konfiguration nicht stillschweigend weiterlaufen

### Testanforderungen
- Test: fehlende Azure-Abhängigkeit führt nicht zum Absturz beim Import
- Test: `AzureSpeechConfig` validiert Pflichtwerte korrekt
- Test: `as_dict()` maskiert `AZURE_SPEECH_KEY`
- Test: ungültige Konfiguration erzeugt verständliche Exception

### Sicherheitsanforderungen
- keine Plain-Text-Secret-Ausgabe in Logs, Fehlermeldungen oder Debug-Output
- keine Default-Keys oder Test-Keys in Dokumentation oder Beispielen
- alle Konfigurationswerte müssen redigiert oder explizit als sensibel markiert sein

### Definition of Done
- Projekt importiert stabil auch bei optionalen Abhängigkeiten
- Kern-Tests bestehen
- Sicherheitsgrundsatz “Secrets niemals im Klartext” ist implementiert

---

## Phase 2 — Zuverlässigkeit und Performance harden

### Ziel
Verzögerungen und Blockierungen eliminieren und das Verhalten unter Last oder bei Azure-Timeouts kontrollieren.

### Aufgaben
- Blocking-Aufrufe mit expliziten Timeouts absichern
- Azure-Calls mit nachvollziehbaren Fehlergrenzen versehen
- Temp-Dateien sauber verwalten und nach Nutzung entfernen
- Dateiströme und Ausgabeformate konsistent verarbeiten
- Laufzeitfehler klar in strukturierte Exceptions übersetzen

### Konkrete Anforderungen
- alle Langzeitoperationen (STT/TTS) müssen Timeouts unterstützen
- Azure-Aufrufe dürfen nicht unbegrenzt hängen bleiben
- temporäre Ausgabe-Dateien müssen bereinigt werden
- Fehlerzustände müssen semantisch sauber in eigene Exceptions übersetzt werden

### Testanforderungen
- Test: Timeout bei Azure-Operation wird sauber erkannt
- Test: fehlerhafte Synthese erzeugt bekannte Exception
- Test: Temp-Dateien werden nach erfolgreicher Verarbeitung bereinigt
- Test: fehlerhafte Eingaben werden nicht in unkontrollierten Dateisystem- oder Codec-Fehlern “verschluckt”

### Sicherheitsanforderungen
- keine ungebundene Dateierzeugung ohne Pfad-Validierung
- keine unkontrollierten Ausgabe-Pfade mit Laufzeitdaten
- kein ungesichertes Loggen von Dateipfaden mit sensiblen Nutzdaten
- Fehlerwege müssen keine Secrets offenlegen

### Definition of Done
- alle kritischen Azure-Calls sind timeout-geschützt
- keine hängenden Prozesse mehr im normalen STT/TTS-Nutzpfad
- Fehlerbehandlung ist deterministisch und dokumentiert

---

## Phase 3 — Hermes-Provider-/Extension-Contract definieren

### Ziel
Das Projekt in das Hermes-Modell als Provider-/Extension-Backend einordnen und die Integration sauber dokumentieren.

### Aufgaben
- Hermes-Provider-Kontext klar definieren
- Interface-Anforderungen für TTS/STT-Provider dokumentieren
- Start-/Stop-/Registrierungsmodell für Hermes-Integration beschreiben
- Konfigurationsschema für Azure Speech erweitern
- Beispiel-Integration für Hermes-Umgebungen erstellen

### Konkrete Anforderungen
- Das Projekt wird als Provider-/Extension-Backend und nicht als generischer Skill positioniert
- ein klarer Integrationspfad für Hermes-Umgebungen muss im Repo dokumentiert sein
- die Konfiguration wird in einem Hermes-geeigneten Namensraum beschrieben
- die API unterstützt die grundlegenden Betriebszyklen: init, configure, call, cleanup

### Testanforderungen
- Test: Provider-Initialisierung mit gültiger Konfiguration
- Test: fehlende Konfiguration erzeugt klare Fehlermeldung
- Test: TTS/STT-Integrationsschritte können als harte Smoke-Tests laufen
- Test: Hermes-bezogene Beispiel-Integration ist reproduzierbar

### Sicherheitsanforderungen
- keine Secrets im Beispielcode oder in öffentlichen Konfigurationssnippets
- Umgebungsvariablen müssen dokumentiert und als sensibel markiert sein
- Provider-Registrierung darf keine Logausgabe mit geheimen Werten produzieren

### Definition of Done
- die Integration ist als “Hermes Speech Provider Extension” dokumentiert
- ein klarer Einstieg für andere Nutzer existiert
- die Providerschnittstelle ist nachvollziehbar und gut testbar

---

## Phase 4 — Öffentliche Nutzbarkeit und Paketierung vorbereiten

### Ziel
Das Projekt soll für andere Nutzer einfach installierbar, konfigurierbar und verlässlich nutzbar sein.

### Aufgaben
- Paketmetadaten und Versionsmodell finalisieren
- Installationsinstruktionen für saubere Python-Umgebungen ergänzen
- Beispielkonfiguration und `.env`-Beispiel setzen
- SECURITY-, CONTRIBUTING- und CHANGELOG-Dateien ergänzen
- Release-Workflow für Versionen und Patches definieren

### Konkrete Anforderungen
- `pip install` aus einer neuen Umgebung muss ohne Handgriffe funktionieren
- Setup-Guide muss klar zwischen “Library” und “Hermes-Extension” unterscheiden
- Nutzer benötigen keine interne Projekt-Context-Informationen, um das Paket zu nutzen
- Veröffentlichungen müssen mit Changelog und Upgrade-Hinweisen begleitet werden

### Testanforderungen
- Test: frische Virtualenv-Installation mit `pip install -e .`
- Test: Smoke-Test mit `AzureSpeechConfig.from_env()` und minimalem TTS/STT-Aufruf
- Test: Installationsfehler und fehlende Umgebungsvariablen werden sauber dargestellt
- Test: Beispielcode funktioniert in einer sauberen Umgebung

### Sicherheitsanforderungen
- Dependency-Scanning in CI muss Teil des Release-Prozesses werden
- keine sensiblen Werte im Repository oder in Beispielen
- sichere Standard-Defaults für Region, Sprache und Voice-Konfiguration
- Sicherheitsdokumentation für verantwortliche Nutzung von Azure Keys

### Definition of Done
- Paket ist installierbar und dokumentiert
- neue Nutzer können in < 15 Minuten loslegen
- Security-Gates sind Teil der Release-Checkliste

---

## Phase 5 — Release, Qualitätskontrolle und Wartung

### Ziel
Das Projekt in einen verlässlichen Community-Stand überführen und Regresionsschutz sicherstellen.

### Aufgaben
- Release-Kandidat validieren
- CI-Pipeline mit Test- und Sicherheitsprüfungen aufsetzen
- Übergabe für Nutzer-Feedback und Bug-Reports vorbereiten
- Versions- und Sicherheitsstrategie dokumentieren
- Regelmäßige Wartungszyklen definieren

### Konkrete Anforderungen
- Test-Suite muss in CI laufen
- Sicherheitschecks müssen regelmäßig automatisiert werden
- Breaking Changes müssen in Changelog und Upgrade-Notes erklärt werden
- öffentliche GitHub-/Release-Docs müssen konsistent sein

### Testanforderungen
- Test: komplette Pytest-Suite in CI
- Test: Dependency-Audit und Secret-Scan im Pipeline-Workflow
- Test: Release-Checkliste für Tagging und Veröffentlichung
- Test: Reproduzierbare Regressionstests für kritische Provider-Funktionen

### Sicherheitsanforderungen
- regelmäßiges Dependency-Auditing
- Secret-Scanning in CI
- keine geheimhaltigen Werte in Commits, Release-Notes oder Tags
- branch protection und review-basierte Freigabe für Releases

### Definition of Done
- Projekt ist releasebereit
- Sicherheit und Tests sind Teil des normalen Entwicklungsprozesses
- das Projekt kann von anderen Nutzern produktiv eingesetzt werden

---

## Prüfplan: Muss-Kriterien vor jedem Release

### Tests
- [ ] `pytest` läuft vollständig grün
- [ ] kritische STT/TTS-Pfade sind durch Regressionstests abgedeckt
- [ ] installierbare Package-Umgebung wurde getestet
- [ ] Beispiel-Workflows wurden in einer sauberen Umgebung ausgeführt

### Sicherheit
- [ ] keine Secrets im Repository oder in Logs
- [ ] Dependency-Audit ist ohne kritische Warnungen
- [ ] Konfigurationssekretisierungen sind implementiert und getestet
- [ ] Release-Checkliste enthält Sicherheits- und Review-Schritte

### Dokumentation
- [ ] Installation ist klar und reproduzierbar
- [ ] Provider-/Extension-Kontext ist erklärt
- [ ] Beispielkonfiguration ist vorhanden
- [ ] Fehlerbehandlung und Limits sind dokumentiert

---

## Reihenfolge der Umsetzung

1. Phase 1: Stabilität und Baseline
2. Phase 2: Zuverlässigkeit und Performance
3. Phase 3: Hermes-Provider-Contract
4. Phase 4: Paketierung und Nutzerfreundlichkeit
5. Phase 5: Release und Pflege

Diese Reihenfolge ist bewusst gewählt, weil technische Stabilität und Sicherheit vor öffentlicher Nutzung und Release kommen müssen.

---

## Empfohlener Projektstatus nach diesem Plan

Nach Abschluss der Phasen ist das Projekt als:

- sichere, wiederverwendbare Azure Speech Provider-Basis
- Hermes-kompatible Speech Extension Foundation
- öffentlich nutzbares Python-Paket

zu klassifizieren.

Nicht als generischer Agent-„Skill“, sondern als provider-/extension-orientierter Hermes-Backend-Teil.

---

## Kurzfazit

Der richtige Weg ist nicht, einfach nur “mehr Features” zu bauen, sondern zunächst das Projekt auf folgende drei Säulen zu stellen:

1. Stabilität
2. Sicherheit
3. klare Hermes-Provider-Integration

Erst dann folgt die öffentliche Bereitstellung und der echte Release.
