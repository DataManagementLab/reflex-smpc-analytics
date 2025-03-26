import json
import re

def parse_sql_query(query):
    # Normalize the query to lowercase and remove excess whitespace
    query = query.strip().lower()

    # Extract table names
    tables = re.findall(r'(from|join)\s+(\w+)', query)
    tables = [table[1] for table in tables]

    # Extract conditions
    conditions = re.findall(r'(\w+\.\w+\s*[=><]\s*\w+)', query)

    return tables, conditions

def generate_query_plan(query):
    tables, conditions = parse_sql_query(query)

    query_plan = {
        "name": "Query Root",
        "children": []
    }

    # Create table scan nodes
    for table in tables:
        table_node = {
            "name": f"Table Scan ({table.capitalize()})",
            "children": []
        }
        query_plan["children"].append(table_node)

    # Add filters to the corresponding table scan nodes
    for condition in conditions:
        table_name = condition.split('.')[0]
        filter_node = {
            "name": f"Filter: {condition}"
        }
        for node in query_plan["children"]:
            if table_name in node["name"].lower():
                node["children"].append(filter_node)
                break

    # Add join node if there are multiple tables
    if len(tables) > 1:
        join_node = {
            "name": "Hash Join",
            "children": [{"name": f"Join Condition: {conditions[-1]}"}]
        }
        query_plan["children"].append(join_node)

    return json.dumps(query_plan, indent=2)

# Example usage
# query = "SELECT * FROM Table1 JOIN Table2 ON Table1.k = Table2.k WHERE Table1.v = 333 AND Table2.v > 445"
# query_plan_json = generate_query_plan(query)
# print(query_plan_json)
