# E-commerce Knowledge Graph with LLM Retrieval

Ask questions about an e-commerce dataset in plain English. An LLM turns the question into a Cypher query, the query runs on a Neo4j knowledge graph, and a second LLM call writes the answer using **only the rows returned from the graph**.

```
User Question -> LLM -> Cypher Query -> Neo4j (read-only) -> Retrieved Rows -> LLM -> Answer
```

## Tech stack

- Python 3.10+
- Neo4j AuraDB Free (cloud graph database)
- Groq API (model: `openai/gpt-oss-120b`)
- Streamlit (web UI, with graph visualisation)

## Knowledge graph

| Nodes | Properties |
|-------|------------|
| Product | product_id, name, price |
| Brand | brand_id, name |
| Category | category_id, name |
| Vendor | vendor_id, name, city |
| Customer | customer_id, name, city |
| Order | order_id, order_date |

```
(Product)-[:MADE_BY]->(Brand)
(Product)-[:BELONGS_TO]->(Category)
(Vendor)-[:SUPPLIES]->(Product)
(Customer)-[:PLACED]->(Order)
(Order)-[:CONTAINS {quantity}]->(Product)
```

The dataset (`data/*.csv`) has 48 nodes and 77 relationships. The word **banana** appears exactly 5 times, in the names of 5 products (Banana Chips, Banana Protein Shake, Banana Face Wash, Banana Bread Mix, Banana Hair Mask).

The dataset is synthetic sample data created for this assignment. The loader is driven by the CSV files in `data/`, so a real dataset can be used by replacing them with files in the same column format.

## Project structure

```
.
├── app.py                  Streamlit web UI (Q&A + graph views)
├── main.py                 Command-line interface
├── requirements.txt
├── .env.example            Template for secrets
├── sample_results.md       Sample questions with results
├── data/                   Sample e-commerce dataset (7 CSV files)
└── src/
    ├── config.py           Reads settings from .env
    ├── database.py         Neo4j connection
    ├── schema.py           Graph schema shown to the LLM
    ├── load_graph.py       Loads the CSV files into Neo4j
    ├── query_runner.py     Safety check + read-only query execution
    ├── text_to_cypher.py   LLM: question -> Cypher
    ├── answer_generator.py LLM: rows -> grounded answer
    ├── graph_view.py       Builds the graph drawings for the UI
    └── pipeline.py         Full flow with error handling
```

## Setup

### 1. Create a free Neo4j AuraDB instance

1. Go to https://console.neo4j.io and create a **Free** instance.
2. Download the credentials `.txt` file when prompted (the password is shown only once).

### 2. Get a Groq API key

Create a key at https://console.groq.com/keys.

### 3. Install

```powershell
git clone https://github.com/choudhary09srishti-boop/E-commerce-graph-.git
cd E-commerce-graph-
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

On macOS or Linux, activate with `source venv/bin/activate` instead.

### 4. Configure

```powershell
Copy-Item .env.example .env
```

Open `.env` and fill in:

| Variable | Value |
|----------|-------|
| NEO4J_URI | from the Aura credentials file, e.g. `neo4j+s://xxxx.databases.neo4j.io` |
| NEO4J_USERNAME | from the credentials file |
| NEO4J_PASSWORD | from the credentials file |
| NEO4J_DATABASE | from the credentials file |
| GROQ_API_KEY | your Groq key |
| GROQ_MODEL | `openai/gpt-oss-120b` |

`.env` is git-ignored, so secrets are never committed.

## Run

Load the dataset into Neo4j (safe to rerun, it uses `MERGE`):

```powershell
python -m src.load_graph
```

Expected: 48 nodes, 77 relationships, and `Banana products: 5`.

Start the web UI:

```powershell
streamlit run app.py
```

The UI has two tabs:
- **Ask a question**: shows the question, the Cypher written by the LLM, the rows retrieved from Neo4j, the grounded answer, and a graph of the entities behind that answer.
- **Knowledge graph**: shows the graph schema and the full graph data, with the 5 banana products highlighted.

Or use the command line:

```powershell
python main.py            # interactive chat
python main.py --samples  # run the sample questions and write sample_results.md
```

## Sample questions

See [sample_results.md](sample_results.md) for 9 questions with the generated Cypher, rows retrieved and answers, including questions the graph cannot answer.

## How answers stay grounded

- The question-to-Cypher LLM sees only the graph schema, never the data.
- The answer LLM sees only the question and the rows returned by Neo4j.
- If a query returns no rows, the answer LLM is not called. The system replies "I could not find this in the knowledge graph."
- If a question cannot be answered with the schema (for example "Who is the prime minister of India?"), the LLM returns `NO_QUERY` and nothing runs.
- Both LLM calls use `temperature=0`.

## Safety

- Generated Cypher must be a single statement starting with `MATCH`, `OPTIONAL MATCH`, `WITH`, `UNWIND` or `RETURN`.
- Queries containing `CREATE`, `MERGE`, `DELETE`, `DETACH`, `SET`, `REMOVE`, `DROP`, `CALL`, `LOAD`, `FOREACH`, `INDEX` or `CONSTRAINT` are rejected before they reach the database.
- Queries run in a read-only Neo4j session, so the database refuses writes even if the check were bypassed.
- Results are capped at 50 rows.

## Verifying the banana requirement

Ask "Which products contain banana?" in the app or CLI. It returns exactly 5 products. The loader also prints the banana count after every load, and the Knowledge graph tab shows the 5 banana products in yellow.

## Logging and errors

Logs are written to `logs/app.log`. Database errors, LLM errors and blocked queries are caught and shown as friendly messages instead of crashing.

## Known limitations

- LLM-written Cypher can be wrong for complex multi-hop questions. The generated query is shown in the UI so it can be inspected.
- The dataset is small and synthetic.
- Neo4j connections use the `certifi` CA bundle, which fixes TLS certificate errors on some Windows machines.