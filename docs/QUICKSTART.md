# Quick Start Guide
## Get Up and Running in 5 Minutes

## Prerequisites
- Python 3.9 or higher installed
- Your clinical trial data files (Excel format)

## Step 1: Installation (2 minutes)

```bash
# Navigate to project directory
cd NestTry

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Data Setup (1 minute)

1. Place your data files in the `data/` folder:
   ```
   data/
   ├── Study 2/
   │   ├── CPID_EDC_Metrics.xlsx
   │   ├── Missing_Pages_Report.xlsx
   │   └── SAE_Dashboard.xlsx
   └── Study 17/
       └── ...
   ```

2. **(Optional)** Configure AI features:
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=sk-your-key-here
   ```

## Step 3: Run the Platform (2 minutes)

### Option A: Interactive Dashboard (Recommended)
```bash
streamlit run src/dashboard/app.py
```
Your browser will open automatically to `http://localhost:8501`

### Option B: Command Line Processing
```bash
python src/main.py
```
Results will be saved to `output/` directory

## What to Expect

### On First Run:
1. **Data ingestion**: 10-30 seconds (depends on file size)
2. **Metric calculation**: 5-15 seconds per study
3. **Dashboard loading**: 2-3 seconds

### Dashboard Views:
- **Executive Dashboard**: Portfolio-level overview
- **Study Analysis**: Detailed study metrics
- **AI Insights**: Generative and Agentic AI recommendations

## Verify Installation

### Test Data Ingestion:
```python
python -c "from src.ingestion import DataIngestionEngine; print('✅ Ingestion OK')"
```

### Test Dashboard:
Visit `http://localhost:8501` and you should see:
- Header: "Clinical Trial Intelligence Platform"
- Metrics cards showing study counts
- Interactive charts

## Troubleshooting

### Issue: "No module named 'src'"
**Solution**: Run from project root directory
```bash
cd NestTry
python src/main.py
```

### Issue: "No data found"
**Solution**: Check data folder structure
```bash
ls -R data/
# Should show Study folders with .xlsx files
```

### Issue: Dashboard not loading
**Solution**: Try a different port
```bash
streamlit run src/dashboard/app.py --server.port 8502
```

## Next Steps

1. ✅ Explore the Executive Dashboard
2. ✅ Drill down into individual studies
3. ✅ Review AI-generated insights
4. ✅ Export results for stakeholders

## Need Help?

- **Documentation**: See `docs/USER_GUIDE.md`
- **Architecture**: See `docs/ARCHITECTURE.md`
- **Demo Guide**: See `docs/DEMO_SCRIPT.md`

## Sample Commands

```bash
# Process all data
python src/main.py

# Launch dashboard
streamlit run src/dashboard/app.py

# View logs
tail -f logs/ctip_*.log

# Export results
ls output/
```

## What's Next?

After you're comfortable with the basics:
- Customize DQI weights in `src/config.py`
- Add more studies to `data/`
- Configure AI features with OpenAI API key
- Share dashboard link with team members

---

**Estimated Total Time**: 5 minutes from clone to dashboard 🚀
