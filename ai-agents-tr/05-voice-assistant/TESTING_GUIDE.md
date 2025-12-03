# Test Kılavuzu - Ses Asistanı

## 🧪 Geliştirilmiş Ses Asistanını Nasıl Test Edersiniz

WSL'de olduğunuz için (mikrofon/hoparlör olmadan), tüm özellikleri test etmek için **metin tabanlı sohbet arayüzünü** kullanın.

---

## ✅ Hızlı Test (Metin Tabanlı Sohbet)

### 1. Etkileşimli Sohbet Asistanını Başlatın

```bash
cd /workspace/all-about-ai/ai-agents/05-voice-assistant
source ../venv/bin/activate
python chat_assistant.py
```

### 2. Bu Örnek Soruları Deneyin

**Teknik Sorular** (Bilgi Tabanını kullanır):
```
Siz: RAG nedir?
Siz: Embedding'leri açıkla
Siz: AI ajanları nedir?
Siz: CrewAI hakkında bilgi ver
Siz: Vektör veritabanı nedir?
```

**Güncel Bilgi** (Web Aramayı kullanır):
```
Siz: Son Python haberleri
Siz: Güncel hava durumu tahmini
Siz: Bugün Bitcoin fiyatı
Siz: Son AI gelişmeleri
```

### 3. Çıkış
`quit` veya `exit` yazın ya da `Ctrl+C` tuşlarına basın

---

## 🎯 Ne Göreceksiniz

Asistan:
1. **Doğru aracı seçecek** - Teknik için Bilgi Tabanı, güncel bilgi için Web Arama
2. **Bilgi alacak** - Bilgi tabanından veya DuckDuckGo'dan
3. **Yanıt oluşturacak** - Qwen3:8b LLM kullanarak
4. **Yanıtı gösterecek** - Açık, özet yanıt

---

## 📊 Test Sonuçları

### Örnek 1: Teknik Soru
```
💬 Siz: RAG nedir?

🤖 Asistan:
RAG, Retrieval-Augmented Generation'ın kısaltmasıdır. AI sistemlerindeki
yanıtların doğruluğunu, alaka düzeyini ve gerçeklere uygunluğunu artırmak
için dış kaynaklardan ilgili bilgilerin alınmasını üretken modellerle
birleştiren bir tekniktir.
```
✅ Kullanıldı: **Bilgi Tabanı Araması**

### Örnek 2: Güncel Bilgi
```
💬 Siz: Son Python haberleri

🤖 Asistan:
TechCrunch, Google News ve Reuters'tan Python ile ilgili güncel haberleri
buldum, Python programlama ve ilgili teknolojilerdeki son gelişmeleri
kapsıyor.
```
✅ Kullanıldı: **Web Arama**

---

## 🔧 Sorun Giderme

### Ollama Çalışmıyor
```bash
# Ollama'yı başlatın
nohup ollama serve > /tmp/ollama.log 2>&1 &

# Çalıştığını doğrulayın
ollama list
```

### Modeller Eksik
```bash
# Gerekli modelleri çekin
ollama pull qwen3:8b
ollama pull qwen3-embedding:0.6b
```

### Qdrant Çalışmıyor
```bash
# Proje kök dizininden
cd /workspace/all-about-ai/ai-agents
docker compose up -d

# Doğrulayın
docker ps | grep qdrant
```

---

## 🎤 Gerçek Sesle Test Etme (Windows/Mac)

Mikrofon ve hoparlörlerle **tam ses asistanını** test etmek istiyorsanız:

### Seçenek 1: Windows/Mac'e Aktarın
1. `05-voice-assistant` klasörünü Windows/Mac'inize kopyalayın
2. Bağımlılıkları yükleyin: `pip install -r requirements.txt`
3. Çalıştırın: `python 06_voice_assistant_enhanced.py`
4. Sorularınızı söyleyin!

### Seçenek 2: WSL'den Windows Kullanın
1. Python scriptini Windows PowerShell/CMD'den çalıştırın
2. Şuraya gidin: `\\wsl$\Ubuntu\workspace\all-about-ai\ai-agents\05-voice-assistant`
3. venv'i etkinleştirin ve ses asistanını çalıştırın

---

## 📝 Hızlı Komutlar Kılavuzu

```bash
# Ses asistanına git
cd /workspace/all-about-ai/ai-agents/05-voice-assistant
source ../venv/bin/activate

# Sadece web aramayı test et
python demo_web_search.py

# Etkileşimli metin sohbeti (WSL için ÖNERİLEN)
python chat_assistant.py

# Tam ses asistanı (mikrofon gerektirir)
python 06_voice_assistant_enhanced.py

# Kurulumu doğrula
python 00_verify_installation.py
```

---

## 🌟 Test Edebileceğiniz Özellikler

### 1. Çift Araç Sistemi
- ✅ Bilgi Tabanı Araması (teknik dokümantasyon)
- ✅ Web Arama (güncel bilgi)

### 2. Akıllı Yönlendirme
- ✅ Ajan hangi aracı kullanacağına karar verir
- ✅ Gerekirse her iki aracı da kullanabilir

### 3. LLM Entegrasyonu
- ✅ Yanıt oluşturma için Qwen3:8b
- ✅ Özet, yardımcı yanıtlar

### 4. Gerçek Zamanlı Arama
- ✅ DuckDuckGo arama
- ✅ API anahtarı gerekmez
- ✅ Gizlilik dostu

---

## 🎓 Çıktıyı Anlama

`chat_assistant.py`'yi çalıştırdığınızda şunu göreceksiniz:

```
🚀 Crew: crew
└── 📋 Task: [görev-id]
    Atandı: AI Asistanı
    Durum: ✅ Tamamlandı
```

Bu şunları gösterir:
- **Crew** - Ajanı yöneten CrewAI framework'ü
- **Task** - Sorunuz
- **Agent** - Onu işleyen AI Asistanı
- **Tools** - Hangi araçlar kullanıldı
- **Final Answer** - Yanıt

---

## 💡 Test İçin İpuçları

1. **Basit Başlayın**: Çalıştığını doğrulamak için "RAG nedir?" ile başlayın
2. **Her İki Aracı da Deneyin**: Teknik VE güncel bilgi soruları sorun
3. **Çıktıyı İzleyin**: Ajanın hangi aracı seçtiğini görün
4. **Birden Fazla Soru**: Bir konuşma yapın, takip soruları sorun
5. **Temiz Çıkış**: Bittiğinde `quit` yazın

---

## ✅ Başarı Kriterleri

Şunlar olduğunda çalıştığını bileceksiniz:
- ✅ Asistan sorulara yanıt veriyor
- ✅ Uygun araçları kullanıyor (KB veya Web)
- ✅ Doğru yanıtlar sağlıyor
- ✅ Çıktıda hata yok

---

## 🚀 Test Etmeye Hazır mısınız?

Bu komutu çalıştırın ve sohbete başlayın:
```bash
python chat_assistant.py
```

Başlamak için sorun: **"RAG nedir?"** 🎉
