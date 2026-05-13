# ===================================================================================
# FILE 1: src/data_processor.py
# ===================================================================================

import pandas as pd
import numpy as np
import re

def _clean_question(text):
    """Strip trailing special chars and normalize Well-being hyphenation."""
    text = str(text).strip()
    text = re.sub(r'[^a-zA-Z0-9\s\.\?\!\"\'\,\;\:\-\(\)]+$', '', text).strip()
    text = text.replace('Wellbeing', 'Well-being').replace('Well being', 'Well-being')
    return text

class SurveyDataProcessor:
    """Processes survey data and calculates all metrics"""
    
    def __init__(self, filepath):
        """Load and parse survey data from Excel"""
        print(f"Loading data from: {filepath}")
        
        self.df = pd.read_excel(filepath, header=None)
        
        # Extract structure — clean both categories and questions
        raw_categories = self.df.iloc[0, 1:].values
        raw_questions = self.df.iloc[1, 1:].values
        self.categories = [_clean_question(c) if pd.notna(c) else c for c in raw_categories]
        self.questions = [_clean_question(q) for q in raw_questions]

        # Get response data
        self.responses = self.df.iloc[2:, :].copy()
        self.responses.columns = ['Role'] + list(raw_questions)
        # Rename columns to match cleaned question names
        rename_map = {raw: clean for raw, clean in zip(raw_questions, self.questions)}
        self.responses.rename(columns=rename_map, inplace=True)
        self.questions = list(self.questions)

        # Remove "Overall Average" row
        self.responses = self.responses[
            self.responses['Role'].astype(str).str.strip() != 'Overall Average'
        ].copy()

        self.responses['Role'] = self.responses['Role'].astype(str).str.strip()
        self.roles = self.responses['Role'].unique().tolist()

        # Map cleaned categories to cleaned questions
        self.category_map = {}
        for raw_cat, clean_cat in zip(raw_categories, self.categories):
            if pd.notna(raw_cat) and clean_cat not in self.category_map:
                mask = [c == raw_cat for c in raw_categories]
                self.category_map[clean_cat] = [self.questions[i] for i, m in enumerate(mask) if m]
        
        print(f"✓ Loaded {len(self.responses)} responses")
        print(f"✓ Roles: {', '.join(self.roles)}")
        print(f"✓ Categories: {', '.join(self.category_map.keys())}")
        print(f"✓ Questions: {len(self.questions)}")
    
    def get_category_questions(self, category):
        """Get all questions for a specific category"""
        return self.category_map.get(category, [])
    
    def calculate_averages(self, questions=None, role=None):
        """Calculate average scores for questions"""
        if role:
            data = self.responses[self.responses['Role'] == role]
        else:
            data = self.responses
        
        if questions is None:
            questions = self.questions
        
        averages = {}
        for question in questions:
            if question in data.columns:
                values = pd.to_numeric(data[question], errors='coerce')
                averages[question] = values.mean()
        
        return averages
    
    def calculate_percent_agree(self, questions=None, role=None):
        """Calculate % of respondents who gave 4 or 5 rating"""
        if role:
            data = self.responses[self.responses['Role'] == role]
        else:
            data = self.responses
        
        if questions is None:
            questions = self.questions
        
        percent_agree = {}
        for question in questions:
            if question in data.columns:
                values = pd.to_numeric(data[question], errors='coerce')
                agree_count = ((values == 4) | (values == 5)).sum()
                total_count = values.notna().sum()
                percent_agree[question] = (agree_count / total_count * 100) if total_count > 0 else 0
        
        return percent_agree
    
    def calculate_distribution(self, question, role=None):
        """Calculate disagree/neutral/agree distribution"""
        if role:
            data = self.responses[self.responses['Role'] == role]
        else:
            data = self.responses
        
        if question not in data.columns:
            return {'disagree': 0, 'neutral': 0, 'agree': 0}
        
        values = pd.to_numeric(data[question], errors='coerce')
        total = values.notna().sum()
        
        if total == 0:
            return {'disagree': 0, 'neutral': 0, 'agree': 0}
        
        disagree = ((values <= 2).sum() / total * 100)
        neutral = ((values == 3).sum() / total * 100)
        agree = ((values >= 4).sum() / total * 100)
        
        return {'disagree': disagree, 'neutral': neutral, 'agree': agree}
    
    def get_all_categories(self):
        """Return list of all categories"""
        return list(self.category_map.keys())

