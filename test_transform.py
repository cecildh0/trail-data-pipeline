"""
Test file for transform.py
Creates a two dataframes sampling the trails and hazards dataframes
then runs transform and sees if the transformed dataframe is cleaned,
formatted, and standardized correctly
"""

import os
import unittest

import pandas as pd

from transform import transform


class TestTransform(unittest.TestCase):
    def test_transform_basic_behavior(self):
        trails_df = pd.DataFrame(
            {
                "Trail Name": ["Test Loop Hike", "Test Out And Back Hike"],
                "Trail Type": ["Loop", "Out-and-back"],
                "Distance": ["2.5 miles", "4.0 miles round trip"],
                "High Point": ["1,200 feet", "900 feet"],
                "Elevation Gain": ["500 feet", "350 feet"],
                "Difficulty": ["Easy", "Moderate"],
                "Seasons": ["All year", "Spring through fall"],
                "Family Friendly": ["Yes", "No"],
                "Backpackable": ["No", "Yes"],
                "Crowded": ["No", "Yes"],
            }
        )

        hazards_df = pd.DataFrame(
            {
                "Name": ["Test Loop Hike", "Test Out And Back Hike"],
                "Rattlesnakes": [0, 1],
                "Ticks": [0, 0],
                "Posionivy": [0, 1],
                "Falling": [0, 0],
            }
        )

        # Run in the project root so transform() writes to the expected path.
        output_path = "data/processed/trails_clean.csv"
        if os.path.exists(output_path):
            os.remove(output_path)

        result_df = transform(trails_df, hazards_df)

        # Length test 
        self.assertEqual(len(result_df), 2)

        # Test expected output columns
        self.assertIn("Hazardous", result_df.columns)
        self.assertIn("Has Rattlesnakes", result_df.columns)
        self.assertIn("Has Poison Ivy", result_df.columns)

        # Makes sure number values are extracted from text correctly
        self.assertEqual(result_df.loc[0, "Distance"], 2.5)
        self.assertEqual(result_df.loc[0, "High Point"], 1200.0)
        self.assertEqual(result_df.loc[1, "Elevation Gain"], 350.0)

        # Hazard standardization checks
        self.assertEqual(result_df.loc[0, "Hazardous"], "No")
        self.assertEqual(result_df.loc[1, "Hazardous"], "Yes")
        self.assertEqual(result_df.loc[1, "Has Rattlesnakes"], "Yes")
        self.assertEqual(result_df.loc[1, "Has Poison Ivy"], "Yes")

        # Transform writes its csv in the right location
        self.assertTrue(os.path.exists(output_path))


if __name__ == "__main__":
    unittest.main()
