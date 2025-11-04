#!/usr/bin/env python3
from graphql import parse
import json
from collections import defaultdict

# --- Utility: Store SDL schema elements ---
# schema_types[type_name] = dict(field_name -> {"args": {arg_name: value}, "subfields": set()})
schema_types = defaultdict(lambda: defaultdict(lambda: {"args": {}, "subfields": set()}))

def add_field_to_schema(type_name, field_name, args=None, subfields=None):
    """Add a field to a type in the inferred SDL schema, including arguments and subfields."""
    field = schema_types[type_name][field_name]
    if args:
        field["args"].update(args)
    if subfields:
        field["subfields"].update(subfields)

# --- Recursive print and SDL collection ---
def print_fields(selections, variables_map, parent_type="Query", indent=2):
    """Recursively print fields and subfields with indentation and build an SDL schema."""
    for selection in selections:
        if selection.kind == 'field':
            field_name = selection.name.value
            line = " " * indent + f"Field: {field_name}"

            # Handle arguments
            args_dict = {}
            if selection.arguments:
                args_list = []
                for arg in selection.arguments:
                    value = arg.value
                    if value.kind == "variable":
                        var_name = value.name.value
                        arg_val = variables_map.get(var_name, f'${var_name}')
                    else:
                        arg_val = getattr(value, 'value', value)
                    args_list.append(f"{arg.name.value}: {arg_val}")
                    args_dict[arg.name.value] = "String"  # assume String type for args
                line += " | Arguments: " + ", ".join(args_list)

            print(line)

            # Recursively handle subfields
            subfields_set = set()
            if selection.selection_set:
                sub_type_name = field_name[0].upper() + field_name[1:]
                print_fields(selection.selection_set.selections, variables_map, sub_type_name, indent + 2)
                subfields_set.add(sub_type_name)

            # Add field to SDL schema
            add_field_to_schema(parent_type, field_name, args=args_dict, subfields=subfields_set)

        elif selection.kind == 'inline_fragment':
            type_cond = selection.type_condition.name.value if selection.type_condition else "interface/union"
            print(" " * indent + f"Inline Fragment: ... on {type_cond}")
            print_fields(selection.selection_set.selections, variables_map, type_cond, indent + 2)

        elif selection.kind == 'fragment_spread':
            print(" " * indent + f"Fragment Spread: ...{selection.name.value}")


with open('queries.json', 'r') as file:
    for line in file:
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            if not isinstance(data, dict):
                print(f"Skipping non-dictionary data (Type: {type(data).__name__}) on line: {line[:50]}...")
                continue # Skip to the next line in the file
            query_value = data.get("query")
            variables = data.get("variables", {})
            if not query_value:
                continue
            ast = parse(query_value)
            for definition in ast.definitions:
                if definition.kind == "operation_definition":
                    op_type_str = (getattr(definition.operation, 'value', None) or
                                   getattr(definition.operation, 'name', str(definition.operation))).capitalize()
                    print()
                    print("------------------------------------------------------")
                    print(f"Operation type: {op_type_str}")
                    print(f"Operation name: {definition.name.value if definition.name else '(anonymous)'}")

                    root_type = op_type_str
                    print_fields(definition.selection_set.selections, variables, parent_type=root_type)

        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")

# --- Write the inferred SDL schema ---
def write_field_sdl(f, field_name, field_info, indent=2):
    """Write a single field with arguments and subfields."""
    args_str = ""
    if field_info["args"]:
        args_str = "(" + ", ".join(f"{k}: {v}" for k, v in field_info["args"].items()) + ")"
    if field_info["subfields"]:
        f.write(" " * indent + f"{field_name}{args_str}: " + list(field_info["subfields"])[0] + "\n")
    else:
        f.write(" " * indent + f"{field_name}{args_str}: String\n")  # default type String

with open("schema.graphql", "w") as sdl_file:
    sdl_file.write("# Auto-generated SDL schema (inferred from queries)\n\n")
    for type_name, fields in schema_types.items():
        sdl_file.write(f"type {type_name} {{\n")
        for field_name, field_info in sorted(fields.items()):
            write_field_sdl(sdl_file, field_name, field_info)
        sdl_file.write("}\n\n")

print("\n✅ SDL schema written to schema.graphql")
