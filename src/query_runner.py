import logging
import re

from neo4j import READ_ACCESS

from src import config
from src.database import get_driver

log = logging.getLogger(__name__)

MAX_ROWS = 50

# A query containing any of these words could change data or call procedures.
FORBIDDEN_WORDS = [
    "CREATE", "MERGE", "DELETE", "DETACH", "SET", "REMOVE",
    "DROP", "CALL", "LOAD", "FOREACH", "INDEX", "CONSTRAINT",
]

ALLOWED_START = ("MATCH", "OPTIONAL", "WITH", "UNWIND", "RETURN")


def check_query_is_safe(query):
    """Raise ValueError unless the query is one read-only Cypher statement."""
    # Remove quoted text first, so a value like 'Set' is not mistaken for a command.
    without_text = re.sub(r"'[^']*'|\"[^\"]*\"", "", query)
    cleaned = without_text.strip().rstrip(";").strip()

    if ";" in cleaned:
        raise ValueError("Only one query is allowed.")
    if not cleaned.upper().startswith(ALLOWED_START):
        raise ValueError("Query must start with MATCH, OPTIONAL MATCH, WITH, UNWIND or RETURN.")
    for word in FORBIDDEN_WORDS:
        if re.search(rf"\b{word}\b", cleaned, re.IGNORECASE):
            raise ValueError(f"Not allowed in a read-only query: {word}")


def run_query(query):
    """Check the query, run it in read-only mode, and return rows as a list of dicts."""
    check_query_is_safe(query)

    driver = get_driver()
    try:
        with driver.session(
            database=config.NEO4J_DATABASE, default_access_mode=READ_ACCESS
        ) as session:
            rows = [record.data() for record in session.run(query)]
    finally:
        driver.close()

    log.info("Query returned %d rows", len(rows))
    return rows[:MAX_ROWS]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    good_query = (
        "MATCH (p:Product) WHERE toLower(p.name) CONTAINS 'banana' "
        "RETURN p.name AS name"
    )
    print(run_query(good_query))

    bad_queries = [
        "MATCH (n) DETACH DELETE n",
        "MATCH (n) SET n.name = 'x' RETURN n",
        "CALL db.labels()",
    ]
    for bad_query in bad_queries:
        try:
            run_query(bad_query)
        except ValueError as error:
            print("Blocked:", error)
            