# Dialectree – Roter Faden: Diskussionsablauf

Dieses Dokument beschreibt den gewünschten Ablauf einer vollständigen Diskussion anhand
eines Leitbeispiels. Es dient als roter Faden für die Implementierungsprioritäten.
Die Abschnitte sind so geordnet, dass jeder auf dem vorherigen aufbaut – jeder Abschnitt
entspricht implizit einer abgrenzbaren Systemfähigkeit.

**Leitbeispiel:** *„Deutschland sollte mehr Migranten aufnehmen"*

---

## 1. Argument anlegen und grob einordnen

Ein Nutzer gibt ein Argument in Prosa ein. Das System legt es als PRO/CONTRA/NEUTRAL-Knoten an.
Der Nutzer (oder ein Hilfs-System) ordnet es einer groben Kategorie zu
(Wirtschaftlich, Juristisch, Moralisch, …) und vergibt erste Tags.
Fehlende Belege können direkt als Tag markiert werden.

```
User (PRO): „Migration ist wichtig, denn wir sind auf diese Leute angewiesen.
             Allein die Krankenversorgung würde sonst gar nicht funktionieren."
→ Kategorie: Wirtschaftlich | Tags: [fehlender Beleg]
→ System: neuer PRO-Knoten wird angelegt.

User (PRO): „Wir haben doch eh einen Fachkräftemangel.
             Migranten können diesen ausgleichen."
→ Kategorie: Wirtschaftlich | Tags: [fehlender Beleg]
→ System: weiterer PRO-Knoten wird angelegt.
```

---

## 2. Argument-Anatomie: Behauptung → Begründung → Beispiel → Implikation

Argumente sind keine atomaren Sätze, sondern haben eine innere Struktur.
Ein Nutzer (oder n8n) kann ein Argument in diese vier Felder zerlegen.
Das ermöglicht später differenziertere Angriffe (z. B. nur die Begründung anfechten,
ohne die Behauptung zu bestreiten).

```
Argument: „Migration ist wichtig für den wirtschaftlichen Wohlstand."
  Behauptung:  „Unsere Gesellschaft ist auf Migration angewiesen."
  Begründung:  „Es gibt zu wenig Menschen, die diese Jobs machen wollen."
  Beispiel:    „Allein die Krankenversorgung würde ohne Migration zusammenbrechen."
  Implikation: „Also ist Migration wirtschaftlich notwendig."
```

---

## 3. Duplikat-Erkennung und Meta-Argumente (ArgumentGroups)

Mehrere Argumente mit gleichem Kern werden unter einem kanonischen Meta-Argument
zusammengefasst. Die Einzelargumente werden zu Beispielen degradiert und verschwinden
aus der Hauptansicht. Das System kann auf Basis von Tag-Ähnlichkeit vorschlagen,
ein neues Argument als weiteres Beispiel einzusortieren.

```
Nutzer erkennt: Arg 1 und Arg 1.2 teilen dasselbe Argumentationsprinzip.
→ Er legt ein Meta-Argument an: „Migration ist wichtig für den wirtschaftlichen Wohlstand."
→ Arg 1 und Arg 1.2 werden als Unter-Beispiele eingehängt.

User (PRO): „Mein Optiker ist auch Syrer und macht einen tollen Job."
→ Tags: [Wirtschaftlich, fehlender Beleg, Anekdote]
→ System erkennt Tag-Ähnlichkeit zu bestehendem Meta-Argument und schlägt Einordnung vor.
→ Nutzer akzeptiert → erscheint als weiteres Beispiel unter dem Meta-Argument.
```

---

## 4. Community-Tagging, Labels und Argument-Ausblendung

Nutzer und Moderatoren können Argumente mit Qualitätslabels versehen.
Labels haben unterschiedliche Autorität (Nutzer-votable vs. Moderator-autoritativ).
Ab bestimmten Schwellwerten wird ein Argument ausgeblendet (aber nicht gelöscht).

```
Moderator schaut sich Arg 1.3 („Optiker-Anekdote") an.
→ Moderator-Tags: [Anekdote, Privatscheiß]
→ Argument wird ausgeblendet; bleibt intern erhalten.

Nutzer fügt zu Arg 2 hinzu: [Totschlag-Argument, Human Rights]
→ Diese Tags sind votable – andere Nutzer können zustimmen oder widersprechen.
```

Spezielle Label-Typen (nicht abschließend):
- `fehlender Beleg` – Behauptung ohne Quelle
- `Anekdote` – Einzelfall, nicht repräsentativ
- `Off-Topic` / `Themaverfehlung` – Argument trifft Fragestellung nicht
- `Totschlag-Argument` – beendet Diskussion ohne inhaltliche Klärung
- `Inhaltslos` / `Spam` – keine verwertbare Aussage
- `Privatscheiß` – irrelevanter persönlicher Erfahrungsbericht

---

## 5. Belegqualität und Quellen

Argumente können Quellen erhalten. Quellen haben einen Typ
(Studie, Statistik, Gesetz, Anekdote, Artikel) und einen Qualitätsscore (0–1).
Fehlende oder schwache Belege werden als eigener Konflikttyp behandelt.

```
User (PRO): „Es gibt Studien, die zeigen, dass Migration den Wohlstand erhöht."
→ Typ: Studie | Tags: [fehlender Beleg] — kein Link angegeben

Nutzer markiert Arg als invalid. Begründung: „Studie fehlt."
→ System erkennt Klärungsbedarf → listet es als offenen Konflikt.
→ Andere Nutzer können die Invalidierung bestätigen oder ablehnen.
→ Bei Bestätigung: Argument wird mit Begründung „unvollständig" ausgeblendet.

Arg 2 (Asylrecht): Link zu Gesetzestext → Typ: Juristisch, Qualität: hoch
```

---

## 6. Nutzerreputation und abgestuftes Stimmrecht

Aktionen erzeugen Einträge im Nutzerprofil – positive wie negative.
Die Reputation beeinflusst, wie stark die Stimme eines Nutzers
in bestimmten Bereichen zählt (domänenspezifisch, nicht global).

```
Meldender Nutzer hatte Recht → Eintrag: „Meldung: fehlender Beleg" (positiv)
Argument-Ersteller → Eintrag: „Fehlender Beleg" (negativ)

Nutzer, die das invalide Argument positiv bewertet hatten → Eintrag: „Incompetence"
Nutzer, die die Meldung negativ bewertet hatten → Eintrag: „Manipulation"

Folge: Stimme zählt in diesem Bereich künftig weniger oder gar nicht mehr.
```

---

## 7. Konflikt-Erkennung und Sub-Diskussionen

Wenn zwei Argumente sich auf faktischer Ebene widersprechen, oder wenn ein Argument
eine implizite Prämisse enthält, die selbst strittig ist, wird automatisch ein
Konflikt eröffnet. Dieser Konflikt ist eine eigenständige (Unter-)Diskussion.
Das Ergebnis fließt als Validitätsscore zurück ins Elternargument.

```
Arg 4 (CONTRA): „Migranten nehmen uns die Arbeitsplätze weg."
→ Tags: [Wirtschaftlich, Schlussfolgerung, Xenophob, Populistisch]

Ein Nutzer ist der Meinung, Arbeitsplätze wegnehmen sei gut (er will eh nicht arbeiten).
→ Er eröffnet Konflikt: „Ist es wünschenswert, dass Arbeitsplätze ‚weggenommen' werden?"
→ System trennt: faktische Frage (werden Arbeitsplätze verdrängt?) vs.
               normative Frage (ist das gut oder schlecht?)
→ Beide Dimensionen werden als separate Konflikt-Knoten aufgemacht.
→ Arg 4 wird ausgeblendet bis zur Klärung.
```

---

## 8. Scope-Management: falscher Scope und Definition Forks

Argumente, die den Scope der Frage verlassen, werden nicht gelöscht,
sondern in eine passendere Diskussion verschoben oder als Anstoß für
eine neue Top-Level-Diskussion genutzt.
Scoped-Down-Versionen einer These müssen den Rest-Scope benennen.

```
Arg: „Der Wunsch eines Migranten herzukommen ist wichtiger als dein Wunsch,
      ihn nicht hier zu haben."
→ Moderator: „Falscher Scope" – Frage war deutschlandspezifisch, nicht universalmoralisch.
→ System schlägt vor: Neues Topic „Ist der Wunsch eines Migranten herzukommen wichtiger
  als dein Wunsch, ihn nicht hier zu haben?" (moralische Meta-Diskussion)

Arg 8: „Es gibt verschiedene Arten von Migration: Arbeitsmigration, Fluchtmigration, …"
→ Nicht ein Argument, sondern ein Kategorisierungsvorschlag.
→ System schlägt vor: Topic „Deutschland sollte mehr Wirtschaftsmigranten aufnehmen"
  (engerer Scope) + Benennung der nicht behandelten Rest-Menge (z. B. Fluchtmigration).
```

---

## 9. Normativ vs. Positiv: Feststellung und Wertvorstellung

Das System unterscheidet faktische Behauptungen (positiv: „Migranten verdrängen X Jobs")
von Wertvorstellungen (normativ: „Das ist gut/schlecht"). Konflikte auf normativer Ebene
werden anders behandelt als faktische Widersprüche.

```
Faktisch (positiv):  „Migranten nehmen Arbeitsplätze weg."     → prüfbar, belegbar
Normativ:            „Das ist schlecht für Deutschland."         → Werturteil, diskutierbar

→ System trennt beide Schichten und macht sie im Argumentationsbaum sichtbar.
→ Rein normative Endpunkte (moralische Prämissen) werden als Blätter markiert –
  sie sind nicht weiter begründbar, nur noch wählbar.
```

---

## 10. Persönliche Sortierung (Anti-Recency-Bias)

Argumente, die früh eingetragen wurden, sollen keine strukturellen Vorteile haben.
Nutzer können die Reihenfolge der Argumente für sich selbst anpassen.
Die eigene Sortierung beeinflusst nicht die globale Ansicht anderer Nutzer.

```
Nutzer A sortiert: [Arg 2, Arg 5, Arg 1, Arg 4]
Nutzer B sieht:    [Arg 1, Arg 4, Arg 2, Arg 5]  (unverändert für Nutzer B)
```

---

## 11. n8n / KI-gestützte Argument-Einordnung

Unstrukturierter Prosa-Input wird automatisch in die Argument-Anatomie überführt
und mit Kategorie, Tags und Positions-Vorschlag versehen.
Der Nutzer bestätigt oder korrigiert den Vorschlag.

```
Input: „Migration ist wichtig, denn wir sind auf diese Leute angewiesen.
        Allein die Krankenversorgung würde sonst gar nicht funktionieren."

n8n-Output:
  Behauptung:  „Unsere Gesellschaft ist auf Migration angewiesen."
  Begründung:  „Es gibt zu wenig Menschen, die diese Jobs machen wollen."
  Beispiel:    „Krankenversorgung würde ohne Migration zusammenbrechen." [Anekdote]
  Implikation: „Migration ist wirtschaftlich notwendig."
  Metadaten:
    position:  PRO
    Kategorie: Wirtschaftlich
    Tags:      [fehlender Beleg, inland economic growth]
```

---

## Aktueller Stand (Stand: März 2026)

| Fähigkeit | Status |
|---|---|
| 1. Argument anlegen (PRO/CONTRA/NEUTRAL) | ✅ implementiert |
| 2. Argument-Anatomie (Claim/Reason/Example) | ❌ offen |
| 3. Meta-Argumente / ArgumentGroups | ⚠️ Modell vorhanden, Verlinkungslogik fehlt |
| 4. Community-Tags & Labels | ✅ Modell vorhanden |
| 5. Belegqualität / Evidence | ✅ Modell vorhanden |
| 6. Nutzerreputation & Stimmrecht | ❌ offen |
| 7. Konflikt-Erkennung & Sub-Diskussionen | ❌ offen |
| 8. Scope-Management / Definition Forks | ⚠️ Modell vorhanden, Logik fehlt |
| 9. Normativ vs. Positiv | ❌ offen |
| 10. Persönliche Sortierung | ❌ offen |
| 11. n8n / KI-Einordnung | ❌ offen (Workflow-Skizze in `n8n/`) |

