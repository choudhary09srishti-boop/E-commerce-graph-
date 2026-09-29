import os

import certifi
from dotenv import load_dotenv
from groq import Groq
from neo4j import GraphDatabase, TrustCustomCAs

load_dotenv(override=True)

host = os.getenv("NEO4J_URI").split("://")[1]
driver = GraphDatabase.driver(
    "neo4j://" + host,
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")),
    encrypted=True,
    trusted_certificates=TrustCustomCAs(certifi.where()),
)
driver.verify_connectivity()
driver.close()
print("Neo4j: OK")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
reply = client.chat.completions.create(
    model=os.getenv("GROQ_MODEL"),
    messages=[{"role": "user", "content": "Say OK"}],
)
print("Groq:", reply.choices[0].message.content)