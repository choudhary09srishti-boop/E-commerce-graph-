import csv
import logging

from src import config
from src.database import get_driver

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

# Unique IDs stop duplicate nodes and make lookups fast.
CONSTRAINTS = [
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Brand) REQUIRE n.brand_id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Category) REQUIRE n.category_id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Vendor) REQUIRE n.vendor_id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Customer) REQUIRE n.customer_id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Product) REQUIRE n.product_id IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Order) REQUIRE n.order_id IS UNIQUE",
]

# (csv file, Cypher query). Order matters: nodes first, then things that link to them.
LOAD_STEPS = [
    (
        "brands.csv",
        """
        UNWIND $rows AS row
        MERGE (b:Brand {brand_id: row.brand_id})
        SET b.name = row.name
        """,
    ),
    (
        "categories.csv",
        """
        UNWIND $rows AS row
        MERGE (c:Category {category_id: row.category_id})
        SET c.name = row.name
        """,
    ),
    (
        "vendors.csv",
        """
        UNWIND $rows AS row
        MERGE (v:Vendor {vendor_id: row.vendor_id})
        SET v.name = row.name, v.city = row.city
        """,
    ),
    (
        "customers.csv",
        """
        UNWIND $rows AS row
        MERGE (c:Customer {customer_id: row.customer_id})
        SET c.name = row.name, c.city = row.city
        """,
    ),
    (
        "products.csv",
        """
        UNWIND $rows AS row
        MERGE (p:Product {product_id: row.product_id})
        SET p.name = row.name, p.price = toInteger(row.price)
        WITH p, row
        MATCH (b:Brand {brand_id: row.brand_id})
        MATCH (c:Category {category_id: row.category_id})
        MATCH (v:Vendor {vendor_id: row.vendor_id})
        MERGE (p)-[:MADE_BY]->(b)
        MERGE (p)-[:BELONGS_TO]->(c)
        MERGE (v)-[:SUPPLIES]->(p)
        """,
    ),
    (
        "orders.csv",
        """
        UNWIND $rows AS row
        MERGE (o:Order {order_id: row.order_id})
        SET o.order_date = date(row.order_date)
        WITH o, row
        MATCH (c:Customer {customer_id: row.customer_id})
        MERGE (c)-[:PLACED]->(o)
        """,
    ),
    (
        "order_items.csv",
        """
        UNWIND $rows AS row
        MATCH (o:Order {order_id: row.order_id})
        MATCH (p:Product {product_id: row.product_id})
        MERGE (o)-[r:CONTAINS]->(p)
        SET r.quantity = toInteger(row.quantity)
        """,
    ),
]


def read_csv(file_name):
    """Read a CSV from the data folder as a list of dicts."""
    with open(config.DATA_DIR / file_name, newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def main():
    driver = get_driver()
    with driver.session(database=config.NEO4J_DATABASE) as session:
        for query in CONSTRAINTS:
            session.run(query)

        for file_name, query in LOAD_STEPS:
            rows = read_csv(file_name)
            session.run(query, rows=rows)
            log.info("Loaded %s (%d rows)", file_name, len(rows))

        nodes = session.run("MATCH (n) RETURN count(n) AS total").single()["total"]
        relationships = session.run("MATCH ()-[r]->() RETURN count(r) AS total").single()["total"]
        banana = session.run(
            "MATCH (p:Product) WHERE toLower(p.name) CONTAINS 'banana' RETURN count(p) AS total"
        ).single()["total"]

    driver.close()
    log.info("Graph has %d nodes and %d relationships", nodes, relationships)
    log.info("Banana products: %d (expected 5)", banana)


if __name__ == "__main__":
    main()