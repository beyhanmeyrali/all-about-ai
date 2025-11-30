# LangChain: Temel Ajan Frameworkü 🔗

> LangChain ile LLM ajanlarının temellerinde ustalaşın

---

## 🎯 Ne Öğreneceksiniz

LangChain, LLM uygulamaları oluşturmak için **temel frameworktür**. Şunları sağlar:

- 🔗 **Zincirler** - LLM çağrılarını birbirine bağlayın
- 📝 **Promptlar** - Dinamik prompt şablonları
- 🧠 **Hafıza** - Konuşma geçmişi yönetimi
- 🛠️ **Araçlar** - Ajanlara yetenekler verin
- 🔄 **Diziler** - Çok adımlı iş akışları

**Gerekli Süre:** 4-5 saat

---

## 📂 Bu Bölümdeki Dosyalar

```
langchain/
├── README.md                    ← Buradasınız
├── 00_installation.py          ← Kurulumu doğrula
├── 01_basic_chain.py           ← İlk zinciriniz
├── 02_prompt_templates.py      ← Dinamik promptlar
├── 03_chains_with_memory.py    ← Konuşma hafızası
├── 04_tools_integration.py     ← Araç çağıran ajanlar
├── 05_sequential_chains.py     ← Çok adımlı iş akışları
├── 06_router_chains.py         ← Koşullu yönlendirme
└── 07_production_agent.py      ← Tam ajan sistemi
```

---

## 🚀 Hızlı Başlangıç

```bash
# Bağımlılıkları yükle
pip install langchain langchain-ollama langchain-core requests

# Ollama'yı doğrula
ollama list  # qwen3:8b göstermeli

# İlk örneği çalıştır
python 01_basic_chain.py
```

---

## 📖 Aşamalı Öğrenme Yolu

### 00 - Kurulum & Ayarlama
**Kavram:** Her şeyin çalıştığını doğrula
**Öğrenecekleriniz:** Ollama + LangChain entegrasyonunu test etme

### 01 - Temel Zincir
**Kavram:** Basit LLM çağrısı
**Öğrenecekleriniz:** LLMChain, temel promptlar, zincirleri çalıştırma

### 02 - Prompt Şablonları
**Kavram:** Değişkenlerle dinamik promptlar
**Öğrenecekleriniz:** PromptTemplate, değişken ikamesi, yeniden kullanılabilir promptlar

### 03 - Hafızalı Zincirler
**Kavram:** Konuşma geçmişini hatırla
**Öğrenecekleriniz:** ConversationBufferMemory, ConversationChain, bağlam yönetimi

### 04 - Araç Entegrasyonu
**Kavram:** Ajanlara yetenekler ver
**Öğrenecekleriniz:** Araç şemaları, AgentExecutor, araç çağırma

### 05 - Sıralı Zincirler
**Kavram:** Çok adımlı iş akışları
**Öğrenecekleriniz:** SequentialChain, zincirler arasında veri aktarımı, karmaşık iş akışları

### 06 - Yönlendirici Zincirler
**Kavram:** Koşullu yönlendirme
**Öğrenecekleriniz:** RouterChain, LLMRouterChain, girdiye dayalı dinamik yönlendirme

### 07 - Üretim Ajanı
**Kavram:** Kurumsal sınıf ajan
**Öğrenecekleriniz:** Hata yönetimi, günlükleme, izleme, en iyi uygulamalar

---

## 🧩 Temel Kavramlar

### Zincir Nedir?

Bir **zincir**, LLM'lere veya diğer yardımcı programlara yapılan bir dizi çağrıdır:

```python
# Basit zincir
Prompt → LLM → Çıktı

# Sıralı zincir
Prompt1 → LLM1 → Prompt2 → LLM2 → Çıktı

# Araç zinciri
Prompt → LLM → Araç Çağrısı → Araç Sonucu → LLM → Çıktı
```

### Neden Zincir Kullanılır?

**Zincirler olmadan:**
```python
# Karmaşık, bakımı zor
response1 = requests.post(...)
data = parse(response1)
response2 = requests.post(...format(data)...)
result = parse(response2)
```

**Zincirlerle:**
```python
# Temiz, yeniden kullanılabilir
chain = PromptTemplate | LLM | OutputParser
result = chain.invoke({"input": "soru"})
```

---

## 🔑 Çekirdek Bileşenler

### 1. LLM'ler (Dil Modelleri)

```python
from langchain_ollama import OllamaLLM

llm = OllamaLLM(
    model="qwen3:8b",
    temperature=0.7
)

response = llm.invoke("Merhaba!")
```

### 2. Promptlar

```python
from langchain.prompts import PromptTemplate

prompt = PromptTemplate(
    template="{topic} hakkında bilgi ver",
    input_variables=["topic"]
)

formatted = prompt.format(topic="Yapay Zeka")
# "Yapay Zeka hakkında bilgi ver"
```

### 3. Zincirler

```python
from langchain.chains import LLMChain

chain = LLMChain(
    llm=llm,
    prompt=prompt
)

result = chain.run(topic="Python")
```

### 4. Hafıza

```python
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

memory = ConversationBufferMemory()
conversation = ConversationChain(
    llm=llm,
    memory=memory
)

# İlk mesaj
conversation.run("Adım John")
# "Tanıştığımıza memnun oldum, John!"

# İkinci mesaj - hatırlıyor!
conversation.run("Adım ne?")
# "Adınız John"
```

### 5. Araçlar

```python
from langchain.tools import Tool

def get_weather(city: str) -> str:
    return f"{city}'da hava: Güneşli, 25°C"

weather_tool = Tool(
    name="get_weather",
    func=get_weather,
    description="Bir şehir için hava durumunu al"
)
```

---

## 🎓 Öğrenme Hedefleri

Bu bölümün sonunda şunları yapacaksınız:

1. ✅ Zincirlerin ne olduğunu ve ne zaman kullanılacağını anlama
2. ✅ Değişkenlerle dinamik promptlar oluşturma
3. ✅ Konuşma hafızasını yönetme
4. ✅ Araçları ajanlarla entegre etme
5. ✅ Çok adımlı sıralı iş akışları oluşturma
6. ✅ Koşullu yönlendirme uygulama
7. ✅ Üretime hazır ajanlar oluşturma

---

## 🔄 Aşamalı Karmaşıklık

```
01_basic_chain.py
   ↓ Dinamik promptlar ekle
02_prompt_templates.py
   ↓ Hafıza ekle
03_chains_with_memory.py
   ↓ Araçlar ekle
04_tools_integration.py
   ↓ Sıralı adımlar ekle
05_sequential_chains.py
   ↓ Yönlendirme mantığı ekle
06_router_chains.py
   ↓ Üretim özellikleri ekle
07_production_agent.py
```

---

## 🐛 Yaygın Sorunlar & Çözümler

### Sorun 1: İçe Aktarma Hataları

```bash
# Hata: No module named 'langchain'
pip install langchain langchain-ollama

# Hata: Cannot import OllamaLLM
pip install --upgrade langchain-ollama
```

### Sorun 2: Ollama Bağlantısı

```python
# Ollama bağlantısını test et
import requests
response = requests.get("http://localhost:11434/api/tags")
print(response.status_code)  # 200 olmalı
```

### Sorun 3: Zincir Çalışmıyor

```python
# Ne olduğunu görmek için ayrıntılı modu etkinleştir
chain = LLMChain(llm=llm, prompt=prompt, verbose=True)
```

---

## 📊 LangChain vs Diğerleri

| Özellik | LangChain | LangGraph | CrewAI |
|---------|-----------|-----------|--------|
| Öğrenme Eğrisi | Kolay ✅ | Orta | Orta |
| En İyisi | Basit zincirler | Karmaşık iş akışları | Çoklu ajan |
| Kurulum Süresi | 5 dk | 10 dk | 15 dk |
| Hafıza | Yerleşik ✅ | Manuel | Yerleşik |
| Araçlar | Kolay ✅ | Manuel | Kolay |
| Yönlendirme | Sınırlı | Mükemmel | İyi |

---

## 🎯 LangChain Ne Zaman Kullanılır

**LangChain kullanın:**
- ✅ İlk ajanınızı oluştururken
- ✅ Basit konuşma yapay zekası
- ✅ Hızlı prototipler
- ✅ Temelleri öğrenirken
- ✅ Sıralı iş akışları

**LangChain kullanmayın:**
- ❌ Karmaşık durum yönetimi gerektiğinde → LangGraph kullanın
- ❌ Çoklu ajan sistemleri → CrewAI kullanın
- ❌ Grafik görselleştirme gerektiğinde → LangGraph kullanın

---

## 🚀 Sonraki Adımlar

Bu bölümü tamamladıktan sonra:

1. Karmaşık iş akışları için **LangGraph**'a geçin
2. Veya çoklu ajan sistemleri için **CrewAI**'a atlayın
3. Veya bilgi erişimi için **03-embeddings-rag**'a devam edin

---

## 📚 Kaynaklar

- [LangChain Dokümanları](https://python.langchain.com/)
- [LangChain GitHub](https://github.com/langchain-ai/langchain)
- [Ollama Entegrasyonu](https://python.langchain.com/docs/integrations/llms/ollama)

---

**Başlamaya hazır mısınız?** `python 01_basic_chain.py` çalıştırın →
