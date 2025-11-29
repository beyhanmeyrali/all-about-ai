import os
import subprocess
import sys
import time

def run_test(script_name):
    print(f"\n{'='*80}")
    print(f"TESTING: {script_name}")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    try:
        # Run the script
        # Use sys.executable to ensure we use the same python interpreter
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout per script
        )
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"[PASS] SUCCESS ({duration:.2f}s)")
            # Print last few lines of output to verify it actually ran
            lines = result.stdout.strip().split('\n')
            print("Last 5 lines of output:")
            for line in lines[-5:]:
                print(f"  {line}")
            return True
        else:
            print(f"[FAIL] FAILED ({duration:.2f}s)")
            print("Error output:")
            print(result.stderr)
            print("Standard output:")
            print(result.stdout)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"[FAIL] TIMEOUT ({time.time() - start_time:.2f}s)")
        return False
    except Exception as e:
        print(f"[FAIL] ERROR: {str(e)}")
        return False

def main():
    # Get all python files starting with digits
    scripts = [f for f in os.listdir('.') if f.endswith('.py') and f[0].isdigit()]
    scripts.sort()
    
    print(f"Found {len(scripts)} scripts to test: {scripts}")
    
    passed = 0
    failed = 0
    
    for script in scripts:
        if run_test(script):
            passed += 1
        else:
            failed += 1
            
    print(f"\n{'='*80}")
    print(f"SUMMARY: {passed} passed, {failed} failed")
    print(f"{'='*80}")
    
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
