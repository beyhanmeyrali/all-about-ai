# LangGraph Framework Eğitimi

Temellerden kurumsal sistemlere kadar LangGraph ile üretim sınıfı ajanlar oluşturmak için tam kılavuz.

## 📚 LangGraph'a Genel Bakış

LangGraph, **durum bilgili, kontrol edilebilir yapay zeka ajan iş akışları** oluşturmak için tasarlanmış, LangChain üzerine inşa edilmiş **düşük seviyeli bir orkestrasyon frameworküdür**. Uygulamaları **graflar** olarak modeller, burada:
- **Düğümler** eylemleri temsil eder (örn. ajanlar veya araçlar)
- **Kenarlar** kontrol akışını tanımlar (örn. sıralı, koşullu veya döngüsel)
- **Durum** yürütmeler boyunca paylaşılır ve kalıcıdır

Bu, **akıl yürütmedeki döngüler** veya **bileşenler arası işbirliği** gibi gerçek dünya senaryolarındaki karmaşıklığı ele almada özellikle güçlü kılar.

### LangGraph Neden Var

Ajanları **kara kutu** olarak ele alan daha basit ajan frameworklerinin aksine, LangGraph şunlar üzerinde **açık kontrol** sağlar:
- ✅ Yürütme yolları
- ✅ Moderasyon döngüleri
- ✅ Kalıcılık ve kontrol noktaları
- ✅ İnsan döngüde iş akışları
- ✅ Çoklu ajan orkestrasyonu

Bu, **üretimde güvenilirlik** sağlar. Hem **Python** hem de **JavaScript**'te mevcuttur ve LLM'lerle (örn. LangChain aracılığıyla) ve harici araçlarla sorunsuz entegre olur.

---

## 🔧 Çoklu Araç Senaryolarını İşleme

Çoklu araç kurulumlarında, LangGraph araçları bir ajanın dinamik olarak çağırabileceği **çağrılabilir fonksiyonlar** olarak ele alır (örn. LangChain'in araç çağırma mekanizması aracılığıyla). Tek bir ajan birden fazla araca erişebilir, ancak grafik yapısı LLM'i bunaltmaktan kaçınmak için **modüler işleme** sağlar (örn. tek bir ajan alanlar arası 10+ araçla zorlanabilir).

### Temel Bileşenler

- **Araçlar**: `@tool` ile dekore edilmiş Python fonksiyonları olarak tanımlanır (`langchain_core.tools`'dan). Her araç, LLM'in ne zaman çağrılacağına karar vermesi için bir ad, açıklama ve şema içerir. Örnekler arasında matematik çözücüler (örn. `PythonREPLTool`), web araması (örn. Serper API) veya veri alma gibi özel fonksiyonlar bulunur.

- **Ajan Düğümü**: Araçlara bağlı bir LLM (örn. GPT-4o veya Qwen) çalıştıran bir grafik düğümü. LLM durum üzerinde akıl yürütür (örn. kullanıcı sorgusu + önceki mesajlar) ve ya bir final yanıt ya da araç çağrıları çıktısı verir.

- **Araç Düğümü**: Çağrılan araçları paralel veya sırayla yürüten, hataları işleyen ve durumu sonuçlarla güncelleyen özel bir düğüm (örn. `langgraph.prebuilt.ToolNode` kullanarak).

- **Koşullu Kenarlar**: Ajanın çıktısına göre yönlendirir—örn. araç çağrıları mevcutsa araç düğümüne git; aksi halde bitir veya başka bir düğüme yönlendir.

- **Durum Yönetimi**: Mesajları, araç çıktılarını ve ara sonuçları izlemek için paylaşılan bir `TypedDict` kullanır (örn. `AgentState = TypedDict("AgentState", {"messages": Annotated[list, add_messages]})`). Kontrol noktaları (örn. `MemorySaver`) oturumlar arası kalıcılığı sağlar.

### Çoklu Araçlar için Yürütme Akışı

1. **Giriş Noktası**: Kullanıcı girdisi grafa girer (örn. `StateGraph.set_entry_point("agent")` aracılığıyla).
2. **Ajan Akıl Yürütmesi**: Ajan düğümü LLM'i çağırır, bu da araç çağrılarına karar verir (örn. "Gerçekler için web_search ve hesaplamalar için math_solver kullan").
3. **Araç Yürütmesi**: Koşullu kenar araç düğümüne yönlendirir, bu da araçları çağırır (verimlilik için paralel çağrıları destekler).
4. **Geri Döngü**: Araç sonuçları duruma eklenir; kenar daha fazla akıl yürütme için ajana geri döner (ReAct gibi döngüleri işler: Reason-Act).
5. **Çıkış**: Araç gerekmiyorsa, final çıktıyla `END`'e yönlendir.

### Örnek Kod Parçacığı (Çoklu Araçlı Tek Ajan)

```python
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent  # Üst düzey yardımcı
# Veya düşük seviye inşa et: from langgraph.prebuilt import ToolNode

class AgentState(TypedDict):
    messages: Annotated[list, "add_messages"]  # Sohbet geçmişini biriktirir

# Araçları tanımla
from langchain_core.tools import tool
@tool
def web_search(query: str) -> str: ...
@tool
def calculator(expression: str) -> str: ...

# Üst düzey: Hızlı kurulum
model = ChatOllama(model="qwen3:8b")
tools = [web_search, calculator]
agent = create_react_agent(model, tools, state_modifier="Özel prompt")

# Düşük seviye: Daha fazla kontrol için özel grafik
graph = StateGraph(AgentState)
graph.add_node("agent", lambda state: {"messages": [model.bind_tools(tools).invoke(state["messages"])]})
graph.add_node("tools", ToolNode(tools))
graph.add_conditional_edges("agent", lambda state: "tools" if state["messages"][-1].tool_calls else END)
graph.add_edge("tools", "agent")
app = graph.compile(checkpointer=MemorySaver())
```

Bu kurulum, araçları gruplandırarak (örn. alana özel alt kümeler) veya yönlendiriciler kullanarak düzinelerce araca ölçeklenir.

---

## 👥 Çoklu Ajan Senaryolarını İşleme

LangGraph'taki çoklu ajan iş akışları, bir grafik aracılığıyla bağlanan birden fazla bağımsız **"aktör"** (her biri kendi promptu, araçları ve mantığı olan LLM destekli bir ajan) içerir. Bu, görev delegasyonu veya paralel işleme gibi işbirliğini sağlayarak insan ekiplerini taklit eder. **Ajanlar varsayılan olarak tam bir taslak paylaşmazlar**—durum kenarlar aracılığıyla seçici olarak aktarılır.

### Temel Bileşenler

- **Bireysel Ajanlar**: Her biri özel promptlar (örn. `ChatPromptTemplate`), LLM'ler ve araçlarla bir alt grafik veya düğümdür. Örneğin, bir "araştırmacı" ajan arama araçları kullanırken, bir "grafik_oluşturucu" kod yürütme kullanır.

- **Süpervizör/Yönlendirici Ajan**: Girdiyi/durumu analiz eden ve uzmanlara yönlendiren merkezi bir düğüm (kendisi bir ajan). "Araçların" aslında diğer ajanlar olduğu araç çağırmayı kullanabilir. "Hesaplama gerekiyorsa math_agent'a, aksi halde web_agent'a yönlendir" gibi promptlar kullanabilir.

- **Devir Araçları**: Ajanların delege etmesi için özel araçlar (örn. `create_handoff_tool(agent_name="Bob")`) (`Command.update` gibi durum güncellemelerini aktarır).

- **Grafik Yapısı**: 
  - **Sıralı/Hiyerarşik**: Ajanlar sırayla çalışır (örn. araştırmacı → analizci).
  - **Paralel**: Eşzamanlı yürütme için süpervizörden birden fazla kenar.
  - **Döngüsel**: İyileştirme için döngüler (örn. süpervizör bir ajanı tekrar çağırır).

- **Durum Yönetimi**: Paylaşılan global durum (örn. ajana özel mesajlar için anahtarlarla) veya ajan başına taslaklar. Moderasyonu (örn. kalite kontrolleri) ve insan döngüde kesintileri destekler.

### Çoklu Ajanlar için Yürütme Akışı

1. **Süpervizöre Girdi**: Kullanıcı sorgusu girer; süpervizör yönlendirmeye karar verir (örn. "GSYİH araştırmasını researcher_agent'a delege et").
2. **Ajan Çağrısı**: Kenarlar uzman düğümlere/alt grafiklere yönlendirir. Her ajan işler (akıl yürütme + araçlar) ve güncellenmiş durumu döndürür.
3. **Koordinasyon**: Süpervizör çıktıları toplar, sonraki adımlara karar verir (örn. "Şimdi chart_generator'a") veya tamamsa bitirir.
4. **İşbirliği**: Ajanlar devredebilir (örn. araştırmacı verileri oluşturucuya aktarır) veya paylaşılan durum aracılığıyla iletişim kurabilir.
5. **Kalıcılık**: Kontrol noktaları kesintiye uğrayan iş akışlarını sürdürmek için durumu kaydeder.

### Örnek Kod Parçacığı (Süpervizör + İki Ajan)

```python
from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate

class MultiAgentState(TypedDict):  # Paylaşılan durum
    messages: Annotated[list, "add_messages"]
    next: str  # Yönlendirme için

# Süpervizör promptu: "Bir süpervizörsün. {researcher|chart_generator}'a yönlendir veya FINISH."
supervisor_prompt = ChatPromptTemplate.from_template(...)
supervisor = supervisor_prompt | model | (lambda output: {"next": output.content})  # Basitleştirilmiş

# Uzman ajanlar (düğüm olarak)
def researcher_node(state): ...  # Arama araçları kullanır
def chart_generator_node(state): ...  # Kod araçları kullanır

graph = StateGraph(MultiAgentState)
graph.add_node("supervisor", supervisor)
graph.add_node("researcher", researcher_node)
graph.add_node("chart_generator", chart_generator_node)
graph.set_entry_point("supervisor")

# Koşullu yönlendirme
def route(state):
    return state["next"] if state["next"] != "FINISH" else END
graph.add_conditional_edges("supervisor", route, {
    "researcher": "researcher",
    "chart_generator": "chart_generator",
    "FINISH": END
})
graph.add_edge("researcher", "supervisor")
graph.add_edge("chart_generator", "supervisor")

app = graph.compile()
```

Bu bir döngü oluşturur: süpervizör → uzman → geri, "FINISH" olana kadar.

---

## 🚨 10 Ajan × 10 Araca Ölçekleme (Bağlam Şişmesi Sorunu)

**10 ajan × her biri 10 araç = 100 araç** veya hatta sadece örtüşen araçlara sahip 10 ajana ölçeklendiğinizde, en büyük risk **bağlam şişmesidir**: LLM promptuna yüzlerce araç şeması tıkıştırmak → yüksek maliyet, gecikme ve en kötüsü, model kafası karışır ve kötü araç seçimleri yapar.

### LangGraph'ın Çözümü: Kanıtlanmış Stratejiler

LangGraph'ın kendisi **bağlamı sihirli bir şekilde küçültmez**, ancak şişmeyi önleyen bilinen her tekniği uygulamak için tam yapı taşlarını verir. İşte insanların üretim LangGraph sistemlerinde gerçekten kullandığı kanıtlanmış stratejiler (2024–2025 en iyi uygulamaları):

| Teknik                           | Şişmeyi nasıl önler                                                              | Bugün LangGraph'ta nasıl uygularsınız                                                                    |
|----------------------------------|----------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| 1. Bir ajan → sadece birkaç araç | Her ajan promptunda en fazla 4–8 araç görür                                     | Her biri kendi küçük araç listesine bağlı 10 ayrı ajan düğümü/alt grafik oluşturun                      |
| 2. Süpervizör + yönlendirme      | Sadece süpervizör ajan listesini görür (araçları değil). Uzmanlar sadece kendi araçlarını görür | Klasik "süpervizör zinciri" deseni (LangGraph çoklu ajan örneklerine bakın)                              |
| 3. Dinamik araç alma             | Araçlar sadece gerektiğinde alınır ve enjekte edilir (araçlar için RAG gibi)   | Belirsizlik yüksek olduğunda araç açıklamalarının vektör DB'sini sorgulayan bir ToolRetriever düğümü kullanın |
| 4. Hiyerarşik / iç içe grafikler | Üst düzey grafik alt grafiklere yönlendirir; her alt grafik kendi izole bağlam penceresine sahiptir | Her ekip (örn. FinanceTeam, ResearchTeam) tek bir düğüm olarak derlenen ayrı bir StateGraph'tır         |
| 5. LLM ile araç yönlendirme      | Süpervizör hangi *ajanı* (yani hangi araç alt kümesini) çağıracağına karar verir — araç şemaları gönderilmez | Süpervizör her "fonksiyonun" aslında başka bir ajan alt grafiğine devir olduğu fonksiyon çağırmayı kullanır |
| 6. Durum budama & özetleme       | Eski mesajlar veya araç sonuçları geri dönmeden önce özetlenir veya atılır     | Süpervizöre dönmeden önce state["messages"] üzerinde özetleme LLM'i çalıştıran bir "compress" düğümü ekleyin |
| 7. Paralel araç yürütme          | Araçlar ToolNode'da çalışır (LLM bağlamı dışında); sonuçlar kısa geri gelir     | ToolNode tüm çağrılan araçları paralel olarak yürütür ve sadece kısa sonuçlar döndürür, tam şemaları asla tekrar döndürmez |

### Gerçek Dünya Deseni (10+ Ajan)

```python
# 1. Süpervizör sadece 10 "ajan devir aracı" görür, 100 gerçek araç görmez
handoff_tools = [
    create_handoff_tool("finance_agent"),
    create_handoff_tool("research_agent"),
    create_handoff_tool("legal_agent"),
    # ... 7 tane daha
]
supervisor = supervisor_prompt | llm.bind_tools(handoff_tools)   # ← sadece 10 şema!

# 2. Her uzman kendi 5–10 aracıyla kendi alt grafiğidir
finance_subgraph = create_finance_team_graph()   # kendi 8 aracına sahip, tamamen ayrı bağlam
research_subgraph = create_research_team_graph() # tavily, tarayıcı vb. var

# 3. Ana grafik
graph.add_node("supervisor", supervisor_node)
graph.add_node("finance", finance_subgraph)      # derlenmiş alt grafik = bir düğüm
graph.add_node("research", research_subgraph)

# Süpervizörden koşullu kenar sadece hangi devir aracının çağrıldığına bakar
graph.add_conditional_edges("supervisor", route_to_agent, {
    "finance_agent": "finance",
    "research_agent": "research",
    "FINISH": END,
})
graph.add_edge("finance", "supervisor")
graph.add_edge("research", "supervisor")
```

**Sonuç:**
- Süpervizör prompt boyutu: 20 ekiple bile ~3–5k token  
- Her uzman prompt boyutu: ~4–8k token (sadece kendi araçları + ilgili geçmiş)  
- **Hiçbir LLM asla tüm 100 aracı aynı anda görmez**

### Bağlamı Kontrol Altında Tutmak için Hızlı Kontrol Listesi

- ❌ Hiçbir zaman herhangi bir düğümde `llm.bind_tools(all_100_tools)` yapmayın  
- ✅ Yaprak ajan başına maksimum 8 araç (ideal 4–6)  
- ✅ Sadece ajan adlarını/yeteneklerini bilen bir süpervizör veya yönlendirici kullanın  
- ✅ Ağır ekipleri alt grafik yapın (ana grafikte tek bir düğüm olurlar)  
- ✅ Uzun döngülerde bir sıkıştırma/özetleme düğümü ekleyin  
- ✅ Mümkün olduğunda tam mesajlar değil tokenlarla akış yapın

---

## 🎯 LangGraph Ne Zaman Kullanılır

### ✅ LangGraph Şunlar İçin Mükemmeldir:

1. **Karmaşık Çok Adımlı İş Akışları**
   - Birden fazla kapılı onay boru hatları
   - Yinelemeli iyileştirme süreçleri
   - Duruma bağlı yönlendirme

2. **Durum Bilgili Ajanlar**
   - Uzun süreli konuşmalar
   - Çok turlu akıl yürütme
   - Oturumlar arası bağlam koruması

3. **Döngüsel İş Akışları**
   - Geri bildirimli yeniden deneme mantığı
   - İnsan döngüde iterasyonlar
   - Kendi kendini iyileştirme döngüleri

4. **Üretim Sistemleri**
   - Kontrol noktası tabanlı kurtarma
   - Denetim izleri
   - Ölçeklenebilir mimariler

### ❌ Şunlar İçin İdeal Değil:

- Basit doğrusal zincirler (LangChain kullanın)
- Durumsuz tek seferlik sorgular
- Temel prompt-yanıt desenleri
- Basit araç çağırma

## 📖 Eğitim Yapısı

### Bölüm 1: Temeller (Betikler 01-03)

**01_simple_langgraph.py** - Çekirdek Kavramlar
- StateGraph temelleri
- Düğüm ve kenar tanımları
- Basit doğrusal iş akışları
- Durum aktarımı ve güncellemeleri

**02_conditional_workflow.py** - Dallanma Mantığı
- Koşullu kenarlar
- Dinamik yönlendirme
- Çok yollu iş akışları
- Karar verme

**03_tools_with_langgraph.py** - Araç Entegrasyonu
- Araç tanımı ve bağlama
- Grafiklerle ReAct deseni
- Araç yürütme düğümleri
- Sonuç toplama

### Bölüm 2: Gelişmiş Özellikler (Betikler 04-07)

**04_checkpoints.py** - Durum Kalıcılığı ⭐
- Kontrol noktaları için MemorySaver
- Çoklu iş parçacığı yönetimi
- Zaman yolculuğu ve geri alma
- Konuşmayı sürdürme
- Dışa/içe aktarma işlevselliği

**05_human_in_loop.py** - Onay İş Akışları ⭐
- Onay kapıları
- Etkileşimli inceleme sistemleri
- Çok adımlı onaylar
- Risk tabanlı yönlendirme
- Geri bildirim toplama

**06_subgraphs.py** - Modüler Kompozisyon ⭐
- Alt grafik oluşturma
- Paralel alt grafik yürütme
- Hiyerarşik mimariler
- Mikroservis desenleri
- Servis izolasyonu

**07_streaming_events.py** - Gerçek Zamanlı Güncellemeler ⭐
- graph.stream() API
- İlerleme takibi
- Hata ayıklama akışı
- Üretim olay sistemleri
- Canlı izleme

### Bölüm 3: Üretim (Betik 08)

**08_production_agent.py** - Tam Sistem ⭐⭐⭐
- Tüm özellikler birleştirildi
- Güvenlik alt grafiği
- Onay iş akışı
- Araç orkestrasyonu
- Hata yönetimi
- Metrikler ve gözlemlenebilirlik
- Üretime hazır desenler

## 🚀 Hızlı Başlangıç

### Kurulum Kontrolü

```bash
cd /workspace/all-about-ai/ai-agents
source venv/bin/activate
python 02-agent-frameworks/langchain/00_installation.py
```

### İlk Grafiğinizi Çalıştırın

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict

class State(TypedDict):
    message: str

def process(state: State) -> State:
    return {"message": f"İşlendi: {state['message']}"}

workflow = StateGraph(State)
workflow.add_node("process", process)
workflow.set_entry_point("process")
workflow.add_edge("process", END)

graph = workflow.compile()
result = graph.invoke({"message": "Merhaba"})
print(result)  # {"message": "İşlendi: Merhaba"}
```

## 🎓 Öğrenme Yolu

### Başlangıç (Hafta 1)
1. Betikleri 01-03 çalıştırın
2. StateGraph temellerini anlayın
3. Basit bir konuşma ajanı oluşturun
4. Koşullu yönlendirme pratik yapın

### Orta Seviye (Hafta 2)
1. Kontrol noktalarında ustalaşın (04)
2. Onay iş akışları uygulayın (05)
3. Alt grafiklerle oluşturun (06)
4. Akış ekleyin (07)

### İleri Seviye (Hafta 3)
1. Üretim ajanını inceleyin (08)
2. Tüm özellikleri birleştirin
3. Özel kurumsal ajan oluşturun
4. Üretim için optimize edin

## 🔑 Temel Kavramlar

### Durum Yönetimi

```python
from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    # Basit durum - her seferinde üzerine yazar
    current_user: str

    # Birikmiş durum - indirgeyici ile ekler
    messages: Annotated[List[str], operator.add]

    # Hesaplanmış durum
    step_count: int
```

### Kontrol Noktaları

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

# Konuşma izolasyonu için thread_id kullanın
config = {"configurable": {"thread_id": "user_123"}}
result = graph.invoke(state, config=config)

# Aynı kontrol noktasından daha sonra devam edin
continued = graph.invoke(new_state, config=config)
```

### Koşullu Yönlendirme

```python
def route(state: State) -> Literal["path_a", "path_b"]:
    return "path_a" if state["score"] > 0.5 else "path_b"

workflow.add_conditional_edges(
    "decision_node",
    route,
    {
        "path_a": "node_a",
        "path_b": "node_b"
    }
)
```

### Akış

```python
for event in graph.stream(initial_state):
    node_name = list(event.keys())[0]
    node_state = event[node_name]
    print(f"Düğüm {node_name}: {node_state}")
```

## 📊 LangGraph vs. LangChain

| Özellik | LangGraph | LangChain |
|---------|-----------|-----------|
| **Mimari** | Grafik tabanlı | Zincir tabanlı |
| **Durum** | Açık, tiplenmiş | Örtük |
| **Döngüler** | Yerel destek | Desteklenmiyor |
| **Kontrol Noktaları** | Yerleşik | Manuel |
| **Karmaşıklık** | Yüksek öğrenme eğrisi | Daha kolay başlangıç |
| **Kullanım Durumu** | Karmaşık ajanlar | Basit iş akışları |
| **Esneklik** | Çok yüksek | Orta |
| **Hata Ayıklama** | Mükemmel | İyi |

## 🛠️ Yaygın Desenler

### Desen 1: ReAct Ajanı

```python
workflow.add_node("think", agent_think)
workflow.add_node("act", agent_act)
workflow.add_node("observe", agent_observe)

workflow.add_conditional_edges(
    "think",
    should_continue,
    {
        "act": "act",
        "finish": END
    }
)

workflow.add_edge("act", "observe")
workflow.add_edge("observe", "think")  # Döngü!
```

### Desen 2: Onay Boru Hattı

```python
workflow.add_node("propose", create_proposal)
workflow.add_node("review", await_human_review)
workflow.add_node("execute", execute_proposal)

workflow.add_conditional_edges(
    "review",
    check_approval,
    {
        "approved": "execute",
        "rejected": "propose",  # Yeniden dene
        "pending": "review"     # Bekle
    }
)
```

### Desen 3: Paralel İşleme

```python
# Paralel alt grafikler oluştur
search_graph = build_search_subgraph()
analysis_graph = build_analysis_subgraph()

workflow.add_node("search", search_graph)
workflow.add_node("analyze", analysis_graph)
workflow.add_node("merge", merge_results)

# Her ikisi de bağımsız çalışır
workflow.add_edge("search", "merge")
workflow.add_edge("analyze", "merge")
```

## 🎯 En İyi Uygulamalar

### 1. Durumunuzu Tipleyin
```python
# İyi
class MyState(TypedDict):
    field: str
    count: int

# Daha iyi - açıklamalarla
class MyState(TypedDict):
    messages: Annotated[List[str], operator.add]
    metadata: Dict[str, Any]
```

### 2. Uzun Konuşmalar İçin Kontrol Noktaları Kullanın
```python
# Çoklu kullanıcı sistemleri için her zaman thread_id kullanın
config = {"configurable": {"thread_id": user_id}}
graph.invoke(state, config=config)
```

### 3. Daha İyi UX İçin Akış Yapın
```python
for event in graph.stream(state):
    # Kullanıcıya gerçek zamanlı güncellemeler gönderin
    send_progress_update(event)
```

### 4. Hataları Zarif Bir Şekilde İşleyin
```python
def node_with_error_handling(state):
    try:
        result = risky_operation()
    except Exception as e:
        state["errors"].append(str(e))
        state["status"] = "error"
        return state

    state["result"] = result
    return state
```

### 5. Modülerlik İçin Alt Grafikler Kullanın
```python
# Yeniden kullanılabilir bileşenler oluşturun
auth_subgraph = build_auth_service()
data_subgraph = build_data_service()

# Daha büyük sisteme birleştirin
workflow.add_node("auth", auth_subgraph)
workflow.add_node("data", data_subgraph)
```

## 🔍 Hata Ayıklama İpuçları

### 1. Ayrıntılı Günlüklemeyi Etkinleştirin
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. Adım Adım İnceleme İçin Akış Kullanın
```python
for event in graph.stream(state):
    print(json.dumps(event, indent=2))
```

### 3. Grafiği Görselleştirin
```python
from langgraph.graph import Graph

# Mermaid diyagramı alın
print(graph.get_graph().draw_mermaid())
```

### 4. Kontrol Noktalarını İnceleyin
```python
state = graph.get_state(config)
print(f"Mevcut değerler: {state.values}")
print(f"Kontrol noktası ID: {state.config}")
```

## 📈 Performans İpuçları

1. **LLM Çağrılarını Minimize Edin**: Mümkün olduğunda toplu işlem yapın
2. **Paralel Alt Grafikler Kullanın**: Bağımsız işlemler için
3. **Önbellekleme Uygulayın**: Tekrarlanan sorgular için
4. **Durum Boyutunu Optimize Edin**: Durumu minimal tutun
5. **Async Kullanın**: I/O bağlı işlemler için

## 🚀 Üretim Kontrol Listesi

- [ ] Kapsamlı hata yönetimi ekleyin
- [ ] Geri çekilme ile yeniden deneme mantığı uygulayın
- [ ] Kalıcı kontrol noktası kullanın (MemorySaver değil)
- [ ] Günlükleme ve izleme ekleyin
- [ ] Hız sınırlama uygulayın
- [ ] Girdi doğrulama ekleyin
- [ ] Metrik toplama kurun
- [ ] Zaman aşımı işlemeyi yapılandırın
- [ ] Güvenlik doğrulama ekleyin
- [ ] Denetim günlüğü uygulayın

## 📚 Ek Kaynaklar

- [LangGraph Dokümantasyonu](https://langchain-ai.github.io/langgraph/)
- [LangGraph Örnekleri](https://github.com/langchain-ai/langgraph/tree/main/examples)
- [Durum Yönetimi Kılavuzu](https://langchain-ai.github.io/langgraph/concepts/low_level/#state)
- [Kontrol Noktası Dokümantasyonu](https://langchain-ai.github.io/langgraph/concepts/persistence/)

## 🎓 Sonraki Adımlar

LangGraph'ta ustalaştıktan sonra şunları düşünün:

1. **CrewAI Framework** (../crewai/)
   - Çoklu ajan işbirliği
   - Rol tabanlı ajanlar
   - Görev delegasyonu

2. **Framework Karşılaştırması** (../comparison/)
   - Her frameworkün ne zaman kullanılacağı
   - Geçiş desenleri
   - Performans kıyaslamaları

3. **Üretim Dağıtımı**
   - Ölçekleme stratejileri
   - İzleme kurulumu
   - Maliyet optimizasyonu

## 💡 Başarı İpuçları

1. **Basit Başlayın**: 01-03 ile başlayın, temellerde ustalaşın
2. **Aşamalı Oluşturun**: Bir seferde bir özellik ekleyin
3. **Kapsamlı Test Edin**: Yerel test için Ollama kullanın
4. **Kodu Okuyun**: Örneklerimiz yoğun şekilde belgelenmiştir
5. **Deney Yapın**: Öğrenmek için örnekleri değiştirin
6. **Özellikleri Birleştirin**: Kendi üretim ajanınızı oluşturun

---

**Durum bilgili ajanlar oluşturmaya hazır mısınız?** `01_simple_langgraph.py` ile başlayın! 🚀

Sorular veya sorunlar için ana [02-agent-frameworks README](../README.md)'ye bakın.
