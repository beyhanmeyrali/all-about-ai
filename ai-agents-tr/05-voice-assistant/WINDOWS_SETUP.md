# Windows Kurulum Kılavuzu - Ses Asistanı

Mikrofon ve hoparlörlerle birlikte ses asistanını Windows'ta çalıştırmak için eksiksiz kılavuz.

---

## 🪟 Windows'ta Hızlı Kurulum

### Ön Gereksinimler

1. **Python 3.12** - [python.org'dan indirin](https://www.python.org/downloads/)
2. **Git** - [git-scm.com'dan indirin](https://git-scm.com/download/win)
3. **Ollama** - [ollama.com'dan indirin](https://ollama.com/download/windows)
4. **Docker Desktop** (Qdrant için) - [İndirin](https://www.docker.com/products/docker-desktop/)

---

## 📦 Adım Adım Kurulum

### 1. Depoyu Klonlayın

PowerShell veya Komut İstemi'ni açın:

```powershell
# Depoyu klonlayın
git clone <depo-url'niz>
cd all-about-ai\ai-agents

# Veya zaten klonlandıysa, sadece gidin
cd yol\to\all-about-ai\ai-agents
```

### 2. Sanal Ortam Oluşturun

```powershell
# venv oluşturun
python -m venv venv

# venv'i etkinleştirin
.\venv\Scripts\activate

# Doğrulayın
python --version
# Python 3.12.x göstermeli
```

### 3. Bağımlılıkları Yükleyin

```powershell
cd 05-voice-assistant

# Tüm bağımlılıkları yükleyin (~3GB indirme)
pip install -r requirements.txt

# Bu şunları yükleyecek:
# - PyTorch (NVIDIA GPU'nuz varsa CUDA ile)
# - Whisper (konuşmadan metine)
# - pyttsx3 (metinden konuşmaya)
# - CrewAI (ajan framework'ü)
# - Diğer tüm bağımlılıklar
```

### 4. Ollama Modellerini Yükleyin

```powershell
# Ollama'yı başlatın (çalışmıyorsa)
# Ollama Windows'ta otomatik başlamalıdır

# Gerekli modelleri çekin
ollama pull qwen3:8b
ollama pull qwen3-embedding:0.6b

# Doğrulayın
ollama list
# Her iki modeli de göstermeli
```

### 5. Qdrant'ı Başlatın (İsteğe Bağlı - Bilgi Tabanı için)

```powershell
# Proje kök dizinine gidin
cd ..

# Qdrant'ı Docker ile başlatın
docker compose up -d

# Doğrulayın
docker ps
# Çalışan qdrant container'ını göstermeli
```

### 6. Kurulumu Doğrulayın

```powershell
cd 05-voice-assistant

# Doğrulama scriptini çalıştırın
python 00_verify_installation.py
```

Beklenen çıktı:
```
✅ PyTorch 2.x.x (CUDA: True/False)
✅ OpenAI Whisper
✅ Silero VAD (model yüklendi)
✅ pyttsx3 TTS
⚠️  sounddevice (ilk çalıştırmada hata gösterebilir - yoksayın)
✅ soundfile
✅ NumPy
✅ SciPy

✅ Geçti: 7/8
```

---

## 🎤 Ses Asistanını Çalıştırma

### Seçenek 1: Geliştirilmiş Asistan (Önerilen)

**Tam özellikler: Bilgi Tabanı + Web Arama**

```powershell
# 05-voice-assistant klasöründe olduğunuzdan emin olun
cd 05-voice-assistant

# Zaten etkin değilse venv'i etkinleştirin
.\venv\Scripts\activate

# Geliştirilmiş asistanı çalıştırın
python 06_voice_assistant_enhanced.py
```

**Ne olur:**
1. Tüm modelleri yükler (ilk seferde ~30 saniye sürer)
2. "Merhaba! Ben senin gelişmiş AI asistanınım..." diye selamlar
3. Sesinizi dinlemeye başlar
4. Konuşmanızı transkribe eder
5. Bilgi Tabanı VEYA Web Arama kullanarak yanıt verir
6. Yanıtı size sesli söyler

**Şunları sormayı deneyin:**
- "RAG nedir?" → Bilgi Tabanını Kullanır
- "Bugün hava nasıl?" → Web Aramayı Kullanır
- "Embedding'leri açıkla" → Bilgi Tabanını Kullanır
- "Son Python haberleri" → Web Aramayı Kullanır

**Durdurmak için:** `Ctrl+C` tuşlarına basın

### Seçenek 2: Metin Tabanlı Sohbet (Mikrofon gerekmez)

```powershell
python chat_assistant.py
```

Sorularınızı konuşmak yerine yazın.

### Seçenek 3: Temel Asistan (Sadece Bilgi Tabanı)

```powershell
python 05_voice_assistant_rag.py
```

Sadece bilgi tabanını kullanır, web arama yok.

---

## 🎯 Bireysel Bileşenleri Test Etme

### Metinden Konuşmayı Test Edin

```powershell
python 03_tts_test.py
```

- Mevcut sesleri listeler
- Test cümlelerini söyler
- Farklı sesleri test etmek için etkileşimli mod

### Konuşmadan Metine Test Edin

```powershell
python 02_whisper_test.py
```

- 5 saniyelik ses kaydeder
- Whisper kullanarak transkribe eder
- Algılanan dili gösterir

### Ses Aktivite Algılamayı Test Edin

```powershell
python 01_vad_test.py
```

- Gerçek zamanlı konuşma algılama
- Ne zaman konuşmaya başladığınızı/durduğunuzu gösterir

### Ses Döngüsünü Test Edin

```powershell
python 04_voice_loop.py
```

- Sürekli dinleme
- Otomatik transkripsiyon
- AI yanıtları yok (sadece transkripsiyon)

---

## ⚙️ Yapılandırma

### Whisper Model Boyutunu Değiştirin

`06_voice_assistant_enhanced.py` dosyasını düzenleyin:

```python
assistant = VoiceAssistantEnhanced(
    whisper_model_size="base",  # Seçenekler: tiny, base, small, medium, large
    tts_voice_index=0
)
```

**Model boyutları:**
- `tiny` - En hızlı, daha az doğru (~75MB)
- `base` - **Önerilen** denge (~150MB)
- `small` - Daha iyi doğruluk (~500MB)
- `medium` - Çok iyi doğruluk (~1.5GB)
- `large` - En iyi doğruluk (~3GB)

### TTS Sesini Değiştirin

```powershell
# Mevcut sesleri görmek için bunu çalıştırın
python -c "import pyttsx3; engine = pyttsx3.init(); voices = engine.getProperty('voices'); [print(f'{i}: {v.name}') for i, v in enumerate(voices)]"
```

Sonra scripti düzenleyin:
```python
assistant = VoiceAssistantEnhanced(
    whisper_model_size="base",
    tts_voice_index=1  # İstediğiniz ses indeksine değiştirin
)
```

### VAD Hassasiyetini Ayarlayın

`06_voice_assistant_enhanced.py` dosyasını düzenleyin, bu sabitleri değiştirin:

```python
VAD_THRESHOLD = 0.5              # Daha düşük = daha hassas (0.0-1.0)
MIN_SPEECH_DURATION_MS = 250     # Minimum konuşma süresi
MIN_SILENCE_DURATION_MS = 500    # Kaydı durdurmadan önceki sessizlik
```

---

## 🔧 Sorun Giderme

### Mikrofon Çalışmıyor

**Windows Ayarlarını Kontrol Edin:**
1. Ayarlar → Gizlilik ve Güvenlik → Mikrofon
2. "Uygulamaların mikrofonunuza erişmesine izin ver"i etkinleştirin
3. Python için etkinleştirin

**Varsayılan Mikrofonu Ayarlayın:**
1. Görev çubuğundaki hoparlör simgesine sağ tıklayın
2. Ses Ayarlarını Aç
3. Giriş → Mikrofonunuzu seçin
4. Mikrofonu test edin

### Ses Oynatma Sorunları

**Hoparlörleri Kontrol Edin:**
1. Hoparlör simgesine sağ tıklayın
2. Ses Ayarlarını Aç
3. Çıkış → Hoparlörlerinizi/kulaklıklarınızı seçin
4. Sesi test edin

### Whisper Model İndirmesi Yavaş

Modeller şuraya indirilir: `C:\Users\<AdIniz>\.cache\whisper\`

- Daha hızlı indirme için daha küçük model (`tiny` veya `base`) kullanın
- İlk çalıştırma modelleri indirir (base için ~150MB)
- Sonraki çalıştırmalar önbelleğe alınan modelleri kullanır

### CUDA/GPU Algılanmıyor

**NVIDIA GPU'nuz varsa:**

```powershell
# CUDA'nın kullanılabilir olup olmadığını kontrol edin
python -c "import torch; print(f'CUDA kullanilabilir: {torch.cuda.is_available()}')"
```

False ama NVIDIA GPU'nuz varsa:
1. NVIDIA sürücülerini yükleyin
2. CUDA Toolkit 11.8+ yükleyin
3. PyTorch'u CUDA desteğiyle yeniden yükleyin

**Sadece CPU (iyi çalışır, sadece daha yavaş):**
- Whisper CPU kullanacak
- ~2 saniye yerine ~10-15 saniye sürer
- Hala kullanılabilir!

### Ollama Yanıt Vermiyor

```powershell
# Ollama'nın çalışıp çalışmadığını kontrol edin
ollama list

# Çalışmıyorsa başlatın
# Ollama otomatik başlamalıdır, ama şunu çalıştırabilirsiniz:
# Başlat Menüsü → Ollama (veya sistem tepsisini kontrol edin)

# Bağlantıyı test edin
curl http://localhost:11434/api/tags
```

### Qdrant Bağlantısı Başarısız

```powershell
# Docker'ın çalışıp çalışmadığını kontrol edin
docker ps

# Qdrant'ı başlatın
docker compose up -d

# Doğrulayın
docker ps | findstr qdrant
```

**Qdrant kullanmak istemiyorsanız:**
- Asistan yine de web arama ile çalışacak!
- Bilgi tabanı hatasını yoksayın
- Veya yerleşik bilgiye sahip metin tabanlı sohbeti kullanın

---

## 🎓 Kullanım Örnekleri

### Örnek Oturum 1: Teknik Sorular

```
🎤 Ses Asistanı Başlatıldı
Mikrofonunuza konuşun...

[Siz konuşuyorsunuz: "RAG nedir?"]

🟢 Dinleniyor...
🔄 Transkribe ediliyor...

💬 Siz: RAG nedir?

🤔 Düşünüyor (KB + Web Arama ile)...
🤖 Asistan: RAG, Retrieval-Augmented Generation'ın kısaltmasıdır.
Kendi verilerinize dayalı doğru, bağlamsal yanıtlar sağlamak için
bilgi getirmeyi LLM üretimi ile birleştiren bir tekniktir.

🔊 Konuşuyor...

[Asistan yanıtı söylüyor]
```

### Örnek Oturum 2: Güncel Bilgi

```
[Siz konuşuyorsunuz: "Bugün hava nasıl?"]

🟢 Dinleniyor...
🔄 Transkribe ediliyor...

💬 Siz: Bugün hava nasıl?

🤔 Düşünüyor (KB + Web Arama ile)...
🤖 Asistan: AccuWeather'dan güncel hava durumu bilgisi buldum,
parçalı bulutlu koşullar ve 72°F sıcaklık gösteriyor...

🔊 Konuşuyor...
```

---

## 📊 Performans Beklentileri

### NVIDIA GPU ile (RTX 3060+):
- Konuşma algılama: Anlık
- Transkripsiyon: ~2 saniye
- Yanıt oluşturma: ~2-3 saniye
- **Toplam yanıt süresi: 4-5 saniye** ⚡

### Sadece CPU (Intel i7/AMD Ryzen 7):
- Konuşma algılama: Anlık
- Transkripsiyon: ~10-15 saniye
- Yanıt oluşturma: ~3-5 saniye
- **Toplam yanıt süresi: 13-20 saniye** 🐢

**Daha hızlı performans için ipuçları:**
- `tiny` veya `base` Whisper modeli kullanın
- Varsa GPU kullanın
- Diğer uygulamaları kapatın

---

## 🌟 Gelişmiş Özellikler

### Sürekli Konuşmayı Etkinleştirin

Şu anda her soru bağımsızdır. Bağlamı korumak için:

1. Ajanı konuşma geçmişini içerecek şekilde değiştirin
2. Önceki S&C'yi bellekte saklayın
3. Bağlama duyarlı yanıtlar için LLM'e iletin

(Bu gelecekteki bir iyileştirmedir)

### Özel Bilgi Ekleyin

Bilgi tabanına kendi belgelerinizi eklemek için:

1. Belgeleri `03-embeddings-rag/data/` klasörüne ekleyin
2. Qdrant'a eklemek için alma scriptini çalıştırın
3. Asistan artık belgeleriniz hakkındaki soruları yanıtlayacak!

### Dili Değiştirin

`06_voice_assistant_enhanced.py` dosyasını düzenleyin:

```python
result = self.whisper_model.transcribe(
    audio,
    language="en",  # Şunlarla değiştirin: "es", "fr", "de", "tr", vb.
    fp16=torch.cuda.is_available()
)
```

Whisper 99+ dili destekler!

---

## 📱 Sonraki Adımlar

### Test Sonrası:

1. **Ajanı özelleştirin** - Talimatları değiştirin, daha fazla araç ekleyin
2. **Kendi bilgi tabanınızı ekleyin** - Kendi belgelerinizi alın
3. **TTS'yi geliştirin** - Farklı sesler veya Coqui TTS deneyin
4. **Uyandırma kelimesi ekleyin** - "Merhaba Asistan" aktivasyonu
5. **Bir UI oluşturun** - Gradio/Streamlit arayüzü

---

## 🆘 Yardım Alma

### Logları Kontrol Edin

```powershell
# Ollama loglarını görüntüleyin
# Kontrol edin: C:\Users\<AdIniz>\.ollama\logs\

# Python hatalarını görüntüleyin
# Hatalar konsolda gösterilecek
```

### Yaygın Sorunlar

| Sorun | Çözüm |
|-------|-------|
| "No module named..." | `pip install -r requirements.txt` |
| "Ollama yanıt vermiyor" | Başlat Menüsü'nden Ollama'yı başlatın |
| "CUDA kullanılamıyor" | NVIDIA sürücüleri + CUDA toolkit yükleyin |
| "Mikrofon algılanmadı" | Windows mikrofon izinlerini kontrol edin |
| "Qdrant bağlantısı başarısız" | `docker compose up -d` |

---

## ✅ Hızlı Başlangıç Kontrol Listesi

- [ ] Python 3.12 yüklü
- [ ] Depo klonlandı
- [ ] Sanal ortam oluşturuldu ve etkinleştirildi
- [ ] Bağımlılıklar yüklendi (`pip install -r requirements.txt`)
- [ ] Ollama yüklü ve modeller çekildi
- [ ] Docker Desktop çalışıyor (isteğe bağlı)
- [ ] Qdrant başlatıldı (isteğe bağlı)
- [ ] Mikrofon ve hoparlörler çalışıyor
- [ ] `python 06_voice_assistant_enhanced.py` çalıştırıldı
- [ ] Konuşmaya başlayın! 🎤

---

## 🎉 Hazırsınız!

Başlamak için komutunuz:

```powershell
cd 05-voice-assistant
.\venv\Scripts\activate
python 06_voice_assistant_enhanced.py
```

Sonra konuşun: **"RAG nedir?"** ve büyüyü izleyin! ✨

---

## 📚 Ek Kaynaklar

- **README.md** - Eksiksiz modül dokümantasyonu
- **TESTING_GUIDE.md** - Detaylı test talimatları
- **ENHANCEMENT_SUMMARY.md** - Teknik uygulama detayları
- **COMPLETION_SUMMARY.md** - Orijinal ses asistanı özellikleri

---

**Keyifli Testler! 🎤🤖**
