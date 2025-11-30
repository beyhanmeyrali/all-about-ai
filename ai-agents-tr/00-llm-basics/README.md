# 00 - LLM Temelleri: Temeli Anlamak 🧠

> LLM'lerin aslında ne olduğunu, nasıl çalıştığını ve neden hiçbir şeyi "hatırlamadığını" öğrenin

---

## 🎯 Öğrenme Hedefleri

Bu bölümün sonunda şunları anlayacaksınız:
- ✅ LLM'ler nedir ve ne DEĞİLDİR
- ✅ LLM'ler neden veri saklamaz (durumsuz hesaplama)
- ✅ Ollama'ya temel API çağrıları nasıl yapılır
- ✅ Yapay zeka frameworklerinin arkasındaki HTTP/REST katmanı
- ✅ Akış (streaming) ve akış olmayan yanıtlar
- ✅ Sistem promptları ve konuşma geçmişi
- ✅ Fine-tuning (ince ayar) ile promptlama arasındaki fark

**Gerekli Süre:** 2-3 saat

---

## 🤔 Bunu Neden Anlamanız Gerekiyor?

**Çoğu eğitim bunu atlar ve doğrudan frameworklere geçer. Bu bir hatadır.**

### Bu Bölümü atlarsanız Ne Olur?

❌ **LLM'lerin bir şeyleri "hatırladığını" sanırsınız** → Konuşmalar devam etmediğinde uygulamalarınızda hatalar olur
❌ **Bağlam yönetiminin neden önemli olduğunu anlamazsınız** → Token sınırlarına takılır ve nedenini merak edersiniz
❌ **Frameworkler kafanızı karıştırır** → LangChain, LangGraph sihir gibi görünür
❌ **Sorunları ayıklayamazsınız** → İşler bozulduğunda, sorunun kodunuzda mı yoksa LLM'de mi olduğunu bilemezsiniz
❌ **Paranızı boşa harcarsınız** → Her API çağrısında gereksiz bağlam gönderirsiniz

### Bunu Anlayarak Ne Kazanacaksınız?

✅ ChatGPT, Claude veya herhangi bir LLM'i çağırdığınızda **tam olarak ne olduğunu bilin**
✅ **Güvenle hata ayıklayın** - Sadece framework'ü değil, HTTP katmanını anlayın
✅ **Herhangi bir dilde inşa edin** - Sadece REST API olduğunu fark edin; JavaScript, Java, Go, ne isterseniz kullanın
✅ **Maliyetleri optimize edin** - Tokenları, bağlam pencerelerini ve bunları nasıl en aza indireceğinizi anlayın
✅ **Frameworkleri takdir edin** - LangChain'in *neden* var olduğunu anlayın (bu karmaşıklığı yönetiyor!)

### Diğer Her Şeyin Temeli

Bu bölüm şunların temelidir:
- **Araç Çağırma** (01) - LLM'lerin araçları *ne zaman* çağıracağını bilmesi gerekir → durumsuzluğu anlamayı gerektirir
- **Ajan Frameworkleri** (02) - Frameworkler durumu yönetir *çünkü* LLM'ler yönetmez → nedenini anlayacaksınız
- **RAG Sistemleri** (03) - LLM'ler verilerinizi bilmez → erişimin (retrieval) neden gerekli olduğunu anlayacaksınız
- **Hafıza Sistemleri** (04) - Uzun süreli hafıza vardır *çünkü* LLM'ler unutur → sorunu önce göreceksiniz

**Bunu atlayın, diğer her şey kafa karıştırıcı bir sihir olacak. Bunda ustalaşın, diğer her şey mükemmel bir anlam kazanacak.**

---

## 🔑 KRİTİK: Her Yazılım REST API ile Yapay Zeka Kullanabilir!

**LLM'lere dalmadan önce şunu anlayın:**

### Yapay Zeka Kullanmak İçin Python'a İhtiyacınız Yok!

LLM'lere **basit HTTP REST API çağrıları** ile erişilir. Bu şununla aynı teknolojidir:
- Bir hava durumu API'sini çağırmak
- Bir veritabanı API'sinden veri çekmek
- Bir sosyal medya API'sine gönderi yapmak

**Bu, HERHANGİ BİR programlama dilinin yapay zeka kullanabileceği anlamına gelir:**

| Dil | Örnek |
|----------|---------|
| **JavaScript** | `fetch('http://localhost:11434/api/chat', {...})` |
| **Java** | `HttpClient.newHttpClient().send(request, ...)` |
| **C#/.NET** | `await httpClient.PostAsync("...", content)` |
| **Go** | `http.Post("http://localhost:11434/api/chat", ...)` |
| **PHP** | `file_get_contents("...", false, $context)` |
| **Ruby** | `Net::HTTP.post(uri, data)` |
| **Swift** | `URLSession.shared.dataTask(with: request)` |
| **Kotlin** | `OkHttpClient().newCall(request).execute()` |
| **Rust** | `reqwest::post("...").json(&data).send()` |
| **Excel VBA Bile!** | `CreateObject("MSXML2.XMLHTTP")` |

### Bu Kurs Neden Python Kullanıyor?

Python kullanıyoruz çünkü:
- ✅ Öğrenmesi ve okuması kolay (eğitimler için harika)
- ✅ Mükemmel hata ayıklama araçları
- ✅ Zengin yapay zeka ekosistemi (LangGraph, CrewAI, Letta)
- ✅ Yapay zeka topluluğunda popüler

**Ancak temel kavramlar HERHANGİ BİR dilde çalışır!**

### Gerçek Dünya Örneği: Mevcut Uygulamanıza Yapay Zeka Ekleyin

```javascript
// Mevcut Node.js/Express uygulamanız
app.post('/api/summarize', async (req, res) => {
  const document = req.body.document;

  // Ollama'yı çağırın (herhangi bir REST API'yi çağırmakla aynı!)
  const response = await fetch('http://localhost:11434/api/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      model: 'qwen3:8b',
      messages: [{
        role: 'user',
        content: `Summarize this: ${document}`
      }]
    })
  });

  const data = await response.json();
  res.json({ summary: data.message.content });
});

// İşte bu kadar! Uygulamanıza yapay zeka eklediniz!
```

### Bu Kurstaki Her Örnek curl İçerir

Her kavram için `curl` örnekleri sağlıyoruz, böylece:
1. Ham HTTP katmanını anlayabilirsiniz
2. Tercih ettiğiniz dilde uygulayabilirsiniz
3. Kod yazmadan test edebilirsiniz
4. API sorunlarını ayıklayabilirsiniz

**Şimdi LLM'lerin aslında ne olduğunu öğrenelim!**

---

## 🧠 Kritik Kavram: LLM'ler Durumsuzdur (Stateless)

### LLM Nedir?

Bir LLM (Büyük Dil Modeli) esasen şudur:
```
Girdiye dayalı olarak bir sonraki tokenı tahmin eden
çok gelişmiş bir örüntü eşleştirme makinesi
```

Şöyle düşünün:
- 📱 Bir **hesap makinesi**: Girdi → İşlem → Çıktı (hafıza yok)
- 🎰 Bir veritabanı **DEĞİL**: Konuşmalarınızı SAKLAMAZ
- 🔄 Hatırlayan bir şey **DEĞİL**: Her API çağrısı bağımsızdır

### Durumsuz Gerçeklik

```python
# Örnek 1: İlk konuşma
response = llm.chat("Adım John")
# LLM: "Tanıştığımıza memnun oldum, John!"

# Örnek 2: Yeni konuşma (durumsuz!)
response = llm.chat("Adım ne?")
# LLM: "Adını bilmiyorum. Bana söylemedin."

# NEDEN? Çünkü LLM Örnek 1'i "hatırlamadı"!
# Her çağrı bağımsızdır. Depolama yok. Hafıza yok.
```

### Nasıl "Hatırlanır": Konuşma Geçmişini Gönderin

```python
# Doğru yol: Tüm konuşma geçmişini gönderin
messages = [
    {"role": "user", "content": "Adım John"},
    {"role": "assistant", "content": "Tanıştığımıza memnun oldum, John!"},
    {"role": "user", "content": "Adım ne?"}
]
response = llm.chat(messages)
# LLM: "Adın John!"

# LLM "hatırlamaz" - her seferinde TÜM mesajları görür!
```

---

## 📚 Bu Bölüm Neleri Kapsıyor

### Bu Dizindeki Dosyalar

```
00-llm-basics/
├── README.md                    ← Buradasınız
├── requirements.txt             ← Python bağımlılıkları
├── 01_basic_chat.py            ← Basit sohbet örneği
├── 02_streaming_chat.py        ← Akış yanıtları
├── 03_conversation_history.py  ← Bağlam yönetimi
├── 04_system_prompts.py        ← Davranışı kontrol etme
├── 05_curl_examples.sh         ← HTTP katmanı örnekleri
└── theory.md                   ← Derinlemesine inceleme: LLM'ler nasıl çalışır
```

### İlerleme

1. **01_basic_chat.py** - Mümkün olan en basit LLM çağrısı
2. **02_streaming_chat.py** - Gerçek zamanlı yanıtlar (daha iyi UX)
3. **03_conversation_history.py** - Bağlamı sürdürme
4. **04_system_prompts.py** - LLM davranışını kontrol etme
5. **05_curl_examples.sh** - HTTP katmanını anlama

---

## 🚀 Hızlı Başlangıç

### 1. Ollama Kurulumu

```bash
# https://ollama.ai adresini ziyaret edin ve işletim sisteminiz için indirin
# Veya Linux'ta:
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Bir Model Çekin

```bash
# qwen2.5:3b kullanıyoruz - hızlı, hafif, iyi kalite
ollama pull qwen2.5:3b

# Çalıştığını doğrulayın
ollama list
```

### 3. Ollama'yı Test Edin

```bash
# Basit sohbet testi
ollama run qwen2.5:3b "Merhaba! 2+2 kaçtır?"

# API testi
curl http://localhost:11434/api/generate -d '{
  "model": "qwen2.5:3b",
  "prompt": "Merhaba!"
}'
```

### 4. Python Bağımlılıklarını Yükleyin

```bash
cd 00-llm-basics
pip install -r requirements.txt
```

### 5. İlk Örneği Çalıştırın

```bash
python 01_basic_chat.py
```

---

## 📖 Ayrıntılı Örnekler

### Örnek 1: Temel Sohbet (01_basic_chat.py)

**Ne Öğreneceksiniz:**
- Basit bir LLM API çağrısı yapma
- İstek/yanıt yapısını anlama
- Her çağrının neden bağımsız (durumsuz) olduğu

**Ana Kod:**
```python
import requests

# Bir LLM çağrısı SADECE budur: HTTP POST isteği!
response = requests.post('http://localhost:11434/api/chat', json={
    "model": "qwen2.5:3b",
    "messages": [{"role": "user", "content": "Merhaba!"}],
    "stream": false
})

# LLM, üretilen metinle birlikte JSON döndürür
print(response.json()['message']['content'])
```

**curl Eşdeğeri:**
```bash
curl -X POST http://localhost:11434/api/chat -d '{
  "model": "qwen2.5:3b",
  "messages": [{"role": "user", "content": "Merhaba!"}],
  "stream": false
}'
```

**Neler Oluyor:**
1. Mesajınızla birlikte HTTP POST gönderirsiniz
2. Ollama'nın LLM'i metni işler
3. LLM bir yanıt üretir (sonraki tokenları tahmin eder)
4. Ollama JSON yanıtı döndürür
5. **Hiçbir yerde depolama olmaz!**

---

### Örnek 2: Akış Yanıtları (02_streaming_chat.py)

**Ne Öğreneceksiniz:**
- Akış neden kullanıcı deneyimini iyileştirir
- Akış yanıtlarını nasıl işlersiniz
- Token-token üretim

**Ana Kod:**
```python
# Tam yanıtı beklemek yerine, üretildikçe tokenları akıtın
response = requests.post('http://localhost:11434/api/chat', json={
    "model": "qwen2.5:3b",
    "messages": [{"role": "user", "content": "Bir şiir yaz"}],
    "stream": true  # Akışı etkinleştir!
}, stream=True)

# Her token geldiğinde yazdırın
for line in response.iter_lines():
    if line:
        chunk = json.loads(line)
        print(chunk['message']['content'], end='', flush=True)
```

**Neden Akış?**
- ⚡ Kullanıcı yanıtı hemen görür
- 🎯 Uzun yanıtlar için daha iyi UX
- 📊 Beklemek yerine ilerlemeyi gösterir

---

### Örnek 3: Konuşma Geçmişi (03_conversation_history.py)

**Ne Öğreneceksiniz:**
- Birden fazla turda bağlamı nasıl sürdürürsünüz
- Konuşma geçmişini yönetme
- Bağlam sınırlarını anlama

**Ana Kod:**
```python
# Konuşmayı bir listede tutun
conversation = []

# Tur 1
conversation.append({"role": "user", "content": "En sevdiğim renk mavi"})
response = llm_call(conversation)
conversation.append({"role": "assistant", "content": response})

# Tur 2 - LLM "hatırlar" çünkü tam geçmişi gönderiyoruz!
conversation.append({"role": "user", "content": "En sevdiğim renk ne?"})
response = llm_call(conversation)  # LLM TÜM mesajları görür
# Yanıt: "En sevdiğim renk mavi!"
```

**Önemli:**
- LLM her seferinde **tüm konuşmayı** görür
- Geçmişi yönetmekten siz sorumlusunuz
- Daha fazla geçmiş = daha fazla token = daha yavaş/daha pahalı

---

### Örnek 4: Sistem Promptları (04_system_prompts.py)

**Ne Öğreneceksiniz:**
- Sistem promptları ile LLM davranışını kontrol etme
- Özelleştirilmiş asistanlar oluşturma
- Prompt mühendisliği temelleri

**Ana Kod:**
```python
messages = [
    {
        "role": "system",
        "content": "Sen yardımcı bir korsan asistansın. Her zaman bir korsan gibi cevap ver!"
    },
    {
        "role": "user",
        "content": "Hava nasıl?"
    }
]

# LLM cevap verecek: "Arrr! Hava verilerine erişimim yok, ahbap!"
```

**Sistem Prompt Kullanım Durumları:**
- 👨‍💼 Müşteri destek botu (arkadaş canlısı, profesyonel)
- 👨‍💻 Kod asistanı (teknik, özlü)
- 👨‍🏫 Eğitmen (eğitici, sabırlı)
- 🏴‍☠️ Yaratıcı kişilikler (korsan, Shakespeare vb.)

---

### Örnek 5: curl Örnekleri (05_curl_examples.sh)

**Ne Öğreneceksiniz:**
- Tüm yapay zeka frameworklerinin altındaki ham HTTP katmanı
- LLM'leri herhangi bir sisteme (sadece Python değil) nasıl entegre edersiniz
- İstek/yanıt yapısı

**Örnekler:**

```bash
# 1. Temel sohbet
curl -X POST http://localhost:11434/api/chat -d '{
  "model": "qwen2.5:3b",
  "messages": [
    {"role": "user", "content": "Merhaba!"}
  ],
  "stream": false
}'

# 2. Sistem promptu ile
curl -X POST http://localhost:11434/api/chat -d '{
  "model": "qwen2.5:3b",
  "messages": [
    {"role": "system", "content": "Sen yardımcı bir asistansın"},
    {"role": "user", "content": "Merhaba!"}
  ],
  "stream": false
}'

# 3. Geçmişli konuşma
curl -X POST http://localhost:11434/api/chat -d '{
  "model": "qwen2.5:3b",
  "messages": [
    {"role": "user", "content": "Adım John"},
    {"role": "assistant", "content": "Tanıştığımıza memnun oldum, John!"},
    {"role": "user", "content": "Adım ne?"}
  ],
  "stream": false
}'
```

**Bu Neden Önemli:**
- Herhangi bir dil/araç bu API'leri çağırabilir (JavaScript, Java, Go vb.)
- Postman, Insomnia veya herhangi bir HTTP istemcisi kullanabilirsiniz
- LangChain gibi frameworklerin arka planda ne yaptığını anlayın

---

## 🧩 Teori Derinlemesine İnceleme

### LLM'ler Nasıl "Düşünür"?

Şunlar hakkında derinlemesine bilgi için [theory.md](./theory.md) dosyasını okuyun:
- Token tahmini ve olasılık
- Dikkat mekanizmaları (basitleştirilmiş)
- Bağlam penceresi boyutu neden önemlidir
- Çıkarım (inference) ve eğitim (training) arasındaki fark
- Fine-tuning neden kalıcıdır, promptlama geçicidir

**Hızlı Özet:**
```
Eğitim/Fine-tuning:
- Model ağırlıklarını değiştirir (kalıcı)
- GPU, zaman, veri gerektirir
- Detaylar için ../fine-tuning/ bakın

Promptlama (burada yaptığımız):
- Geçici davranış değişikliği
- Sadece farklı metin gönderme
- Model değişikliği yok
```

---

## 🎯 Ana Çıkarımlar

### Şimdi Neleri Anlamalısınız

1. **LLM'ler durumsuzdur**
   - API çağrıları arasında hafıza yoktur
   - Her çağrı bağımsızdır
   - Konuşma geçmişini siz yönetirsiniz

2. **LLM'ler verilerinizi saklamaz**
   - Girdiyi işler ve çıktı üretir
   - Bir veritabanı değil, hesap makinesi gibidir
   - "Hatırlamak" için konuşma geçmişini kullanın

3. **HTTP katmanı basittir**
   - JSON ile POST isteği
   - LLM JSON yanıtı döndürür
   - Herhangi bir dilden/araçtan çağrılabilir

4. **Sistem promptları davranışı kontrol eder**
   - LLM'in nasıl davranması gerektiğini tanımlayın
   - Geçici (sadece o konuşma için)
   - Fine-tuning gibi kalıcı değil

5. **Akış UX'i iyileştirir**
   - Tokenlar üretildikçe gelir
   - Kullanıcı anında ilerlemeyi görür
   - Uzun yanıtlar için daha iyi

---

## 🚀 Sonraki Adımlar

### Şuna Hazırsınız:
✅ [01-tool-calling](../01-tool-calling) - LLM'lere fonksiyon çağırma ile süper güçler verin

### Devam Etmeden Önce:

Bu kendi kendine testi çalıştırın:
```bash
# Bunun neden olduğunu açıklayabilir misiniz?
ollama run qwen2.5:3b "Adım Alice"
# Yanıt: "Merhaba Alice!"

ollama run qwen2.5:3b "Adım ne?"
# Yanıt: "Adını bilmiyorum"

# Cevap: Çünkü her ollama çalıştırması ayrı,
# bağımsız bir API çağrısıdır. Paylaşılan durum yok!
```

---

## 🐛 Hata Ayıklama İpuçları

### Yaygın Sorunlar

**1. "Connection refused" hatası**
```bash
# Çözüm: Ollama'nın çalıştığından emin olun
ollama serve  # Ollama sunucusunu başlat
```

**2. "Model not found"**
```bash
# Çözüm: Önce modeli çekin
ollama pull qwen2.5:3b
```

**3. "Response is slow"**
```bash
# Çözüm: Daha iyi algılanan hız için akış kullanın
# Veya daha küçük bir model kullanın
ollama pull qwen2.5:1.5b  # Daha küçük = daha hızlı
```

**4. "Context too long"**
- Eski konuşma geçmişini kırpın
- Her modelin bir bağlam sınırı vardır (genellikle 2048-8192 token)
- 1 token ≈ 0.75 kelime

---

## 📚 Ek Kaynaklar

- [Ollama Dokümantasyonu](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [OpenAI API Referansı](https://platform.openai.com/docs/api-reference) (benzer yapı)
- [theory.md](./theory.md) - LLM iç yapısına derinlemesine bakış

---

**Sıradaki:** [01-tool-calling](../01-tool-calling) - Fonksiyon çağırma ile LLM'lere nasıl süper güçler vereceğinizi öğrenin →
