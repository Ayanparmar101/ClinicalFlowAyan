# Quick Reference - Clean Codebase Structure

## 📁 Where to Find Things

### Running the Application
```bash
# Dashboard
streamlit run src/dashboard/app.py

# CLI
python src/main.py
```

### Testing
```bash
# All tests
pytest tests/

# Specific test
pytest tests/test_name.py

# With coverage
pytest tests/ --cov=src --cov-report=html
```

### Utilities
```bash
# Run any utility script
python scripts/script_name.py
```

## 📂 Directory Guide

| What you need | Where to look |
|--------------|---------------|
| **Main application code** | `src/` |
| **Clinical ops logic** | `clinical-ops-rt/` |
| **Test files** | `tests/` |
| **Utility scripts** | `scripts/` |
| **Documentation** | `docs/` |
| **Study data** | `data/Study N_CPID_Input Files - Anonymization/` |
| **Generated reports** | `output/` |
| **Application logs** | `logs/` |

## 🔍 Quick File Finder

### Core Application
- Entry point: `src/main.py`
- Dashboard: `src/dashboard/app.py`
- Config: `src/config.py`
- Data loading: `src/ingestion/`
- Metrics: `src/metrics/`
- AI: `src/ai/`

### Clinical Operations
- State management: `clinical-ops-rt/model/`
- Risk metrics: `clinical-ops-rt/metrics/`
- Data loaders: `clinical-ops-rt/ingestion/`
- AI algorithms: `clinical-ops-rt/ai/`

### Documentation
- Architecture: `docs/ARCHITECTURE.md`
- User guide: `docs/USER_GUIDE.md`
- Project structure: `docs/PROJECT_STRUCTURE.md`
- Setup: `docs/QUICKSTART.md`
- API setup: `docs/GEMINI_SETUP.md`

### Configuration
- Environment variables: `.env`
- Python packages: `requirements.txt`
- Git ignore rules: `.gitignore`

## 🚀 Common Tasks

### Adding a New Test
1. Create test file in `tests/test_your_feature.py`
2. Follow naming convention: `test_*.py`
3. Run: `pytest tests/test_your_feature.py`

### Adding a New Script
1. Create script in `scripts/your_script.py`
2. Update `scripts/README.md` with description
3. Run: `python scripts/your_script.py`

### Adding Documentation
1. Create markdown file in `docs/YOUR_TOPIC.md`
2. Link from main `README.md` if needed

### Checking Study Data
- Study files: `data/Study N_CPID_Input Files - Anonymization/`
- Each study has Excel files for different data types

## ⚙️ Development Workflow

1. **Start Development**
   ```bash
   # Activate virtual environment
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

2. **Make Changes**
   - Edit files in `src/` or `clinical-ops-rt/`
   - Add tests in `tests/`

3. **Test Changes**
   ```bash
   pytest tests/
   ```

4. **Run Application**
   ```bash
   streamlit run src/dashboard/app.py
   ```

5. **Check Logs** (if issues)
   - Look in `logs/` directory

## 🛠️ Troubleshooting

### Import Errors
- Ensure you're in project root: `C:\Users\Ayan Parmar\Desktop\NestTry`
- Check virtual environment is activated

### Missing Data
- Check `data/` directory for study folders
- Each study needs proper Excel files

### API Errors
- Check `.env` file has `GEMINI_API_KEY`
- See `docs/GEMINI_API_FIX_GUIDE.md`

### Test Failures
- Run specific test: `pytest tests/test_name.py -v`
- Check logs in `logs/` directory

## 📋 File Naming Conventions

- **Tests**: `test_*.py` in `tests/`
- **Scripts**: `descriptive_name.py` in `scripts/`
- **Docs**: `TITLE_IN_CAPS.md` in `docs/`
- **Source**: `module_name.py` in `src/` or `clinical-ops-rt/`

## ✅ Keep It Clean

**DO:**
- ✓ Put tests in `tests/`
- ✓ Put scripts in `scripts/`
- ✓ Put docs in `docs/`
- ✓ Keep root directory minimal

**DON'T:**
- ✗ Add test files to root
- ✗ Add script files to root
- ✗ Commit `__pycache__/` or `.pyc` files
- ✗ Add large files without updating `.gitignore`

---

**Need more details?** See `docs/PROJECT_STRUCTURE.md` or `CLEANUP_SUMMARY.md`
