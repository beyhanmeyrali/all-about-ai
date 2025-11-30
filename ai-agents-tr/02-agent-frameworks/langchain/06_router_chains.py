#!/usr/bin/env python3
"""
Örnek 06: Yönlendirici Zincirler - Koşullu Yönlendirme
================================================

İstekleri içeriğe göre farklı işleyicilere nasıl yönlendireceğinizi öğrenin!

Ne öğreneceksiniz:
- Koşullu yönlendirme (eğer bu → işleyici A, değilse → işleyici B)
- LLM tabanlı yönlendirme (yapay zekanın rotayı belirlemesine izin ver)
- Kural tabanlı yönlendirme (programatik mantık)
- Çoklu hedef yönlendirme
- Üretim yönlendirme desenleri

Akıllı istek yönlendirmesini bu şekilde oluşturursunuz!

Yazar: Beyhan MEYRALI
"""

from typing import Dict, Any, Literal
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnableBranch


# =============================================================================
# BÖLÜM 1: Basit Kural Tabanlı Yönlendirici
# =============================================================================

class SimpleRouter:
    """
    if/else mantığı kullanan basit yönlendirici.

    Anahtar kelimelere göre farklı işleyicilere yönlendirir.
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Yönlendiriciyi başlat."""
        print(f"\n[BAŞLAT] {model} ile SimpleRouter oluşturuluyor...")
        self.llm = OllamaLLM(model=model, temperature=0.7)

        # Uzmanlaşmış işleyicileri tanımla
        self.handlers = {
            "technical": self._create_technical_handler(),
            "creative": self._create_creative_handler(),
            "business": self._create_business_handler(),
        }

        print("[BAŞLAT] ✅ Yönlendirici 3 işleyici ile hazır!")

    def _create_technical_handler(self):
        """Teknik sorular için işleyici."""
        prompt = PromptTemplate.from_template(
            """Teknik bir uzmansın. Bu teknik soruyu yanıtla:

{question}

Teknik Cevap:"""
        )
        return prompt | self.llm | StrOutputParser()

    def _create_creative_handler(self):
        """Yaratıcı istekler için işleyici."""
        prompt = PromptTemplate.from_template(
            """Yaratıcı bir yazarsın. Buna yaratıcı yanıt ver:

{question}

Yaratıcı Yanıt:"""
        )
        return prompt | self.llm | StrOutputParser()

    def _create_business_handler(self):
        """İş soruları için işleyici."""
        prompt = PromptTemplate.from_template(
            """Bir iş danışmanısın. Bu iş sorusunu yanıtla:

{question}

İş Cevabı:"""
        )
        return prompt | self.llm | StrOutputParser()

    def route(self, question: str) -> str:
        """
        Soruyu uygun işleyiciye yönlendir.

        Argümanlar:
            question: Kullanıcı sorusu

        Döndürür:
            Seçilen işleyiciden gelen yanıt
        """
        # Basit anahtar kelime tabanlı yönlendirme
        question_lower = question.lower()

        if any(word in question_lower for word in ["kod", "programlama", "teknik", "api"]):
            print("[YÖNLENDİRİCİ] → teknik işleyici")
            handler = self.handlers["technical"]
        elif any(word in question_lower for word in ["hikaye", "yaratıcı", "yaz", "şiir"]):
            print("[YÖNLENDİRİCİ] → yaratıcı işleyici")
            handler = self.handlers["creative"]
        elif any(word in question_lower for word in ["iş", "pazar", "strateji", "gelir"]):
            print("[YÖNLENDİRİCİ] → iş işleyici")
            handler = self.handlers["business"]
        else:
            print("[YÖNLENDİRİCİ] → teknik işleyici (varsayılan)")
            handler = self.handlers["technical"]

        return handler.invoke({"question": question})


# =============================================================================
# BÖLÜM 2: LLM Tabanlı Akıllı Yönlendirici
# =============================================================================

class IntelligentRouter:
    """
    Hangi işleyicinin kullanılacağına karar vermek için LLM kullanan yönlendirici.

    LLM soruyu analiz eder ve en iyi işleyiciyi seçer.
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Akıllı yönlendiriciyi başlat."""
        self.llm = OllamaLLM(model=model, temperature=0.0)  # Tutarlı yönlendirme için düşük sıcaklık
        self.answer_llm = OllamaLLM(model=model, temperature=0.7)

    def route(self, question: str) -> str:
        """
        LLM kararı kullanarak yönlendir.

        Adım 1: LLM kategoriyi belirler
        Adım 2: Uygun işleyiciye yönlendir
        """
        # Adım 1: LLM'den kategorize etmesini iste
        categorize_prompt = PromptTemplate.from_template(
            """Bu soruyu BİR kategoriye ayır:
- teknik (programlama, kod, API'ler, teknoloji)
- yaratıcı (yazma, hikayeler, sanat, yaratıcı görevler)
- iş (strateji, pazarlama, gelir, iş tavsiyesi)

Soru: {question}

Kategori (sadece bir kelime):"""
        )

        category_chain = categorize_prompt | self.llm | StrOutputParser()
        category = category_chain.invoke({"question": question}).strip().lower()

        print(f"[LLM YÖNLENDİRİCİ] Kategori: {category}")

        # Adım 2: İşleyiciye yönlendir
        if "teknik" in category or "technical" in category:
            handler_prompt = "Teknik bir uzmansın. Yanıtla: {question}"
        elif "yaratıcı" in category or "creative" in category:
            handler_prompt = "Yaratıcı bir yazarsın. Yanıtla: {question}"
        elif "iş" in category or "business" in category:
            handler_prompt = "Bir iş danışmanısın. Yanıtla: {question}"
        else:
            handler_prompt = "Bu soruyu yanıtla: {question}"

        # İşleyiciyi çalıştır
        prompt = PromptTemplate.from_template(handler_prompt)
        chain = prompt | self.answer_llm | StrOutputParser()

        return chain.invoke({"question": question})


# =============================================================================
# BÖLÜM 3: RunnableBranch ile Modern LCEL Yönlendirici
# =============================================================================

class ModernRouter:
    """
    RunnableBranch kullanan modern yönlendirici (LCEL yaklaşımı).

    Bu, LangChain 1.1.0+'da ÖNERİLEN yoldur
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Modern yönlendiriciyi başlat."""
        self.llm = OllamaLLM(model=model, temperature=0.7)

    def create_router_chain(self):
        """
        RunnableBranch kullanarak yönlendirici oluştur.

        Soru içeriğine göre dallanır.
        """

        # İşleyicileri tanımla
        technical_prompt = PromptTemplate.from_template(
            "Teknik Uzman: {question}\n\nCevap:"
        )
        creative_prompt = PromptTemplate.from_template(
            "Yaratıcı Yazar: {question}\n\nYanıt:"
        )
        general_prompt = PromptTemplate.from_template(
            "Asistan: {question}\n\nCevap:"
        )

        # Her dal için zincir oluştur
        technical_chain = technical_prompt | self.llm
        creative_chain = creative_prompt | self.llm
        general_chain = general_prompt | self.llm

        # Yönlendirme mantığını tanımla
        def is_technical(input_dict):
            """Teknik soru mu kontrol et."""
            question = input_dict["question"].lower()
            return any(word in question for word in ["kod", "code", "programlama", "programming", "api", "teknik", "technical"])

        def is_creative(input_dict):
            """Yaratıcı istek mi kontrol et."""
            question = input_dict["question"].lower()
            return any(word in question for word in ["hikaye", "story", "şiir", "poem", "yaratıcı", "creative", "yaz", "write"])

        # Dal oluştur (modern LCEL yolu)
        branch = RunnableBranch(
            (is_technical, technical_chain),
            (is_creative, creative_chain),
            general_chain  # varsayılan
        )

        return branch

    def route(self, question: str) -> str:
        """Soruyu dal üzerinden yönlendir."""
        chain = self.create_router_chain()
        result = chain.invoke({"question": question})
        return result


# =============================================================================
# DEMOLAR
# =============================================================================

def demo_simple_router():
    """Demo: Basit anahtar kelime tabanlı yönlendirici."""
    print("\n" + "="*70)
    print("DEMO 1: Basit Kural Tabanlı Yönlendirici")
    print("="*70)

    router = SimpleRouter()

    questions = [
        "Python fonksiyonu nasıl yazarım?",
        "Uzay hakkında kısa bir hikaye yaz",
        "Yeni başlayanlar için iyi bir iş stratejisi nedir?"
    ]

    for q in questions:
        print(f"\n[S]: {q}")
        answer = router.route(q)
        print(f"[C]: {answer[:100]}...")


def demo_intelligent_router():
    """Demo: LLM tabanlı yönlendirme."""
    print("\n" + "="*70)
    print("DEMO 2: LLM Tabanlı Akıllı Yönlendirici")
    print("="*70)

    router = IntelligentRouter()

    question = "REST API'lerini basit terimlerle açıkla"
    print(f"\n[S]: {question}")
    answer = router.route(question)
    print(f"[C]: {answer[:150]}...")


def demo_modern_router():
    """Demo: Modern LCEL yönlendirici."""
    print("\n" + "="*70)
    print("DEMO 3: Modern LCEL Yönlendirici (RunnableBranch)")
    print("="*70)

    router = ModernRouter()

    questions = [
        "Bana bir Python kod örneği göster",
        "Yapay zeka hakkında bir haiku yaz"
    ]

    for q in questions:
        print(f"\n[S]: {q}")
        answer = router.route(q)
        print(f"[C]: {answer[:100]}...")


def main():
    """Ana giriş noktası."""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║         Örnek 06: Yönlendirici Zincirler                          ║
║                                                                   ║
║  Bu şunları gösterir:                                            ║
║  • Kural tabanlı yönlendirme (anahtar kelime eşleştirme)        ║
║  • LLM tabanlı yönlendirme (akıllı kategorilendirme)            ║
║  • Modern LCEL yönlendirme (RunnableBranch)                     ║
║  • Çoklu hedef yönlendirme                                       ║
║  • Üretim yönlendirme desenleri                                  ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Demoları çalıştır
    demo_simple_router()
    demo_intelligent_router()
    demo_modern_router()

    # Özet
    print("\n" + "="*70)
    print("✅ TAMAMLANDI!")
    print("="*70)
    print("\n🎓 Ne öğrendiniz:")
    print("  1. Kural tabanlı yönlendirme (anahtar kelime eşleştirme)")
    print("  2. LLM tabanlı yönlendirme (akıllı kararlar)")
    print("  3. RunnableBranch (modern LCEL yaklaşımı)")
    print("  4. Çoklu işleyici yönlendirme desenleri")
    print("  5. Üretim yönlendirme en iyi uygulamaları")
    print("\n📖 Temel Kavramlar:")
    print("  • Yönlendirici = İstekleri uygun işleyicilere yönlendirir")
    print("  • Dal = Zincirlerde koşullu mantık")
    print("  • İşleyici = Her kategori için uzmanlaşmış işleme")
    print("  • Yönlendirme = Dinamik vs Statik")
    print("\n💡 Ne Zaman Kullanılır:")
    print("  • Çoklu alan sohbet botları (teknik, yaratıcı, iş)")
    print("  • Uzmanlaşmış uzman sistemler")
    print("  • Modeller arasında yük dengeleme")
    print("  • Departmana özel yönlendirme")
    print("\n➡️  Sıradaki: python 07_production_agent.py")
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
