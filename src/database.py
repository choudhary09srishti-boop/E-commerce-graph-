import certifi
from neo4j import GraphDatabase, TrustCustomCAs

from src import config


def get_driver():
    """Create a Neo4j driver. certifi provides the CA bundle so TLS works on Windows."""
    host = config.NEO4J_URI.split("://")[1]
    return GraphDatabase.driver(
        "neo4j://" + host,
        auth=(config.NEO4J_USERNAME, config.NEO4J_PASSWORD),
        encrypted=True,
        trusted_certificates=TrustCustomCAs(certifi.where()),
    )