# Ses Asistanı Modülü

%100 yerel olarak çalışan RAG entegrasyonlu eksiksiz bir Sesli GPT asistanı oluşturun.

## 🎯 Genel Bakış

Bu modül, şunları birleştiren tam bir ses asistanı uygular:
- **Ses Aktivite Algılama (VAD)** - Konuşmayı algılamak için Silero VAD
- **Konuşmadan Metne (STT)** - Doğru transkripsiyon için Whisper
- **RAG Ajanı** - Qdrant bilgi tabanı ile CrewAI ajanı
- **Metinden Konuşmaya (TTS)** - Yanıtları konuşmak için pyttsx3

## 📁 Modül Yapısı

```
05-voice-assistant/
├── README.md                        # Bu dosya
├── requirements.txt                 # Bağımlılıklar
├── 00_verify_installation.py       # Tüm bileşenlerin kurulu olduğunu doğrula
├── 01_vad_test.py                  # Silero VAD'ı tek başına test et
├── 02_whisper_test.py              # Whisper STT'yi tek başına test et
├── 03_tts_test.py                  # TTS'yi tek başına test et
├── 04_voice_loop.py                # VAD + Whisper entegrasyonu
├── 05_voice_assistant_rag.py       # RAG ile eksiksiz ses asistanı
├── tools_web_search.py             # Web arama aracı (DuckDuckGo)
└── 06_voice_assistant_enhanced.py  # ✨ GELİŞMİŞ: RAG + Web Arama
```

## 🚀 Hızlı Başlangıç

### 1. Bağımlılıkları Yükleyin

```bash
# Sanal ortamı etkinleştirin
source ../venv/bin/activate  # Linux/Mac
# veya
..\venv\Scripts\activate     # Windows

# Bağımlılıkları yükleyin (~2-3GB indirme PyTorch + Whisper için)
pip install -r requirements.txt
```

### 2. Kurulumu Doğrulayın

```bash
python 00_verify_installation.py
```

### 3. Qdrant'ı Başlatın (RAG için Gerekli)

```bash
# Proje kök dizininden
docker compose up -d
```

### 4. Ses Asistanını Çalıştırın

**Seçenek A: Temel RAG Asistanı** (sadece bilgi tabanı)
```bash
python 05_voice_assistant_rag.py
```

**Seçenek B: Gelişmiş Asistan** (✨ ÖNERİLEN - bilgi tabanı + web arama)
```bash
python 06_voice_assistant_enhanced.py
```

Gelişmiş asistan:
1. ✅ Sizi selamlayacak
2. 🎤 Sesiniz için sürekli dinleyecek
3. 🔄 Sorularınızı yazıya dökecek
4. 🧠 Teknik konular için bilgi tabanında arama yapacak
5. 🌐 Güncel bilgiler için web'de arama yapacak
6. 🔊 Cevapları seslendirecek

## 🌟 Gelişmiş Özellikler (YENİ!)

### Web Arama Entegrasyonu

**06_voice_assistant_enhanced.py** gerçek zamanlı web arama yeteneği ekler:

**Neden Web Arama?**
- Bilgi tabanında teknik dokümantasyon var
- Web arama güncel, gerçek zamanlı bilgi sağlar
- İkisinin en iyisi: teknik uzmanlık + güncel olaylar

**Ne Sorabilirsiniz?**

**Teknik Sorular** (Bilgi Tabanını kullanır):
- "RAG nedir?"
- "Gömmeler nasıl çalışır?"
- "Yapay zeka ajanları nedir?"

**Güncel Bilgiler** (Web Arama kullanır):
- "Bugün hava nasıl?"
- "En son Python haberleri"
- "Güncel Bitcoin fiyatı"

## 📚 Tam Dokümantasyon

Detaylı bilgi için İngilizce dokümantasyona bakın:
- **README.md (EN)** - Eksiksiz modül dokümantasyonu
- **WINDOWS_SETUP.md (EN)** - Windows kurulum rehberi
- **TESTING_GUIDE.md (EN)** - Test talimatları

## 🔗 Diğer Modüllerle Entegrasyon

- **03-embeddings-rag:** Qdrant vektör veritabanını kullanır
- **04-integrated-agents:** RAG ajan uygulamasını kullanır
- **02-agent-frameworks:** CrewAI framework'ünü kullanır
- **00-llm-basics:** LLM çıkarımı için Ollama kullanır

---

**Başlamaya hazır mısınız?** `python 06_voice_assistant_enhanced.py` komutunu çalıştırın ve konuşmaya başlayın! 🎤
