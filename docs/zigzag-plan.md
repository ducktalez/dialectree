# Dialectree – Zigzag View: Datenstruktur & Detailplan

> **Status:** Aktiv. Ersetzt die frühere Version, die nur den API-backed Zigzag-View ohne Stufen beschrieb.
> Die Kurzfassung ist in [`implementation-plan.md` § Phase Z](implementation-plan.md#phase-z--dynamic-zigzag-view) integriert.

---

## 1. Grundkonzept: 5-Stufen-Verfeinerungsmodell

Eine Diskussion durchläuft sechs Stufen der Analyse (0–5). Jede Stufe **baut auf der vorherigen auf** und fügt neue Informationsschichten hinzu. Dieselbe Datengrundstruktur (`ArgumentNode`) wird schrittweise reicher — kein Bruch, keine neue Tabelle pro Stufe.

| Stufe | Name | Was wird hinzugefügt | Implementierungsstatus |
|-------|------|---------------------|----------------------|
| **0** | Rohdaten / Transkript / YAML | Roher Diskussionstext als YAML-File; maschinenlesbar und menschenlesbar | ✅ Implementiert |
| **1** | Zickzack-Basiszuordnung | Argumente chronologisch Seiten zugeordnet, erster Zickzack, roter Faden implizit über `parent_id` | ✅ Implementiert |
| **2** | Strukturverfeinerung / Split | Jeder Turn wird aufgedröselt; mehrere Sub-Argumente pro Turn; Splits referenzieren ihr Basis-Argument via `split_from_id` | ✅ Implementiert |
| **3** | Zickzack Einordnung | Bewertungen, argumentative Verfeinerungen — **nur auf Argumente**, nicht auf Verbindungen | ⚙️ TODO: post-dev |
| **4** | Meta-Einordnung | Argumentgruppen, Klassifizierung als Quelle / Grundannahme etc. | ⚙️ TODO: post-dev |
| **5** | Diskussionsnetz | Diskussion in Cross-Topic-Meta-Netz einordnen; braucht `AbstractArgument`-Modell | 🔭 Geplant — separate Spezifikation erforderlich |

### Prinzipien

- **Gleiche Visualisierung** in allen Stufen — der Canvas ändert sich nicht, nur welche Daten gefiltert werden.
- **Roter Faden** ist implizit: er ergibt sich aus der `parent_id`-Kette. Er wird nicht explizit gespeichert und nicht gesondert visualisiert.
- **Additive Komplexität**: Stufe 2 erweitert Stufe 1, Stufe 3 erweitert Stufe 2, usw.
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
| Stufe 3–4 Felder | ❌ TODO: post-dev | Labels, Bewertungen, Argumentgruppen existieren im Modell, sind aber noch nicht mit dem Stufensystem verknüpft. |
| Stufe 5 Modell | ❌ Geplant | Braucht `AbstractArgument` + Cross-Topic-Links. Erst spezifizieren, dann implementieren. |

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

Unterhalb der Topic-Tabs, oberhalb des Mode-Toggle: **Stufen-Tabs 0–5**.

| Stufe | Button-Label | Inhalt |
|-------|-------------|--------|
| 0 | `📄 Transkript` | YAML-Textblock via `/transcript`; kein Canvas |
| 1 | `1️⃣ Basis` | Zigzag Canvas mit `?stage=1` |
| 2 | `2️⃣ Verfeinerung` | Zigzag Canvas mit `?stage=2` |
| 3 | `3️⃣ Einordnung` | ⚙️ Placeholder: "Noch nicht implementiert" |
| 4 | `4️⃣ Meta` | ⚙️ Placeholder: "Noch nicht implementiert" |
| 5 | `5️⃣ Netz` | 🔭 Placeholder: "Diskussionsnetz — separate Spezifikation erforderlich" |

---

## 6. YAML-Datei: `backend/app/data/quoten_blueprint.yaml`

Enthält alle Stufen-Informationen als strukturierte YAML-Blöcke. Dient als:
- **Leseformat** für Entwickler und Agenten
- **Quelle** für `Topic.transcript_yaml` im Seed-Skript
- **Referenz** für zukünftige automatische Verarbeitungs-Pipelines (Scraper, Video-Transkripte)

Symbolische IDs (B1, A1 etc.) statt Datenbank-IDs — die YAML ist unabhängig vom DB-State lesbar.

---

## 7. Offene Entscheidungen

| Frage | Status | Notiz |
|-------|--------|-------|
| Wie wird der rote Faden in Stufe 2 visuell unterscheidbar? | Offen | Bisher nicht implementiert. Erst diskutieren. |
| Stufe 2: Baum vs. chronologisch? | Chronologisch (vorerst) | Baum-Layout würde Render-Änderungen erfordern. Deferred. |
| Edge-Kommentieren (Verbindungen kommentieren) | Deferred | Soll zu einem späteren Zeitpunkt diskutiert werden. |
| Stufe 3+4 Felder | TODO: post-dev | Labels/Bewertungen im Modell vorhanden, Stufen-Verknüpfung fehlt. |
| Stufe 5 Datenmodell | Separate Spezifikation | `AbstractArgument`, Cross-Topic-Links, multiple Versionen (Steelman, neutral, radikal). |


## 8. Wichtig

Dieser Plan sollte eigentlich in Implementation-Plan enthalten sein. Lösche dieses File und alle seine Vorkommen nach der Implementierung. 