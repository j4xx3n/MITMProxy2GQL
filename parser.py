#!/usr/bin/env python3
from graphql import parse
import json


# Fixed print_fields function
def print_fields(selections, variables_map, indent=2):
  """Recursively print all fields and subfields with indentation and argument values."""
  for selection in selections:
    # Check the kind of the selection node
    if selection.kind == 'field':
      # --- Handle FieldNode (Regular Field) ---
      
      # Print field name
      line = " " * indent + f"Field: {selection.name.value}"
      
      # Include arguments if present
      if selection.arguments:
        args_list = []
        for arg in selection.arguments:
          value = arg.value
          if value.kind == "variable":
            # Use the provided variable map to look up the value
            var_name = value.name.value
            args_list.append(f"{arg.name.value}: {variables_map.get(var_name, f'${var_name}')}")
          else:
            # Safely get the value for scalar types
            args_list.append(f"{arg.name.value}: {getattr(value, 'value', value)}") 
        line += " | Arguments: " + ", ".join(args_list)

      print(line)

      # Recursively print subfields (for FieldNodes)
      if selection.selection_set:
        print_fields(selection.selection_set.selections, variables_map, indent + 2)

    elif selection.kind == 'inline_fragment':
      # --- Handle InlineFragmentNode (e.g., ... on TypeName { ... }) ---
      type_cond = selection.type_condition.name.value if selection.type_condition else "interface/union"
      print(" " * indent + f"Inline Fragment: ... on {type_cond}")
      
      # Recursively print subfields (for InlineFragmentNodes)
      if selection.selection_set:
        print_fields(selection.selection_set.selections, variables_map, indent + 2)
        
    elif selection.kind == 'fragment_spread':
      # --- Handle FragmentSpreadNode (e.g., ...MyFragment) ---
      print(" " * indent + f"Fragment Spread: ...{selection.name.value}")
      # Note: Resolving the fields of the fragment is more complex and typically done
      # by looking up the fragment definition in ast.definitions.
      # For now, we'll just print the spread name.


      
with open('queries.json', 'r') as file:
    for line in file:
      line = line.strip()
      if not line:
        continue
      try:
        data = json.loads(line)
        queryValue = data.get("query")
        # 3. Rename or keep the variable name consistent (using 'variables' for clarity)
        variables = data.get("variables", {}) # Default to empty dict if 'variables' key is missing
        if not queryValue:
                continue

        ast = parse(queryValue)

        for definition in ast.definitions:
          if definition.kind == "operation_definition":
            print()
            print("------------------------------------------------------")
            print(f"Operation type: {definition.operation}")
            print(f"Operation name: {definition.name.value if definition.name else '(anonymous)'}")
            # 4. Pass the 'variables' dictionary when calling the function
            print_fields(definition.selection_set.selections, variables)

      except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {e}")