#!/usr/bin/env python3
"""
Building Access Control System Analyzer

This application reads building access control system logs and generates various reports.
"""

import csv
import os
import argparse
from datetime import datetime
from collections import defaultdict

class BuildingAccessAnalyzer:
    def __init__(self, data_file):
        """Initialize the analyzer with the data file path."""
        self.data_file = data_file
        self.data = []
        self.load_data()
    
    def load_data(self):
        """Load data from the CSV file."""
        try:
            with open(self.data_file, 'r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    self.data.append(row)
            print(f"Successfully loaded {len(self.data)} records from {self.data_file}")
        except Exception as e:
            print(f"Error loading data: {e}")
    
    def generate_busy_time_report(self, output_file=None):
        """
        Generate a report showing the busiest hour for each unit based on access patterns.
        
        Args:
            output_file: Optional file path to save the report. If None, prints to console.
            
        Returns:
            str: The report content as a string
        """
        unit_hour_counts = defaultdict(lambda: defaultdict(int))
        
        # Process each record
        for record in self.data:
            # Extract unit number and timestamp
            unit_number = record.get('CardFirstName', '').strip()
            timestamp_str = record.get('AccessTimestamp', '').strip()
            
            if unit_number and timestamp_str:
                try:
                    # Parse the timestamp to extract the hour
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S')
                    hour = timestamp.hour
                    
                    # Increment the count for this unit and hour
                    unit_hour_counts[unit_number][hour] += 1
                except ValueError:
                    # Skip records with invalid timestamp format
                    continue
        
        # Find the busiest hour for each unit
        unit_busy_times = {}
        for unit, hour_counts in unit_hour_counts.items():
            if hour_counts:  # Only process units with valid data
                # Find the hour(s) with the maximum count
                max_count = max(hour_counts.values())
                busiest_hours = [hour for hour, count in hour_counts.items() if count == max_count]
                
                # Sort by hour for consistent results
                busiest_hours.sort()
                
                # Format as comma-separated string if multiple hours have the same count
                busiest_time = '; '.join(f"{hour}:00" for hour in busiest_hours)
                unit_busy_times[unit] = busiest_time
        
        # Generate report
        report_lines = ["Unit Number (First Name),Busiest Time(s) (Hour:Minute)"]
        for unit, busiest_time in sorted(unit_busy_times.items()):
            report_lines.append(f"{unit},{busiest_time}")
        
        report_content = "\n".join(report_lines)
        
        # Output the report
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w') as file:
                file.write(report_content)
            print(f"Busy time report saved to {output_file}")
        else:
            print("\nBusiest Time Report:")
            print(report_content)
        
        return report_content

    def generate_unit_fob_report(self, output_file=None):
        """
        Generate a report showing which unit numbers (first names) used which fobs.
        
        Args:
            output_file: Optional file path to save the report. If None, prints to console.
        """
        unit_fobs = defaultdict(set)
        
        # Process each record
        for record in self.data:
            # Extract unit number (first name) and fob info
            unit_number = record.get('CardFirstName', '').strip()
            card_batch = record.get('CardBatch', '').strip()
            card_number = record.get('CardNumber', '').strip()
            
            # Create fob identifier
            fob_id = f"{card_batch}-{card_number}"
            
            # Add to the mapping
            if unit_number:
                unit_fobs[unit_number].add(fob_id)
        
        # Generate report
        report_lines = ["Unit Number (First Name),Fob IDs (CardBatch-CardNumber)"]
        for unit, fobs in sorted(unit_fobs.items()):
            fobs_str = "; ".join(sorted(fobs))
            report_lines.append(f"{unit},{fobs_str}")
        
        report_content = "\n".join(report_lines)
        
        # Output the report
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w') as file:
                file.write(report_content)
            print(f"Report saved to {output_file}")
        else:
            print("\nUnit to Fob Report:")
            print(report_content)
        
        return report_content

def main():
    """Main function to run the application."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Building Access Control System Analyzer')
    parser.add_argument('-f', '--file', default="sampleData.csv", 
                        help='Path to the CSV data file (default: sampleData.csv)')
    args = parser.parse_args()
    
    # File paths
    data_file = args.file
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    # Initialize analyzer
    analyzer = BuildingAccessAnalyzer(data_file)
    
    # Generate unit to fob report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(reports_dir, f"unit_fob_report_{timestamp}.csv")
    analyzer.generate_unit_fob_report(output_file)
    
    # Generate busy time report
    busy_time_output_file = os.path.join(reports_dir, f"busy_time_report_{timestamp}.csv")
    analyzer.generate_busy_time_report(busy_time_output_file)
    
    # Also print to console
    analyzer.generate_unit_fob_report()

if __name__ == "__main__":
    main()