import os
import subprocess
import sys
import time

def run_test(script_name):
    print(f"\n{'='*80}")
    print(f"TEST EDİLİYOR: {script_name}")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    try:
        # Betiği çalıştır
        # Aynı python yorumlayıcısını kullandığımızdan emin olmak için sys.executable kullanın
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            timeout=300  # Betik başına 5 dakika zaman aşımı
        )
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"[GEÇTİ] BAŞARILI ({duration:.2f}s)")
            # Gerçekten çalıştığını doğrulamak için çıktının son birkaç satırını yazdırın
            lines = result.stdout.strip().split('\n')
            print("Çıktının son 5 satırı:")
            for line in lines[-5:]:
                print(f"  {line}")
            return True
        else:
            print(f"[KALDI] BAŞARISIZ ({duration:.2f}s)")
            print("Hata çıktısı:")
            print(result.stderr)
            print("Standart çıktı:")
            print(result.stdout)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"[KALDI] ZAMAN AŞIMI ({time.time() - start_time:.2f}s)")
        return False
    except Exception as e:
        print(f"[KALDI] HATA: {str(e)}")
        return False

def main():
    # Rakamlarla başlayan tüm python dosyalarını al
    scripts = [f for f in os.listdir('.') if f.endswith('.py') and f[0].isdigit()]
    scripts.sort()
    
    print(f"Test edilecek {len(scripts)} betik bulundu: {scripts}")
    
    passed = 0
    failed = 0
    
    for script in scripts:
        if run_test(script):
            passed += 1
        else:
            failed += 1
            
    print(f"\n{'='*80}")
    print(f"ÖZET: {passed} geçti, {failed} kaldı")
    print(f"{'='*80}")
    
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
