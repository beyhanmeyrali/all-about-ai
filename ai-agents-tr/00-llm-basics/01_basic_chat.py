#!/usr/bin/env python3
"""
Örnek 1: Ollama ile Temel Sohbet (OOP Tarzı)
==============================================

Bu, Nesne Yönelimli Programlama (OOP) kullanarak yapılabilecek EN BASİT LLM etkileşimidir.
Hem OOP hem de LLM temellerini anlamak için mükemmeldir.

Ne öğreneceksiniz:
- Yapay zeka kodunu sınıflar (OOP deseni) kullanarak nasıl yapılandırırsınız
- Bir LLM'e temel API çağrısı nasıl yapılır
- İstek/yanıt yapısı
- LLM'ler neden durumsuzdur (çağrılar arasında hafıza yoktur)

OOP Avantajları:
- Kod yeniden kullanılabilir (kolayca birden fazla bot oluşturun)
- Bakımı ve genişletilmesi daha kolaydır
- Sorumlulukların daha temiz ayrılması
- Endüstri standardı desen

Yazar: Beyhan MEYRALI
"""

import requests
import json
from typing import Optional, List, Dict


# =============================================================================
# OOP DESENİ: LLM Bot Sınıfı
# =============================================================================

class OllamaBot:
    """
    Ollama LLM ile iletişim kuran basit bir chatbot.

    Bu sınıf, bir LLM ile sohbet etmek için gereken tüm işlevselliği kapsar.
    Bu sınıfın her örneği bir bot yapılandırmasını temsil eder.

    Örnek kullanım:
        bot = OllamaBot(model="qwen3:8b")
        response = bot.ask("2+2 kaçtır?")
        print(response)
    """

    def __init__(self,
                 model: str = "qwen3:8b",
                 base_url: str = "http://localhost:11434",
                 timeout: int = 60):
        """
        Chatbot'u başlatır.

        Argümanlar:
            model: Kullanılacak Ollama modeli (varsayılan: qwen3:8b)
            base_url: Ollama API uç noktası (varsayılan: http://localhost:11434)
            timeout: Saniye cinsinden istek zaman aşımı (varsayılan: 60)

        Not: Bu KURUCU (CONSTRUCTOR) metodudur - yeni bir bot oluşturduğunuzda çalışır.
        """
        self.model = model
        self.base_url = base_url
        self.timeout = timeout
        self.api_endpoint = f"{base_url}/api/chat"

        # Konuşma geçmişini saklamak için örnek değişkeni
        # Her bot örneğinin kendi geçmişi vardır!
        self.messages: List[Dict[str, str]] = []

        print(f"[TAMAM] OllamaBot başlatıldı")
        print(f"[TAMAM] Model: {self.model}")
        print(f"[TAMAM] Uç nokta: {self.api_endpoint}")

    def ask_question(self, question: str, stream: bool = False) -> Optional[str]:
        """
        LLM'e tek bir soru gönderir ve yanıt alır.

        Bu, botun ÇEKİRDEK metodudur - HTTP iletişimini yönetir.

        Argümanlar:
            question: LLM'e sorulacak soru
            stream: Eğer True ise, akış yanıtı al (gelecek kullanım için)

        Döndürür:
            LLM'in yanıtı string olarak, veya hata oluşursa None

        Nasıl çalışır:
        1. Yükü (payload) hazırla (sorunuzu içeren JSON)
        2. Ollama'ya HTTP POST isteği gönder
        3. Yanıtı ayrıştır (parse et)
        4. Cevabı döndür
        """

        # Adım 1: İstek yükünü hazırla
        # Bu, Ollama'nın beklediği JSON yapısıdır
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",  # Bu mesajı kim gönderiyor
                    "content": question  # Asıl mesaj içeriği
                }
            ],
            "stream": stream  # Tam yanıtı bir kerede al (token-token değil)
        }

        # Adım 2: Ollama'ya POST isteği gönder
        print(f"\n[KULLANICI] {question}")
        print(f"[BİLGİ] {self.model} modeline gönderiliyor...")

        try:
            response = requests.post(
                self.api_endpoint,
                json=payload,
                timeout=self.timeout
            )

            # Adım 3: İsteğin başarılı olup olmadığını kontrol et
            if response.status_code == 200:
                # JSON yanıtını ayrıştır
                response_data = response.json()

                # Yanıttan LLM'in mesajını çıkar
                # Yanıt yapısı: response['message']['content']
                llm_response = response_data['message']['content']

                print(f"[YZ] {llm_response}")
                return llm_response
            else:
                error_msg = f"Hata {response.status_code}: {response.text}"
                print(f"[HATA] {error_msg}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"[HATA] Bağlantı başarısız: {e}")
            print("[İPUCU] Ollama'nın çalıştığından emin olun: ollama serve")
            return None

    def chat(self, user_message: str) -> Optional[str]:
        """
        Kolaylık metodu - ask_question() ile aynı ama daha kısa isimli.

        Bu, daha iyi geliştirici deneyimi için bir TAKMA AD (ALIAS) metodudur.
        """
        return self.ask_question(user_message)

    def reset(self):
        """
        Botun konuşma geçmişini sıfırla.

        Bu, mesaj listesini temizler, taze bir başlangıç için yararlıdır.
        """
        self.messages = []
        print("[BİLGİ] Konuşma geçmişi temizlendi")

    def get_model_info(self) -> Dict:
        """
        Mevcut model hakkında bilgi al.

        Döndürür:
            Model bilgilerini içeren sözlük
        """
        return {
            "model": self.model,
            "endpoint": self.api_endpoint,
            "timeout": self.timeout
        }


# =============================================================================
# GÖSTERİM: LLM'LER NEDEN DURUMSUZDUR
# =============================================================================

def demonstrate_stateless_behavior():
    """
    Bu gösterim, LLM'lerin önceki konuşmaları "hatırlamadığını" gösterir.
    Her API çağrısı tamamen bağımsızdır.

    Bu, kavramı gösteren bir FONKSİYONDUR (sınıf metodu değil).
    """

    print("\n" + "="*70)
    print("GÖSTERİM: LLM'ler Durumsuzdur (Hafıza Yoktur)")
    print("="*70)

    # Bir bot örneği oluştur
    bot = OllamaBot(model="qwen3:8b")

    # Konuşma 1
    print("\n--- Konuşma 1 ---")
    bot.ask_question("Adım Alice ve Python programlamayı seviyorum")

    # Konuşma 2: Önceki konuşma hakkında soru sorma
    print("\n--- Konuşma 2 (ayrı API çağrısı) ---")
    bot.ask_question("Adım ne?")

    # Beklenen sonuç: LLM ismi bilmeyecek!
    # Neden? Çünkü her ask_question() çağrısı bağımsızdır.
    # İkinci çağrı, birinci çağrıdan haberdar değildir.

    print("\n" + "="*70)
    print("AÇIKLAMA:")
    print("LLM adınızı bilmediğini söyledi çünkü her API çağrısı")
    print("tamamen bağımsızdır. LLM'ler çağrılar arasında veri saklamaz.")
    print("Hatırlamak için, konuşma geçmişini göndermemiz gerekir (bkz. Örnek 3)")
    print("="*70)


# =============================================================================
# OOP İLE ETKİLEŞİMLİ MOD
# =============================================================================

def interactive_chat():
    """
    OllamaBot sınıfımızı kullanan etkileşimli sohbet döngüsü.
    Not: Bu sürümün hafızası YOKTUR - her mesaj bağımsızdır!

    Bu, sınıfın pratik bir uygulamada nasıl KULLANILACAĞINI gösterir.
    """

    print("\n" + "="*70)
    print("ETKİLEŞİMLİ MOD - Temel Sohbet (Hafıza Yok)")
    print("="*70)
    print("LLM ile sohbet etmek için mesajlarınızı yazın")
    print("Komutlar:")
    print("  'quit' veya 'exit' - Programdan çık")
    print("  'help' - Bu mesajı göster")
    print("  'info' - Bot bilgilerini göster")
    print("="*70)

    # Bot örneğimizi oluştur
    # Bu NESNE ÖRNEKLEMEDİR (OBJECT INSTANTIATION) - bir sınıftan nesne oluşturma
    bot = OllamaBot(model="qwen3:8b")

    while True:
        # Kullanıcı girdisi al
        user_input = input("\n[SİZ] ").strip()

        # Komutları işle
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("[BİLGİ] Hoşçakal!")
            break

        if user_input.lower() == 'help':
            print("\nKomutlar: quit, exit, help, info")
            print("Not: Bu sohbetin hafızası YOKTUR. Her mesaj bağımsızdır.")
            continue

        if user_input.lower() == 'info':
            info = bot.get_model_info()
            print(f"\nBot Bilgisi: {json.dumps(info, indent=2)}")
            continue

        if not user_input:
            print("[BİLGİ] Lütfen bir mesaj girin")
            continue

        # Bot örneğimizi kullanarak LLM'e mesaj gönder
        # Bu, ask_question() metodunu çağırır
        bot.ask_question(user_input)

        # ÖNEMLİ: Konuşmayı hiçbir yere kaydetmediğimize dikkat edin!
        # Bu, LLM'in önceki mesajları hatırlamayacağı anlamına gelir.
        # Konuşma geçmişi için, bkz. örnek 03_conversation_history.py


# =============================================================================
# GELİŞMİŞ: Birden Fazla Bot (OOP Avantajı)
# =============================================================================

def demonstrate_multiple_bots():
    """
    OOP avantajını göster: Birden fazla bot örneği oluşturma.

    Bu, OOP'nin neden güçlü olduğunu gösterir - aynı anda çalışan
    farklı yapılandırmalara sahip birden fazla botunuz olabilir!
    """

    print("\n" + "="*70)
    print("OOP AVANTAJI: Çoklu Bot Örnekleri")
    print("="*70)

    # İki farklı bot oluştur
    bot1 = OllamaBot(model="qwen3:8b")
    bot2 = OllamaBot(model="qwen3:8b")  # Farklı bir model olabilir

    print("\n[Bot 1] Bir soru soruluyor...")
    bot1.ask_question("Fransa'nın başkenti neresidir?")

    print("\n[Bot 2] Farklı bir soru soruluyor...")
    bot2.ask_question("2+2 kaçtır?")

    # Her bot kendi durumunu bağımsız olarak korur!
    print("\n" + "="*70)
    print("AÇIKLAMA:")
    print("OOP ile kolayca birden fazla bot örneği oluşturabilirsiniz.")
    print("Her örneğin kendi yapılandırması ve durumu vardır.")
    print("Bu, global değişkenler kullanmaktan çok daha temizdir!")
    print("="*70)


# =============================================================================
# CURL EŞDEĞERİ
# =============================================================================

def show_curl_equivalent():
    """
    Aynı şeyi yapan curl komutunu göster.
    Bu, HTTP katmanını anlamanıza yardımcı olur.

    OOP ile bile, arka planda hala sadece HTTP'dir!
    """

    print("\n" + "="*70)
    print("CURL EŞDEĞERİ (Arka Planda Ne Olur)")
    print("="*70)
    print("""
OllamaBot sınıfı bu HTTP isteğini gönderir:

curl -X POST http://localhost:11434/api/chat -d '{
  "model": "qwen3:8b",
  "messages": [
    {"role": "user", "content": "Merhaba! 2+2 kaçtır?"}
  ],
  "stream": false
}'

OOP Avantajları vs Ham curl:
✅ Yeniden kullanılabilir kod (kolayca birden fazla bot oluşturun)
✅ Yerleşik hata yönetimi
✅ Genişletmesi kolay (sınıfa özellikler ekleyin)
✅ Daha temiz kod yapısı
✅ Endüstri standardı desen

Ama unutmayın: Arka planda hala sadece HTTP'dir!
Ollama'yı HERHANGİ BİR dilden çağırabilirsiniz (bkz. 05_curl_examples.sh)
    """)
    print("="*70)


# =============================================================================
# ANA PROGRAM
# =============================================================================

def main():
    """
    Ana giriş noktası - tüm özellikleri gösterir.

    Bu, gösterimleri yöneten PROSEDÜREL bir fonksiyondur.
    """

    print("""
╔═══════════════════════════════════════════════════════════════════╗
║              Örnek 1: Temel LLM Sohbeti (OOP Tarzı)               ║
║                                                                   ║
║  Öğrenin:                                                         ║
║  • Sınıflar kullanarak yapay zeka kodu nasıl yapılandırılır       ║
║  • Basit bir LLM API çağrısı nasıl yapılır                        ║
║  • İstek/yanıt yapısı                                             ║
║  • LLM'ler neden durumsuzdur (hafıza yok)                         ║
║  • Üretim kodu için OOP avantajları                               ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Bir bot örneği oluştur
    # Bu NESNE ÖRNEKLEMEYİ gösterir
    bot = OllamaBot(model="qwen3:8b")

    # Test 1: Botumuzu kullanarak basit soru
    print("\n--- Test 1: Basit Soru ---")
    bot.ask_question("Fransa'nın başkenti neresidir?")

    # Test 2: Matematik sorusu
    print("\n--- Test 2: Matematik Sorusu ---")
    bot.chat("15 çarpı 7 kaçtır?")  # Daha kısa takma adı kullanarak

    # Test 3: Durumsuz davranışı göster
    demonstrate_stateless_behavior()

    # Test 4: Çoklu botları göster (OOP avantajı)
    demonstrate_multiple_bots()

    # curl eşdeğerini göster
    show_curl_equivalent()

    # Etkileşimli mod
    print("\n[BİLGİ] Etkileşimli mod başlatılıyor...")
    print("[HATIRLATMA] Bu sohbetin hafızası YOKTUR. Hafıza için örnek 03'e bakın.")
    interactive_chat()


# =============================================================================
# GİRİŞ NOKTASI
# =============================================================================

if __name__ == "__main__":
    """
    Bu blok, betik doğrudan çalıştırıldığında çalışır.
    Programın GİRİŞ NOKTASIDIR.
    """

    # Başlamadan önce Ollama'nın erişilebilir olup olmadığını kontrol et
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("[UYARI] Ollama çalışıyor ancak beklenmeyen durum döndürdü")
    except requests.exceptions.RequestException:
        print("[HATA] Ollama'ya bağlanılamıyor!")
        print("[İPUCU] Ollama'nın çalıştığından emin olun:")
        print("       1. https://ollama.ai adresinden yükleyin")
        print("       2. Çalıştırın: ollama serve")
        print("       3. Modeli çekin: ollama pull qwen3:8b")
        exit(1)

    # Ana programı çalıştır
    main()


# =============================================================================
# GÖSTERİLEN OOP KAVRAMLARI
# =============================================================================
"""
BU DOSYADAKİ TEMEL OOP KAVRAMLARI:

1. SINIF (CLASS):
   - Nesneler oluşturmak için taslak
   - OllamaBot bizim sınıfımızdır

2. NESNE/ÖRNEK (OBJECT/INSTANCE):
   - bot = OllamaBot() bir örnek oluşturur
   - Her örneğin kendi verileri vardır (self.model, self.messages vb.)

3. KURUCU (__init__):
   - Nesne oluşturulduğunda çalışan özel metot
   - Örnek değişkenlerini başlatır

4. ÖRNEK METOTLARI (INSTANCE METHODS):
   - Sınıfa ait fonksiyonlar
   - ask_question(), chat(), reset() metotlardır
   - İlk parametre olarak her zaman 'self' alırlar

5. ÖRNEK DEĞİŞKENLERİ (INSTANCE VARIABLES):
   - Her nesneye ait veriler
   - self.model, self.messages, self.base_url
   - Her örneğin kendi kopyası vardır

6. KAPSÜLLEME (ENCAPSULATION):
   - Veri ve metotları bir araya getirme
   - Tüm LLM mantığı tek bir sınıftadır

7. YENİDEN KULLANILABİLİRLİK (REUSABILITY):
   - Kolayca birden fazla bot oluşturulabilir
   - Yeni özellikler için sınıf genişletilebilir

YAPAY ZEKA/LLM KODU İÇİN NEDEN OOP:
- Üretim kod tabanları OOP kullanır
- Bakımı ve testi daha kolaydır
- Daha temiz kod organizasyonu
- Endüstri standardı desen
- Gerçek dünya yazılım mühendisliği ile eşleşir

Bunu fonksiyonel/prosedürel tarzla karşılaştırın - OOP çok daha temizdir!
"""
