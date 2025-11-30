#!/usr/bin/env python3
"""
Örnek 2: Konuşma Geçmişi ile Akışlı Sohbet
====================================================

Konuşma bağlamını nasıl sürdüreceğinizi ve yanıtları nasıl yöneteceğinizi öğrenin.

Ne öğreneceksiniz:
- Konuşma geçmişini (hafıza) nasıl sürdürürsünüz
- Konuşma geçmişine neden ihtiyaç duyulur (LLM'ler durumsuzdur)
- LLM yanıtlarını temizleme (düşünme etiketlerini kaldırma)
- API çağrıları için hata yönetimi

YENİ BAŞLAYANLAR İÇİN HATA AYIKLAMA İPUÇLARI:
---------------------------
1. "Connection refused" (Bağlantı reddedildi) alırsanız:
   - Ollama'nın çalıştığından emin olun: `ollama serve`
   - Ollama'nın erişilebilir olup olmadığını kontrol edin: `curl http://localhost:11434/api/tags`

2. "Model not found" (Model bulunamadı) alırsanız:
   - Önce modeli çekin: `ollama pull qwen3:8b`
   - Mevcut modelleri kontrol edin: `ollama list`

3. Yanıtlar tuhafsa veya düşünme (thinking) içeriyorsa:
   - clean_response() metodu <think> etiketlerini kaldırır
   - O fonksiyona daha fazla temizleme mantığı ekleyebilirsiniz

4. LLM'e ne gönderildiğini görmek için:
   - requests.post() öncesine şunu ekleyin: `print(json.dumps(payload, indent=2))`
   - Bu, gönderilen tam JSON'ı gösterir

5. Konuşma geçmişini ayıklamak için:
   - Geçmiş boyutunu görmek için ekleyin: `print(f"Mesajlar: {len(self.messages)}")`
   - Tam konuşmayı görmek için ekleyin: `print(self.messages)`

Yazar: Beyhan MEYRALI
"""
import requests
import json
from fastapi import FastAPI, HTTPException
import uvicorn

class OllamaBot:
    """
    Konuşma geçmişini koruyan basit bir chatbot.

    Bu sınıf şunları gösterir:
    - Konuşma geçmişi yönetimi ('messages' listesi)
    - API hata yönetimi
    - Yanıt temizleme

    Her örnek kendi konuşma geçmişini korur!
    """

    def __init__(self, model="qwen3:8b", base_url="http://localhost:11434"):
        """
        Chatbot'u başlatır.

        Argümanlar:
            model: Kullanılacak Ollama modeli (varsayılan: qwen3:8b)
            base_url: Ollama API uç noktası

        Hata Ayıklama: Bu başarısız olursa, `ollama serve` ile Ollama'nın çalışıp çalışmadığını kontrol edin
        """
        self.model = model
        self.base_url = base_url

        # Bu liste konuşma geçmişini saklar!
        # Her soru sorduğunuzda, buraya eklenir
        # LLM önceki mesajları bu şekilde "hatırlar"
        self.messages = []

        print(f"[TAMAM] Ollama botu şu modelle başlatıldı: {model}")
        print(f"[TAMAM] Ollama temel URL'si: {base_url}")

    def ask_question(self, question):
        """
        Ollama'ya bir soru gönder ve konuşma geçmişini sürdür.

        Bu metot:
        1. Sorunuzu konuşma geçmişine ekler
        2. TÜM geçmişi LLM'e gönderir (bu şekilde "hatırlar")
        3. Yanıtı alır
        4. Yanıtı geçmişe ekler
        5. Temizlenmiş yanıtı döndürür

        Hata Ayıklama: Burada hata alırsanız, yükü (payload) görmek için print ifadeleri ekleyin
        """
        try:
            url = f"{self.base_url}/api/chat"

            # ÖNEMLİ: Kullanıcı mesajını konuşma geçmişine ekle
            # Konuşmayı zamanla bu şekilde oluşturuyoruz
            self.messages.append({"role": "user", "content": question})
            
            # Yükü hazırla
            # NOT: TÜM mesajları (tüm konuşma geçmişini) gönderiyoruz
            # LLM bu yüzden "hatırlar" - her seferinde her şeyi görür!
            payload = {
                "model": self.model,
                "messages": self.messages,  # <- Tam konuşma geçmişi!
                "stream": False,  # Tam yanıtı bir kerede al
                "options": {
                    "temperature": 0.1,  # Düşük = daha odaklı, Yüksek = daha yaratıcı
                    "top_p": 0.9  # Nucleus örnekleme parametresi
                }
            }

            # HATA AYIKLAMA: LLM'e ne gönderildiğini görmek için yorumu kaldırın
            # print(f"[HATA AYIKLAMA] Yük: {json.dumps(payload, indent=2)}")
            
            print(f"[SOR] Soruluyor: {question}")
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                response_data = response.json()
                ai_response = response_data.get("message", {}).get("content", "")
                
                # Yanıttan düşünme etiketlerini filtrele
                cleaned_response = self.clean_response(ai_response)
                
                # Asistan yanıtını konuşmaya ekle
                self.messages.append({"role": "assistant", "content": cleaned_response})
                
                # Windows'ta kodlama sorunlarını ele al
                try:
                    print(f"[TAMAM] Yanıt: {cleaned_response}")
                except UnicodeEncodeError:
                    # ASCII-güvenli çıktıya geri dön
                    safe_response = cleaned_response.encode('ascii', 'replace').decode('ascii')
                    print(f"[TAMAM] Yanıt: {safe_response}")
                return cleaned_response
            else:
                error_msg = f"Ollama API Hatası: {response.status_code} - {response.text}"
                print(f"[HATA] {error_msg}")
                return error_msg
                
        except Exception as e:
            error_msg = f"Bağlantı hatası: {str(e)}"
            print(f"[HATA] {error_msg}")
            return error_msg

    def clean_response(self, response):
        """
        Yanıttan düşünme etiketlerini ve içeriğini kaldır.

        Bazı modeller "düşünme süreçlerini" <think> etiketleri içinde verir.
        Kullanıcıya sadece son cevabı göstermek için bunları kaldırıyoruz.

        Örnek:
            Girdi:  "<think>Hesaplayayım...</think>Cevap 4"
            Çıktı: "Cevap 4"

        Hata Ayıklama: Tuhaf çıktı görürseniz, kaldırılacak başka etiketler olup olmadığını kontrol edin
        """
        import re
        # <think>...</think> bloklarını kaldır
        # 're.DOTALL' bayrağı '.' karakterinin yeni satırlarla da eşleşmesini sağlar
        cleaned = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)

        # Kalan boş satırları ve fazladan boşlukları kaldır
        cleaned = '\n'.join(line.strip() for line in cleaned.split('\n') if line.strip())
        return cleaned.strip()

    def reset_conversation(self):
        """Konuşma geçmişini sıfırla"""
        self.messages = []
        print("[BİLGİ] Konuşma geçmişi sıfırlandı")


# FastAPI uygulaması
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Merhaba Dünya - Ollama Temel Sohbet", "model": "qwen3:8b"}

async def ollama_chat(query: str):
    try:
        bot = OllamaBot()
        answer = bot.ask_question(query)
        return {"ai_response": answer, "model": "qwen3:8b"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/{query}")
async def chat_get(query: str):
    return await ollama_chat(query)

def main():
    """Temel sohbet işlevselliğini test et"""
    try:
        bot = OllamaBot()
        
        # Önceden tanımlanmış soruları test et
        print("\n" + "="*50)
        print("ÖNCEDEN TANIMLANMIŞ TESTLER ÇALIŞTIRILIYOR")
        print("="*50)
        
        bot.ask_question("Fransa'nın başkenti neresidir?")
        bot.ask_question("Bana kısa bir şaka yap")
        
        print("\n[BAŞARILI] Önceden tanımlanmış testler başarıyla tamamlandı!")
        
        # Etkileşimli soru sorma
        print("\n" + "="*50)
        print("ETKİLEŞİMLİ MOD - Kendi sorularınızı sorun!")
        print("Oturumu kontrol etmek için 'quit', 'exit' veya 'reset' yazın")
        print("="*50)
        
        while True:
            try:
                user_question = input("\n[SİZ] Sorunuzu girin: ").strip()
                
                if user_question.lower() in ['quit', 'exit', 'q']:
                    print("[BİLGİ] Etkileşimli moddan çıkılıyor...")
                    break
                
                if user_question.lower() == 'reset':
                    bot.reset_conversation()
                    continue
                
                if not user_question:
                    print("[BİLGİ] Lütfen bir soru girin veya çıkmak için 'quit' yazın")
                    continue
                
                result = bot.ask_question(user_question)
                # Sonuç zaten ask_question metodunda yazdırıldı
                
            except KeyboardInterrupt:
                print("\n[BİLGİ] Kullanıcı tarafından kesildi. Çıkılıyor...")
                break
            except Exception as e:
                print(f"[HATA] Soru işlenirken hata: {str(e)}")
                continue
        
    except Exception as e:
        print(f"[HATA] Hata: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    # Doğrudan testi çalıştır
    main()
    
    # FastAPI sunucusunu çalıştırmak için yorumu kaldırın
    # uvicorn.run(app, host="0.0.0.0", port=8002)

# Örnek URL'ler:
# http://127.0.0.1:8002/chat/tallest%20man%20in%20the%20world
# http://127.0.0.1:8002/chat/weather%20in%20istanbul
