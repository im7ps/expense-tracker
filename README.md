# expense-tracker

Programma da terminale che importa movimenti da file CSV, assegna le categorie e mostra il totale delle spese per categoria in un mese.

## Requisiti

- Python 3.11 o superiore

## Installazione

Dalla cartella del progetto:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[test]"
```

## Configurazione delle regole

Copia il file di esempio e adattalo ai tuoi movimenti:

```bash
cp config/rules.example.json config/rules.json
```

Il file è un oggetto JSON `"parola chiave": "categoria"`. Una regola corrisponde se la parola compare nella descrizione del movimento, senza distinguere maiuscole e minuscole. Vince la prima regola del file. I movimenti senza regola finiscono in `non_categorizzato`.

## Importare un file

```bash
expense-tracker import tests/fixtures/sorgente_a.csv --source sorgente_a --rules config/rules.json
```

- `--source`: `sorgente_a` (colonne `data;descrizione;importo`, date `GG/MM/AAAA`, importi con virgola) oppure `sorgente_b` (colonne `date,description,amount`, date ISO `AAAA-MM-GG`, importi con punto).
- `--rules`: facoltativo. Senza di esso tutti i movimenti sono `non_categorizzato`.
- `--db`: facoltativo. Database SQLite dove vengono salvati i movimenti (default `expenses.db` nella cartella corrente).

Le righe non valide vengono saltate con un avviso e l'import continua. Reimportare lo stesso file sostituisce i movimenti già salvati di quel file, senza duplicarli.

## Report mensile

```bash
expense-tracker report --year 2026 --month 1
```

Mostra il totale delle spese per categoria nel mese indicato. Sono considerati solo gli importi negativi; le entrate non vengono sommate.

## Test

```bash
pytest
```
