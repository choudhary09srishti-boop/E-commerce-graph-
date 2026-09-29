import logging

from groq import Groq

from src import config
from src.schema import GRAPH_SCHEMA

log = logging.getLogger(__name__)

SYSTEM_PROMPT = f"""You convert questions into Neo4j Cypher queries.

Graph schema:
{GRAPH_SCHEMA}

Rules:
- Output only the Cypher query. No explanation, no markdown, no backticks.
- Read-only queries only (MATCH ... RETURN).
- Use only the labels, relationships and properties in the schema.
- Compare text case-insensitively: toLower(x.name) CONTAINS toLower('value').
- Give every returned value a readable alias, for example p.name AS product.
- End with LIMIT 50.
- If the question cannot be answered with this schema, output exactly: NO_QUERY

Example question: Which products from brand FreshFarm are supplied by vendor GreenLeaf Traders?
Example query:
MATCH (v:Vendor)-[:SUPPLIES]->(p:Product)-[:MADE_BY]->(b:Brand)
WHERE toLower(b.name) CONTAINS toLower('FreshFarm')
AND toLower(v.name) CONTAINS toLower('GreenLeaf Traders')
RETURN p.name AS product
LIMIT 50
"""


def clean_query(text):
    """Remove code fences the model may add despite instructions."""
    return text.replace("```cypher", "").replace("```", "").strip()


def question_to_cypher(question):
    """Ask the LLM for a Cypher query. Returns None if it cannot be answered."""
    client = Groq(api_key=config.GROQ_API_KEY)
    reply = client.chat.completions.create(
        model=config.GROQ_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
    )
    query = clean_query(reply.choices[0].message.content)
    log.info("Generated Cypher: %s", query)

    if query == "NO_QUERY":
        return None
    return query


if __name__ == "__main__":
    from src.query_runner import run_query

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    questions = [
        "Which products contain banana?",
        "Which products from brand NutriBite are supplied by Sharma Wholesale?",
        "What did Aarav Mehta order?",
        "Who is the prime minister of India?",
    ]
    for question in questions:
        print("\nQ:", question)
        query = question_to_cypher(question)
        if query is None:
            print("A: cannot be answered from the graph")
        else:
            print("Rows:", run_query(query))