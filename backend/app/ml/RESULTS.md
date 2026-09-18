# NER vs regex vs hybrid (same test texts)

Field-level precision / recall / F1. A predicted field counts as a hit
only when status is `detected` and the normalized value matches gold.
Numbers are computed by `python -m app.ml.train_ner`, not hand-written.

Test documents: **78**

## Micro scores

| system | precision | recall | F1 |
|---|---:|---:|---:|
| regex_only | 0.9291 | 0.2449 | 0.3876 |
| ner_only | 1.0000 | 0.9850 | 0.9925 |
| hybrid | 1.0000 | 0.9682 | 0.9839 |

## Recall on manufacturer / origin / dates

| system | manufacturer | country_of_origin | manufacturing_date | expiry_date |
|---|---:|---:|---:|---:|
| regex_only | 0.1282 | 0.2703 | 0.2632 | 0.2740 |
| ner_only | 0.9872 | 0.9730 | 0.9868 | 0.9863 |
| hybrid | 0.9872 | 0.9865 | 0.9868 | 0.9863 |

## Per-field F1 (hybrid)

| field | P | R | F1 | support |
|---|---:|---:|---:|---:|
| product_name | 1.0000 | 0.8590 | 0.9241 | 78 |
| mrp | 1.0000 | 0.9872 | 0.9935 | 78 |
| net_quantity | 1.0000 | 0.9872 | 0.9935 | 78 |
| manufacturer | 1.0000 | 0.9872 | 0.9935 | 78 |
| country_of_origin | 1.0000 | 0.9865 | 0.9932 | 74 |
| manufacturing_date | 1.0000 | 0.9868 | 0.9934 | 76 |
| expiry_date | 1.0000 | 0.9863 | 0.9931 | 73 |

## Note

Hybrid recall is higher than regex on manufacturer / origin / dates on this test split.

## Token/entity seqeval (NER model on TEST)

- precision: 0.9943
- recall: 0.9924
- f1: 0.9934

