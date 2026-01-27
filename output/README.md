# Output Directory

Processed results and exported reports are saved here.

## Structure

After running `python src/main.py`, you'll find:

```
output/
├── Study 2/
│   ├── Study_2_subject_metrics.csv
│   └── Study_2_site_metrics.csv
├── Study 17/
│   ├── Study_17_subject_metrics.csv
│   └── Study_17_site_metrics.csv
└── ...
```

## Output Files

### Subject Metrics CSV
Contains calculated metrics for each subject:
- Subject ID, Site ID, Study
- Missing visits/pages percentages
- Open/closed queries
- SDV status
- DQI score
- Risk level
- Clean patient status

### Site Metrics CSV
Contains aggregated site-level metrics:
- Site ID, Study
- Number of subjects
- Total missing visits/pages
- Total open queries
- Performance score
- Average DQI

## Usage

These CSV files can be:
- Imported into Excel for custom analysis
- Shared with study teams
- Used for executive reporting
- Archived for historical tracking

## Notes

- Files are overwritten on each run
- Backup important results before reprocessing
- Original source data is never modified
