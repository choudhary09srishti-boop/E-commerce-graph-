from src.query_runner import run_query

NODE_COLORS = {
    "Product": "#A5D8FF",
    "Brand": "#FFD8A8",
    "Category": "#D0BFFF",
    "Vendor": "#B2F2BB",
    "Customer": "#FFC9C9",
    "Order": "#DEE2E6",
}
BANANA_COLOR = "#FFE066"
ANSWER_COLOR = "#FF8787"

SCHEMA_RELATIONSHIPS = [
    ("Product", "MADE_BY", "Brand"),
    ("Product", "BELONGS_TO", "Category"),
    ("Vendor", "SUPPLIES", "Product"),
    ("Customer", "PLACED", "Order"),
    ("Order", "CONTAINS", "Product"),
]

# Every relationship in the graph, with readable names for both ends.
GRAPH_QUERY = """
MATCH (a)-[r]->(b)
RETURN labels(a)[0] AS from_label, coalesce(a.name, a.order_id) AS from_name,
       type(r) AS relationship,
       labels(b)[0] AS to_label, coalesce(b.name, b.order_id) AS to_name
"""

DOT_HEADER = [
    "digraph G {",
    "rankdir=LR;",
    'node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=10];',
    'edge [fontname="Helvetica", fontsize=8];',
]


def load_graph_rows():
    """Fetch every relationship from Neo4j (read-only)."""
    return run_query(GRAPH_QUERY, max_rows=500)


def build_schema_dot():
    """Graphviz drawing of the node types and how they connect."""
    lines = list(DOT_HEADER)
    for label, color in NODE_COLORS.items():
        lines.append(f'"{label}" [fillcolor="{color}"];')
    for start, relationship, end in SCHEMA_RELATIONSHIPS:
        lines.append(f'"{start}" -> "{end}" [label="{relationship}"];')
    lines.append("}")
    return "\n".join(lines)


def node_style(label, name, highlighted_names):
    """Return (color, border width) for a node.

    highlighted_names=None means the full graph, where banana products are yellow.
    Otherwise nodes named in highlighted_names are red (the entities in the answer).
    """
    if highlighted_names is None:
        highlighted = label == "Product" and "banana" in name.lower()
        color = BANANA_COLOR
    else:
        highlighted = name in highlighted_names
        color = ANSWER_COLOR

    if highlighted:
        return color, 3
    return NODE_COLORS[label], 1


def build_dot(rows, highlighted_names=None):
    """Graphviz drawing of graph relationship rows."""
    lines = list(DOT_HEADER)
    seen = set()
    edges = []

    for row in rows:
        for label, name in (
            (row["from_label"], row["from_name"]),
            (row["to_label"], row["to_name"]),
        ):
            if (label, name) not in seen:
                seen.add((label, name))
                color, border = node_style(label, name, highlighted_names)
                lines.append(
                    f'"{label}:{name}" [label="{name}", fillcolor="{color}", penwidth={border}];'
                )
        edges.append(
            f'"{row["from_label"]}:{row["from_name"]}" -> '
            f'"{row["to_label"]}:{row["to_name"]}" [label="{row["relationship"]}"];'
        )

    lines += edges
    lines.append("}")
    return "\n".join(lines)


def build_data_dot(rows):
    """The whole graph, with banana products highlighted."""
    return build_dot(rows)


def build_answer_dot(all_rows, result_rows):
    """The part of the graph behind one answer, or None if no graph entities were returned.

    Every value in the retrieved rows that matches a node name is highlighted,
    and the relationships touching those nodes are drawn around them.
    """
    names = {str(value) for row in result_rows for value in row.values()}
    related = [
        row for row in all_rows
        if row["from_name"] in names or row["to_name"] in names
    ]
    if not related:
        return None
    return build_dot(related, names)