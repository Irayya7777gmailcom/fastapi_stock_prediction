"""
Test script for uploading Excel files to the API
"""
import requests
import sys
from pathlib import Path

def upload_files(hist_path: str, live_path: str, api_url: str = "http://localhost:8000"):
    """
    Upload Historical.xlsx and Live.xlsx to the API
    
    Args:
        hist_path: Path to Historical.xlsx
        live_path: Path to Live.xlsx
        api_url: Base API URL (default: http://localhost:8000)
    """
    hist_file = Path(hist_path)
    live_file = Path(live_path)
    
    # Check if files exist
    if not hist_file.exists():
        print(f"❌ Historical file not found: {hist_path}")
        return False
    
    if not live_file.exists():
        print(f"❌ Live file not found: {live_path}")
        return False
    
    print(f"📤 Uploading files...")
    print(f"   Historical: {hist_file.name} ({hist_file.stat().st_size / 1024:.1f} KB)")
    print(f"   Live: {live_file.name} ({live_file.stat().st_size / 1024:.1f} KB)")
    
    try:
        # Prepare files
        files = {
            'historical_file': open(hist_path, 'rb'),
            'live_file': open(live_path, 'rb')
        }
        
        # Upload
        upload_url = f"{api_url}/api/v1/upload/excel-files"
        print(f"\n🚀 Uploading to: {upload_url}")
        
        response = requests.post(upload_url, files=files, timeout=300)
        
        # Close files
        files['historical_file'].close()
        files['live_file'].close()
        
        # Check response
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Upload successful!")
            print(f"\n📊 Processing Results:")
            result = data.get('processing_result', {})
            print(f"   Stocks processed: {result.get('stocks_processed', 0)}/{result.get('total_stocks', 0)}")
            
            errors = result.get('errors', [])
            if errors:
                print(f"\n⚠️  Errors ({len(errors)} stocks):")
                for err in errors[:5]:  # Show first 5 errors
                    print(f"   - {err}")
            else:
                print(f"   No errors!")
            
            return True
        else:
            print(f"\n❌ Upload failed!")
            print(f"   Status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection failed!")
        print(f"   Make sure the server is running at: {api_url}")
        print(f"   Start server with: python main.py")
        return False
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False


def check_status(api_url: str = "http://localhost:8000"):
    """Check processing status"""
    try:
        status_url = f"{api_url}/api/v1/upload/status"
        response = requests.get(status_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n📈 Last Processing Status:")
            
            if data.get('status') == 'no_data':
                print(f"   No processing performed yet")
            else:
                last_proc = data.get('last_processing', {})
                print(f"   Stocks processed: {last_proc.get('stocks_processed', 0)}")
                print(f"   Status: {last_proc.get('status', 'unknown')}")
                print(f"   Time: {last_proc.get('processed_at', 'unknown')}")
                print(f"   Message: {last_proc.get('message', '')}")
        else:
            print(f"   Status check failed: {response.status_code}")
    
    except Exception as e:
        print(f"   Error checking status: {str(e)}")


if __name__ == "__main__":
    print("=" * 60)
    print("Excel File Upload Test Script")
    print("=" * 60)
    
    if len(sys.argv) < 3:
        print("\n📝 Usage:")
        print(f"   python {sys.argv[0]} <historical.xlsx> <live.xlsx> [api_url]")
        print("\nExample:")
        print(f"   python {sys.argv[0]} Historical.xlsx Live.xlsx")
        print(f"   python {sys.argv[0]} Historical.xlsx Live.xlsx http://localhost:8000")
        sys.exit(1)
    
    hist_path = sys.argv[1]
    live_path = sys.argv[2]
    api_url = sys.argv[3] if len(sys.argv) > 3 else "http://localhost:8000"
    
    # Upload files
    success = upload_files(hist_path, live_path, api_url)
    
    if success:
        print("\n" + "=" * 60)
        check_status(api_url)
        print("=" * 60)
        print(f"\n🎉 Done! Access dashboard at: {api_url}")
    else:
        sys.exit(1)
