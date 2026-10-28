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

## Time and interpretation

The historical snapshot is a knowledge-availability snapshot. A 2025 event first supported by a 2026 source is not retroactively inserted into the 2025 graph. The current snapshot may include that historical event with its real later observation. Event time, report publication and source-observation time are separate.

US patent `ownedBy` records identify the recorded assignee at grant, at the real grant date; they do not assert current ownership. Inventor attribution has unknown invention time. The selected PatentsView snapshot became available on 2025-07-01; normalized source names are not presented as having been observed at earlier grant dates. Inventor identities may be scoped to a patent application and must not be counted as globally resolved people.

Static industry classification, source-directory product portfolios and executive roles without explicit start/end remain undated. An open appointment interval is only known through its source observation; it is not proof of indefinite later employment. Planned assertions are distinct from asserted facts. `human_gold=0` is retained.

Chinese display labels do not change IDs or identity resolution. Auxiliary translations and approximate transliterations are marked; the Chinese patent search labels marked `not_full_title_translation=true` are not claimed to be full title translations.

## Evidence and reuse

Evidence `start`/`end` use Unicode codepoint offsets in the original normalized text, with the half-open convention `[start,end)`. They are not byte offsets. The referenced document supplies `text_sha256` and `text_length`. `quote_sha256` hashes the UTF-8 bytes of the withheld original quote; `quote_length` counts codepoints. PDF page numbers, table geometry, original ZIP/member byte offsets, figure SHA and image-region coordinates are retained where present. Re-fetch the source lawfully and use the recorded normalization/version and hashes to verify a reference. No complete source text, quote, figure pixels or visual transcription is shipped.

Public access to a document does not give this project a blanket redistribution license. Third-party policies, corporate disclosures, professional reports, directories, patent PDFs and figures remain subject to their respective rights and terms. These files do not relicense those originals. Source-specific `license`, `usage_rights` and URLs remain in the document metadata. No claim of official corporate Chinese names or human identity verification is created by a display translation.

The selected US source-record snapshot is attributed to the United States Patent and Trademark Office / PatentsView, Zenodo record **15783125**, version 2, published **2025-07-01**, licensed **CC BY 4.0**: https://zenodo.org/records/15783125 ; https://creativecommons.org/licenses/by/4.0/ . This public graph is a filtered and transformed extraction; source excerpts and bulk archive contents are omitted. Original ZIP SHA, member, row SHA and byte coordinates are retained for attribution and reproducibility.

The repository code license, if present, applies to code in its stated scope. It does not grant rights to third-party originals. A permissive license must not be inferred merely because a field is downloadable. This distribution makes no blanket license grant over all source materials.

## Reproduction and validation

The public transformation is deterministic (gzip header time is zero). Its build and finalization scripts operate on read-only local v4 exports. Counts, original ID sequences and fact signatures are compared with those exports, then the actual compressed outputs are re-read and checked for prohibited content/credential fields. Source originals, SQLite, full GraphML, internal candidates, manuscript drafts, collection logs and session headers are deliberately outside this distribution.

For full downloads, download the repository ZIP or the versioned `.jsonl.gz` files linked by the repository README. The separate experiment subset has its own selection and split documentation; these full snapshots are not train/test splits.
