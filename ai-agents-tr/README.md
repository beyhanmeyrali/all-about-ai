**Not:** `ai-agents-tr` klasörü, orijinal `ai-agents` klasörünün Türkçe çevirisidir. Geliştirme ve test süreçleri orijinal klasörde tamamlandığında, bu `-tr` klasörü birebir aynı kod içeriğiyle güncellenir; ancak tüm yorum satırları ve README dosyaları Türkçe olarak sunulur.

# Yapay Zeka Ajanları: Sıfırdan Zirveye 🤖

> Sadece *nasıl* kullanılacağını değil, *neden* frameworklere ihtiyacınız olduğunu anlayarak üretim seviyesinde yapay zeka ajanları oluşturmayı öğrenin.

[![Python](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLMs-blue.svg)](https://ollama.ai/)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agents-orange.svg)](https://github.com/langchain-ai/langgraph)

**Oluşturan:** [Beyhan MEYRALI](https://www.linkedin.com/in/beyhanmeyrali/)

> 🔗 **LinkedIn'de Öne Çıkanlar:** [Duyurunun tamamını okuyun](https://lnkd.in/dDJE6VZH)

---

## 🎯 Felsefe

**ChatGPT'ye bir mesaj gönderdiğinizde tam olarak ne olduğunu biliyor musunuz?**

Çoğu eğitim, karmaşıklığı kütüphanelerin arkasına gizler. "Sadece bu framework'ü içe aktarın ve çalıştırın."

**Ben, öğrenmenin en iyi yolunun sıfırdan, yerel olarak inşa etmek ve değişkenlerin debugger'da nasıl değiştiğini izlemek olduğuna inanıyorum.**

### YZ Frameworklerini Körüne Kullanmayın. Önce *Neden* İhtiyacınız Olduğunu Öğrenin. 🛠️

İşte bu yüzden bu açık kaynak serisini başlattım: **Yapay Zeka Ajanları - Sıfırdan Zirveye.**

Çoğu eğitim doğrudan karmaşık frameworklere atlar ve sizi aslında ne olduğu konusunda kafanız karışık bırakır.

**Bu repo tam tersi bir yaklaşımı benimsiyor.**

---

## 🗺️ Yol Haritası - Ham Python'dan Üretime

Temelden inşa ediyoruz:

1.  **Temel:** Ham HTTP çağrıları ve OOP Python sınıfları ✅ *Şu an mevcut!*
2.  **Mekanik:** Manuel araç çağırma ve özyineleme (recursion) ✅ *Şu an mevcut!*
3.  **Farkındalık:** Manuel durum yönetiminin *neden* karmaşıklaştığını anlamak
4.  **Çözüm:** Frameworklerin Tanıtımı (LangChain, LangGraph, CrewAI) ✅ *Şu an mevcut!*
5.  **Entegrasyon:** Vektör veritabanları ile RAG Sistemleri 🚧 *Yakında*
6.  **Hafıza:** Letta (MemGPT) ile uzun süreli bağlam 🚧 *Yakında*
7.  **Ses:** Tam Sesli Asistan 🚧 *Yakında*

---

## 🎓 Bu Repoyu Nasıl Kullanmalısınız

1.  Teori için her klasördeki **README'yi okuyun**
2.  Pratiği görmek için **Kodu bir debugger ile çalıştırın**
3.  **Yorumları İnceleyin** - Her betikte kapsamlı açıklamalar var

Her şey yerel olarak **Ollama** ve **Qwen** ile çalışır. **API anahtarı gerekmez.**

---

## 🚀 Ne İnşa Edeceksiniz

Bu rehberin sonunda, ChatGPT'nin ses moduna benzer **tam işlevsel bir Sesli GPT** inşa edeceksiniz, şunları içerecek:
- 🎙️ Gerçek zamanlı konuşma tanıma (Whisper)
- 🧠 Akıllı konuşma yönetimi (LangGraph)
- 💾 Uzun süreli hafıza (Letta/MemGPT)
- 🔧 Araç kullanımı ve fonksiyon çağırma
- 🗣️ Doğal metin-konuşma yanıtları
- 🏠 **%100 makinenizde yerel olarak çalışır**

---

## 📖 Öğrenme Felsefesi

### Bu Rehber Neden Farklı

1.  **Framework Kullanmadan Önce Sıfırdan İnşa Et** - Sadece "nasıl"ı değil, "neden"i anla
2.  **Önce-Yerel** - Her şey Ollama (yerel LLM'ler) ve yerel Whisper üzerinde çalışır
3.  **Debugger Dostu** - Bir debugger ile adım adım ilerlemek için tasarlanmış, yoğun yorumlu kod
4.  **HTTP/REST Örnekleri** - Her örnek `curl` komutları içerir, böylece HTTP katmanını anlarsınız
5.  **Uygulamalı** - Oyuncak örnekler değil, gerçek uygulamalar inşa edin
6.  **Kara Kutu Yok** - LLM'lerin, araçların, ajanların ve hafızanın arka planda nasıl çalıştığını anlayın

### Önemli Kavram: LLM'ler Durumsuzdur (Stateless)!

🔴 **Kritik Anlayış**: LLM'ler veri SAKLAMAZ. Onlar hesap makineleri gibidir:
- Girdi → İşleme → Çıktı
- Önceki konuşmaların hafızası yoktur (konuşma geçmişini göndermezseniz)
- Verileriniz hakkında bilgisi yoktur (fine-tune etmezseniz veya RAG kullanmazsanız)
- Her API çağrısı bağımsızdır

Bu yüzden şunlara ihtiyacımız var:
- **Bağlam yönetimi** - Konuşma geçmişini gönderme
- **RAG (Erişim)** - Vektör veritabanlarından ilgili verileri getirme
- **Hafıza sistemleri** - Uzun süreli bağlamı kalıcı hale getirme (Letta/MemGPT)
- **Fine-tuning** - Model ağırlıklarını gerçekten değiştirme (bkz. `../fine-tuning/`)

---

## 🗂️ Kurs Yapısı

### 📚 [00-llm-basics](./00-llm-basics) - Temeli Anlamak
**Süre:** 2-3 saat

**Ne Öğreneceksiniz:**
- LLM'ler aslında nasıl çalışır (durumsuz hesaplama)
- LLM'ler neden hiçbir şeyi "hatırlamaz"
- Ollama ile temel API çağrıları
- Daha iyi UX için akış (streaming) yanıtları
- HTTP anlayışı için basit curl örnekleri
- Prompt teknikleri ve sistem promptları

**Ana Fikir:** LLM'ler güçlü örüntü eşleştiricilerdir, veritabanı değildirler.

---

### 🔧 [01-tool-calling](./01-tool-calling) - LLM'lere Süper Güçler Vermek
**Süre:** 3-4 saat

**Ne Öğreneceksiniz:**
- Fonksiyon/araç çağırma temelleri
- LLM'ler araçları ne zaman kullanacağına nasıl karar verir
- **Özyinelemeli (Recursive) araç çağırma** (işin sırrı!)
- Gerçek dünya örnekleri: Hava durumu API'si, Veritabanı sorguları
- Hata yönetimi ve yeniden deneme mantığı
- Çok adımlı araç orkestrasyonu

**Ana Örnekler:**
- ✅ Temel hava durumu aracı (tek çağrı)
- ✅ ERP/Veritabanı entegrasyonu
- ✅ Sırayla birden fazla aracı çağırabilen özyinelemeli ajan
- ✅ Her uç nokta için curl örnekleri

**Ana Fikir:** Araçlar, LLM'leri sohbet botlarından ajanlara dönüştürür.

---

## 🤔 Neden Frameworklere İhtiyacımız Var? (Farkındalık)

**Bu en önemli bölümdür.** `01-tool-calling` içinde manuel araç çağırmayı inşa ettikten sonra temelleri anlayacaksınız. Ancak işler karmaşıklaştığında ne olur?

### Sorun: Manuel Durum Yönetimi Hızla Karmaşıklaşır

Diyelim ki manuel bir özyinelemeli ajan inşa ettiniz (örneğin `01-tool-calling/03_recursive_agent.py` gibi). Basit durumlar için harika çalışır:

```python
# Basit durum: Gayet iyi çalışır!
Kullanıcı: "Tokyo'da hava nasıl?"
→ LLM get_weather("Tokyo") çağırır
→ Sonucu döndür
✅ 2 adımda bitti
```

Peki ya bu gerçek dünya senaryoları?

#### Senaryo 1: Dallanan Mantıkla Çok Adımlı İşlem
```python
Kullanıcı: "En iyi 3 yapay zeka şirketini araştır, sonra her biri için:
       1. Hisse senedi fiyatını al
       2. En son haberlerini analiz et
       3. Onları karşılaştır ve birini öner"

Manuel yaklaşım sorunları:
❌ Hangi şirkette olduğunuzu nasıl takip edersiniz? (Durum yönetimi)
❌ 2. adım bir şirket için başarısız olursa ne olur? (Hata kurtarma)
❌ Araştırmayı nasıl paralel hale getirirsiniz? (Eşzamanlılık)
❌ Yarıda çökerse nasıl devam edersiniz? (Kalıcılık)
❌ Hangi adımın başarısız olduğunu nasıl ayıklarsınız? (Gözlemlenebilirlik)
```

#### Senaryo 2: Koşullu Döngüler
```python
Kullanıcı: "Paris'te geceliği 100$'ın altında bir otel bulana kadar aramaya devam et"

Manuel yaklaşım sorunları:
❌ Vazgeçmeden önce kaç iterasyon? (Döngü kontrolü)
❌ Sonsuz döngüleri nasıl önlersiniz? (Güvenlik)
❌ Neleri denediğinizi nasıl takip edersiniz? (Hafıza)
❌ Ya LLM halüsinasyon görür ve aracı hiç çağırmazsa? (Doğrulama)
```

#### Senaryo 3: İnsan Döngüde (Human-in-the-Loop)
```python
Kullanıcı: "Bir e-posta taslağı hazırla, incelememe izin ver, sonra gönder"

Manuel yaklaşım sorunları:
❌ Yürütmeyi nasıl duraklatıp onay beklersiniz? (Kesmeler)
❌ Tam olarak aynı durumdan nasıl devam edersiniz? (Kontrol noktası oluşturma)
❌ Kullanıcı taslağı değiştirmek isterse ne olur? (Durum güncellemeleri)
```

#### Senaryo 4: Çoklu Ajan İşbirliği
```python
Kullanıcı: "Bir araştırmacı veri bulsun, bir analist işlesin,
       ve bir yazar rapor oluştursun"

Manuel yaklaşım sorunları:
❌ Ajanlar nasıl iletişim kurar? (Mesaj iletimi)
❌ Ajanlar arasında nasıl yönlendirme yaparsınız? (Orkestrasyon)
❌ Ajanların farklı araçlara ihtiyacı varsa ne olur? (Bağlam izolasyonu)
❌ 10 ajan × 10 araç = 100 aracı nasıl yönetirsiniz? (Bağlam şişmesi)
```

### Manuel Çözüm Bir Kabusa Dönüşür

Tüm bunları manuel olarak halletmeye çalışırsanız, kodunuz şuna dönüşür:

```python
# Sizin güzel 50 satırlık özyinelemeli ajanınız şuna dönüşür...
class ManuelKarmasikAjan:
    def __init__(self):
        self.state = {}  # Manuel durum takibi
        self.history = []  # Manuel geçmiş
        self.checkpoints = {}  # Manuel kalıcılık
        self.retry_counts = {}  # Manuel hata yönetimi
        self.loop_guards = {}  # Manuel döngü önleme
        self.pending_approvals = {}  # Manuel insan-döngüde
        # ... 500 satır daha basmakalıp kod ...
    
    def execute(self, query):
        # 1000 satırlık if/else makarna kodu
        # Bunu ayıklarken iyi şanslar! 😱
```

**Aslında bir framework'ü yeniden inşa ediyorsunuz... ama kötü bir şekilde.**

### Sahneye Çıkar: Ajan Frameworkleri

İşte **tam da bu yüzden** LangGraph ve CrewAI gibi frameworkler var. Şunları sağlarlar:

| Sorun | Framework Çözümü |
|---------|-------------------|
| Durum yönetimi | Tip tanımlı şemalarla yerleşik durum grafikleri |
| Hata kurtarma | Otomatik yeniden denemeler ve yedek yollar |
| Kalıcılık | İş akışlarını sürdürmek için kontrol noktaları (checkpointers) |
| Döngüler & çevrimler | Maksimum iterasyonlu kontrollü çevrimler |
| İnsan-döngüde | Kesme/devam etme mekanizmaları |
| Çoklu ajan | Süpervizör kalıpları ve mesaj yönlendirme |
| Bağlam şişmesi | Hiyerarşik grafikler ve araç yönlendirme |
| Hata ayıklama | Görsel grafik inceleme ve izleme |

### "Aha!" Anı

Manuel durum yönetimiyle boğuştuktan sonra şunları takdir edeceksiniz:

```python
# LangGraph: Aynı karmaşık iş akışı 50 satırda
from langgraph.graph import StateGraph, END

graph = StateGraph(AgentState)
graph.add_node("researcher", research_node)
graph.add_node("analyst", analyst_node)
graph.add_node("writer", writer_node)
graph.add_conditional_edges("researcher", should_continue)
graph.add_edge("analyst", "writer")
graph.set_entry_point("researcher")

app = graph.compile(checkpointer=MemorySaver())  # ← Kalıcılık!
result = app.invoke(input, config={"thread_id": "123"})  # ← Devam ettirilebilir!
```

**İşte frameworklerin gücü budur.** Sihir değil—sadece yaygın kalıplar için iyi tasarlanmış soyutlamalar.

---

### 🕸️ [02-agent-frameworks](./02-agent-frameworks) - Profesyonel Ajan Geliştirme
**Süre:** 6-8 saat

**Ne Öğreneceksiniz:**
- **LangGraph** - Karmaşık iş akışları için durum makineleri
- **CrewAI** - Çoklu ajan işbirliği
- Ne zaman framework, ne zaman ham araç çağırma kullanılmalı
- Grafik tabanlı ajan tasarım kalıpları
- Ajan yürütme akışlarını ayıklama

**Projeler:**
- 🎯 Müşteri destek ajanı (LangGraph)
- 🎯 Çoklu ajan araştırma ekibi (CrewAI)
- 🎯 İş akışı otomasyon ajanı

**Ana Fikir:** Frameworkler, karmaşık ajan davranışları için yapı sağlar.

---

### 📊 [03-rag-systems](./03-rag-systems) - LLM'lere Verilerinizi Öğretmek
**Süre:** 5-6 saat

**Ne Öğreneceksiniz:**
- Vektör veritabanları (Qdrant, ChromaDB)
- Embeddingler ve anlamsal arama
- Belge işleme ve parçalama stratejileri
- LangGraph entegrasyonu ile RAG
- Performans optimizasyonu

**RAG Neden Önemli:**
- LLM'ler SİZİN verilerinizi bilmez
- Fine-tuning pahalı ve yavaştır
- RAG gerçek zamanlı, güncellenebilir bilgi sağlar
- Özel/dinamik veriler için uygun maliyetlidir

**Projeler:**
- 📚 Belge Soru-Cevap sistemi
- 📚 Kod arama asistanı
- 📚 Şirket bilgi tabanı

**Ana Fikir:** RAG, LLM'leri sizin dünyanıza bağlama yolunuzdur.

---

### 🧠 [04-memory-systems](./04-memory-systems) - Uzun Süreli Bağlam
**Süre:** 4-5 saat

**Ne Öğreneceksiniz:**
- Bağlam pencereleri neden yeterli değil
- **Letta (MemGPT)** mimarisi
- Uzun süreli hafıza kalıpları
- Bağlam önceliklendirme stratejileri
- Letta + LangGraph entegrasyonu

**Hafıza Sorunu:**
```
Hafıza Olmadan:
Kullanıcı: "Adım John"
YZ: "Tanıştığımıza memnun oldum, John"
[5 dakika sonra]
Kullanıcı: "Adım ne?"
YZ: "Bilmiyorum, bana söylemedin"

Letta ile:
Kullanıcı: "Adım John"
YZ: "Tanıştığımıza memnun oldum, John" [uzun süreli hafızaya kaydeder]
[5 dakika sonra]
Kullanıcı: "Adım ne?"
YZ: "Adın John!" [hafızadan getirir]
```

**Ana Fikir:** Hafıza sistemleri gerçekten kalıcı asistanlar sağlar.

---

### 🎙️ [05-voice-gpt](./05-voice-gpt) - Sesli Asistanınızı İnşa Etmek
**Süre:** 8-10 saat

**Ne Öğreneceksiniz:**
- **Whisper** entegrasyonu (yerel konuşmadan yazıya)
- Yerel modellerle metinden konuşmaya (TTS)
- Gerçek zamanlı ses akışı
- Konuşmalar için LangGraph durum yönetimi
- Her şeyi birleştirme: Whisper → LangGraph → Letta → TTS

**Final Projesi: Sesli GPT**
```
Siz → Whisper (STT) → LangGraph (Ajan) → Letta (Hafıza) → TTS → Siz
          ↓                    ↓                  ↓
      "Hava nasıl?"       [Araçları kullanır] [Önceki konuşmaları
                           [RAG'dan getirir]    hatırlar]
```

**Ana Özellikler:**
- 🎤 Eller serbest sesli etkileşim
- 🧠 Konuşma bağlamını hatırlar
- 🔍 Belgelerinizi arayabilir (RAG)
- 🛠️ Araçları çağırabilir (hava durumu, takvim vb.)
- 🏠 %100 yerel olarak çalışır

**Ana Fikir:** Bu, öğrendiğiniz her şeyin zirvesidir.

---

## 🚀 Hızlı Başlangıç

### Ön Koşullar & Kurulum

#### Adım 1: Ollama Kurulumu

**Windows:**
```powershell
# https://ollama.ai/download/windows adresinden indirin
# Veya winget kullanın
winget install Ollama.Ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**macOS:**
```bash
brew install ollama
```

**Kurulumu Doğrulayın:**
```bash
ollama --version
```

#### Adım 2: Gerekli Modelleri Çekin

Yerel ajanlar için 2025'teki en iyi akıl yürütme + araç çağırma modeli olan **Qwen3:8b**'yi kullanıyoruz:

```bash
# Ana LLM (Q4_K_M kuantizasyon - en iyi kalite/hız dengesi)
ollama pull qwen3:8b

# RAG için embedding modeli (buna daha sonra ihtiyacınız olacak)
ollama pull nomic-embed-text

# Modellerin hazır olduğunu doğrulayın
ollama list
```

**Neden Qwen3:8b?**
- ✅ **Mükemmel araç çağırma** - Yerel fonksiyon çağırma desteği
- ✅ **Güçlü akıl yürütme** - Birçok 13B modelden daha iyi performans gösterir
- ✅ **Sorunsuz çalışır** - ~5GB RAM, CPU'da hızlı, GPU'da çok hızlı
- ✅ **8B parametre** - Kalite vs kaynak kullanımı için tatlı nokta
- ✅ **128K bağlam penceresi** - Büyük konuşmaları/belgeleri yönetir
- ✅ **En yeni model** - 2024 sonlarında yayınlandı, son teknoloji mimari

#### Adım 3: Ollama Sunucusunu Başlatın

```bash
# Ollama kurulumdan sonra varsayılan olarak servis olarak çalışır
# Ancak gerekirse manuel olarak başlatın:
ollama serve

# Sunucuyu test edin
curl http://localhost:11434/api/tags
```

#### Adım 4: Docker Kurulumu (Sadece Qdrant için)

Docker'ı **SADECE** Qdrant (vektör veritabanı) için kullanıyoruz. Diğer her şey yerel çalışır.

**Windows/Mac:**
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) yükleyin

**Linux:**
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
# Grup değişikliklerinin etkili olması için çıkış yapıp tekrar girin
```

#### Adım 5: Qdrant'ı Başlatın (Tek Komut!)

```bash
cd ai-agents

# docker-compose kullanarak Qdrant'ı başlatın
docker compose up -d

# Qdrant'ın çalıştığını doğrulayın
curl http://localhost:6333/health

# Qdrant Web Arayüzüne Erişim
# Tarayıcıyı açın: http://localhost:6333/dashboard
```

**Docker'da ne çalışır:**
- ✅ Qdrant (vektör veritabanı) - İzolasyon ve kolay yönetim için Docker

**Yerel olarak ne çalışır (Docker'da DEĞİL):**
- ✅ Ollama (daha iyi GPU erişimi, daha hızlı çıkarım)
- ✅ Python ajanları (IDE'nizle daha kolay hata ayıklama)
- ✅ SQLite (dosya tabanlı, sunucu gerekmez)
- ✅ Whisper, TTS (daha iyi donanım erişimi)

#### Adım 6: Python Bağımlılıklarını Yükleyin

```bash
# Sanal ortam oluşturun (önerilir)
python -m venv venv
source venv/bin/activate  # Windows'ta: venv\Scripts\activate

# Tüm kurs için tüm bağımlılıkları yükleyin
pip install -r requirements.txt

# Veya gerektiğinde bölüm başına yükleyin
cd 00-llm-basics
pip install -r requirements.txt
```

### İlk Yapay Zeka Ajanınız (30 saniye)

```bash
# curl ile test edin
curl -X POST http://localhost:11434/api/chat -d '{
  "model": "qwen3:8b",
  "messages": [{"role": "user", "content": "Merhaba! 2+2 kaçtır?"}],
  "stream": false
}'

# Veya ilk örneği çalıştırın
cd 00-llm-basics
python 01_basic_chat.py
```

### Kurulumunuzu Doğrulayın

Bu hızlı sağlık kontrolünü çalıştırın:

```bash
# Ollama'yı kontrol et
ollama list | grep qwen3:8b

# Qdrant'ı kontrol et (başlattıysanız)
curl http://localhost:6333/health

# Python ortamını kontrol et
python -c "import requests; print('✅ Python kurulumu TAMAM')"
```

Tüm kontroller geçerse, başlamaya hazırsınız! 🎉

---

## 💡 Temel Kavramlar Açıklaması

### 0. Her Yazılım Yapay Zeka Kullanabilir (Sadece REST API!)

**🔑 Kritik Anlayış:** LLM'leri kullanmak için Python'a, frameworklere veya özel kütüphanelere ihtiyacınız yok!

LLM'lere **basit HTTP REST API çağrıları** ile erişilir. Bu şu anlama gelir:

```javascript
// JavaScript/Node.js
fetch('http://localhost:11434/api/chat', {
  method: 'POST',
  body: JSON.stringify({
    model: 'qwen3:8b',
    messages: [{role: 'user', content: 'Merhaba!'}]
  })
})

// Hatta curl!
curl -X POST http://localhost:11434/api/chat -d '{...}'
```

**Bunun Anlamı:**
- ✅ **Mevcut web uygulamanıza** YZ ekleyin (PHP, Ruby, Java, .NET vb.)
- ✅ REST çağrıları ile **eski sistemlerle** entegre edin
- ✅ Herhangi bir dilde **herhangi bir HTTP istemci kütüphanesini** kullanın
- ✅ Python'da yeniden yazmaya gerek yok!
- ✅ **Mobil uygulamalarla** çalışır (iOS, Android)
- ✅ **Excel VBA** bile HTTP üzerinden LLM'leri çağırabilir!

**Bu kursta Python kullanıyoruz çünkü:**
- Öğrenmesi ve okuması kolay
- Harika hata ayıklama araçları
- Zengin ekosistem (LangGraph, CrewAI vb.)

**Ama unutmayın:** REST API her yerden çalışır!

---

### 1. Bağlam Şişmesi Sorunu (Neden Hafıza Yönetimine İhtiyacınız Var)

**🔴 Kritik Sorun:** Her araç çağrısı bağlam pencerenizi PATLATIR!

**Örnek - Basit Bir Hava Durumu Sorgusu:**
```
Tur 1:
Kullanıcı: "Tokyo'da hava nasıl?"
→ Bağlam: ~20 token

LLM Yanıtı: [tool_call: get_weather(city="Tokyo")]
→ Bağlam: ~50 token

Araç Sonucu: {"temp": 25, "condition": "sunny", "humidity": 60, ...}
→ Bağlam: ~100 token

LLM Final Cevabı: "Tokyo'da hava 25°C ve güneşli"
→ Bağlam: ~120 token

TOPLAM: TEK bir soru için 120 token
```

**Şimdi bir konuşmada 10 araç çağrısı ile:**
```
Kullanıcı 10 soru sorar → 10 araç çağrısı → 10 sonuç

Bağlam boyutu: ~1,200 token (sadece araçlar için!)
Artı konuşma geçmişi: ~2,000 token
TOPLAM: 3,200 token

Sorun: Bağlam pencerenizi HIZLA tüketiyorsunuz!
```

#### Bu Neden Önemli

**Bağlam Penceresi Sınırları:**
| Model | Bağlam Sınırı | Şişmeden Sonra Maliyet |
|-------|---------------|---------------------|
| Qwen3:8b | 128K token | Ücretsiz (yerel) ama daha yavaş |
| GPT-4 | 128K token | 1 milyon token başına 10$+ |
| Claude | 200K token | 1 milyon token başına 15$+ |

**Şişme Kademesi:**
```
5 araç kullanan turlu konuşma:

Tur 1:  120 token
Tur 2:  120 + 120 = 240 token
Tur 3:  240 + 120 = 360 token
Tur 4:  360 + 120 = 480 token
Tur 5:  480 + 120 = 600 token

10 turdan sonra: 1,200 token
50 turdan sonra: 6,000 token
100 turdan sonra: 12,000 token

HER SEFERİNDE tüm önceki araç çağrılarını + sonuçlarını gönderiyorsunuz!
```

#### Kısa Süreli vs Uzun Süreli Hafıza (Çözüm)

**Kısa Süreli Hafıza (Çalışma Hafızası):**
```python
# LLM'in şu anda gördüğü
messages = [
    {"role": "system", "content": "Sen yardımcı bir asistansın"},
    {"role": "user", "content": "Hava nasıl?"},
    {"role": "assistant", "tool_calls": [...]},  # ← Şişme!
    {"role": "tool", "content": "{...}"},        # ← Şişme!
    {"role": "assistant", "content": "Güneşli"}
]

Sorun: Bunu yönetmezseniz bu liste SONSUZA KADAR büyür!
```

**Uzun Süreli Hafıza (Kalıcı Depolama):**
```python
# Letta/MemGPT yaklaşımı
core_memory = {
    "user_preferences": "Celsius sever, nemden nefret eder",
    "conversation_style": "Kısa cevapları tercih eder",
    "important_facts": "Tokyo'da yaşıyor, uzaktan çalışıyor"
}

# Sadece mevcut soru için gerekeni getir
# Şişmiş araç çağrı geçmişi yok!
```

#### Frameworkler Bağlam Şişmesini Nasıl Çözer

**❌ Saf Yaklaşım (Frameworkler Olmadan Yapacağınız):**
```python
# Her turda HER ŞEYİ gönder
messages = [...]  # Tarihin tüm 10,000 tokenı
response = llm.chat(messages)  # Yavaş! Pahalı!
```

**✅ LangGraph Çözümü:**
```python
# Kontrol Noktası Oluşturma - Durumu kaydet, bağlamı kırp
from langgraph.checkpoint import MemorySaver

checkpointer = MemorySaver()

# Aktif bağlamda sadece son N turu tut
# Eski turlar kontrol noktası deposuna kaydedilir
graph = StateGraph(state_schema)
graph.add_node("agent", agent_node)
graph.compile(checkpointer=checkpointer)

# Bağlam küçük kalır, geçmiş geri getirilebilir!
```

**✅ CrewAI Çözümü:**
```python
# Her ajanın sınırlı bağlamı vardır
# Yönetici ajanlar arasında orkestrasyon yapar, özetler
class ResearchCrew:
    def __init__(self):
        # Araştırmacı sadece araştırma bağlamını görür
        self.researcher = Agent(
            role="Researcher",
            memory=ShortTermMemory(max_tokens=2000)
        )
        # Yazar sadece son özeti görür
        self.writer = Agent(
            role="Writer",
            memory=ShortTermMemory(max_tokens=2000)
        )
```

**✅ Letta (MemGPT) Çözümü:**
```python
# Çekirdek hafıza (her zaman yüklü) + Arşiv hafızası (gerektiğinde getirilir)
agent = Agent(
    core_memory={
        "persona": "...",      # ~200 token (her zaman bağlamda)
        "human": "..."         # ~200 token (her zaman bağlamda)
    },
    archival_memory=QdrantMemory(  # Sınırsız! RAG ile getirilir
        collection_name="user_123_memories"
    )
)

# Sadece ilgili hafızalar bağlama çekilir
# Konuşma geçmişinin %99'u Qdrant'ta kalır!
```

---

### 2. LLM'ler Veritabanı DEĞİLDİR

```python
# ❌ YANLIŞ ZİHİNSEL MODEL
llm.remember("En sevdiğim renk mavi")
print(llm.recall("En sevdiğim renk ne?"))  # Bu mevcut değil!

# ✅ DOĞRU ZİHİNSEL MODEL
messages = [
    {"role": "user", "content": "En sevdiğim renk mavi"},
    {"role": "assistant", "content": "Anlaşıldı!"},
    {"role": "user", "content": "En sevdiğim renk ne?"}
]
# LLM her seferinde TÜM mesajları görür ve yanıt üretir
response = llm.chat(messages)
```

### 3. Araç Çağırma Sadece Yapılandırılmış Çıktıdır

```python
# LLM araçları "çalıştırmaz"
# "Lütfen bu fonksiyonu çalıştır" diyen JSON çıktısı verir
{
  "function": "get_weather",
  "arguments": {"city": "Tokyo"}
}

# Fonksiyonu SİZ çalıştırırsınız
weather = get_weather("Tokyo")

# Sonra sonucu LLM'e SİZ geri gönderirsiniz
messages.append({"role": "tool", "content": weather})
response = llm.chat(messages)
```

---

## 🛠️ Teknoloji Yığını

### Tam Yerel Yığın (2025 Üretime Hazır)

| Bileşen | Teknoloji | Neden Bu Seçim |
|-----------|-----------|-----------------|
| **LLM** | Qwen3:8b (Q4_K_M) | En iyi araç çağırma modeli, 128K bağlam, güçlü akıl yürütme |
| **Embeddingler** | nomic-embed-text | #1 yerel embedding modeli, Qdrant-optimize |
| **Vektör VT** | Qdrant (Docker) | Çok hızlı, HNSW, payload filtreleme, binary kuantizasyon |
| **İlişkisel VT** | SQLite | Sıfır yapılandırma, dosya tabanlı, konuşma geçmişi için mükemmel |
| **Ajan Framework** | LangGraph | Üretim sınıfı durum makineleri, en iyi hata ayıklama |
| **Çoklu Ajan** | CrewAI | İşbirlikçi ajan ekipleri, rol tabanlı iş akışları |
| **Hafıza** | Letta (MemGPT) | Uzun süreli hafıza, kişilik evrimi |
| **Gözlemlenebilirlik** | LangFuse (yerel) | Açık kaynak LLM izleme, Docker olmadan çalışır |
| **Konuşmadan Yazıya** | Whisper (yerel) | OpenAI'nin modeli, yerel çalışır |
| **Metinden Konuşmaya** | Coqui TTS | Yerel, yüksek kaliteli ses sentezi |
| **Web Otomasyonu** | Playwright | Ajanlar için tarayıcı kontrolü |
| **API Framework** | FastAPI | Modern Python web framework'ü |
| **Arayüz** | Streamlit/Gradio | Hızlı prototipleme, güzel arayüzler |

### Neden Bu Yığın Kazanır

**Cloud LLM'lere Karşı:**

| Cloud LLM'ler | Yerel (Ollama + Qwen3:8b) |
|------------|---------------------------|
| 💰 Token başına ödeme (1M token için 0.50$-2$) | ✅ **Sonsuza kadar ücretsiz** |
| 🔓 Veri 3. tarafa gönderilir | ✅ **%100 özel** |
| 🌐 İnternet gerektirir | ✅ **Çevrimdışı çalışır** |
| ⚡ Çok hızlı (büyük veri merkezleri) | ⚡ **Yeterince hızlı** (5-10 tok/sn CPU, 80-120 GPU) |
| 🎯 En iyi kalite (GPT-4) | 🎯 **Mükemmel kalite** (akıl yürütmede GPT-3.5'i yener) |
| 🔧 API hız sınırları | ✅ **Sınır yok** |
| 📊 Sınırlı bağlam (8-32K) | ✅ **128K bağlam penceresi** |

**En İyi Uygulama:** Bu yığınla yerel olarak prototipleyin, kritik parçaları gerekirse buluta dağıtın.

### Donanım Gereksinimleri

**Minimum (Sadece CPU):**
- 16GB RAM (Model için 12GB + sistem için 4GB)
- 4-çekirdekli CPU
- 15GB disk alanı

**Önerilen (GPU):**
- 16GB RAM
- 8-çekirdekli CPU
- **6GB+ VRAM'li NVIDIA GPU** (RTX 3060, 4060 Ti vb.)
- 50GB disk alanı (modeller + vektör indeksleri için)

---

## 📚 Öğrenme Yolu Önerileri

### Yol 1: Tam Başlangıç (30-40 saat)
```
00-llm-basics → 01-tool-calling → 02-agent-frameworks → 05-voice-gpt
```
*Başlangıçta RAG ve Letta'yı atlayın, temel ajan kavramlarına odaklanın*

### Yol 2: Üretime Hızlı Geçiş (15-20 saat)
```
01-tool-calling → 02-agent-frameworks (Sadece LangGraph) → 03-rag-systems
```
*LLM temellerini bildiğinizi varsayar, CrewAI ve Sesi atlar*

---

## 🤝 Katkıda Bulunma

Bu repo, topluluk için bir öğrenme kaynağıdır. Şunları bulursanız PR açmaktan çekinmeyin:
- Hatalar
- Daha iyi açıklamalar
- Yeni ajan örnekleri
- Performans iyileştirmeleri

---

## 📄 Lisans

MIT Lisansı - İstediğiniz gibi kullanın, öğrenin ve inşa edin!
