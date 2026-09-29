import logging

from groq import GroqError
from neo4j.exceptions import DriverError, Neo4jError

from src.answer_generator import NOT_FOUND_MESSAGE, rows_to_answer
from src.query_runner import run_query
from src.text_to_cypher import question_to_cypher

log = logging.getLogger(__name__)


def ask(question):
    """Run the full flow: question -> Cypher -> graph rows -> answer.

    Returns a dict with the question, cypher, rows and answer.
    Errors are logged and turned into a friendly answer instead of a crash.
    """
    result = {"question": question, "cypher": None, "rows": [], "answer": ""}
    log.info("Question: %s", question)

    try:
        cypher = question_to_cypher(question)
        result["cypher"] = cypher

        if cypher is None:
            result["answer"] = NOT_FOUND_MESSAGE
            return result

        result["rows"] = run_query(cypher)
        result["answer"] = rows_to_answer(question, result["rows"])

    except ValueError as error:
        log.warning("Unsafe query blocked: %s", error)
        result["answer"] = "The generated query was blocked by the safety check."
    except (Neo4jError, DriverError) as error:
        log.error("Graph database error: %s", error)
        result["answer"] = "The graph database returned an error. Please try again."
    except GroqError as error:
        log.error("LLM error: %s", error)
        result["answer"] = "The LLM service returned an error. Please try again."

    return result
