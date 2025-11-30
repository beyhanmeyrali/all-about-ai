# CrewAI: Çoklu Ajan Ekiplerini Orkestre Etme 🚣‍♂️

> "Yetenek maç kazandırır, ancak takım çalışması ve zeka şampiyonluk kazandırır." – Michael Jordan

## 🪟 Windows Kullanıcıları: WSL2 Kurulumu Gerekli

CrewAI, C++ derleme araçlarına ihtiyaç duyan ChromaDB gerektirir. Bu örnekleri Windows'ta çalıştırmanın en kolay yolu WSL2 (Linux için Windows Alt Sistemi) kullanmaktır.

**📖 Tam kurulum talimatları için [WSL2_SETUP.md](./WSL2_SETUP.md) dosyasına bakın.**

**Hızlı Başlangıç:**
```bash
# PowerShell'de (Yönetici olarak)
wsl --install

# Yeniden başlattıktan sonra, Ubuntu'da:
cd /mnt/d/workspace/all-about-ai/ai-agents/02-agent-frameworks/crewai
python3 -m venv .venv
source .venv/bin/activate
pip install crewai crewai-tools langchain-ollama
python 01_simple_crew.py
```

**Neden WSL2?**
- ✅ Tam CrewAI işlevselliği (tüm hafıza özellikleri çalışır)
- ✅ Betik değişikliği gerekmez
- ✅ Genel olarak AI/ML geliştirme için daha iyidir
- ✅ Tek seferlik kurulum

**Alternatifler:** Docker veya yerel Linux/Mac

---

CrewAI, **rol yapan, otonom yapay zeka ajanlarını** orkestre etmek için tasarlanmış bir frameworktür. İşbirlikçi zekayı teşvik ederek, CrewAI ajanların sorunsuz bir şekilde birlikte çalışmasını sağlar ve tek bir ajanın halletmesi zor olan karmaşık görevlerin üstesinden gelir.

## 🧠 Temel Kavramlar

### 1. Ajanlar (Takım Üyeleri)
Ajanlar, görevleri yerine getirmek, kararlar almak ve diğer ajanlarla iletişim kurmak için programlanmış otonom birimlerdir. Onları, her biri belirli becerilere ve yapılacak belirli bir işe sahip bir takımın üyeleri olarak düşünün.
- **Rol:** İş unvanları nedir? (örn. "Kıdemli Araştırmacı")
- **Hedef:** Neyi başarmaya çalışıyorlar? (örn. "Çığır açan teknolojileri ortaya çıkarmak")
- **Arka Plan:** Kişilikleri ve geçmişleri nedir? (LLM'in karakterde kalmasına yardımcı olur)

### 2. Görevler (Atamalar)
Görevler, ajanların tamamlaması gereken belirli atamalardır.
- **Açıklama:** Ne yapılması gerekiyor?
- **Beklenen Çıktı:** Sonuç neye benzemeli?
- **Ajan:** Bu görevden kim sorumlu?

### 3. Ekip (Takım)
Bir Ekip (Crew), bir dizi görevi başarmak için birlikte çalışan işbirlikçi bir ajan grubunu temsil eder.
- **Süreç:** Birlikte nasıl çalışırlar? (Sıralı, Hiyerarşik)
- **Ayrıntılı:** İç monologlarını görmek istiyor musunuz?

## 🚀 Neden CrewAI?

LangChain ve LangGraph *tek* güçlü ajanlar veya tanımlanmış iş akışları oluşturmak için harika olsa da, CrewAI bir uzmanlar **takımına** ihtiyacınız olduğunda parlar.

| Özellik | Tek Ajan | CrewAI (Çoklu Ajan) |
|---------|----------|---------------------|
| **Odak** | Genelci | Uzman |
| **Karmaşıklık** | Doğrusal düşünme | Paralel/İşbirlikçi düşünme |
| **Hata Düzeltme** | Sadece kendi kendini düzeltme | Akran değerlendirmesi & delegasyon |
| **Yaratıcılık** | Tek bir bakış açısıyla sınırlı | Farklı bakış açıları |

## 🛠️ Yerel Yığın

CrewAI'ı yerel olarak çalışan **Ollama** ile kullanacağız.

- **LLM:** `qwen3:8b` (Ollama aracılığıyla)
- **Framework:** `crewai`

## 📂 Örnekler Yapısı

1. **00_crew_basics.py** - Çoklu ajan sistemlerinin "Merhaba Dünya"sı
2. **01_simple_crew.py** - 2 ajanlı bir araştırma ekibi
3. **02_sequential_tasks.py** - Ajanlar arasında veri aktarımı
4. **03_hierarchical_crew.py** - Çalışanlara delege eden yönetici
5. **04_tools_in_crew.py** - Ajanlara süper güçler (araçlar) verme
6. **07_production_crew.py** - Tam bir içerik oluşturma stüdyosu

Hadi ilk yapay zeka takımınızı kuralım! 🚀
