"""Manage conjugations.json data operations."""

from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import json


class ConjugationDataManager:
    """Manage conjugations.json data operations"""
    
    def __init__(self, data_provider=None, project_root: Path = None):
        self.data_provider = data_provider
        self.project_root = project_root or Path.cwd()
        self.data_file = self.project_root / "conjugations.json"
    
    def load_conjugations(self) -> Dict[str, Any]:
        """Load conjugation data"""
        if self.data_provider:
            return self.data_provider.load_data('conjugations')
        
        # Default file-based loading
        if not self.data_file.exists():
            return {
                'conjugations': {},
                'metadata': {
                    'created': datetime.now().isoformat(),
                    'description': 'Spanish verb conjugation practice cards',
                    'total_cards': 0
                }
            }
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load conjugation data: {e}")
    
    def save_conjugations(self, data: Dict[str, Any]) -> bool:
        """Save conjugation data"""
        if self.data_provider:
            return self.data_provider.save_data('conjugations', data)
        
        # Update metadata
        data['metadata'] = {
            **data.get('metadata', {}),
            'last_updated': datetime.now().isoformat(),
            'version': '2.0',
            'total_cards': len(data.get('conjugations', {}))
        }
        
        # Default file-based saving
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            raise RuntimeError(f"Failed to save conjugation data: {e}")
    
    def add_conjugations(self, conjugations: List[Dict[str, Any]]) -> bool:
        """Add new conjugations to data"""
        conj_data = self.load_conjugations()
        
        if 'conjugations' not in conj_data:
            conj_data['conjugations'] = {}
        
        for conjugation in conjugations:
            card_id = conjugation['CardID']
            conj_data['conjugations'][card_id] = conjugation
        
        return self.save_conjugations(conj_data)
    
    def conjugation_exists(self, card_id: str) -> bool:
        """Check if conjugation already exists"""
        conj_data = self.load_conjugations()
        return card_id in conj_data.get('conjugations', {})
    
    def get_conjugation(self, card_id: str) -> Dict[str, Any]:
        """Get specific conjugation by card ID"""
        conj_data = self.load_conjugations()
        return conj_data.get('conjugations', {}).get(card_id, {})
    
    def list_conjugations(self) -> List[Dict[str, Any]]:
        """List all conjugations"""
        conj_data = self.load_conjugations()
        return list(conj_data.get('conjugations', {}).values())
    
    def remove_conjugation(self, card_id: str) -> bool:
        """Remove a conjugation by card ID"""
        conj_data = self.load_conjugations()
        
        if card_id in conj_data.get('conjugations', {}):
            del conj_data['conjugations'][card_id]
            return self.save_conjugations(conj_data)
        
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about conjugation data"""
        conj_data = self.load_conjugations()
        conjugations = conj_data.get('conjugations', {})
        
        # Analyze verbs, tenses, persons
        verbs = set()
        tenses = set()
        persons = set()
        
        for conjugation in conjugations.values():
            if 'InfinitiveVerb' in conjugation:
                verbs.add(conjugation['InfinitiveVerb'])
            if 'Tense' in conjugation:
                tenses.add(conjugation['Tense'])
            if 'Person' in conjugation:
                persons.add(conjugation['Person'])
        
        return {
            'total_cards': len(conjugations),
            'unique_verbs': len(verbs),
            'tenses_covered': list(tenses),
            'persons_covered': list(persons),
            'verbs': list(verbs)
        }