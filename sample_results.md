# Sample questions and results

## 1. Which products contain banana?

**Cypher:**
```cypher
MATCH (p:Product)
WHERE toLower(p.name) CONTAINS toLower('banana')
RETURN p.name AS product
LIMIT 50
```

**Rows retrieved:** 5

**Answer:**

The products that contain banana are:

- Banana Chips  
- Banana Protein Shake  
- Banana Face Wash  
- Banana Bread Mix  
- Banana Hair Mask

## 2. How many products contain banana?

**Cypher:**
```cypher
MATCH (p:Product)
WHERE toLower(p.name) CONTAINS toLower('banana')
RETURN count(p) AS product_count
LIMIT 50
```

**Rows retrieved:** 1

**Answer:**

5

## 3. Which products from brand NutriBite are supplied by Sharma Wholesale?

**Cypher:**
```cypher
MATCH (v:Vendor)-[:SUPPLIES]->(p:Product)-[:MADE_BY]->(b:Brand)
WHERE toLower(b.name) CONTAINS toLower('NutriBite')
  AND toLower(v.name) CONTAINS toLower('Sharma Wholesale')
RETURN p.name AS product, b.name AS brand, v.name AS vendor
LIMIT 50
```

**Rows retrieved:** 4

**Answer:**

The NutriBite products supplied by Sharma Wholesale are:

- Banana Protein Shake  
- Banana Bread Mix  
- Peanut Butter Crunchy  
- Cold Coffee Can

## 4. What did Aarav Mehta order?

**Cypher:**
```cypher
MATCH (c:Customer)-[:PLACED]->(o:Order)-[r:CONTAINS]->(p:Product)
WHERE toLower(c.name) CONTAINS toLower('Aarav Mehta')
RETURN c.name AS customer, o.order_id AS order_id, p.name AS product, r.quantity AS quantity
LIMIT 50
```

**Rows retrieved:** 4

**Answer:**

Aarav Mehta ordered:

- 2 Banana Chips  
- 1 Green Tea Pack  
- 3 Banana Protein Shake  
- 1 Peanut Butter Crunchy

## 5. Which vendor supplies the Smart Watch?

**Cypher:**
```cypher
MATCH (v:Vendor)-[:SUPPLIES]->(p:Product)
WHERE toLower(p.name) CONTAINS toLower('Smart Watch')
RETURN v.name AS vendor, p.name AS product
LIMIT 50
```

**Rows retrieved:** 1

**Answer:**

Metro Supplies.

## 6. Which customers bought products from the brand TechNova?

**Cypher:**
```cypher
MATCH (c:Customer)-[:PLACED]->(o:Order)-[r:CONTAINS]->(p:Product)-[:MADE_BY]->(b:Brand)
WHERE toLower(b.name) CONTAINS toLower('TechNova')
RETURN c.name AS customer, o.order_id AS order_id, p.name AS product, b.name AS brand, r.quantity AS quantity
LIMIT 50
```

**Rows retrieved:** 3

**Answer:**

Rohan Gupta and Kabir Singh.

## 7. How many products are in each category?

**Cypher:**
```cypher
MATCH (c:Category)<-[:BELONGS_TO]-(p:Product)
RETURN c.name AS category, count(p) AS product_count
LIMIT 50
```

**Rows retrieved:** 6

**Answer:**

- Snacks: 4  
- Beverages: 3  
- Beauty: 3  
- Electronics: 2  
- Home and Kitchen: 2  
- Apparel: 2

## 8. Which products from brand GlowUp are supplied by GreenLeaf Traders?

**Cypher:**
```cypher
MATCH (v:Vendor)-[:SUPPLIES]->(p:Product)-[:MADE_BY]->(b:Brand)
WHERE toLower(b.name) CONTAINS toLower('GlowUp')
AND toLower(v.name) CONTAINS toLower('GreenLeaf Traders')
RETURN p.name AS product, b.name AS brand, v.name AS vendor
LIMIT 50
```

**Rows retrieved:** 0

**Answer:**

I could not find this in the knowledge graph.

## 9. Who is the prime minister of India?

**Cypher:**
```cypher
NO_QUERY
```

**Rows retrieved:** 0

**Answer:**

I could not find this in the knowledge graph.
