import unittest
import pandas as pd
import numpy as np

# Import functions to test
from src.data.normalizers import clean_text, parse_skills, normalize_skill_name, normalize_difficulty
from src.data.cleaners import clean_career_interests, clean_career_transferable, clean_skill_dependencies

class TestKnowledgeBasePipeline(unittest.TestCase):
    
    def test_clean_text(self):
        self.assertEqual(clean_text("  machine   learning  "), "machine learning")
        self.assertEqual(clean_text(""), "")
        self.assertEqual(clean_text(None), "")
        self.assertEqual(clean_text("   "), "")
        
    def test_parse_skills_coursera(self):
        skills_str = "Drama  Comedy  film  unix shells"
        parsed = parse_skills(skills_str, source="coursera")
        self.assertEqual(parsed, ["Drama", "Comedy", "film", "unix shells"])
        
    def test_parse_skills_comma(self):
        skills_str = "Python, Pandas; Machine Learning | Deep Learning"
        parsed = parse_skills(skills_str)
        self.assertEqual(parsed, ["Python", "Pandas", "Machine Learning", "Deep Learning"])
        
    def test_normalize_difficulty(self):
        self.assertEqual(normalize_difficulty("beginner"), "Beginner")
        self.assertEqual(normalize_difficulty("Mixed"), "Intermediate")
        self.assertEqual(normalize_difficulty("not calibrated"), "Not Calibrated")
        self.assertEqual(normalize_difficulty("conversant"), "Conversant")
        self.assertEqual(normalize_difficulty(""), "Not Calibrated")
        self.assertEqual(normalize_difficulty(None), "Not Calibrated")
        
    def test_normalize_skill_name_alias(self):
        display, norm = normalize_skill_name("ml")
        self.assertEqual(display, "Machine Learning")
        self.assertEqual(norm, "machine learning")
        
    def test_normalize_skill_name_casing(self):
        display, norm = normalize_skill_name("sql")
        self.assertEqual(display, "SQL")
        self.assertEqual(norm, "sql")
        
        display, norm = normalize_skill_name("machine learning")
        self.assertEqual(display, "Machine Learning")
        self.assertEqual(norm, "machine learning")
        
    def test_clean_career_interests_shift(self):
        # Create a mock dataframe with shifted columns
        data = {
            "career\\_id": ["CAR038"],
            "career\\_title": ["Generative AI Engineer"],
            "career_domain": ["Artificial Intelligence"],
            "interest\\_type": ["Investigative"],
            "interest\\_score": [4.8],
            "interest\\_description": ["Requires researching advanced neural network architectures like transformers."],
            "career\\_description": ["Generative AI Engineers build models capable of generating text"],
            "Unnamed: 7": ["images"],
            "Unnamed: 8": ["or code."]
        }
        df = pd.DataFrame(data)
        cleaned_df = clean_career_interests(df)
        
        self.assertNotIn("Unnamed: 7", cleaned_df.columns)
        self.assertNotIn("Unnamed: 8", cleaned_df.columns)
        self.assertEqual(cleaned_df.iloc[0]["career_description"], "Generative AI Engineers build models capable of generating text,images,or code.")

if __name__ == '__main__':
    unittest.main()
