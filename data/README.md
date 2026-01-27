# Data Directory

Place your clinical trial data files here in the following structure:

```
data/
├── Study 2/
│   ├── CPID_EDC_Metrics.xlsx
│   ├── Missing_Pages_Report.xlsx
│   ├── SAE_Dashboard.xlsx
│   ├── GlobalCodingReport_MedDRA.xlsx
│   ├── GlobalCodingReport_WHODD.xlsx
│   ├── Missing_Lab_Name_and_Missing_Ranges.xlsx
│   ├── Visit_Projection_Tracker.xlsx
│   ├── Inactivated_Form_Folder_Report.xlsx
│   └── Compiled_EDRR.xlsx
├── Study 17/
│   └── (same file types)
└── Study 18/
    └── (same file types)
```

## Supported File Types

- **EDC Metrics**: Files containing "EDC_Metrics" or "CPID"
- **Missing Pages**: Files containing "Missing_Pages"
- **SAE Dashboard**: Files containing "SAE" and "Dashboard"
- **Coding Reports**: Files containing "Coding", "MedDRA", or "WHO"
- **Lab Reports**: Files containing "Lab" and "Missing" or "Range"
- **Visit Projections**: Files containing "Visit_Projection"
- **Inactivated Forms**: Files containing "Inactivated"
- **EDRR**: Files containing "EDRR"

## Notes

- File names are flexible as long as they contain the keywords above
- Both .xlsx and .xls formats are supported
- Data is processed locally and never transmitted externally
- Original files are never modified
