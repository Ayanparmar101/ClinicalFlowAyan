"""
Simple test to verify installation and basic functionality
"""
import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from src.ingestion import DataIngestionEngine
        print("✅ Ingestion module OK")
    except ImportError as e:
        print(f"❌ Ingestion module failed: {e}")
        return False
    
    try:
        from src.harmonization import CanonicalDataModel
        print("✅ Harmonization module OK")
    except ImportError as e:
        print(f"❌ Harmonization module failed: {e}")
        return False
    
    try:
        from src.metrics import MetricsEngine, DataQualityIndex
        print("✅ Metrics module OK")
    except ImportError as e:
        print(f"❌ Metrics module failed: {e}")
        return False
    
    try:
        from src.intelligence import RiskIntelligence
        print("✅ Intelligence module OK")
    except ImportError as e:
        print(f"❌ Intelligence module failed: {e}")
        return False
    
    try:
        from src.ai import GenerativeAI, CRAAgent, DataQualityAgent, TrialManagerAgent
        print("✅ AI module OK")
    except ImportError as e:
        print(f"❌ AI module failed: {e}")
        return False
    
    return True


def test_dependencies():
    """Test that required packages are installed"""
    print("\nTesting dependencies...")
    
    required_packages = [
        'pandas',
        'numpy',
        'streamlit',
        'plotly',
        'openpyxl',
        'loguru'
    ]
    
    all_ok = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} OK")
        except ImportError:
            print(f"❌ {package} missing")
            all_ok = False
    
    return all_ok


def test_directories():
    """Test that required directories exist"""
    print("\nTesting directory structure...")
    
    base_dir = Path(__file__).parent
    required_dirs = [
        base_dir / "src",
        base_dir / "data",
        base_dir / "output",
        base_dir / "logs",
        base_dir / "docs"
    ]
    
    all_ok = True
    for directory in required_dirs:
        if directory.exists():
            print(f"✅ {directory.name}/ exists")
        else:
            print(f"❌ {directory.name}/ missing")
            all_ok = False
    
    return all_ok


def main():
    """Run all tests"""
    print("="*60)
    print("Clinical Trial Intelligence Platform - Installation Test")
    print("="*60)
    
    results = []
    
    # Test imports
    results.append(("Module imports", test_imports()))
    
    # Test dependencies
    results.append(("Dependencies", test_dependencies()))
    
    # Test directories
    results.append(("Directory structure", test_directories()))
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n🎉 All tests passed! System is ready.")
        print("\nNext steps:")
        print("1. Place data files in data/ folder")
        print("2. Run: python src/main.py")
        print("   OR")
        print("   Run: streamlit run src/dashboard/app.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\nTry:")
        print("1. pip install -r requirements.txt")
        print("2. Ensure you're in the project root directory")
        return 1


if __name__ == "__main__":
    sys.exit(main())
