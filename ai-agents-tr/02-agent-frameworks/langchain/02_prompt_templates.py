#!/usr/bin/env python3
"""
Örnek 02: Gelişmiş Prompt Şablonları
======================================

Prompt şablonlarında ustalaşın - etkili yapay zeka ajanlarının temeli.

Ne öğreneceksiniz:
- Farklı prompt şablonu türleri
- Değişken ikamesi
- Few-shot prompting (Az örnekle öğrenme)
- Sohbet promptları vs tamamlama promptları
- Prompt mühendisliği için en iyi uygulamalar

Bu, gelişmiş prompting tekniklerini göstererek 01_basic_chain.py üzerine inşa eder.

Yazar: Beyhan MEYRALI
"""

from typing import List, Dict, Any
from langchain_ollama import OllamaLLM
from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    FewShotPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.output_parsers import StrOutputParser


class PromptTemplateExamples:
    """
    Farklı prompt şablonu türlerinin kapsamlı örnekleri.

    Bu sınıf, üretimde kullanılan tüm ana prompt şablonu desenlerini gösterir.
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Bir LLM ile başlat."""
        print(f"\n[BAŞLAT] LLM oluşturuluyor: {model}")
        self.llm = OllamaLLM(model=model, temperature=0.7)

    def example_1_basic_template(self):
        """Tek değişkenli temel şablon."""
        print("\n" + "="*70)
        print("ÖRNEK 1: Temel Şablon (Tek Değişken)")
        print("="*70)

        template = "Bana {topic} hakkında {adjective} bir gerçek söyle."

        prompt = PromptTemplate(
            template=template,
            input_variables=["adjective", "topic"]
        )

        # LCEL Zinciri
        chain = prompt | self.llm | StrOutputParser()

        # Farklı girdilerle test et
        result1 = chain.invoke({"adjective": "ilginç", "topic": "okyanus"})
        result2 = chain.invoke({"adjective": "şaşırtıcı", "topic": "kuantum fiziği"})

        print(f"\n✅ Sonuç 1: {result1[:100]}...")
        print(f"✅ Sonuç 2: {result2[:100]}...")

    def example_2_multiline_template(self):
        """Karmaşık çok satırlı şablon."""
        print("\n" + "="*70)
        print("ÖRNEK 2: Çok Satırlı Şablon (Daha İyi Yapı)")
        print("="*70)

        template = """Sen uzman bir {role}sin.

Görev: {task}

Bağlam:
{context}

Gereksinimler:
1. Özlü ol
2. Örnekler kullan
3. Pratik ol

Lütfen cevabını ver:"""

        prompt = PromptTemplate(
            template=template,
            input_variables=["role", "task", "context"]
        )

        chain = prompt | self.llm | StrOutputParser()

        result = chain.invoke({
            "role": "Python geliştiricisi",
            "task": "Liste comprehension'ları açıkla",
            "context": "Temel for döngülerini bilen yeni başlayanlara öğretiyorsun"
        })

        print(f"\n✅ Sonuç: {result[:200]}...")

    def example_3_few_shot_prompting(self):
        """Örneklerle few-shot öğrenme."""
        print("\n" + "="*70)
        print("ÖRNEK 3: Few-Shot Prompting (Örneklerden Öğrenme)")
        print("="*70)

        # Örnekleri tanımla
        examples = [
            {
                "input": "mutlu",
                "output": "neşeli, sevinçli, keyifli"
            },
            {
                "input": "üzgün",
                "output": "melankolik, kederli, mahzun"
            },
        ]

        # Örnek şablonu oluştur
        example_template = """
Girdi: {input}
Çıktı: {output}
"""

        example_prompt = PromptTemplate(
            template=example_template,
            input_variables=["input", "output"]
        )

        # Few-shot şablonu oluştur
        few_shot_prompt = FewShotPromptTemplate(
            examples=examples,
            example_prompt=example_prompt,
            prefix="Her kelime için 3 eş anlamlı ver:\n",
            suffix="\nGirdi: {word}\nÇıktı:",
            input_variables=["word"]
        )

        chain = few_shot_prompt | self.llm | StrOutputParser()

        # Yeni kelime ile test et
        result = chain.invoke({"word": "kızgın"})

        print("\n[GÖNDERİLEN PROMPT]:")
        print(few_shot_prompt.format(word="kızgın"))
        print(f"\n✅ Sonuç: {result}")

    def example_4_chat_template(self):
        """Sistem ve kullanıcı mesajlarıyla sohbet tarzı promptlar."""
        print("\n" + "="*70)
        print("ÖRNEK 4: Sohbet Şablonu (Sistem + Kullanıcı Mesajları)")
        print("="*70)

        chat_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "Sen bir {role}sin. Her zaman {style} tarzında yanıt veriyorsun."
            ),
            HumanMessagePromptTemplate.from_template(
                "{user_message}"
            )
        ])

        chain = chat_prompt | self.llm | StrOutputParser()

        result = chain.invoke({
            "role": "korsan kaptanı",
            "style": "korsan",
            "user_message": "Bugün hava nasıl?"
        })

        print(f"\n✅ Sonuç: {result[:200]}...")

    def example_5_conditional_template(self):
        """Koşullu mantıklı şablon."""
        print("\n" + "="*70)
        print("ÖRNEK 5: Koşullu Şablon (Dinamik İçerik)")
        print("="*70)

        def create_conditional_prompt(include_examples: bool) -> str:
            """İsteğe bağlı örnekler bölümü ile prompt oluştur."""
            base = "Şu soruyu yanıtla: {question}\n"

            if include_examples:
                base += "\nCevabında 2-3 örnek ver.\n"

            return base

        # Örneklerle
        prompt_with_ex = PromptTemplate(
            template=create_conditional_prompt(True),
            input_variables=["question"]
        )

        # Örneksiz
        prompt_without_ex = PromptTemplate(
            template=create_conditional_prompt(False),
            input_variables=["question"]
        )

        chain_with = prompt_with_ex | self.llm | StrOutputParser()
        chain_without = prompt_without_ex | self.llm | StrOutputParser()

        question = "Programlamada özyineleme (recursion) nedir?"

        result_with = chain_with.invoke({"question": question})
        result_without = chain_without.invoke({"question": question})

        print(f"\n✅ Örneklerle: {result_with[:150]}...")
        print(f"\n✅ Örneksiz: {result_without[:150]}...")


class ProductionPromptAgent:
    """
    Optimize edilmiş promptlarla üretime hazır ajan.

    Bu, üretim prompt mühendisliği için en iyi uygulamaları gösterir.
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Ajanı başlat."""
        self.llm = OllamaLLM(model=model, temperature=0.7)

        # Farklı görevler için farklı promptlar
        self.prompts = {
            "summarize": self._create_summarize_prompt(),
            "extract": self._create_extract_prompt(),
            "classify": self._create_classify_prompt(),
        }

        # Zincirleri oluştur
        self.chains = {
            name: prompt | self.llm | StrOutputParser()
            for name, prompt in self.prompts.items()
        }

    def _create_summarize_prompt(self) -> PromptTemplate:
        """Özetleme için prompt."""
        template = """Aşağıdaki metni {num_sentences} cümlede özetle.

Metin:
{text}

Özet:"""
        return PromptTemplate(
            template=template,
            input_variables=["text", "num_sentences"]
        )

    def _create_extract_prompt(self) -> PromptTemplate:
        """Bilgi çıkarma için prompt."""
        template = """Aşağıdaki metinden {information_type} çıkar.

Metin:
{text}

Çıkarılan {information_type}:"""
        return PromptTemplate(
            template=template,
            input_variables=["text", "information_type"]
        )

    def _create_classify_prompt(self) -> PromptTemplate:
        """Sınıflandırma için prompt."""
        template = """Aşağıdaki metni şu kategorilerden birine sınıflandır:
{categories}

Metin:
{text}

Kategori:"""
        return PromptTemplate(
            template=template,
            input_variables=["text", "categories"]
        )

    def summarize(self, text: str, num_sentences: int = 2) -> str:
        """Metni özetle."""
        return self.chains["summarize"].invoke({
            "text": text,
            "num_sentences": num_sentences
        })

    def extract(self, text: str, information_type: str) -> str:
        """Metinden bilgi çıkar."""
        return self.chains["extract"].invoke({
            "text": text,
            "information_type": information_type
        })

    def classify(self, text: str, categories: List[str]) -> str:
        """Metni sınıflandır."""
        return self.chains["classify"].invoke({
            "text": text,
            "categories": ", ".join(categories)
        })


def demo_production_agent():
    """Üretim ajanını göster."""
    print("\n" + "="*70)
    print("DEMO: Çoklu Prompt Türleriyle Üretim Ajanı")
    print("="*70)

    agent = ProductionPromptAgent()

    # Özetlemeyi test et
    text = """
    Yapay Zeka (AI), nasıl çalıştığımızı ve yaşadığımızı dönüştürüyor.
    Makine öğrenimi algoritmaları artık verilerdeki kalıpları tanıyabiliyor,
    tahminler yapabiliyor ve hatta yeni içerik oluşturabiliyor. Derin öğrenme,
    makine öğreniminin bir alt kümesi, insan beynine benzer şekillerde
    bilgiyi işlemek için sinir ağlarını kullanıyor.
    """

    print("\n[1] Özetleme:")
    summary = agent.summarize(text, num_sentences=2)
    print(f"   {summary}")

    # Çıkarmayı test et
    print("\n[2] Bilgi Çıkarma:")
    extracted = agent.extract(text, information_type="bahsedilen ana teknolojiler")
    print(f"   {extracted}")

    # Sınıflandırmayı test et
    review = "Bu ürün harika! Şimdiye kadarki en iyi alışveriş!"
    print("\n[3] Sınıflandırma:")
    category = agent.classify(
        review,
        categories=["olumlu", "olumsuz", "nötr"]
    )
    print(f"   {category}")


def main():
    """Ana giriş noktası."""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║         Örnek 02: Gelişmiş Prompt Şablonları                      ║
║                                                                   ║
║  Bu şunları gösterir:                                            ║
║  • Değişkenli temel şablonlar                                   ║
║  • Çok satırlı yapılandırılmış şablonlar                        ║
║  • Few-shot prompting                                           ║
║  • Sohbet şablonları (sistem + kullanıcı)                       ║
║  • Üretime hazır prompt desenleri                               ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Örnekleri çalıştır
    examples = PromptTemplateExamples()
    examples.example_1_basic_template()
    examples.example_2_multiline_template()
    examples.example_3_few_shot_prompting()
    examples.example_4_chat_template()
    examples.example_5_conditional_template()

    # Üretim demosu
    demo_production_agent()

    # Özet
    print("\n" + "="*70)
    print("✅ TAMAMLANDI!")
    print("="*70)
    print("\n🎓 Ne öğrendiniz:")
    print("  1. Değişken ikameli temel şablonlar")
    print("  2. Yapı için çok satırlı şablonlar")
    print("  3. Daha iyi sonuçlar için few-shot prompting")
    print("  4. Sohbet şablonları (sistem + kullanıcı mesajları)")
    print("  5. Üretim desenleri (özetle, çıkar, sınıflandır)")
    print("\n📖 En İyi Uygulamalar:")
    print("  • Promptlarınızda spesifik olun")
    print("  • Karmaşık görevler için örnekler (few-shot) kullanın")
    print("  • Promptları net bölümlerle yapılandırın")
    print("  • Tutarlılık için şablonları yeniden kullanın")
    print("\n➡️  Sıradaki: python 03_chains_with_memory.py")
    print("="*70)


if __name__ == "__main__":
    main()
