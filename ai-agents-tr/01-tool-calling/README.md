# 01 - Araç Çağırma: LLM'lere Süper Güçler Vermek 🔧

> LLM'leri sohbet botlarından gerçek dünyayla etkileşime girebilen ajanlara dönüştürün

---

## 🎯 Öğrenme Hedefleri

Bu bölümün sonunda şunları anlayacaksınız:
- ✅ Araç/fonksiyon çağırma aslında nedir
- ✅ LLM'ler araçları ne zaman kullanacağına nasıl karar verir
- ✅ **Özyinelemeli (Recursive)/Ajan araç çağırma** (oyun değiştirici!)
- ✅ Gerçek dünya araç entegrasyonları oluşturma
- ✅ Hata yönetimi ve yeniden deneme mantığı
- ✅ Çok adımlı araç orkestrasyonu

**Gerekli Süre:** 3-4 saat

---

## 🤔 Neden Araç Çağırmaya İhtiyacınız Var?

**Araç çağırma olmadan, LLM'ler sadece süslü sohbet botlarıdır. Bununla birlikte, ajanlara dönüşürler.**

### Bu Bölümü Atlarsanız Ne Olur?

❌ **LLM'iniz gerçek verilere erişemez** → Gerçek hava durumunu, veritabanlarını, API'leri kontrol etmek yerine halüsinasyon görür
❌ **Yararlı uygulamalar oluşturamazsınız** → Sohbet botları eğlencelidir, ancak iş YAPAN ajanlar değerlidir
❌ **Frameworkleri anlamazsınız** → LangGraph, CrewAI araç çağırma üzerine kuruludur - temeli bilmeniz gerekir
❌ **Hata ayıklamada zorlanırsınız** → Araçlar çalışmadığında, sorunun LLM'de mi, şemada mı yoksa kodunuzda mı olduğunu bilemezsiniz
❌ **"Ajan" kavramını kaçırırsınız** → Özyinelemeli döngü, LLM'leri akıllı yapan şeydir - bunu atlarsanız asla anlayamazsınız

### Bunu Anlayarak Ne Kazanacaksınız?

✅ **LLM'leri ajanlara dönüştürün** - Hava durumunu kontrol edebilir, veritabanlarını sorgulayabilir, e-posta gönderebilir, her şeyi yapabilirler!
✅ **Gerçek uygulamalar oluşturun** - Sadece sohbet değil, aslında yararlı yazılımlar
✅ **Ajan döngüsünü anlayın** - Tüm yapay zeka ajanlarına güç veren özyinelemeli desen
✅ **Araç sorunlarını ayıklayın** - Bir aracın neden çağrılmadığını veya yanlış parametreler aldığını tam olarak bilin
✅ **Frameworkleri takdir edin** - LangGraph'ın neyi otomatikleştirdiğini anlayın (bu özyinelemeli döngüdür!)

### Üretim Ajanlarına Giden Köprü

Bu bölüm şunlar arasındaki köprüdür:
- **LLM Temelleri** (00) - LLM'lerin durumsuz olduğunu öğrendiniz → Şimdi onlara dünyayla etkileşim kurmaları için araçlar verin
- **Ajan Frameworkleri** (02) - Frameworkler, burada manuel olarak oluşturacağınız özyinelemeli döngüyü otomatikleştirir
- **Gerçek Uygulamalar** - Her yararlı yapay zeka uygulaması araç çağırma kullanır: ChatGPT eklentileri, GitHub Copilot, sesli asistanlar

**Araç çağırma olmadan, LLM'ler hesap makinesidir. Bununla birlikte, aslında bir şeyler YAPABİLEN ajanlardır.**

---

## 🧠 Kritik Kavram: Araç Çağırma Yürütme (Execution) DEĞİLDİR

### Araç Çağırma Nedir?

**Büyük Yanılgı:**
```
❌ YANLIŞ: "LLM hava durumu API'sini çağırır"
✅ DOĞRU: "LLM, 'lütfen bu argümanlarla hava durumu API'sini çağır' diyen JSON çıktısı verir"
```

**Aslında Nasıl Çalışır:**

```python
# Adım 1: Bir soru sorarsınız
user: "Tokyo'da hava nasıl?"

# Adım 2: LLM bir araç çağrısı ile yanıt verir (sadece JSON!)
llm_response = {
    "tool_calls": [{
        "function": "get_weather",
        "arguments": {"city": "Tokyo"}
    }]
}

# Adım 3: Fonksiyonu SİZ çalıştırırsınız (LLM değil!)
weather = get_weather("Tokyo")  # Bu kodu siz çalıştırırsınız

# Adım 4: Sonucu LLM'e geri gönderirsiniz
messages.append({"role": "tool", "content": weather})
final = llm.chat(messages)

# Adım 5: LLM, doğal dil üretmek için araç sonucunu kullanır
llm: "Tokyo'da hava güneşli, 25°C"
```

**LLM asla kod yürütmez!** Sadece:
1. Bir aracın ne zaman yararlı olacağını tanır
2. Fonksiyon adı + argümanlarla yapılandırılmış JSON çıktısı verir
3. Fonksiyonu çalıştırmanızı ve sonuçları geri göndermenizi bekler

---

## 🔄 Ajan Döngüsü: Özyinelemeli Araç Çağırma

### Tek Araç Çağırma vs Özyinelemeli (Ajan)

**Basit Araç Çağırma:**
```
Kullanıcı → LLM → Araç Çağrısı → Yürüt → LLM → Cevap
             (bir kez)
```

**Özyinelemeli/Ajan Araç Çağırma:**
```
Kullanıcı → LLM → Araç Çağrısı → Yürüt → LLM → Araç Çağrısı → Yürüt → LLM → Cevap
                  ↑______________________________|  ↑_______________________|
                         (tekrarlayabilir!)             (tekrarlayabilir!)
```

### Örnek: Çok Adımlı Görev

**Soru:** "Yöneticimin şehrinde hava nasıl?"

**Basit yaklaşım:** Yapamaz (2 araç çağrısı gerekir)

**Özyinelemeli yaklaşım:**
```python
# Adım 1: LLM get_my_manager() çağırır
manager = get_my_manager()  # Döndürür: {"name": "Alice", "city": "Paris"}

# Adım 2: LLM sonucu görür, get_weather() çağırır
weather = get_weather("Paris")  # Döndürür: {"temp": 18, "condition": "cloudy"}

# Adım 3: LLM sonuçları birleştirir
"Yöneticiniz Alice Paris'te, orada hava şu anda 18°C ve bulutlu."
```

**LLM'leri "ajan" yapan budur!** Şunları yapabilirler:
- Birden fazla aracı birbirine zincirlemek
- Bir aracın çıktısını diğerine girdi olarak kullanmak
- Karmaşık çok adımlı görevleri otonom olarak çözmek

---

## 📚 Bu Bölüm Neleri Kapsıyor

### Bu Dizindeki Dosyalar

```
01-tool-calling/
├── README.md                          ← Buradasınız
├── requirements.txt                   ← Python bağımlılıkları
├── 01_basic_weather_tool.py          ← Basit tek araç
├── 02_multiple_tools.py              ← Çoklu araç seçenekleri
├── 03_recursive_agent.py             ← Güçlü ajan döngüsü!
├── 04_erp_integration.py             ← Gerçek dünya ERP örneği
├── 05_error_handling.py              ← Sağlam araç çağırma
├── 06_curl_examples.sh               ← HTTP katmanı örnekleri
└── tools/
    ├── weather.py                    ← Hava durumu API aracı
    ├── database.py                   ← Veritabanı sorgu araçları
    └── erp_simulator.py              ← ERP sistemi simülasyonu
```

---

## 🚀 Hızlı Başlangıç

### 1. Bağımlılıkları Yükleyin

```bash
cd 01-tool-calling
pip install -r requirements.txt
```

### 2. Ollama'nın Çalıştığından Emin Olun

```bash
# Ollama'yı doğrulayın
curl http://localhost:11434/api/tags

# qwen2.5:3b modeline sahip olduğunuzdan emin olun
ollama pull qwen2.5:3b
```

### 3. İlk Örneği Çalıştırın

```bash
python 01_basic_weather_tool.py
```

---

## 📖 Ayrıntılı Örnekler

### Örnek 1: Temel Hava Durumu Aracı (01_basic_weather_tool.py)

**Ne Öğreneceksiniz:**
- LLM'ler için araç şemaları tanımlama
- LLM'ler yanıtlardan araç çağrılarını nasıl ayrıştırır
- Araç sonuçlarını LLM'e geri gönderme

**Ana Kod:**
```python
# Araç şemasını tanımla (LLM'e hangi araçların mevcut olduğunu söyler)
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Bir şehir için güncel hava durumunu al",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Şehir adı"
                }
            },
            "required": ["city"]
        }
    }
}]

# Araçlarla birlikte LLM'e gönder
response = llm.chat(messages, tools=tools)

# LLM bir araç çağrısı ile yanıt verebilir
if response.tool_calls:
    tool_call = response.tool_calls[0]
    city = tool_call.arguments['city']

    # Fonksiyonu SİZ çalıştırırsınız
    weather = get_weather(city)

    # Sonucu geri gönder
    messages.append({"role": "tool", "content": weather})
    final = llm.chat(messages, tools=tools)
```

**curl Örneği:**
```bash
# Adım 1: Mevcut araçlarla soru gönder
curl -X POST http://localhost:11434/api/chat -d '{
  "model": "qwen2.5:3b",
  "messages": [{"role": "user", "content": "Weather in Tokyo?"}],
  "tools": [{
    "type": "function",
    "function": {
      "name": "get_weather",
      "description": "Get weather",
      "parameters": {
        "type": "object",
        "properties": {
          "city": {"type": "string"}
        }
      }
    }
  }]
}'
```

---

### Örnek 2: Çoklu Araçlar (02_multiple_tools.py)

**Ne Öğreneceksiniz:**
- LLM'e birden fazla araç seçeneği verme
- LLM doğru aracı nasıl seçer
- Farklı araç imzalarını yönetme

**Mevcut Araçlar:**
- `get_weather(city)` - Hava durumu bilgisi
- `search_web(query)` - Web araması
- `calculate(expression)` - Matematik hesaplamaları

**Ana Fikir:**
LLM hangi aracı kullanacağını şunlara göre seçer:
- Araç açıklamaları
- Kullanıcı sorgusu bağlamı
- Parametre gereksinimleri

---

### Örnek 3: Özyinelemeli Ajan (03_recursive_agent.py) ⭐

**Ne Öğreneceksiniz:**
- Ajan döngüsünü oluşturma
- Çok adımlı araç orkestrasyonunu yönetme
- Özyinelemeyi ne zaman durdurmalı

**Ajan Döngüsü:**
```python
def agent_loop(user_message):
    """
    Araçları birden çok kez kullanabilen özyinelemeli ajan.
    Bir LLM'i bir AJANA dönüştüren şey budur!
    """

    messages = [{"role": "user", "content": user_message}]
    max_iterations = 10  # Sonsuz döngüleri önle

    for iteration in range(max_iterations):
        # LLM'i çağır
        response = llm.chat(messages, tools=tools)

        # LLM'in bir araç kullanmak isteyip istemediğini kontrol et
        if response.tool_calls:
            print(f"[AJAN] İterasyon {iteration + 1}: Araçlar kullanılıyor...")

            # LLM'in istediği her aracı çalıştır
            for tool_call in response.tool_calls:
                function_name = tool_call.function.name
                arguments = tool_call.arguments

                # Aracı çalıştır
                result = execute_tool(function_name, arguments)

                # Araç sonucunu konuşmaya ekle
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

            # Döngüye devam et - LLM daha fazla araç çağırabilir!
            continue

        else:
            # Daha fazla araç çağrısı yok - LLM'in son cevabı var
            print(f"[AJAN] {iteration + 1} iterasyondan sonra bitti")
            return response.content

    print("[AJAN] Maksimum iterasyona ulaşıldı!")
    return "Görev çok karmaşık, iterasyon sınırı aşıldı"
```

**Örnek Yürütme:**
```
Kullanıcı: "Yöneticimin şehrinde hava nasıl?"

[AJAN] İterasyon 1: Araçlar kullanılıyor...
  → Çağrılıyor get_my_manager()
  → Sonuç: {"name": "Alice", "city": "Paris"}

[AJAN] İterasyon 2: Araçlar kullanılıyor...
  → Çağrılıyor get_weather(city="Paris")
  → Sonuç: {"temp": 18, "condition": "cloudy"}

[AJAN] 2 iterasyondan sonra bitti
Final: "Yöneticiniz Alice Paris'te, orada hava 18°C ve bulutlu."
```

---

### Örnek 4: ERP Entegrasyonu (04_erp_integration.py)

**Ne Öğreneceksiniz:**
- Gerçek dünya iş aracı entegrasyonu
- Karmaşık, iç içe araç çağrıları
- Yapılandırılmış verileri yönetme

**Bukalemun örneklerinizden uyarlandı!**

**Mevcut Araçlar:**
- `get_employees_by_manager(manager_id)` - Ekip üyelerini al
- `get_payroll_by_employee(employee_id)` - Maaş bilgisini al
- `update_payroll(employee_id, salary, bonus)` - Maaş bordrosunu güncelle

**Karmaşık Sorgu Örneği:**
```
Kullanıcı: "ID 2'ye sahip yöneticinin ekibi için toplam maaş bordrosu maliyetini al"

Ajan yürütmesi:
1. get_employees_by_manager(2)
   → 5 çalışan döndürür
2. get_payroll_by_employee(emp1)
3. get_payroll_by_employee(emp2)
4. get_payroll_by_employee(emp3)
5. get_payroll_by_employee(emp4)
6. get_payroll_by_employee(emp5)
7. Toplamı hesapla ve yanıtla

Toplam: 6 araç çağrısı otomatik olarak orkestre edildi!
```

---

### Örnek 5: Hata Yönetimi (05_error_handling.py)

**Ne Öğreneceksiniz:**
- Araç yürütme hatalarını yönetme
- Yeniden deneme mantığı
- LLM'e hata bağlamı sağlama

**Yaygın Hata Senaryoları:**
```python
# Senaryo 1: Geçersiz parametreler
try:
    weather = get_weather(city="XYZ123")  # Geçersiz şehir
except ValueError as e:
    # Hatayı LLM'e geri gönder
    messages.append({
        "role": "tool",
        "content": f"Hata: {str(e)}. Lütfen geçerli bir şehir adı ile deneyin."
    })
    # LLM düzeltilmiş parametrelerle yeniden deneyebilir!

# Senaryo 2: API zaman aşımı
try:
    result = call_external_api(params)
except TimeoutError:
    # LLM'i zaman aşımı hakkında bilgilendir
    messages.append({
        "role": "tool",
        "content": "API zaman aşımı. Servis kullanılamıyor olabilir."
    })
    # LLM alternatif önerebilir veya sınırlamayı kabul edebilir

# Senaryo 3: İzin reddedildi
try:
    data = access_database(query)
except PermissionError:
    messages.append({
        "role": "tool",
        "content": "Erişim reddedildi. Bu işlem için izniniz yok."
    })
```

**Akıllı LLM'ler şunları yapabilir:**
- Farklı parametrelerle yeniden deneme
- Alternatif araçlar kullanma
- Sınırlamaları kullanıcılara açıklama

---

## 🎯 Temel Desenler

### Desen 1: Basit Araç Çağırma
```
Kullanıcı → LLM → Araç → LLM → Yanıt
```
Kullanım: Tek işlem gerektiğinde

### Desen 2: Özyinelemeli Ajan
```
Kullanıcı → LLM → Araç → LLM → Araç → LLM → Yanıt
              ↑_______________|
```
Kullanım: Çok adımlı görevler, karmaşık sorgular

### Desen 3: Paralel Araçlar
```
Kullanıcı → LLM → [Araç1, Araç2, Araç3] → LLM → Yanıt
```
Kullanım: Birden fazla bağımsız işlem

### Desen 4: Sıralı Boru Hattı (Pipeline)
```
Kullanıcı → LLM → Araç1 → LLM → Araç2(Araç1 çıktısını kullanır) → LLM → Yanıt
```
Kullanım: Her adım önceki sonuca bağlı olduğunda

---

## 🐛 Hata Ayıklama İpuçları

### Araç Çağrılmıyor mu?

**Kontrol Edin:**
1. Araç açıklaması açık mı
2. Kullanıcı sorgusu araç amacıyla eşleşiyor mu
3. LLM isteğinde tools parametresi var mı

```python
# Hata Ayıklama: LLM'in hangi araçları gördüğünü yazdırın
print("Mevcut araçlar:", json.dumps(tools, indent=2))
```

### Yanlış Parametreler?

**Araç şemasını düzeltin:**
```python
# ❌ Belirsiz açıklama
"description": "Veri al"

# ✅ Açık açıklama
"description": "Belirli bir şehir için güncel hava durumunu al. Sıcaklığı Celsius ve hava durumunu döndürür."
```

### Sonsuz Döngü?

**İterasyon sınırı ekleyin:**
```python
MAX_ITERATIONS = 10

for i in range(MAX_ITERATIONS):
    response = llm.chat(messages, tools=tools)
    if not response.tool_calls:
        break
else:
    print("Uyarı: Maksimum iterasyona ulaşıldı!")
```

### Araç Çağrısı Ayrıştırma Hataları?

**Araç yanıtını doğrulayın:**
```python
def execute_tool(name, args):
    try:
        # Argümanları doğrula
        if name == "get_weather":
            if "city" not in args:
                return "Hata: 'city' parametresi eksik"

        # Aracı çalıştır
        result = tools[name](**args)
        return json.dumps(result)

    except Exception as e:
        # Hatayı araç sonucu olarak döndür
        return f"{name} çalıştırılırken hata: {str(e)}"
```

---

## 📊 Performans İpuçları

### 1. Araç Çağrılarını En Aza İndirin

```python
# ❌ Kötü: Aynı veri için birden fazla çağrı
weather_tokyo = get_weather("Tokyo")
weather_paris = get_weather("Paris")

# ✅ İyi: Birden fazla şehri işleyen toplu araç
weather = get_weather_batch(["Tokyo", "Paris"])
```

### 2. Araç Sonuçlarını Önbelleğe Alın

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_weather(city):
    # Tekrarlanan çağrılar için sonuçlar önbelleğe alınır
    return fetch_weather_api(city)
```

### 3. Araç Çağrılarını Zaman Aşımına Uğratın

```python
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Araç yürütme zaman aşımı")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(10)  # 10 saniye zaman aşımı

try:
    result = slow_tool_function()
finally:
    signal.alarm(0)  # Zaman aşımını iptal et
```

---

## 🚀 Sonraki Adımlar

### Şuna Hazırsınız:
✅ [02-agent-frameworks](../02-agent-frameworks) - Üretim ajanları için LangGraph & CrewAI kullanın

### Pratik Alıştırmaları:

1.  `02_multiple_tools.py` dosyasına **yeni bir araç ekleyin**
2.  Çok adımlı matematik yapabilen bir **hesap makinesi ajanı oluşturun**
3.  Kayıtları sorgulayabilen ve güncelleyebilen bir **veritabanı ajanı oluşturun**
4.  Araçlar başarısız olduğunda **yeniden deneme mantığı uygulayın**

---

## 📚 Ek Kaynaklar

- [OpenAI Fonksiyon Çağırma Rehberi](https://platform.openai.com/docs/guides/function-calling)
- [Ollama Araç Çağırma Dokümanları](https://github.com/ollama/ollama/blob/main/docs/api.md#tools)
- [Bukalemun örnekleriniz](../../chameleon/basics) - Gerçek dünya kalıpları

---

**Sıradaki:** [02-agent-frameworks](../02-agent-frameworks) - LangGraph ile profesyonel ajan geliştirme →
