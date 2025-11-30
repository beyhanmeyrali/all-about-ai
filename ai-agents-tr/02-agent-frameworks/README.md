# 02 - Ajan Frameworkleri: Sıfırdan Üretime 🕸️

> LangChain, LangGraph ve CrewAI'da ustalaşın - Üretim sınıfı çoklu ajan sistemleri oluşturun

---

## 🎯 Nelerde Ustalaşacaksınız

Bu bölüm, üretimde kullanılan **üç ana ajan frameworkünü** kapsar:

1. **LangChain** - Temel (zincirler, hafıza, araçlar)
2. **LangGraph** - Durumlu iş akışları (grafikler, kalıcılık, karmaşık mantık)
3. **CrewAI** - Çoklu ajan ekipleri (rol tabanlı işbirliği)

**Sonunda**, şunları yapabilen üretime hazır ajanlar oluşturacaksınız:
- 🔄 Karmaşık çok adımlı iş akışlarını yürütme
- 🧠 Konuşma hafızasını ve durumunu koruma
- 🛠️ Birden fazla aracı akıllıca orkestre etme
- 👥 Çoklu ajan ekipleri olarak işbirliği yapma
- 📊 Üretim ortamlarına ölçekleme

**Gerekli Süre:** 12-15 saat

---

## 📂 Klasör Yapısı

```
02-agent-frameworks/
├── README.md                          ← Buradasınız
├── requirements.txt                   ← Tüm framework bağımlılıkları
│
├── langchain/                         ← LangChain Frameworkü
│   ├── README.md
│   ├── 00_installation.py            ← Kurulum & doğrulama
│   ├── 01_basic_chain.py             ← Basit LLM zinciri
│   ├── 02_prompt_templates.py        ← Dinamik promptlar
│   ├── 03_chains_with_memory.py      ← Konuşma hafızası
│   ├── 04_tools_integration.py       ← Araç çağırma
│   ├── 05_sequential_chains.py       ← Çok adımlı zincirler
│   ├── 06_router_chains.py           ← Koşullu yönlendirme
│   └── 07_production_agent.py        ← Tam üretim örneği
│
├── langgraph/                         ← LangGraph Frameworkü
│   ├── README.md
│   ├── 00_why_langgraph.py           ← Ne zaman LangGraph kullanılmalı
│   ├── 01_simple_langgraph.py        ← Temel iş akışı ✅
│   ├── 02_conditional_workflow.py    ← Dallanma mantığı ✅
│   ├── 03_tools_with_langgraph.py    ← Araç orkestrasyonu ✅
│   ├── 04_checkpoints.py             ← Durum kalıcılığı
│   ├── 05_human_in_loop.py           ← İnsan onayı düğümleri
│   ├── 06_subgraphs.py               ← İç içe iş akışları
│   ├── 07_streaming_events.py        ← Gerçek zamanlı güncellemeler
│   └── 08_production_agent.py        ← Kurumsal sınıf ajan
│
├── crewai/                            ← CrewAI Frameworkü
│   ├── README.md
│   ├── 00_crew_basics.py             ← Ajanlar, görevler, ekipler
│   ├── 01_simple_crew.py             ← İlk çoklu ajan sistemi
│   ├── 02_sequential_tasks.py        ← Görev bağımlılıkları
│   ├── 03_hierarchical_crew.py       ← Yönetici + çalışanlar
│   ├── 04_tools_in_crew.py           ← Paylaşılan araç kullanımı
│   ├── 05_memory_crew.py             ← Ekip hafıza sistemleri
│   ├── 06_delegation.py              ← Ajan delegasyonu
│   └── 07_production_crew.py         ← Tam araştırma ekibi
│
└── comparison/                        ← Framework Karşılaştırması
    ├── README.md
    ├── same_task_all_frameworks.py   ← Aynı görev, 3 yol
    ├── performance_comparison.py     ← Hız & kaynak kullanımı
    └── when_to_use_what.md          ← Karar rehberi
```

---

## 🚀 Hızlı Başlangıç

### 1. Tüm Frameworkleri Yükleyin

```bash
cd 02-agent-frameworks
pip install -r requirements.txt
```

### 2. Ollama'yı Doğrulayın

```bash
# Ollama'nın çalıştığını kontrol edin
ollama list

# qwen3:8b görmelisiniz
# Değilse: ollama pull qwen3:8b
```

### 3. Yolunuzu Seçin

**Yol A: Tamamen Yeni Başlayan**
```bash
# LangChain temelleri ile başlayın
cd langchain
python 01_basic_chain.py

# Sonra LangGraph'a geçin
cd ../langgraph
python 01_simple_langgraph.py

# Son olarak CrewAI
cd ../crewai
python 01_simple_crew.py
```

**Yol B: Üretime Hızlı Geçiş**
```bash
# Üretim örneklerine atlayın
python langchain/07_production_agent.py
python langgraph/08_production_agent.py
python crewai/07_production_crew.py
```

**Yol C: Framework Karşılaştırması**
```bash
# Aynı görevi tüm frameworklerde görün
cd comparison
python same_task_all_frameworks.py
```

---

## 🧩 Framework Genel Bakış

### LangChain: İsviçre Çakısı

**Nedir:**
- Genel amaçlı LLM frameworkü
- Zincirler, promptlar, hafıza, araçlar
- Basit-orta karmaşıklık için harika

**Ne zaman kullanılmalı:**
- ✅ Hızlı prototipler
- ✅ Standart LLM iş akışları
- ✅ Temelleri öğrenme
- ✅ Basit sıralı görevler

**Ne zaman KULLANILMAMALI:**
- ❌ Karmaşık durum yönetimi gerektiğinde
- ❌ Koşullu dallanma iş akışlarında
- ❌ Ajan mantığını görselleştirmeniz gerektiğinde

**Örnek:**
```python
from langchain_ollama import OllamaLLM
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

llm = OllamaLLM(model="qwen3:8b")
prompt = PromptTemplate.from_template("{topic} hakkında bilgi ver")
chain = LLMChain(llm=llm, prompt=prompt)

result = chain.run(topic="Yapay zeka ajanları")
```

---

### LangGraph: Üretim İş Akışları

**Nedir:**
- Ajanlar için durum makinesi frameworkü
- Düğümler, kenarlar, koşullu yönlendirme
- LangChain üzerine kurulu ama daha güçlü

**Ne zaman kullanılmalı:**
- ✅ Karmaşık çok adımlı iş akışları
- ✅ Koşullu mantık (if/else) gerektiğinde
- ✅ Oturumlar arası durum kalıcılığı
- ✅ Üretim sınıfı ajanlar
- ✅ Akışları ayıklamanız/görselleştirmeniz gerektiğinde

**Ne zaman KULLANILMAMALI:**
- ❌ Basit tek adımlı görevler
- ❌ Temelleri öğrenirken (çok karmaşık)
- ❌ Hızlı prototipler

**Örnek:**
```python
from langgraph.graph import StateGraph, END

def agent_node(state):
    # Durumu işle
    return {"answer": "sonuç"}

workflow = StateGraph(State)
workflow.add_node("agent", agent_node)
workflow.set_entry_point("agent")
workflow.add_edge("agent", END)

app = workflow.compile()
result = app.invoke({"question": "Merhaba"})
```

---

### CrewAI: Çoklu Ajan Ekipleri

**Nedir:**
- Çoklu ajan işbirliği frameworkü
- Birlikte çalışan rol tabanlı ajanlar
- Yerleşik görev delegasyonu ve yönetimi

**Ne zaman kullanılmalı:**
- ✅ Birden fazla uzmanlaşmış ajan gerektiğinde
- ✅ Farklı beceriler gerektiren karmaşık görevler
- ✅ Hiyerarşik iş akışları (yönetici + çalışanlar)
- ✅ Ajan delegasyonu ve işbirliği
- ✅ Araştırma, içerik oluşturma, analiz

**Ne zaman KULLANILMAMALI:**
- ❌ Tek ajan yeterliyse
- ❌ Basit doğrusal iş akışları
- ❌ Her adım üzerinde ince kontrol gerektiğinde

**Örnek:**
```python
from crewai import Agent, Task, Crew

researcher = Agent(
    role="Araştırmacı",
    goal="Bilgi bul",
    tools=[search_tool]
)

writer = Agent(
    role="Yazar",
    goal="Rapor yaz",
    tools=[]
)

task1 = Task(description="Yapay zekayı araştır", agent=researcher)
task2 = Task(description="Rapor yaz", agent=writer)

crew = Crew(agents=[researcher, writer], tasks=[task1, task2])
result = crew.kickoff()
```

---

## 📊 Framework Karşılaştırması

| Özellik | LangChain | LangGraph | CrewAI |
|---------|-----------|-----------|--------|
| **Öğrenme Eğrisi** | Kolay | Orta | Orta |
| **En İyisi** | Basit zincirler | Karmaşık iş akışları | Çoklu ajan ekipleri |
| **Durum Yönetimi** | Temel | Gelişmiş | Yerleşik |
| **Koşullu Mantık** | Sınırlı | Mükemmel | İyi |
| **Çoklu Ajan** | Manuel | Manuel | Yerel |
| **Görselleştirme** | Hayır | Evet | Hayır |
| **Üretime Hazır** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Dokümantasyon** | Mükemmel | İyi | İyi |
| **Topluluk** | Büyük | Büyüyen | Büyüyen |

---

## 🎓 Öğrenme Yolu

### 1. Hafta: Temeller (LangChain)
- **1-2. Gün:** Temel zincirler ve promptlar
- **3-4. Gün:** Hafıza ve konuşma
- **5-6. Gün:** Araçlar ve sıralı zincirler
- **7. Gün:** Tam bir LangChain ajanı oluşturun

### 2. Hafta: Gelişmiş İş Akışları (LangGraph)
- **1-2. Gün:** Durum grafikleri ve düğümler
- **3-4. Gün:** Koşullu kenarlar ve yönlendirme
- **5-6. Gün:** Kalıcılık ve akış
- **7. Gün:** Tüm özelliklere sahip üretim ajanı

### 3. Hafta: Çoklu Ajan Sistemleri (CrewAI)
- **1-2. Gün:** Ajanlar, görevler, ekipler
- **3-4. Gün:** Hiyerarşik ekipler
- **5-6. Gün:** Karmaşık işbirliği desenleri
- **7. Gün:** Bir araştırma ekibi oluşturun

---

## 🏗️ Aşamalı Karmaşıklık

Her framework bölümü bu deseni izler:

```
00_basics.py          ← Merhaba Dünya seviyesi
   ↓
01_simple.py          ← Tek özellik
   ↓
02_intermediate.py    ← Özellikleri birleştirme
   ↓
03_advanced.py        ← Karmaşık desenler
   ↓
04_production.py      ← Kurumsal sınıf
```

**Öğrenme Felsefesi:**
1. **Sıfırdan Kahramana** - Her kavram sıfırdan açıklanır
2. **Öncekinin Üzerine İnşa Etme** - Her betik bir öncekini genişletir
3. **OOP Tasarımı** - Profesyonel, yeniden kullanılabilir kod
4. **Tamamen Test Edilmiş** - Tüm betikler Ollama ile çalışır
5. **Üretime Hazır** - Gerçek dünya desenleri

---

## 🔧 Ustalaşacağınız Yaygın Desenler

### Desen 1: Araç Çağıran Ajan
- LangChain: `AgentExecutor`
- LangGraph: Koşullu döngüler
- CrewAI: Araçlı ajan

### Desen 2: Çok Adımlı İş Akışı
- LangChain: `SequentialChain`
- LangGraph: Durum grafiği
- CrewAI: Sıralı görevler

### Desen 3: Koşullu Yönlendirme
- LangChain: `RouterChain`
- LangGraph: Koşullu kenarlar
- CrewAI: Yönetici ajan

### Desen 4: Hafıza Yönetimi
- LangChain: `ConversationBufferMemory`
- LangGraph: Durum kalıcılığı
- CrewAI: Ekip hafızası

---

## 🐛 Hata Ayıklama İpuçları

### LangChain Sorunları
```python
# Ayrıntılı modu etkinleştir
chain = LLMChain(llm=llm, prompt=prompt, verbose=True)

# LLM'e ne gönderildiğini görün
print(chain.prompt.format(topic="test"))
```

### LangGraph Sorunları
```python
# Düğümlere hata ayıklama çıktıları ekleyin
def my_node(state):
    print(f"[HATA AYIKLAMA] Durum: {state}")
    result = process(state)
    print(f"[HATA AYIKLAMA] Sonuç: {result}")
    return result
```

### CrewAI Sorunları
```python
# Ayrıntılı ve tam çıktıyı etkinleştir
crew = Crew(
    agents=[...],
    tasks=[...],
    verbose=True,
    full_output=True
)
```

---

## 🎯 Ana Çıkarımlar

### Her Framework Ne Zaman Kullanılmalı:

**LangChain kullanın:**
- İlk ajanınızı oluştururken
- Basit konuşma yapay zekası
- Hızlı prototipler
- Temelleri öğrenirken

**LangGraph kullanın:**
- Karmaşık çok adımlı iş akışları
- Durum kalıcılığı gerektiğinde
- Koşullu mantık gerektiğinde
- Üretim dağıtımı
- Akışları görselleştirmek istediğinizde

**CrewAI kullanın:**
- Birden fazla uzmanlaşmış ajan
- Görev delegasyonu gerektiğinde
- Hiyerarşik iş akışları
- Araştırma/içerik oluşturma
- Ajan işbirliği

**Birden Fazla Framework kullanın:**
- Kurumsal uygulamalar
- Farklı bileşenler farklı desenlere ihtiyaç duyduğunda
- Maksimum esneklik gerektiğinde

---

## 📚 Her Alt Klasör Ne İçerir

### `/langchain` - Temel Framework
Temel zincirlerden üretim ajanlarına kadar tam rehber. Promptlar, hafıza, araçlar ve sıralı iş akışlarında ustalaşın.

### `/langgraph` - Durum Makinesi Frameworkü
Durum yönetimi, koşullu yönlendirme, kalıcılık ve insan döngüde desenleri ile karmaşık iş akışları oluşturun.

### `/crewai` - Çoklu Ajan Frameworkü
Roller, görevler, delegasyon ve hiyerarşik yönetim ile işbirlikçi ajan ekipleri oluşturun.

### `/comparison` - Framework Karşılaştırması
Aynı görevlerin üç frameworkte de uygulandığını görün. Ödünleşimleri anlayın ve bilinçli kararlar verin.

---

## 🚀 Sonraki Adımlar

Bu bölümü tamamladıktan sonra şunlara hazır olacaksınız:

1. **[03-embeddings-rag](../03-embeddings-rag)** - Bilgi erişimi ekleyin
2. **[04-memory-systems](../04-memory-systems)** - Letta ile uzun süreli hafıza
3. **[05-voice-gpt](../05-voice-gpt)** - Ses özellikli ajanlar

---

## 📖 Ek Kaynaklar

- [LangChain Dokümantasyonu](https://python.langchain.com/)
- [LangGraph Dokümantasyonu](https://langchain-ai.github.io/langgraph/)
- [CrewAI Dokümantasyonu](https://docs.crewai.com/)
- [Ollama Dokümantasyonu](https://github.com/ollama/ollama)

---

## 🤝 Proje Yapısı Felsefesi

**Neden Bu Yapı?**
- 📁 **Framework ayrımı** - Her framework kendi klasöründe
- 🔢 **Aşamalı numaralandırma** - Net sıralama için 00'dan 99'a
- 🎓 **Sıfırdan kahramana** - Her framework tamamen öğretilir
- 🏗️ **OOP tasarımı** - Profesyonel, bakımı kolay kod
- ✅ **Tamamen test edilmiş** - Tüm betikler Ollama ile çalışır

**En İyi Uygulamalar:**
1. Framework temelleri ile başlayın
2. Her birinin ne zaman kullanılacağını anlayın
3. Aşamalı olarak karmaşık örnekler oluşturun
4. Frameworkleri aynı görevlerle karşılaştırın
5. İhtiyaçlarınız için doğru aracı seçin

---

**Başlamaya hazır mısınız?** Şununla başlayın:
- **Yeni Başlayanlar:** [langchain/01_basic_chain.py](./langchain/01_basic_chain.py)
- **Orta Seviye:** [langgraph/01_simple_langgraph.py](./langgraph/01_simple_langgraph.py)
- **İleri Seviye:** [crewai/01_simple_crew.py](./crewai/01_simple_crew.py)

---

*"Doğru framework karmaşık ajanları basitleştirir. Yanlış olan basit ajanları karmaşıklaştırır."*
