"""
Knowledge database utilities for retrieving plant information.
"""

import json
from typing import Dict, Optional
from pathlib import Path


class KnowledgeDB:
    """
    Handler for medicinal plant knowledge database.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize the knowledge database.
        
        Args:
            db_path: Path to the knowledge_db.json file
        """
        self.db_path = Path(db_path)
        self.knowledge = self._load_db()
    
    def _load_db(self) -> Dict:
        """
        Load the knowledge database from JSON file.
        
        Returns:
            Dictionary containing plant information
        """
        with open(self.db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_plant_info(self, class_name: str) -> Optional[Dict]:
        """
        Retrieve information for a specific plant class.
        
        Args:
            class_name: Name of the plant class (e.g., 'jasminum')
        
        Returns:
            Dictionary with plant information or None if not found
        """
        return self.knowledge.get(class_name)
    
    def get_formatted_info(self, class_name: str) -> Dict:
        """
        Get formatted plant information ready for API response.
        
        Args:
            class_name: Name of the plant class
        
        Returns:
            Dictionary with formatted information, or empty dict if not found
        """
        info = self.get_plant_info(class_name)
        
        if info is None:
            return {
                "Scientific Name": "Information not available",
                "Medicinal Uses": [],
                "Active Compounds": [],
                "Precautions": "Information not available",
                "Sources": []
            }
        
        return {
            "Scientific Name": info.get("Scientific Name", "N/A"),
            "Medicinal Uses": info.get("Medicinal Uses", []),
            "Active Compounds": info.get("Active Compounds", []),
            "Precautions": info.get("Precautions", "N/A"),
            "Sources": info.get("Sources", [])
        }
