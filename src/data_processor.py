# ===================================================================================
# FILE 1: src/data_processor.py
# ===================================================================================

import pandas as pd
import numpy as np
import re

def _clean_question(text):
    """Strip trailing special chars and normalize Well-being hyphenation."""
    if pd.isna(text):
        return ""
    text = str(text).strip()
    text = re.sub(r'[^a-zA-Z0-9\s\.\?\!\"\'\,\;\:\-\(\)]+$', '', text).strip()
    text = text.replace('Wellbeing', 'Well-being').replace('Well being', 'Well-being')
    return text or "Unnamed Question"


def _make_unique_labels(labels):
    """Ensure each label is unique to avoid duplicate DataFrame columns."""
    seen = {}
    unique = []
    for label in labels:
        base = label or "Unnamed Question"
        count = seen.get(base, 0) + 1
        seen[base] = count
        unique.append(base if count == 1 else f"{base} [{count}]")
    return unique

class SurveyDataProcessor:
    """Processes survey data and calculates all metrics"""

    CATEGORY_ORDER = [
        "Communication",
        "Inspiration",
        "Performance",
        "Culture",
        "Well-being",
    ]
    
    def __init__(self, filepath):
        """Load and parse survey data from Excel"""
        print(f"Loading data from: {filepath}")
        
        self.df = pd.read_excel(filepath, header=None)
        
        # Extract structure — clean both categories and questions
        raw_categories = self.df.iloc[0, 1:].values
        raw_questions = self.df.iloc[1, 1:].values
        self.categories = [_clean_question(c) if pd.notna(c) else c for c in raw_categories]
        cleaned_questions = [_clean_question(q) for q in raw_questions]
        self.questions = _make_unique_labels(cleaned_questions)

        # Get response data
        self.responses = self.df.iloc[2:, :].copy()
        # Use unique cleaned questions directly as column names.
        self.responses.columns = ['Role'] + list(self.questions)

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

    def _get_numeric_series(self, data, question):
        """Return a numeric Series for a question, even if duplicate columns exist."""
        if question not in data.columns:
            return None

        values = data[question]

        # Defensive handling in case duplicate columns still slip through.
        if isinstance(values, pd.DataFrame):
            return values.apply(pd.to_numeric, errors='coerce').mean(axis=1, skipna=True)

        return pd.to_numeric(values, errors='coerce')
    
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
            values = self._get_numeric_series(data, question)
            if values is not None:
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
            values = self._get_numeric_series(data, question)
            if values is not None:
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
        
        values = self._get_numeric_series(data, question)
        if values is None:
            return {'disagree': 0, 'neutral': 0, 'agree': 0}
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

    def get_ordered_categories(self):
        """Return categories in the preferred report order."""
        categories = self.get_all_categories()
        order_lookup = {name.lower(): idx for idx, name in enumerate(self.CATEGORY_ORDER)}

        def _key(category):
            idx = order_lookup.get(str(category).lower())
            return (idx if idx is not None else 999, str(category))

        return sorted(categories, key=_key)

    def get_ordered_roles(self):
        """Return roles in preferred legend/report order: SLT, Director, Team Member."""
        roles = list(self.roles)

        def _rank(role):
            name = str(role).lower()
            if "slt" in name:
                return 0
            if "director" in name or "direct manager" in name or "manager" in name:
                return 1
            if "team" in name:
                return 2
            return 999

        return sorted(roles, key=lambda r: (_rank(r), str(r)))
