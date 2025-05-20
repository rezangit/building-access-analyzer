# Building Access Analyzer

A Python application that analyzes building access control system logs and generates reports about unit access patterns.

## Description

The Building Access Analyzer processes CSV data from building access control systems and generates reports showing which units (apartments) have which access fobs assigned to them and when they are most active. This helps building management keep track of access credentials, ensure proper security protocols, and understand access patterns.

## Features

- Loads and processes building access data from CSV files
- Generates reports showing which units have which fobs assigned
- Analyzes access patterns to identify busy times for each unit
- Handles multiple fobs per unit
- Sorts output by unit number for easy reference
- Saves reports to CSV files with timestamps
- Accepts custom data file path via command line

## Requirements

- Python 3.6 or higher

## Installation

Clone the repository:

```bash
git clone https://github.com/rezangit/building-access-analyzer.git
cd building-access-analyzer
```

No additional dependencies are required as the application uses only Python standard libraries.

## Usage

1. Place your access control data in a CSV file in the project directory. The CSV should have the following columns:
   - UnitID
   - CardFirstName (used as the unit number)
   - CardLastName
   - CardBatch
   - CardNumber

2. Run the analyzer:

```bash
# Using the default data file (sampleData.csv)
python3 building_access_analyzer.py

# OR specify a custom data file
python3 building_access_analyzer.py -f last3month.csv
python3 building_access_analyzer.py --file path/to/your/data.csv
```

3. The application will:
   - Load the data from the specified CSV file (or sampleData.csv by default)
   - Generate a report showing which units have which fobs
   - Generate a report showing the busiest time periods for each unit
   - Save the reports to the `reports` directory with a timestamp
   - Print the unit-fob report to the console

## Command Line Options

| Option | Description |
|--------|-------------|
| `-f FILE`, `--file FILE` | Path to the CSV data file (default: sampleData.csv) |

## Sample Data Format

The input CSV file should have the following format:

```
UnitID,CardFirstName,CardLastName,CardBatch,CardNumber,AccessTimestamp
A101,unit101,unit101 resident,210,54321,2023-05-15T08:30:00
B102,unit102,unit102 resident,220,65432,2023-05-15T09:15:00
```

The `AccessTimestamp` field should be in ISO 8601 format (YYYY-MM-DDTHH:MM:SS).

## Output Format

The application generates two types of reports:

### Unit to Fob Report

```
Unit Number (First Name),Fob IDs (CardBatch-CardNumber)
unit101,210-54321
unit102,220-65432
unit103,230-76543
unit104,240-87654; 250-98765
```

### Busy Time Report

```
Unit Number (First Name),Busiest Time(s) (Hour:Minute)
unit101,8:00
unit102,9:00
unit103,12:00
unit104,14:00
```

If multiple hours have the same maximum count of access events, they will be listed separated by semicolons (e.g., `8:00; 14:00`).

## Testing

The project includes a comprehensive test suite. To run the tests:

```bash
python3 -m unittest test_building_access_analyzer.py
```

The tests cover:
- Basic functionality
- Multiple fobs per unit
- Empty data handling
- Malformed data handling
- Sorting
- Duplicate fob handling
- Busy time analysis
- Multiple busy hours handling

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

- rezangit