GRAPH_SCHEMA = """
Nodes and their properties:
(:Product {product_id, name, price})
(:Brand {brand_id, name})
(:Category {category_id, name})
(:Vendor {vendor_id, name, city})
(:Customer {customer_id, name, city})
(:Order {order_id, order_date})

Relationships:
(:Product)-[:MADE_BY]->(:Brand)
(:Product)-[:BELONGS_TO]->(:Category)
(:Vendor)-[:SUPPLIES]->(:Product)
(:Customer)-[:PLACED]->(:Order)
(:Order)-[:CONTAINS {quantity}]->(:Product)
"""
