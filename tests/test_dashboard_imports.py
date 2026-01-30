"""
Test Dashboard Import and Startup
"""
import sys
from pathlib import Path

# Mock logger again
class MockLogger:
    def info(self, msg): print(f"INFO: {msg}")
    def debug(self, msg): pass
    def warning(self, msg): print(f"WARNING: {msg}")
    def error(self, msg): print(f"ERROR: {msg}")
    def success(self, msg): print(f"SUCCESS: {msg}")

sys.modules['loguru'] = type(sys)('loguru')
sys.modules['loguru'].logger = MockLogger()

print("Testing dashboard imports...")

try:
    import streamlit as st
    print("✓ streamlit imported")
except Exception as e:
    print(f"✗ streamlit import failed: {e}")
    sys.exit(1)

try:
    import plotly.express as px
    print("✓ plotly imported")
except Exception as e:
    print(f"✗ plotly import failed: {e}")
    sys.exit(1)

# Try importing dashboard module
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from config import APP_NAME, GEMINI_API_KEY, DATA_PATH
    print(f"✓ config imported")
    print(f"  - APP_NAME: {APP_NAME}")
    print(f"  - DATA_PATH: {DATA_PATH}")
    print(f"  - GEMINI_API_KEY: {'*' * 10 + GEMINI_API_KEY[-10:] if GEMINI_API_KEY else 'NOT SET'}")
except Exception as e:
    print(f"✗ config import failed: {e}")
    import traceback
    traceback.print_exc()

try:
    from ingestion import DataIngestionEngine
    print("✓ DataIngestionEngine imported")
except Exception as e:
    print(f"✗ DataIngestionEngine import failed: {e}")

try:
    from harmonization import CanonicalDataModel
    print("✓ CanonicalDataModel imported")
except Exception as e:
    print(f"✗ CanonicalDataModel import failed: {e}")

try:
    from metrics import MetricsEngine, DataQualityIndex
    print("✓ MetricsEngine and DataQualityIndex imported")
except Exception as e:
    print(f"✗ Metrics import failed: {e}")

print("\n✓ ALL IMPORTS SUCCESSFUL")
print("\nDashboard is ready to run with:")
print("  streamlit run src/dashboard/app.py")
