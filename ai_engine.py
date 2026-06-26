import numpy as np
import re
from collections import Counter

class AIEngine:
    def __init__(self):
        self.solutions_data = []
        self.keyword_index = {}
    
    def prepare_solutions(self, solutions):
        """Build keyword search index from solutions"""
        self.solutions_data = solutions
        
        for idx, sol in enumerate(solutions):
            # Extract all words from problem and symptoms
            text = f"{sol['problem']} {sol['symptoms']}"
            words = set(re.findall(r'\b\w+\b', text.lower()))
            
            for word in words:
                if len(word) > 2:  # Ignore very short words
                    if word not in self.keyword_index:
                        self.keyword_index[word] = []
                    self.keyword_index[word].append(idx)
        
        print(f"Prepared {len(solutions)} solutions with {len(self.keyword_index)} keywords")
        return True
    
    def find_best_match(self, user_query, top_k=3):
        """Find matching solutions using keyword scoring"""
        if not self.solutions_data:
            return []
        
        # Extract keywords from user query
        query_words = set(re.findall(r'\b\w+\b', user_query.lower()))
        
        # Score each solution based on keyword matches
        scores = np.zeros(len(self.solutions_data))
        
        for word in query_words:
            if len(word) > 2 and word in self.keyword_index:
                for idx in self.keyword_index[word]:
                    scores[idx] += 1
        
        # Get top matches
        top_indices = np.argsort(scores)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                confidence = min(round(float(scores[idx]) / len(query_words) * 100, 2), 95)
                results.append({
                    'solution': self.solutions_data[idx],
                    'confidence': confidence
                })
        
        return results