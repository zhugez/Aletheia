# OpenSearch + Qdrant Adapters (v1 plan)

## OpenSearch index fields
- chunk_id (keyword)
- source_id (keyword)
- title (text+keyword)
- chapter (keyword)
- page_start (integer)
- page_end (integer)
- text_content (text, BM25)

## Qdrant payload fields
- chunk_id
- source_id
- title
- chapter
- page_start
- page_end
- language

## Retrieval flow
1. BM25 top_n from OpenSearch
2. Vector top_n from Qdrant
3. Merge + dedupe
4. Rerank
5. Return citation-ready top_k
