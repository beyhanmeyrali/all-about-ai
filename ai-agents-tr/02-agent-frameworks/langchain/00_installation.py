#!/usr/bin/env python3
"""
Örnek 00: Kurulum & Ayar Doğrulama
==============================================

Bu betik, ortamınızın LangChain için doğru şekilde kurulduğunu doğrular.

Neyi kontrol eder:
- Ollama sunucusu çalışıyor mu
- qwen3:8b modeli mevcut mu
- LangChain ve bağımlılıklar yüklü mü
- Temel LangChain + Ollama entegrasyonu çalışıyor mu

Diğer örneklerden önce bunu İLK OLARAK çalıştırın!

Yazar: Beyhan MEYRALI
"""

import sys
from typing import Dict, Any


class SetupVerifier:
    """
    LangChain + Ollama kurulumunu doğrula.

    Bu sınıf tüm ön koşulları kontrol eder ve yararlı hata mesajları sağlar.
    """

    def __init__(self):
        """Doğrulayıcıyı başlat."""
        self.checks_passed = []
        self.checks_failed = []

    def check_imports(self) -> bool:
        """Gerekli tüm paketlerin yüklü olup olmadığını kontrol et."""
        print("\n[KONTROL 1] Python paketleri doğrulanıyor...")

        required_packages = {
            "requests": "requests",
            "langchain": "langchain",
            "langchain_ollama": "langchain-ollama",
            "langchain_core": "langchain-core",
        }

        for module_name, package_name in required_packages.items():
            try:
                __import__(module_name)
                print(f"  ✅ {package_name} yüklü")
                self.checks_passed.append(f"{package_name} yüklü")
            except ImportError:
                print(f"  ❌ {package_name} yüklü DEĞİL")
                print(f"     Çözüm: pip install {package_name}")
                self.checks_failed.append(f"{package_name} eksik")
                return False

        return True

    def check_ollama_server(self) -> bool:
        """Ollama sunucusunun çalışıp çalışmadığını kontrol et."""
        print("\n[KONTROL 2] Ollama sunucusu doğrulanıyor...")

        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)

            if response.status_code == 200:
                print("  ✅ Ollama sunucusu çalışıyor")
                self.checks_passed.append("Ollama sunucusu çalışıyor")
                return True
            else:
                print(f"  ❌ Ollama şu durum kodunu döndürdü: {response.status_code}")
                self.checks_failed.append("Ollama doğru yanıt vermiyor")
                return False

        except Exception as e:
            print(f"  ❌ Ollama'ya bağlanılamıyor: {e}")
            print("     Çözüm: Başka bir terminalde 'ollama serve' çalıştırın")
            self.checks_failed.append("Ollama'ya bağlanılamıyor")
            return False

    def check_model_available(self) -> bool:
        """qwen3:8b modelinin mevcut olup olmadığını kontrol et."""
        print("\n[KONTROL 3] qwen3:8b modeli doğrulanıyor...")

        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)

            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model.get("name", "") for model in models]

                # qwen3:8b'yi kontrol et
                if any("qwen3:8b" in name.lower() for name in model_names):
                    print("  ✅ qwen3:8b modeli mevcut")
                    self.checks_passed.append("qwen3:8b mevcut")
                    return True
                else:
                    print("  ❌ qwen3:8b modeli bulunamadı")
                    print(f"     Mevcut modeller: {', '.join(model_names)}")
                    print("     Çözüm: ollama pull qwen3:8b")
                    self.checks_failed.append("qwen3:8b çekilmemiş")
                    return False
            else:
                print("  ❌ Model listesi alınamadı")
                self.checks_failed.append("Modeller listelenemiyor")
                return False

        except Exception as e:
            print(f"  ❌ Modeller kontrol edilirken hata: {e}")
            self.checks_failed.append("Modelleri listeleme hatası")
            return False

    def check_langchain_ollama_integration(self) -> bool:
        """Temel LangChain + Ollama entegrasyonunu test et."""
        print("\n[KONTROL 4] LangChain + Ollama entegrasyonu test ediliyor...")

        try:
            from langchain_ollama import OllamaLLM

            # LLM örneği oluştur
            llm = OllamaLLM(
                model="qwen3:8b",
                temperature=0.7
            )

            # Basit bir çağrı dene
            print("  Test ediliyor: '2+2=?' ...")
            response = llm.invoke("Sadece sayı ile cevap ver: 2+2=?")

            print(f"  Yanıt: {response[:100]}...")
            print("  ✅ LangChain + Ollama entegrasyonu çalışıyor!")
            self.checks_passed.append("Entegrasyon testi geçti")
            return True

        except Exception as e:
            print(f"  ❌ Entegrasyon testi başarısız: {e}")
            self.checks_failed.append("Entegrasyon testi başarısız")
            return False

    def run_all_checks(self) -> bool:
        """Tüm doğrulama kontrollerini çalıştır."""
        print("="*70)
        print("LangChain + Ollama Kurulum Doğrulama")
        print("="*70)

        # Tüm kontrolleri çalıştır
        checks = [
            self.check_imports(),
            self.check_ollama_server(),
            self.check_model_available(),
            self.check_langchain_ollama_integration(),
        ]

        # Özeti yazdır
        print("\n" + "="*70)
        print("DOĞRULAMA ÖZETİ")
        print("="*70)

        if all(checks):
            print("\n✅ TÜM KONTROLLER GEÇTİ!")
            print(f"\nGeçen ({len(self.checks_passed)}):")
            for check in self.checks_passed:
                print(f"  ✅ {check}")
            print("\n🎉 LangChain öğrenmeye başlamaya hazırsınız!")
            print("\nSonraki adım: 'python 01_basic_chain.py' çalıştırın")
            return True
        else:
            print("\n❌ BAZI KONTROLLER BAŞARISIZ")
            print(f"\nGeçen ({len(self.checks_passed)}):")
            for check in self.checks_passed:
                print(f"  ✅ {check}")

            print(f"\nBaşarısız ({len(self.checks_failed)}):")
            for check in self.checks_failed:
                print(f"  ❌ {check}")

            print("\n🔧 DÜZELTME GEREKLİ:")
            print("  1. Eksik paketleri yükle: pip install langchain langchain-ollama")
            print("  2. Ollama'yı başlat: ollama serve")
            print("  3. Modeli çek: ollama pull qwen3:8b")
            print("  4. Bu betiği tekrar çalıştır")
            return False

        print("="*70)


def main():
    """Ana giriş noktası."""
    verifier = SetupVerifier()
    success = verifier.run_all_checks()

    # Uygun kodla çık
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
