# Dialectree – Zigzag View: Datenstruktur & Detailplan

> **Status:** Aktiv. Ersetzt die frühere Version, die nur den API-backed Zigzag-View ohne Stufen beschrieb.
> Die Kurzfassung ist in [`implementation-plan.md` § Phase Z](implementation-plan.md#phase-z--dynamic-zigzag-view) integriert.

---

## 1. Grundkonzept: 6-Stufen-Verfeinerungsmodell

Eine Diskussion durchläuft sieben Stufen der Analyse (0–6). Jede Stufe **baut auf der vorherigen auf** und fügt neue Informationsschichten hinzu. Dieselbe Datengrundstruktur (`ArgumentNode`) wird schrittweise reicher — kein Bruch, keine neue Tabelle pro Stufe.

| Stufe | Name | Was wird hinzugefügt | Implementierungsstatus |
|-------|------|---------------------|----------------------|
| **0** | Rohdaten / Transkript / YAML | Roher Diskussionstext als YAML-File; maschinenlesbar und menschenlesbar | ✅ Implementiert |
| **1** | Zickzack-Basiszuordnung | Argumente chronologisch Seiten zugeordnet, erster Zickzack, roter Faden implizit über `parent_id` | ✅ Implementiert |
| **2** | Split-Prozess | **Arbeitsschritt** (kein Repräsentationsschritt). Zeigt Original-Argumente UND ihre Splits gleichzeitig. Basis-Argumente bleiben im Roh-Stil. Ermöglicht Split-Erstellung und Verbindungspflege. | ✅ Implementiert |
| **3** | Verfeinerung | Nur die Split-Argumente bleiben sichtbar; Originale, die gesplittet wurden, verschwinden. Zwei Verbindungsarten: Chronologie + logische Referenz. | ⬜ Pending |
| **4** | Zickzack Einordnung | Bewertungen, argumentative Verfeinerungen — **nur auf Argumente**, nicht auf Verbindungen | ⚙️ TODO: post-dev |
| **5** | Meta-Einordnung | Argumentgruppen, Klassifizierung als Quelle / Grundannahme etc. | ⚙️ TODO: post-dev |
| **6** | Diskussionsnetz | Diskussion in Cross-Topic-Meta-Netz einordnen; braucht `AbstractArgument`-Modell | 🔭 Geplant — separate Spezifikation erforderlich |

### Was jede Stufe NEU hinzufügt (UI-Sicht)

Jede Stufe beschreibt hier, **was im UI passieren soll** — diese Beschreibung dient als Spezifikation, bevor etwas in HTML umgesetzt wird. Die HTML-Datei (`zickzack.html`) implementiert diese Beschreibung und referenziert sie per `<!-- DESIGN: ... -->`.

| Stufe | Änderung zur vorherigen Stufe |
|-------|-------------------------------|
| **0 → 1** | Statt Text: erster Zigzag-Canvas. Schlichte, **transkript-artige** Textblöcke (farblos, Rohformat) links (PRO) und rechts (CONTRA), verbunden durch Linien. **Keine** Buttons, Labels, Votes oder Kommentare. Kein analytischer Inhalt — nur das Gesagte. |
| **1 → 2** | **Arbeitsschritt:** Original-Argumente UND ihre Splits werden **gleichzeitig** sichtbar (Ausnahme von der Minimal-Regel — dient der Split-Erstellung). Basis-Argumente behalten den Roh-Stil. Split-Argumente erscheinen mit ✂-Badge. Drei Verbindungsarten: Ursprungs-Argument (grau), chronologischer Fluss (farbig) und Cross-Split (farbig gestrichelt). |
| **2 → 3** | Originale, die gesplittet wurden, **verschwinden**. Nur Split-Argumente bleiben. Zwei Verbindungsarten: chronologisch (gestrichelt) + logische Referenz (durchgezogen). Die eigentliche verfeinerte Ansicht. |
| **3 → 4** | *[TODO]* Interaktive Features: Votes, Kommentare, Conflict-Zone-Badges, Edge-Type-Marker, Opens-Conflict-Hinweise. |
| **4 → 5** | *[TODO]* Argumentgruppen, Klassifizierung. |
| **5 → 6** | *[Geplant]* Cross-Topic-Einordnung. |

#### Stufe 0 — Transkript

- Kein Canvas/Visualisierung.
- Zeigt das Transkript in einem **editierbaren Textarea** (YAML oder Freitext).
- Immer editierbar — leeres Textarea wenn kein Transkript vorhanden, statt Placeholder.
- **Speichern-Button** schreibt via `PUT /api/topics/{id}/transcript` zurück.
- TODO: "Stufen generieren"-Button — aus dem Transkripttext automatisch Stufe-1-Argumente ableiten (erfordert KI-Pipeline, deferred).

#### Stufe 1 — Basiszuordnung (Rohe Zuordnung)

Stufe 1 ist die **letzte Rohform** der Argumentation — nur strukturell zugeordnet.

- **Inhalt:** Ausschließlich das **tatsächlich Gesagte**. Keine Eröffnungsthesen hinzufügen, keine analytischen Einordnungen, keine Referenzen auf andere Argumente (keine „3.1", „2.2" etc.). Das rohe Transkript wird lediglich den Seiten (PRO/CONTRA) zugeordnet.
- **Nummerierung:** Die Durchnummerierung (R1, L2, A₁ etc.) dient nur zur **Referenzierung während der Entwicklungsphase** und ist keine inhaltliche Einordnung.
- **Karten:** Nur Titel + Beschreibungstext. Kein Collapse-Toggle, keine Votes, keine Kommentare, keine Conflict-Zone-Badges, keine Edge-Type-Marker.
- **Visueller Stil:** Transkript-artig / Notepad-Stil. **Farblos** (kein Positions-Grün/Rot), rohes Datenformat. Die Karten sollen sich von verfeinerten Stufe-2-Argumenten visuell abheben und klar als „Rohdaten" erkennbar sein.
- **Layout:** Einfache lineare Kette — jedes Argument wird chronologisch als nächster Block dargestellt. PRO links, CONTRA rechts.
- **Verbindungen:** Jede Karte verbindet sich mit der **vorherigen Karte** (einfacher Zickzack). Keine Referenz per `parent_id` — rein chronologisch.
- **Keine Siblings:** Auch wenn die API `sibling_ids` zurückgibt, werden sie in Stufe 1 ignoriert. Jedes Argument steht allein.

#### Stufe 2 — Split-Prozess (Arbeitsschritt)

Stufe 2 ist ein **Arbeitsschritt**, kein Repräsentationsschritt. Er dient der Erstellung und Pflege von Splits.

- **Ausnahme:** Zeigt **ausnahmsweise Informationen doppelt** an — sowohl die Original-Argumente als auch ihre Splits sind gleichzeitig sichtbar. Das ist nötig, damit man beim Splitten sieht, was man aufdröselt.
- **Basis-Argumente (stage_added=1):** Behalten den **Roh-/Notepad-Stil** aus Stufe 1 (farblos, gestrichelt, Monospace). Sie sollen klar als „Rohdaten" erkennbar bleiben, auch neben den verfeinerten Splits.
- **Split-Argumente (stage_added=2):** Erscheinen im normalen Karten-Stil mit ✂-Split-Badge. Sub-Nummern (2.1, 3.1, …) werden sichtbar.
- **Button-Label:** `2️⃣ Split-Prozess` (Nummer statt Schere-Emoji).
- **Vier Verbindungsarten:**
  1. **Roh-Kette** (Positions-farbig, dick, gedimmt): Verbindungen zwischen den Original-Argumenten (R1→L2→R3→L4). Dicker und weniger leuchtend als Split-Verbindungen — Proportionalität: ein Roh-Argument enthält mehr konsolidierte Information.
  2. **Ursprungs-Argument** (grau/neutral, gestrichelt): Verbindung vom Split zum Original-Argument (`split_from_id`). Zeigt die Zugehörigkeit zum gesplitteten Basis-Argument. Setzt an der unteren Kartenseite an.
  3. **Blauer chronologischer Fluss** (Topic-blau `#1f6feb`, kurvige Linie): Durchläuft die entfaltete Sequenz (Topic → R1 → L2.1 → L2.2 → R3.1 → R3.2 → L4.1 → …). Verläuft **mittig durch die Karten** (nicht am Rand), um sich semantisch von den Argumentations-Verbindungen abzuheben. Kurviger Stil signalisiert Fluss/Ablauf.
  4. **Split-zu-Split-Verbindungen** (leuchtend grün/rot, gerade Linie): Spezifische Verbindungen zwischen Splits verschiedener Seiten, basierend auf `parent_id`. Beispiel: (3.1) → (2.1), (3.2) → (2.2), alle (4.x) → (3.2). Die `parent_id` eines Splits zeigt auf das **spezifische Gegen-Split**, auf das er antwortet.
- **GUI-Editing (deferred):** Perspektivisch soll man hier Split-Sets erstellen und Verbindungen interaktiv ziehen können — siehe `implementation-plan.md`.
- **Karten verschiebbar:** Alle Karten können per Drag & Drop verschoben werden, um Verbindungen besser sichtbar zu machen. Alle Verbindungslinien folgen der Karte.

##### Split-Modell

- Splits arbeiten die **Essenz** eines Arguments heraus und sind **personalisierbar** unterteilbar.
- **Jedes Argument** kann prinzipiell aufgesplittet werden — auch zum Aufgliedern logischer Probleme (z.B. ein Argument mit zwei vermischten Behauptungen).
- Wenn ein Argument aufgesplittet wird, **referenzieren die Split-Versionen das Original** via `split_from_id`. So wird sichergestellt, dass relevante Punkte nicht unter den Tisch fallen.
- `parent_id` eines Splits zeigt auf das **spezifische Gegen-Split**, auf das er antwortet (z.B. R3.1 → L2.1). Layout-Gruppierung erfolgt über `split_from_id`, nicht über `parent_id`.

#### Stufe 3 — Verfeinerung (Ergebnis-Ansicht)

Stufe 3 ist die eigentliche **verfeinerte Ansicht** — das Ergebnis des Split-Prozesses.

- **Originale verschwinden:** Basis-Argumente, die gesplittet wurden (d.h. auf die ein `split_from_id` zeigt), werden **nicht mehr angezeigt**. Nur die Split-Argumente bleiben.
- **Nicht gesplittete Originale bleiben:** Basis-Argumente ohne Splits bleiben sichtbar (im normalen Karten-Stil, nicht mehr im Roh-Stil).
- **Kernregel:** Original-Argument und seine Split-Versionen werden NIE gleichzeitig angezeigt. Die gezeigte Information soll minimal sein.
- **Zwei Verbindungsarten:** Chronologie (gestrichelt, mittig) + logische Referenz (durchgezogen, seitlich, farbcodiert). Siehe Verbindungsarten-Tabelle unten.

##### Zwei Verbindungsarten

Stufe 3 führt die Unterscheidung zwischen **chronologischem Ablauf** und **logischer Referenz** ein:

| Verbindungsart | Zweck | Stil |
|----------------|-------|------|
| **Ablauf** (Chronologie) | Zeichnet den zeitlichen Verlauf der Diskussion nach — „wer hat wann gesprochen" | Gestrichelt, fließender Verlauf, Farbe passend zum Diskussions-Topic (zur Nachverfolgung) |
| **Logische Referenz** | Zeigt, welches (Sub-)Argument ein anderes inhaltlich adressiert — „worauf antwortet das" | Grün (PRO) / Rot (CONTRA), durchgezogen, gerade Linie |

Um die beiden Verbindungsarten besser zu unterscheiden, sollte die **chronologische Verbindung immer mittig** an der Karte andocken, während logische Referenzen an den Seiten ansetzen.

##### Split-Visualisierung (deferred — siehe implementation-plan.md)

Idealerweise kann man bei jedem Split-Argument per Button temporär auf das Haupt-Argument visuell „umschalten". Um die Regel einzuhalten (keine Information doppelt anzeigen), würden dabei auch die anderen Split-Argumente desselben Sets ausgeblendet. Diese Visualisierung ist komplex und wird als späterer Implementation-Plan-Punkt umgesetzt. Das Datenmodell ist bereits korrekt (`split_from_id`).

#### Stufe 4–6 (TODO)

- Stufe 4 aktiviert die interaktiven Features: Votes, Kommentare, Conflict-Zone-Badges, Edge-Type-Marker, Opens-Conflict-Hinweise, Collapse-Toggle.
- Stufe 5 fügt Argumentgruppen und Klassifizierungen hinzu.
- Stufe 6 erfordert ein Cross-Topic-Datenmodell.

### Prinzipien

- **Minimale Information**: Nie mehr Daten anzeigen als für die aktuelle Stufe nötig. In Stufe 3 sind Originale und Splits nie gleichzeitig sichtbar. **Ausnahme:** Stufe 2 (Split-Prozess) zeigt beides — sie ist ein Arbeitsschritt.
- **Roter Faden** ist implizit: er ergibt sich aus der `parent_id`-Kette. Er wird nicht explizit gespeichert und nicht gesondert visualisiert.
- **Stufe 1 = Rohdaten**: Kein analytischer Inhalt, keine Referenzen, transkript-artiger visueller Stil.
- **Stufe 2 = Split-Prozess**: Arbeitsschritt. Originale im Roh-Stil + Splits im normalen Stil gleichzeitig sichtbar.
- **Stufe 3 = Verfeinerung**: Ergebnis. Nur Splits sichtbar, gesplittete Originale verschwinden. Zwei Verbindungsarten.
- **Additive Komplexität**: Jede Stufe erweitert die vorherige.
- **Kein Edge-Kommentieren** (vorerst): Kommentare und Labels beziehen sich nur auf Argumente, nicht auf Verbindungen. Zu einem späteren Zeitpunkt zu diskutieren.

---

## 2. Datenmodell: Neue Felder

### 2.1 `Topic`

| Neues Feld | Typ | Beschreibung |
|------------|-----|-------------|
| `transcript_yaml` | Text, nullable | Vollständiges YAML mit Rohdaten aller Stufen (Stufe 0). Maschinenlesbar für Agenten. |

### 2.2 `ArgumentNode`

| Neues Feld | Typ | Default | Beschreibung |
|------------|-----|---------|-------------|
| `stage_added` | Integer | 1 | In welcher Stufe wurde dieser Node eingeführt? Stufe 1 = Basisargument, Stufe 2 = Split-Derivat. |
| `split_from_id` | FK → argument_nodes, nullable | null | Referenz auf das Basisargument (Stufe 1), aus dem dieser Stufe-2-Split extrahiert wurde. |

### 2.3 Was NICHT neu ins Modell kommt (Begründung)

| Konzept | Entscheidung | Begründung |
|---------|-------------|------------|
| `is_thread_primary` | ❌ Nicht implementiert | Der rote Faden ist über `parent_id` implizit bestimmbar und nicht eindeutig festlegbar. Keine Persistierung. |
| Edge-Kommentare | ❌ Deferred | Vorerst nur Argumente kommentierbar. Später zu diskutieren. |
| Stufe 4–5 Felder | ❌ TODO: post-dev | Labels, Bewertungen, Argumentgruppen existieren im Modell, sind aber noch nicht mit dem Stufensystem verknüpft. |
| Stufe 6 Modell | ❌ Geplant | Braucht `AbstractArgument` + Cross-Topic-Links. Erst spezifizieren, dann implementieren. |

### 2.4 Bestehende Felder (Phase Z, unverändert)

| Feld | Typ | Beschreibung |
|------|-----|-------------|
| `conflict_zone` | Enum: `FACT`, `CAUSAL`, `VALUE` | Argumentationsebene (Fakten / Kausalität / Werte) |
| `edge_type` | Enum: `COMMUNITY_NOTE`, `CONSEQUENCES`, `WEAKENING`, `REFRAME`, `CONCESSION` | Wie dieses Argument auf sein Parent reagiert |
| `is_edge_attack` | Boolean | Greift die Verbindung an, nicht den Inhalt (undercutting defeater) |
| `opens_conflict` | String, nullable | Name des neuen Konfliktfeldes, das hier eröffnet wird |

---

## 3. Blueprint: Quotenrassismus-Diskussion

Die **Quotenrassismus-Diskussion** ist der kanonische Blueprint durch alle Stufen. Argumentnamen stehen **immer am Anfang** des Titels (`"B₁: …"`, `"A₁: …"`).

### 3.1 Stufe 1 — Basisstruktur (stage_added = 1)

```
[Topic: Sind Quotenregelungen rassistisch?]
         │
         ▼
   ┌──────────────────────────────────────────┐
   │ B₁: Quotenregelungen sind Diskriminierung │  (L, PRO)
   └──────────────────────────────────────────┘
         │
         ▼
   ┌─────────────────────────────────────────────────────────┐
   │ A₁: Strukturelle Benachteiligung erfordert Korrektur     │  (R, CONTRA)
   └─────────────────────────────────────────────────────────┘
         │
         ▼
   ┌──────────────────────────────────────────────────────────────┐
   │ A₂: Konsens — Diskriminierung schlecht, Methode umstritten   │  (NEUTRAL)
   └──────────────────────────────────────────────────────────────┘
         │
         ▼
   ┌────────────────────────────────────────────────┐
   │ A₃: Was IST Rassismus? — Definitionsebene klären│  (L, Edge Attack)
   └────────────────────────────────────────────────┘
         │
         ▼
   ┌──────────────────────────────────────────────────────────────────┐
   │ A₄: Definitionskonflikt — mehrere Positionen zur Rassismus-Def. │  (NEUTRAL)
   └──────────────────────────────────────────────────────────────────┘
         │
         ▼
   ┌────────────────────────────────────────────────────────────────┐
   │ A₅: Bad Faith — Definitionsverschiebung als Totschlagargument  │  (L, PRO)
   └────────────────────────────────────────────────────────────────┘
```

### 3.2 Stufe 2 — Splits (stage_added = 2, split_from_id → Basis)

Jeder Basis-Node kann in Teil-Argumente aufgedröselt werden. Die Splits haben:
- **`parent_id`** = denselben Parent wie ihr Basis-Node (referenzieren den Gegner)
- **`split_from_id`** = das Basis-Argument aus Stufe 1

| Basis | Splits |
|-------|--------|
| B₁ | B₁a: Leistungsprinzip über alles · B₁b: Individuelle Rechte vs. Gruppenidentität |
| A₁ | A₁a: Diverse Teams liefern bessere Ergebnisse |
| A₄ | A₄a: Akademische Def. · A₄b: Alltagsdef. · A₄c: Beide kontextabhängig |

---

## 4. API

### `GET /api/topics/{id}/zigzag?stage=N`

Gibt eine **flache, chronologisch sortierte** Liste aller ArgumentNodes zurück, gefiltert nach `stage_added <= N`.

**Default:** `stage=2` (volle Sicht). Zulässige Werte: 1–2 (Stufen 3–5 haben noch keine zusätzlichen Nodes).

```json
{
  "topic": { "id": 2, "title": "🔧 Blueprint: Quotenrassismus-Diskussion" },
  "stage": 1,
  "steps": [
    {
      "id": 10,
      "parent_id": null,
      "title": "B₁: Quotenregelungen sind Diskriminierung",
      "position": "PRO",
      "stage_added": 1,
      "split_from_id": null,
      "conflict_zone": "VALUE",
      "edge_type": null,
      "is_edge_attack": false,
      "opens_conflict": null,
      "vote_score": 0,
      "sibling_ids": [],
      "created_at": "..."
    }
  ]
}
```

### `GET /api/topics/{id}/transcript`

Gibt das rohe `transcript_yaml` des Topics zurück.

```json
{
  "topic_id": 2,
  "transcript_yaml": "meta:\n  title: ..."
}
```

---

## 5. UI: Stufen-Navigation

Unterhalb der Topic-Tabs, oberhalb des Mode-Toggle: **Stufen-Tabs 0–6**.

| Stufe | Button-Label | Inhalt |
|-------|-------------|--------|
| 0 | `📄 Transkript` | Editierbares Textarea via `/transcript`; kein Canvas; Speichern-Button |
| 1 | `1️⃣ Basis` | Zigzag Canvas mit `?stage=1` |
| 2 | `✂️ Split-Prozess` | Zigzag Canvas mit `?stage=2` — Arbeitsschritt, Originale + Splits sichtbar |
| 3 | `3️⃣ Verfeinerung` | Zigzag Canvas mit `?stage=2` — nur Splits sichtbar, gesplittete Originale ausgeblendet |
| 4 | `4️⃣ Einordnung` | ⚙️ Placeholder: "Noch nicht implementiert" |
| 5 | `5️⃣ Meta` | ⚙️ Placeholder: "Noch nicht implementiert" |
| 6 | `6️⃣ Netz` | 🔭 Placeholder: "Diskussionsnetz — separate Spezifikation erforderlich" |

---

## 6. Transkript-Dateien: `backend/app/data/`

Das Transkript-Feld (`Topic.transcript_yaml`) ist frei — es kann YAML oder Markdown enthalten. Beide Formate werden im Textarea (Stage 0) angezeigt und können gespeichert werden.

| Datei | Format | Zweck | Topic |
|-------|--------|-------|-------|
| `quoten_diskussion.md` | Markdown | Neue Diskussion: „Sollte es Quoten für Minderheiten geben?" — menschenlesbar, einfache Notation | Topic 1 |
| `quoten_blueprint.yaml` | YAML | Technischer Blueprint: alle 5 Stufen maschinenlesbar eingebettet | Topic 2 |

### Markdown-Notation für Diskussionstranskripte

```
## R1 — NEIN            ← Turn-Nummer + Seite (R=NEIN/CONTRA-Quoten, L=JA/PRO-Quoten)
Argument-Text.

## L2
- **(2.1)** Text.       ← Argument-Bezeichner im Turn
- **(2.2)** ↩ 1 — ...  ← Antwortet auf Turn 1

> ⚑ Sub-Streitpunkt: "Thema"   ← Meta-Hinweis / Teilstreit
```

Symbolische Bezeichner (R1, L2, 2.1 etc.) sind unabhängig von Datenbank-IDs lesbar.

---

## 7. Offene Entscheidungen

| Frage | Status | Notiz |
|-------|--------|-------|
| Wie wird der rote Faden in Stufe 2 visuell unterscheidbar? | ✅ Entschieden | Zwei Verbindungsarten: Chronologie (gestrichelt, mittig) + logische Referenz (durchgezogen, seitlich). Siehe § Stufe 2. |
| Stufe 2: Baum vs. chronologisch? | Chronologisch (vorerst) | Baum-Layout würde Render-Änderungen erfordern. Deferred. |
| Split-Toggle-Visualisierung | Deferred | Button zum Umschalten Original ↔ Splits. Komplex — siehe implementation-plan.md. |
| Edge-Kommentieren (Verbindungen kommentieren) | Deferred | Soll zu einem späteren Zeitpunkt diskutiert werden. |
| Stufe 4+5 Felder | TODO: post-dev | Labels/Bewertungen im Modell vorhanden, Stufen-Verknüpfung fehlt. |
| Stufe 6 Datenmodell | Separate Spezifikation | `AbstractArgument`, Cross-Topic-Links, multiple Versionen (Steelman, neutral, radikal). |


## 8. Wichtig

Dieser Plan sollte eigentlich in Implementation-Plan enthalten sein. Lösche dieses File und alle seine Vorkommen nach der Implementierung.
