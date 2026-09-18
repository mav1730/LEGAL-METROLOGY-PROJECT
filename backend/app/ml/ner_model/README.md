# NER weights directory

Train DistilBERT and write files here:

```
python -m app.ml.make_dataset
python -m app.ml.train_ner
```

Expected after a successful run:

- `config.json`
- `tokenizer` files (`tokenizer.json` / `vocab.txt` / `tokenizer_config.json`)
- `model.safetensors` (gitignored — too large)
- `label2id.json` (15 BIO tags)

The Flask app loads this folder with `local_files_only=True`. It will not
download DistilBERT on `/api/scan/*` requests. If the folder is empty,
`EXTRACTOR_MODE=hybrid` falls back to regex.
