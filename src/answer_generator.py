import json
import logging

from groq import Groq

from src import config

log = logging.getLogger(__name__)

NOT_FOUND_MESSAGE = "I could not find this in the knowledge graph."

SYSTEM_PROMPT = f"""You answer questions using only the graph data provided.

Rules:
- Use only the rows in the data. Do not use outside knowledge.
- Do not guess or add details that are not in the rows.
- Keep the answer short and clear.
- If the rows do not answer the question, reply exactly: {NOT_FOUND_MESSAGE}
"""


def rows_to_answer(question, rows):
    """Write a plain-English answer from the rows. No rows means no answer."""
    if not rows:
        return NOT_FOUND_MESSAGE

    client = Groq(api_key=config.GROQ_API_KEY)
    user_message = f"Question: {question}\n\nGraph data:\n{json.dumps(rows, default=str)}"
    reply = client.chat.completions.create(
        model=config.GROQ_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )
    return reply.choices[0].message.content.strip()


if __name__ == "__main__":
    from src.query_runner import run_query
    from src.text_to_cypher import question_to_cypher

    logging.basicConfig(level=logging.WARNING)

    questions = [
        "Which products contain banana?",
        "What did Aarav Mehta order?",
        "Which products from brand GlowUp are supplied by GreenLeaf Traders?",
        "Who is the prime minister of India?",
    ]
    for question in questions:
        print("\nQ:", question)
        query = question_to_cypher(question)
        rows = run_query(query) if query else []
        print("A:", rows_to_answer(question, rows))