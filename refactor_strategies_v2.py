import os

SOURCE_DIR = r"c:\Users\mayur\OneDrive\Desktop\Azalyst_Live_Trader\azalyst\strategies"
TARGET_DIR = r"c:\Users\mayur\OneDrive\Desktop\Azalyst_Live_Trader\app\engine\strategies"

def refactor():
    strategy_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith(".py") and f != "__init__.py"]

    registry = {}
    
    for f in strategy_files:
        if f == "htf_filter.py":
            continue
            
        src_path = os.path.join(SOURCE_DIR, f)
        with open(src_path, "r", encoding="utf-8") as file:
            content = file.read()
            
        module_name = f.replace(".py", "")
        class_name = "".join(word.capitalize() for word in module_name.split("_")) + "Strategy"
        
        # Replace imports
        content = content.replace("from azalyst.config", "from app.engine.constants")
        content = content.replace("from azalyst.candlestick", "from app.engine.analysis.candlestick_patterns")
        
        # Rename main signal function to avoid conflict with class method
        content = content.replace("def signal(df: pd.DataFrame) -> int:", "def _signal(df: pd.DataFrame) -> int:")
        # Some strategies might not have the type hint exactly like that, let's be safe:
        content = content.replace("def signal(df):", "def _signal(df):")
        
        # Append class definition
        class_def = f"""
from app.engine.strategies.base_strategy import BaseStrategy, SignalType

class {class_name}(BaseStrategy):
    name: str = "{module_name}"

    def signal(self, df: pd.DataFrame) -> SignalType:
        return _signal(df)
"""
        
        with open(os.path.join(TARGET_DIR, f), "w", encoding="utf-8") as target_file:
            target_file.write(content + "\n" + class_def)
            
        registry[module_name] = class_name
        print(f"Refactored {module_name} -> {class_name}")

if __name__ == "__main__":
    refactor()
