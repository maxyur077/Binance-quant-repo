from __future__ import annotations

import ast
import os
import textwrap

SOURCE_DIR = r"c:\Users\mayur\OneDrive\Desktop\Azalyst_Live_Trader\azalyst\strategies"
TARGET_DIR = r"c:\Users\mayur\OneDrive\Desktop\Azalyst_Live_Trader\app\engine\strategies"

def refactor_strategies():
    os.makedirs(TARGET_DIR, exist_ok=True)
    strategy_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith(".py") and f != "__init__.py"]

    registry = {}
    
    for f in strategy_files:
        src_path = os.path.join(SOURCE_DIR, f)
        with open(src_path, "r", encoding="utf-8") as file:
            content = file.read()
            
        module_name = f.replace(".py", "")
        class_name = "".join(word.capitalize() for word in module_name.split("_")) + "Strategy"
        
        # We need to extract the logic from `def signal(df):` or similar.
        # We will parse the AST to find the signal function.
        tree = ast.parse(content)
        imports = []
        signal_body = ""
        
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                # Keep imports but drop local azalyst ones as we will inject them
                if isinstance(node, ast.ImportFrom) and node.module and "azalyst" in node.module:
                    continue
                imports.append(ast.get_source_segment(content, node))
            elif isinstance(node, ast.FunctionDef) and node.name == "signal":
                # Get the body of the signal function
                signal_body = ""
                for stmt in node.body:
                    signal_body += ast.get_source_segment(content, stmt) + "\n"
        
        imports_str = "\n".join(imports)
        indented_body = textwrap.indent(signal_body, "        ")
        
        refactored_content = f"""from __future__ import annotations

from typing import cast
import pandas as pd
import numpy as np

{imports_str}

from app.engine.strategies.base_strategy import BaseStrategy, SignalType
from app.engine.constants import BUY, SELL, HOLD


class {class_name}(BaseStrategy):
    name: str = "{module_name}"

    def signal(self, df: pd.DataFrame) -> SignalType:
{indented_body}
"""
        
        target_path = os.path.join(TARGET_DIR, f)
        with open(target_path, "w", encoding="utf-8") as target_file:
            target_file.write(refactored_content)
            
        registry[module_name] = class_name
        print(f"Refactored {module_name} -> {class_name}")

    # Write __init__.py for strategies
    init_lines = ["from __future__ import annotations\n\nfrom typing import Dict, Type\nfrom app.engine.strategies.base_strategy import BaseStrategy\n"]
    for mod, cls in registry.items():
        init_lines.append(f"from .{mod} import {cls}")
        
    init_lines.append("\nMULTI_STRATEGIES: Dict[str, BaseStrategy] = {")
    for mod, cls in registry.items():
        init_lines.append(f'    "{mod}": {cls}(),')
    init_lines.append("}\n")
    
    with open(os.path.join(TARGET_DIR, "__init__.py"), "w", encoding="utf-8") as init_file:
        init_file.write("\n".join(init_lines))

if __name__ == "__main__":
    refactor_strategies()
