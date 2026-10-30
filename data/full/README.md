# Full graph: public structured distribution

This directory is separate from the experiment subset. It preserves every formal v4 entity, core assertion, temporal fact, time value, ID and graph-structure record in both knowledge snapshots. It contains extracted facts and source references, without third-party full texts, source excerpts, paragraph bodies or images.

| Snapshot | Formal entities | Core assertions (asserted + planned) | Temporal facts (asserted + planned) | Industry structure | Product portfolio |
|---|---:|---:|---:|---:|---:|
| Current: 2026-10-28 | 45,230 | 49,612 (49,611 + 1) | 47,407 (47,406 + 1) | 723 | 289 |
| As of 2025-12-31 | 43,940 | 37,920 (37,919 + 1) | 36,424 (36,423 + 1) | 347 | 289 |

The core assertion and distinct-fact totals in the original statistics exclude the one planned record. The JSONL tables retain it and its modality. Unknown event dates remain null; they are not missing records to be discarded.

## Files

- `current/` and `asof-2025/`: UTF-8 JSONL, compressed with gzip. Each physical line is one JSON object. Use ordinary file iteration, not Unicode `splitlines()` on the entire decoded file.
- `entities.jsonl.gz`: the seven formal entity types, original canonical names, Chinese display labels, aliases, stable identity scopes and evidence references.
- `assertions.jsonl.gz`: all core relation assertions, modalities, verification tiers, source visibility, event/observation time and provenance.
- `temporal_facts.jsonl.gz`: facts aggregated by the source v4 rule, with supporting assertion IDs.
- `quadruples_event.jsonl.gz`, `quadruples_observation.jsonl.gz`: event axis and source-observation axis. `unknown_event_time.jsonl.gz` is the explicit null-event subset. The two quadruple tables also have convenience `.csv.gz` files.
- `classification_structure.jsonl.gz`, `industry_taxonomy.jsonl.gz`: industry hierarchy and facets; these are metadata structures, not extra core ontology predicates.
- `product_portfolio.jsonl.gz`: reported company-to-product portfolio metadata; it does not establish manufacture, supply, ownership or a production start date.
- `supplementary_relations.jsonl.gz`: separate exhibition/transaction supplement, outside the 26 core relations. `supplementary_entities.jsonl.gz` contains only the 243 extra endpoints required to interpret this layer, marked `formal_graph_member=false`; they are not part of the formal entity count and are not evidence of verified main business.
- `identity_alignment.jsonl.gz`: original explicit source-ID alignment map. A retired source ID need not be a formal node.
- `documents.jsonl.gz`: source URL, publisher, publication/observation status, licenses and raw/text SHA256, lengths, paragraph counts and original archive/member/row byte anchors. Original source files and local filesystem paths are omitted.
- `mentions.jsonl.gz`: entity/document mention IDs and exact Unicode coordinates; mention text is withheld.
- `manifest.json`: hashes, counts and unchanged semantic signatures, checked after re-reading each gzip file. `sanitization.json` records removed-field counts; `statistics.json` retains the source graph statistics.
- `public-schema.json`: JSON Schema definitions for table records. `_withheld_fields` contains only hashes/lengths for omitted prose or source content.
