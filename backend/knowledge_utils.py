import json
from typing import Dict, Any

class KnowledgeBase:
    def __init__(self, json_path: str):
        self.knowledge_data = self._load_json(json_path)
        
    def _load_json(self, json_path: str) -> Dict[str, Any]:
        """Load the knowledge base JSON file."""
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    def get_leaf_info(self, leaf_class: str) -> Dict[str, Any]:
        """Get knowledge base information for a specific leaf class."""
        if leaf_class not in self.knowledge_data:
            raise KeyError(f"No information found for leaf class: {leaf_class}")
        return self.knowledge_data[leaf_class]