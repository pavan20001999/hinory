# HINORY

An interactive timeline map of the Hindu traditions: 837 saints, sages and scholars, 2,150 temples, mathas and shrines, and the guru–disciple links between them, from 800 BCE to 2000 CE.

Open `site/index.html` in a browser. It is a single self-contained page (D3 is loaded from cdnjs).

## What's on the page

- **Map:** drag the year slider or press play to see who was alive in each region at any moment. Filter by category, language, women saints, and temple tradition. Arcs show guru → disciple links.
- **Saints:** searchable, sortable directory with tradition, region, language and how firm each date is.
- **Temples:** every temple with its deity, tradition, circuit (Jyotirlinga, Divya Desam, Shakti Pitha…), construction date where known, and its official website.
- **Detail cards:** each saint shows gurus, disciples, contemporaries in the same tradition and temples within 40 km; each temple shows the saints pinned nearby.

## Data

| File | Contents |
|---|---|
| `data/figures.csv` | 837 people: dates, category, tradition, region, language, place, coordinates, attestation (H historical / T traditional / L legendary), Wikipedia title, note |
| `data/temples.csv` | 2,150 temples: deity, tradition, circuit, built year, coordinates, protected-monument flag, official website, Wikipedia title |
| `data/lineage.csv` | Guru → disciple pairs (ids refer to `figures.csv`) |
| `data/curated_figures.txt`, `data/curated_temples.txt` | Hand-curated seed lists |
| `data/rivers.js` | Approximate courses of eight sacred rivers |

### Sources

1. The original HINORY roster (August 2026): 513 figures and 102 temples with notes and temple-board links.
2. A hand-curated list of acharyas, Alvars, Nayanars, Varkari and Haridasa saints, Kerala-school mathematicians and modern teachers.
3. A pull from **Wikidata** (CC0) and **English Wikipedia** on 27 Oct 2026:
   - people in Hindu saint, philosopher, yogi, Ayurveda and Carnatic categories, born before 1940, with a known place;
   - every Hindu temple in South Asia with a Wikipedia article and coordinates;
   - official websites from Wikidata (P856) and article infoboxes, with news, travel and blog links removed.

The base map is Natural Earth land (public domain, via `world-atlas`). It shows no modern borders on purpose.

## Caveats

- Coordinates are town-level. A person is pinned to the place most tied to them (birthplace, seat or samadhi).
- Dates for imported records come straight from Wikidata. Check a figure's Wikipedia page before quoting a date.
- Temple websites were not all re-checked for reachability; some may have moved or lapsed.
- Wikipedia's category coverage is uneven across regions.

## Rebuilding

`scripts/merge.py` merges the three sources and `scripts/clean_web.py` filters temple websites. They expect the intermediate inputs used during the October 2026 build (the original roster and the Wikidata export), which are not included here; `data/*.csv` is the merged result.
