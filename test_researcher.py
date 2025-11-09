"""
Debug script to test visualization generation independently
Run this from the PROJECT ROOT (not from agents/ folder):
    python test_researcher.py
"""

import os
import sys

# Make sure we're in the project root
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)
sys.path.insert(0, project_root)

print(f"📁 Working directory: {os.getcwd()}")
print(f"📁 Python path: {sys.path[0]}")

from agents.researcher import Researcher

def test_researcher():
    """Test the researcher agent independently"""
    
    print("=" * 60)
    print("🧪 RESEARCHER AGENT TEST")
    print("=" * 60)
    
    # Check data files exist
    yelp_path = "data/Hybrid_Yelp_Restaurant_Sales.csv"
    menu_path = "data/Menu_Sales_Data.csv"
    
    print(f"\n📁 Checking data files...")
    if not os.path.exists(yelp_path):
        print(f"❌ Missing: {yelp_path}")
        return
    if not os.path.exists(menu_path):
        print(f"❌ Missing: {menu_path}")
        return
    
    print(f"✅ Found: {yelp_path}")
    print(f"✅ Found: {menu_path}")
    
    # Create researcher
    print(f"\n🔬 Creating Researcher agent...")
    researcher = Researcher(yelp_path, menu_path)
    
    # Run analysis
    print(f"\n📊 Running analysis...")
    result = researcher.run()
    
    # Check results
    print(f"\n" + "=" * 60)
    print("📋 RESULTS")
    print("=" * 60)
    
    print(f"\n🔑 Facts ({len(result.facts)}):")
    for key, value in result.facts.items():
        print(f"  • {key}: {value}")
    
    print(f"\n📈 Figures ({len(result.figures)}):")
    for fig_path in result.figures:
        abs_path = os.path.abspath(fig_path)
        exists = os.path.exists(abs_path)
        status = "✅" if exists else "❌"
        size = os.path.getsize(abs_path) if exists else 0
        print(f"  {status} {fig_path}")
        print(f"     → Absolute: {abs_path}")
        print(f"     → Exists: {exists}")
        print(f"     → Size: {size:,} bytes")
    
    # Check outputs directory
    print(f"\n📂 Outputs Directory:")
    outputs_dir = "outputs"
    if os.path.exists(outputs_dir):
        files = os.listdir(outputs_dir)
        print(f"  Found {len(files)} files in {outputs_dir}/")
        for f in files:
            full_path = os.path.join(outputs_dir, f)
            size = os.path.getsize(full_path)
            print(f"  • {f} ({size:,} bytes)")
    else:
        print(f"  ❌ Directory does not exist: {outputs_dir}")
    
    print(f"\n" + "=" * 60)
    print("✅ Test Complete!")
    print("=" * 60)
    
    return result

if __name__ == "__main__":
    try:
        test_researcher()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()