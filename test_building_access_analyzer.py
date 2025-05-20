#!/usr/bin/env python3
"""
Tests for the Building Access Control System Analyzer
"""

import os
import csv
import unittest
import tempfile
from building_access_analyzer import BuildingAccessAnalyzer

class TestBuildingAccessAnalyzer(unittest.TestCase):
    def setUp(self):
        """Set up test environment with a temporary test data file."""
        # Create a temporary file for test data
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_data_file = os.path.join(self.temp_dir.name, "test_data.csv")
        
        # Create test data with consistent UnitID for each CardFirstName (unit number)
        test_data = [
            {
                "UnitID": "A101", 
                "CardFirstName": "unit101", 
                "CardLastName": "unit101 resident", 
                "CardBatch": "210", 
                "CardNumber": "54321",
                "AccessTimestamp": "2023-05-15T08:30:00"
            },
            {
                "UnitID": "B102", 
                "CardFirstName": "unit102", 
                "CardLastName": "unit102 resident", 
                "CardBatch": "220", 
                "CardNumber": "65432",
                "AccessTimestamp": "2023-05-15T09:15:00"
            },
            # Another record for unit102 with same UnitID but accessing a different door
            {
                "UnitID": "B102", 
                "CardFirstName": "unit102", 
                "CardLastName": "unit102 resident", 
                "CardBatch": "220", 
                "CardNumber": "65432",
                "AccessTimestamp": "2023-05-15T09:30:00"
            },
            # Another record for unit102 with same UnitID but accessing a different door
            {
                "UnitID": "B102", 
                "CardFirstName": "unit102", 
                "CardLastName": "unit102 resident", 
                "CardBatch": "220", 
                "CardNumber": "65432",
                "AccessTimestamp": "2023-05-15T18:45:00"
            },
            {
                "UnitID": "C103", 
                "CardFirstName": "unit103", 
                "CardLastName": "unit103 resident", 
                "CardBatch": "230", 
                "CardNumber": "76543",
                "AccessTimestamp": "2023-05-15T12:10:00"
            },
            # First fob for unit104
            {
                "UnitID": "D104", 
                "CardFirstName": "unit104", 
                "CardLastName": "unit104 resident", 
                "CardBatch": "240", 
                "CardNumber": "87654",
                "AccessTimestamp": "2023-05-15T14:20:00"
            },
            # Second fob for unit104 (same UnitID but different fob)
            {
                "UnitID": "D104", 
                "CardFirstName": "unit104", 
                "CardLastName": "unit104 resident", 
                "CardBatch": "250", 
                "CardNumber": "98765",
                "AccessTimestamp": "2023-05-15T14:25:00"
            }
        ]
        
        # Write test data to CSV file
        with open(self.test_data_file, 'w', newline='') as file:
            fieldnames = ["UnitID", "CardFirstName", "CardLastName", "CardBatch", "CardNumber", "AccessTimestamp"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(test_data)
        
        # Create a temporary output directory
        self.output_dir = os.path.join(self.temp_dir.name, "reports")
        os.makedirs(self.output_dir, exist_ok=True)
        self.output_file = os.path.join(self.output_dir, "test_report.csv")
        
        # Initialize the analyzer with test data
        self.analyzer = BuildingAccessAnalyzer(self.test_data_file)
    
    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()
    
    def test_load_data(self):
        """Test that data is loaded correctly."""
        self.assertEqual(len(self.analyzer.data), 7)  # Updated to match new test data count
        self.assertEqual(self.analyzer.data[0]["CardFirstName"], "unit101")
        self.assertEqual(self.analyzer.data[1]["CardFirstName"], "unit102")
    
    def test_generate_unit_fob_report(self):
        """Test that the unit fob report is generated correctly."""
        # Generate the report
        report_content = self.analyzer.generate_unit_fob_report(self.output_file)
        
        # Check that the file was created
        self.assertTrue(os.path.exists(self.output_file))
        
        # Check the content of the report
        expected_lines = [
            "Unit Number (First Name),Fob IDs (CardBatch-CardNumber)",
            "unit101,210-54321",
            "unit102,220-65432",
            "unit103,230-76543",
            "unit104,240-87654; 250-98765"  # unit104 has two fobs
        ]
        
        # Read the actual content
        with open(self.output_file, 'r') as file:
            actual_lines = [line.strip() for line in file.readlines()]
        
        # Compare expected vs actual
        self.assertEqual(len(actual_lines), len(expected_lines))
        for expected, actual in zip(expected_lines, actual_lines):
            self.assertEqual(expected, actual)
        
        # Also check the returned content
        report_lines = report_content.strip().split('\n')
        self.assertEqual(len(report_lines), len(expected_lines))
        for expected, actual in zip(expected_lines, report_lines):
            self.assertEqual(expected, actual)
    
    def test_multiple_fobs_per_unit(self):
        """Test that the analyzer correctly identifies units with multiple fobs."""
        # Generate the report
        report_content = self.analyzer.generate_unit_fob_report(self.output_file)
        
        # Parse the report to check for multiple fobs
        units_with_multiple_fobs = {}
        
        # Skip the header line
        for line in report_content.strip().split('\n')[1:]:
            unit, fobs_str = line.split(',', 1)
            fobs = fobs_str.split('; ')
            if len(fobs) > 1:
                units_with_multiple_fobs[unit] = fobs
        
        # Verify that unit104 has multiple fobs
        self.assertIn('unit104', units_with_multiple_fobs)
        self.assertEqual(len(units_with_multiple_fobs['unit104']), 2)
        self.assertIn('240-87654', units_with_multiple_fobs['unit104'])
        self.assertIn('250-98765', units_with_multiple_fobs['unit104'])
        
        # Verify that other units don't have multiple fobs
        self.assertNotIn('unit101', units_with_multiple_fobs)
        self.assertNotIn('unit102', units_with_multiple_fobs)
        self.assertNotIn('unit103', units_with_multiple_fobs)
        
        # Verify the consistency between UnitID and CardFirstName
        unit_to_unitid = {}
        for record in self.analyzer.data:
            unit = record["CardFirstName"]
            unitid = record["UnitID"]
            if unit in unit_to_unitid:
                # Check that the UnitID is consistent for the same unit
                self.assertEqual(unit_to_unitid[unit], unitid, 
                                f"UnitID mismatch for {unit}: {unit_to_unitid[unit]} vs {unitid}")
            else:
                unit_to_unitid[unit] = unitid
    
    def test_empty_data(self):
        """Test that the analyzer handles empty data gracefully."""
        # Create an empty data file
        empty_data_file = os.path.join(self.temp_dir.name, "empty_data.csv")
        with open(empty_data_file, 'w', newline='') as file:
            fieldnames = ["UnitID", "CardFirstName", "CardLastName", "CardBatch", "CardNumber", "AccessTimestamp"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            # No rows written - empty data
        
        # Initialize analyzer with empty data
        empty_analyzer = BuildingAccessAnalyzer(empty_data_file)
        
        # Check that data is empty but initialized
        self.assertEqual(len(empty_analyzer.data), 0)
        
        # Generate report with empty data
        empty_output_file = os.path.join(self.output_dir, "empty_report.csv")
        report_content = empty_analyzer.generate_unit_fob_report(empty_output_file)
        
        # Check that the file was created
        self.assertTrue(os.path.exists(empty_output_file))
        
        # Check that the report only contains the header
        expected_lines = ["Unit Number (First Name),Fob IDs (CardBatch-CardNumber)"]
        
        # Read the actual content
        with open(empty_output_file, 'r') as file:
            actual_lines = [line.strip() for line in file.readlines()]
        
        self.assertEqual(len(actual_lines), len(expected_lines))
        self.assertEqual(actual_lines[0], expected_lines[0])
    
    def test_malformed_data(self):
        """Test that the analyzer handles malformed data gracefully."""
        # Create a file with malformed data (missing fields)
        malformed_data_file = os.path.join(self.temp_dir.name, "malformed_data.csv")
        with open(malformed_data_file, 'w', newline='') as file:
            fieldnames = ["UnitID", "CardFirstName", "CardLastName", "CardBatch", "CardNumber", "AccessTimestamp"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            # Write some rows with missing data
            writer.writerow({
                "UnitID": "A101", 
                "CardFirstName": "unit101", 
                "CardLastName": "unit101 resident", 
                # Missing CardBatch
                "CardNumber": "54321",
                "AccessTimestamp": "2023-05-15T08:30:00"
            })
            writer.writerow({
                "UnitID": "B102", 
                "CardFirstName": "unit102", 
                # Missing CardLastName
                "CardBatch": "220", 
                "CardNumber": "65432",
                "AccessTimestamp": "2023-05-15T09:15:00"
            })
            writer.writerow({
                "UnitID": "C103", 
                # Missing CardFirstName
                "CardLastName": "unit103 resident", 
                "CardBatch": "230", 
                "CardNumber": "76543",
                "AccessTimestamp": "2023-05-15T12:10:00"
            })
        
        # Initialize analyzer with malformed data
        malformed_analyzer = BuildingAccessAnalyzer(malformed_data_file)
        
        # Check that data is loaded
        self.assertEqual(len(malformed_analyzer.data), 3)
        
        # Generate report with malformed data
        malformed_output_file = os.path.join(self.output_dir, "malformed_report.csv")
        report_content = malformed_analyzer.generate_unit_fob_report(malformed_output_file)
        
        # Check that the file was created
        self.assertTrue(os.path.exists(malformed_output_file))
        
        # Check the content of the report - should handle missing data gracefully
        # Only unit101 and unit102 should appear (unit103 has no CardFirstName)
        with open(malformed_output_file, 'r') as file:
            actual_lines = [line.strip() for line in file.readlines()]
        
        # Check that unit101 is in the report with a blank or default fob ID
        unit101_line = None
        unit102_line = None
        for line in actual_lines:
            if line.startswith("unit101"):
                unit101_line = line
            elif line.startswith("unit102"):
                unit102_line = line
        
        self.assertIsNotNone(unit101_line, "unit101 should be in the report")
        self.assertIsNotNone(unit102_line, "unit102 should be in the report")
        
        # unit101 should have a fob ID with missing batch
        self.assertIn("-54321", unit101_line)
        
        # unit102 should have a normal fob ID
        self.assertIn("220-65432", unit102_line)
    
    def test_sorting(self):
        """Test that the report is sorted by unit number."""
        # Generate the report
        report_content = self.analyzer.generate_unit_fob_report(self.output_file)
        
        # Parse the report to get unit numbers
        unit_numbers = []
        for line in report_content.strip().split('\n')[1:]:  # Skip header
            unit, _ = line.split(',', 1)
            unit_numbers.append(unit)
        
        # Check that unit numbers are sorted
        sorted_unit_numbers = sorted(unit_numbers)
        self.assertEqual(unit_numbers, sorted_unit_numbers)
    
    def test_generate_busy_time_report(self):
        """Test that the busy time report is generated correctly."""
        # Generate the report
        busy_output_file = os.path.join(self.output_dir, "busy_time_report.csv")
        report_content = self.analyzer.generate_busy_time_report(busy_output_file)
        
        # Check that the file was created
        self.assertTrue(os.path.exists(busy_output_file))
        
        # Check the content of the report
        expected_lines = [
            "Unit Number (First Name),Busiest Time(s) (Hour:Minute)",
            "unit101,8:00",
            "unit102,9:00",
            "unit103,12:00",
            "unit104,14:00"
        ]
        
        # Read the actual content
        with open(busy_output_file, 'r') as file:
            actual_lines = [line.strip() for line in file.readlines()]
        
        # Compare expected vs actual
        self.assertEqual(len(actual_lines), len(expected_lines))
        for expected, actual in zip(expected_lines, actual_lines):
            self.assertEqual(expected, actual)
        
        # Also check the returned content
        report_lines = report_content.strip().split('\n')
        self.assertEqual(len(report_lines), len(expected_lines))
        for expected, actual in zip(expected_lines, report_lines):
            self.assertEqual(expected, actual)
    
    def test_empty_data_busy_time_report(self):
        """Test that the analyzer handles empty data gracefully for busy time report."""
        # Create an empty data file
        empty_data_file = os.path.join(self.temp_dir.name, "empty_data.csv")
        with open(empty_data_file, 'w', newline='') as file:
            fieldnames = ["UnitID", "CardFirstName", "CardLastName", "CardBatch", "CardNumber", "AccessTimestamp"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            # No rows written - empty data
        
        # Initialize analyzer with empty data
        empty_analyzer = BuildingAccessAnalyzer(empty_data_file)
        
        # Generate report with empty data
        empty_output_file = os.path.join(self.output_dir, "empty_busy_report.csv")
        report_content = empty_analyzer.generate_busy_time_report(empty_output_file)
        
        # Check that the file was created
        self.assertTrue(os.path.exists(empty_output_file))
        
        # Check that the report only contains the header
        expected_lines = ["Unit Number (First Name),Busiest Time(s) (Hour:Minute)"]
        
        # Read the actual content
        with open(empty_output_file, 'r') as file:
            actual_lines = [line.strip() for line in file.readlines()]
        
        self.assertEqual(len(actual_lines), len(expected_lines))
        self.assertEqual(actual_lines[0], expected_lines[0])
    
    def test_duplicate_fob_ids(self):
        """Test that duplicate fob IDs for the same unit are handled correctly."""
        # Create test data with duplicate fob IDs for the same unit
        duplicate_data_file = os.path.join(self.temp_dir.name, "duplicate_data.csv")
        with open(duplicate_data_file, 'w', newline='') as file:
            fieldnames = ["UnitID", "CardFirstName", "CardLastName", "CardBatch", "CardNumber", "AccessTimestamp"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            # Write some rows with duplicate fob IDs
            writer.writerow({
                "UnitID": "A101", 
                "CardFirstName": "unit101", 
                "CardLastName": "unit101 resident", 
                "CardBatch": "210", 
                "CardNumber": "54321",
                "AccessTimestamp": "2023-05-15T08:30:00"
            })
            # Duplicate entry for unit101
            writer.writerow({
                "UnitID": "A101", 
                "CardFirstName": "unit101", 
                "CardLastName": "unit101 resident", 
                "CardBatch": "210", 
                "CardNumber": "54321",
                "AccessTimestamp": "2023-05-15T08:45:00"
            })
            # Different unit
            writer.writerow({
                "UnitID": "B102", 
                "CardFirstName": "unit102", 
                "CardLastName": "unit102 resident", 
                "CardBatch": "220", 
                "CardNumber": "65432",
                "AccessTimestamp": "2023-05-15T09:15:00"
            })
        
        # Initialize analyzer with duplicate data
        duplicate_analyzer = BuildingAccessAnalyzer(duplicate_data_file)
        
        # Generate report
        duplicate_output_file = os.path.join(self.output_dir, "duplicate_report.csv")
        report_content = duplicate_analyzer.generate_unit_fob_report(duplicate_output_file)
        
        # Parse the report to check for duplicate handling
        unit_to_fobs = {}
        for line in report_content.strip().split('\n')[1:]:  # Skip header
            unit, fobs_str = line.split(',', 1)
            fobs = fobs_str.split('; ')
            unit_to_fobs[unit] = fobs
        
        # Check that unit101 has only one fob ID (duplicates should be removed)
        self.assertEqual(len(unit_to_fobs["unit101"]), 1)
        self.assertEqual(unit_to_fobs["unit101"][0], "210-54321")

    def test_multiple_busy_hours(self):
        """Test that the analyzer correctly identifies multiple busy hours when tied."""
        # Create a file with multiple busy hours for the same unit
        multiple_busy_file = os.path.join(self.temp_dir.name, "multiple_busy.csv")
        with open(multiple_busy_file, 'w', newline='') as file:
            fieldnames = ["UnitID", "CardFirstName", "CardLastName", "CardBatch", "CardNumber", "AccessTimestamp"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            # Write data with multiple busy hours for unit101
            writer.writerow({
                "UnitID": "A101", 
                "CardFirstName": "unit101", 
                "CardLastName": "unit101 resident", 
                "CardBatch": "210", 
                "CardNumber": "54321",
                "AccessTimestamp": "2023-05-15T08:30:00"
            })
            writer.writerow({
                "UnitID": "A101", 
                "CardFirstName": "unit101", 
                "CardLastName": "unit101 resident", 
                "CardBatch": "210", 
                "CardNumber": "54321",
                "AccessTimestamp": "2023-05-15T08:45:00"
            })
            # Same count for another hour (2 entries at hour 14)
            writer.writerow({
                "UnitID": "A101", 
                "CardFirstName": "unit101", 
                "CardLastName": "unit101 resident", 
                "CardBatch": "210", 
                "CardNumber": "54321",
                "AccessTimestamp": "2023-05-15T14:15:00"
            })
            writer.writerow({
                "UnitID": "A101", 
                "CardFirstName": "unit101", 
                "CardLastName": "unit101 resident", 
                "CardBatch": "210", 
                "CardNumber": "54321",
                "AccessTimestamp": "2023-05-15T14:45:00"
            })
        
        # Initialize analyzer with this data
        multiple_busy_analyzer = BuildingAccessAnalyzer(multiple_busy_file)
        
        # Generate report
        multiple_busy_output = os.path.join(self.output_dir, "multiple_busy_report.csv")
        report_content = multiple_busy_analyzer.generate_busy_time_report(multiple_busy_output)
        
        # Parse the report
        unit101_busy_times = None
        for line in report_content.strip().split('\n'):
            if line.startswith("unit101"):
                unit101_busy_times = line.split(',')[1]
                break
        
        # Check that both hours are reported
        self.assertIsNotNone(unit101_busy_times, "unit101 should be in the report")
        self.assertIn("8:00", unit101_busy_times)
        self.assertIn("14:00", unit101_busy_times)
        
        # The hours should be reported in order
        self.assertEqual(unit101_busy_times, "8:00; 14:00")


if __name__ == "__main__":
    unittest.main()