#!/usr/bin/env python3
"""
Örnek 05: Sıralı Zincirler - Çok Adımlı İş Akışları
=====================================================

Karmaşık iş akışları için birden fazla LLM çağrısını nasıl zincirleneceğini öğrenin!

Ne öğreneceksiniz:
- Sıralı işleme (adım1 → adım2 → adım3)
- Adımlar arasında veri aktarımı
- LCEL (LangChain İfade Dili) - Modern yaklaşım
- Veri işleme için dönüşüm zincirleri
- Üretim boru hattı desenleri

GERÇEK çok adımlı ajanları bu şekilde oluşturursunuz!

Yazar: Beyhan MEYRALI
"""

from typing import Dict, Any, List
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


# =============================================================================
# BÖLÜM 1: Basit Sıralı Zincir (LCEL Stili)
# =============================================================================

class SimpleSequentialPipeline:
    """
    LCEL (LangChain İfade Dili) kullanarak basit sıralı boru hattı.

    Bu, LangChain 1.1.0+'da işlemleri zincirlemenin MODERN yoludur.
    Bileşenleri zincirleme için boru operatörünü (|) kullanır.
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Boru hattını başlat."""
        print(f"\n[BAŞLAT] {model} ile SimpleSequentialPipeline oluşturuluyor...")
        self.llm = OllamaLLM(model=model, temperature=0.7)
        print("[BAŞLAT] ✅ Boru hattı hazır!")

    def create_story_pipeline(self):
        """
        2 adımlı bir boru hattı oluştur: Fikir üret → Hikaye yaz

        Döndürür:
            Çalıştırılabilir zincir
        """
        print("\n[BORU HATTI] Hikaye oluşturma boru hattı inşa ediliyor...")

        # Adım 1: Hikaye fikri üret
        idea_prompt = PromptTemplate.from_template(
            "Bir cümlede yaratıcı bir {genre} hikaye fikri üret."
        )

        # Adım 2: Fikri tam hikayeye genişlet
        story_prompt = PromptTemplate.from_template(
            "Bu hikaye fikrini al ve 3 paragraflık kısa bir hikaye yaz:\n\n{idea}"
        )

        # LCEL kullanarak zincirle (boru operatörü)
        # idea_prompt | llm → fikir üretir
        # Sonra bunu story_prompt | llm'e aktar → tam hikaye üretir

        chain = (
            idea_prompt
            | self.llm
            | (lambda idea: {"idea": idea})
            | story_prompt
            | self.llm
            | StrOutputParser()
        )

        print("[BORU HATTI] ✅ Boru hattı: idea_prompt | llm | story_prompt | llm")
        return chain

    def run(self, genre: str) -> str:
        """Boru hattını çalıştır."""
        print(f"\n[ÇALIŞTIR] {genre} hikayesi oluşturuluyor...")

        chain = self.create_story_pipeline()
        result = chain.invoke({"genre": genre})

        print(f"\n[SONUÇ] Hikaye oluşturuldu!")
        return result


# =============================================================================
# BÖLÜM 2: Çok Adımlı Veri İşleme Boru Hattı
# =============================================================================

class DataProcessingPipeline:
    """
    Veri çıkarma ve işleme için çok adımlı boru hattı.

    Adımlar: Çıkar → Analiz Et → Özetle
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Boru hattını başlat."""
        self.llm = OllamaLLM(model=model, temperature=0.3)

    def create_analysis_pipeline(self):
        """
        3 adımlı analiz boru hattı oluştur.

        Adım 1: Ana noktaları çıkar
        Adım 2: Duyguyu analiz et
        Adım 3: Özet oluştur
        """

        # Adım 1: Ana noktaları çıkar
        extract_prompt = PromptTemplate.from_template(
            """Bu metinden ana noktaları madde listesi olarak çıkar:

Metin: {text}

Ana Noktalar:"""
        )

        # Adım 2: Duyguyu analiz et
        sentiment_prompt = PromptTemplate.from_template(
            """Bu ana noktaların duygusunu analiz et:

{key_points}

Duygu (olumlu/olumsuz/nötr):"""
        )

        # Adım 3: Özet oluştur
        summary_prompt = PromptTemplate.from_template(
            """Final özet oluştur:

Ana Noktalar: {key_points}
Duygu: {sentiment}

Özet:"""
        )

        # Boru hattını oluştur
        def extract_step(input_dict):
            """Adım 1: Ana noktaları çıkar."""
            result = (extract_prompt | self.llm).invoke(input_dict)
            return {"key_points": result, "text": input_dict["text"]}

        def sentiment_step(input_dict):
            """Adım 2: Duyguyu analiz et."""
            result = (sentiment_prompt | self.llm).invoke(input_dict)
            return {
                "key_points": input_dict["key_points"],
                "sentiment": result
            }

        def summary_step(input_dict):
            """Adım 3: Özet oluştur."""
            result = (summary_prompt | self.llm | StrOutputParser()).invoke(input_dict)
            return result

        # Bunları birbirine zincirle
        from langchain_core.runnables import RunnableLambda

        chain = (
            RunnableLambda(extract_step)
            | RunnableLambda(sentiment_step)
            | RunnableLambda(summary_step)
        )

        return chain

    def analyze(self, text: str) -> str:
        """Metni boru hattından geçirerek analiz et."""
        print("\n[BORU HATTI] 3 adımlı analiz çalıştırılıyor...")
        print("  Adım 1: Ana noktalar çıkarılıyor...")
        print("  Adım 2: Duygu analiz ediliyor...")
        print("  Adım 3: Özet oluşturuluyor...")

        chain = self.create_analysis_pipeline()
        result = chain.invoke({"text": text})

        return result


# =============================================================================
# BÖLÜM 3: Hata Yönetimli Üretim Boru Hattı
# =============================================================================

class ProductionPipeline:
    """
    Hata yönetimi ve günlükleme ile üretim sınıfı boru hattı.
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Üretim boru hattını başlat."""
        self.llm = OllamaLLM(model=model, temperature=0.5)

    def create_content_pipeline(self):
        """
        İçerik oluşturma boru hattı: Araştır → Taslak → Yaz → Düzenle
        """

        # Adım 1: Araştır
        research_prompt = PromptTemplate.from_template(
            """'{topic}' konusunu araştır ve 3 ana gerçeği listele.

Gerçekler:"""
        )

        # Adım 2: Taslak oluştur
        outline_prompt = PromptTemplate.from_template(
            """Bu gerçeklere dayanarak bir blog yazısı taslağı oluştur:

{facts}

Taslak:"""
        )

        # Adım 3: İçerik yaz
        write_prompt = PromptTemplate.from_template(
            """Bu taslağı takip ederek bir blog yazısı yaz:

{outline}

Blog Yazısı:"""
        )

        # Hata yönetimiyle boru hattı oluştur
        def safe_step(prompt, step_name):
            """Güvenli yürütme için sarmalayıcı."""
            def execute(input_dict):
                try:
                    print(f"  [{step_name}] İşleniyor...")
                    result = (prompt | self.llm).invoke(input_dict)
                    print(f"  [{step_name}] ✅ Tamamlandı")
                    return result
                except Exception as e:
                    print(f"  [{step_name}] ❌ Hata: {e}")
                    return f"{step_name}'de hata: {str(e)}"
            return execute

        # Hata yönetimiyle zincirle
        from langchain_core.runnables import RunnableLambda

        chain = (
            RunnableLambda(lambda x: {"topic": x["topic"]})
            | RunnableLambda(safe_step(research_prompt, "ARAŞTIRMA"))
            | (lambda facts: {"facts": facts})
            | RunnableLambda(safe_step(outline_prompt, "TASLAK"))
            | (lambda outline: {"outline": outline})
            | RunnableLambda(safe_step(write_prompt, "YAZMA"))
            | StrOutputParser()
        )

        return chain

    def create_content(self, topic: str) -> str:
        """Boru hattı aracılığıyla içerik oluştur."""
        print(f"\n[ÜRETİM] İçerik oluşturuluyor: {topic}")

        chain = self.create_content_pipeline()
        result = chain.invoke({"topic": topic})

        return result


# =============================================================================
# DEMOLAR
# =============================================================================

def demo_simple_sequential():
    """Demo: Basit 2 adımlı boru hattı."""
    print("\n" + "="*70)
    print("DEMO 1: Basit Sıralı Boru Hattı")
    print("="*70)

    pipeline = SimpleSequentialPipeline()
    story = pipeline.run("bilim kurgu")

    print("\n[HİKAYE]:")
    print("-" * 70)
    print(story)
    print("-" * 70)


def demo_data_processing():
    """Demo: Çok adımlı veri işleme."""
    print("\n" + "="*70)
    print("DEMO 2: Veri İşleme Boru Hattı")
    print("="*70)

    text = """
    Yeni yapay zeka ürün lansmanı büyük bir başarıydı! Müşteri geri bildirimleri
    son derece olumlu oldu. Satışlar beklentileri %150 aştı. Ekip
    inanılmaz derecede çok çalıştı ve harika bir sonuç verdi. Bazı küçük hatalar
    bildirildi ancak hızlıca düzeltildi.
    """

    pipeline = DataProcessingPipeline()
    summary = pipeline.analyze(text)

    print("\n[ÖZET]:")
    print("-" * 70)
    print(summary)
    print("-" * 70)


def demo_production_pipeline():
    """Demo: Üretim boru hattı."""
    print("\n" + "="*70)
    print("DEMO 3: Üretim İçerik Boru Hattı")
    print("="*70)

    pipeline = ProductionPipeline()
    content = pipeline.create_content("Yapay zeka ajanlarının faydaları")

    print("\n[İÇERİK]:")
    print("-" * 70)
    print(content)
    print("-" * 70)


def main():
    """Ana giriş noktası."""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║         Örnek 05: Sıralı Zincirler                                ║
║                                                                   ║
║  Bu şunları gösterir:                                            ║
║  • LCEL (LangChain İfade Dili) - Modern yaklaşım               ║
║  • | operatörü ile işlemleri borulama                           ║
║  • Çok adımlı sıralı iş akışları                                ║
║  • Adımlar arasında veri dönüşümü                               ║
║  • Üretim boru hattı desenleri                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Demoları çalıştır
    demo_simple_sequential()
    demo_data_processing()
    demo_production_pipeline()

    # Özet
    print("\n" + "="*70)
    print("✅ TAMAMLANDI!")
    print("="*70)
    print("\n🎓 Ne öğrendiniz:")
    print("  1. LCEL (LangChain İfade Dili) - Modern zincirleme")
    print("  2. Sıralı işlemler için boru operatörü (|)")
    print("  3. Çok adımlı iş akışları (çıkar → analiz et → özetle)")
    print("  4. Zincir adımları arasında veri aktarımı")
    print("  5. Hata yönetimiyle üretim desenleri")
    print("\n📖 Temel Kavramlar:")
    print("  • Sıralı = Birbiri ardına bir adım")
    print("  • LCEL = Modern LangChain zincirleme (kullanımdan kaldırılmadı)")
    print("  • Boru (|) = Bileşenleri birbirine bağla")
    print("  • Dönüşüm = Adımlar arasında veriyi değiştir")
    print("\n💡 LCEL vs Eski SequentialChain:")
    print("  ESKİ (kullanımdan kaldırıldı): SequentialChain([chain1, chain2])")
    print("  YENİ (LCEL):                   prompt | llm | parser")
    print("  LCEL daha basit, daha esnek ve kullanımdan kaldırılmadı!")
    print("\n➡️  Sıradaki: python 06_router_chains.py")
    print("="*70)


if __name__ == "__main__":
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("[UYARI] Ollama doğru çalışmıyor olabilir")
    except:
        print("[HATA] Ollama'ya bağlanılamıyor!")
        print("  Çözüm: ollama serve")
        exit(1)

    main()
