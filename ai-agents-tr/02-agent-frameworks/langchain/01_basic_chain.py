#!/usr/bin/env python3
"""
Örnek 01: Temel LangChain - İlk Zinciriniz
===============================================

Bu, mümkün olan EN BASİT LangChain örneğidir.
Temel kavramları öğrenin: LLM, Prompt, Zincir.

Ne öğreneceksiniz:
- Bir LLM örneği nasıl oluşturulur
- Basit bir prompt nasıl oluşturulur
- Bunlar nasıl birbirine zincirlenir
- Zincir nasıl çağrılır

Bu, LangChain için "Merhaba Dünya"nızdır!

HATA AYIKLAMA İPUÇLARI:
--------------
1. OllamaLLM bulunamazsa:
   pip install langchain-ollama

2. Bağlantı başarısız olursa:
   - Ollama'nın çalıştığını kontrol edin: ollama serve
   - Modelin var olduğunu kontrol edin: ollama list

3. Ne olduğunu görmek için:
   - LLMChain'de verbose=True ayarlayın
   - print() ifadeleri ekleyin

Yazar: Beyhan MEYRALI
"""

from typing import Dict, Any
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


class BasicChainAgent:
    """
    Soruları yanıtlayan basit bir LangChain ajanı.

    Bu, en temel LangChain desenini gösterir:
    Prompt → LLM → Yanıt

    Özellikler:
        llm: Dil modeli örneği
        prompt_template: Promptları biçimlendirmek için şablon
        chain: Her şeyi bir araya getiren LLMChain
    """

    def __init__(self, model: str = "qwen3:8b", temperature: float = 0.7):
        """
        Temel zincir ajanını başlat.

        Argümanlar:
            model: Ollama model adı
            temperature: LLM sıcaklığı (0.0 = deterministik, 1.0 = yaratıcı)
        """
        print(f"\n[BAŞLAT] {model} ile BasicChainAgent oluşturuluyor...")

        # Adım 1: LLM örneği oluştur
        self.llm = self._create_llm(model, temperature)

        # Adım 2: Prompt şablonu oluştur
        self.prompt_template = self._create_prompt_template()

        # Adım 3: Zinciri oluştur
        self.chain = self._create_chain()

        print("[BAŞLAT] ✅ Ajan başarıyla başlatıldı!")

    def _create_llm(self, model: str, temperature: float) -> OllamaLLM:
        """
        Bir Ollama LLM örneği oluştur.

        Bu, Ollama ile konuşan çekirdek bileşendir.

        Argümanlar:
            model: Model adı
            temperature: Yaratıcılık seviyesi

        Döndürür:
            Yapılandırılmış OllamaLLM örneği
        """
        print(f"  LLM oluşturuluyor: {model} (temperature={temperature})")

        llm = OllamaLLM(
            model=model,
            temperature=temperature,
            # base_url="http://localhost:11434",  # Varsayılan, özelleştirilebilir
        )

        return llm

    def _create_prompt_template(self) -> PromptTemplate:
        """
        Bir prompt şablonu oluştur.

        Şablonlar, farklı girdilerle promptları yeniden kullanmamızı sağlar.

        Döndürür:
            PromptTemplate örneği
        """
        print("  Prompt şablonu oluşturuluyor...")

        template = """Yardımsever bir yapay zeka asistanısın.

Kullanıcı sorusu: {question}

Lütfen net ve özlü bir cevap ver."""

        prompt = PromptTemplate(
            template=template,
            input_variables=["question"]
        )

        return prompt

    def _create_chain(self):
        """
        LCEL zincirini oluştur.

        Bu, LCEL kullanarak promptu ve LLM'i yeniden kullanılabilir bir zincirde birleştirir.

        Döndürür:
            Yapılandırılmış LCEL zinciri
        """
        print("  LCEL zinciri oluşturuluyor...")

        # Modern LCEL sözdizimi: prompt | llm | parser
        chain = self.prompt_template | self.llm | StrOutputParser()

        return chain

    def ask(self, question: str) -> str:
        """
        Bir soru sor ve cevap al.

        Bu, kullanacağınız ana metoddur.

        Argümanlar:
            question: Sorulacak soru

        Döndürür:
            LLM'in cevabı
        """
        print(f"\n[SORULUYOR] {question}")

        try:
            # LCEL invoke kullanarak zinciri çalıştır
            response = self.chain.invoke({"question": question})

            print(f"[CEVAP] {response[:100]}...")
            return response

        except Exception as e:
            error_msg = f"Hata: {str(e)}"
            print(f"[HATA] {error_msg}")
            return error_msg

    def ask_with_details(self, question: str) -> Dict[str, Any]:
        """
        Bir soru sor ve ayrıntılı bilgi al.

        Bu, arka planda ne olduğunu gösterir.

        Argümanlar:
            question: Sorulacak soru

        Döndürür:
            Soru, cevap ve meta veri içeren sözlük
        """
        print(f"\n[AYRINTILI SOR] {question}")

        # Promptu biçimlendir
        formatted_prompt = self.prompt_template.format(question=question)

        print(f"\n[LLM'E GÖNDERİLEN PROMPT]:")
        print("-" * 70)
        print(formatted_prompt)
        print("-" * 70)

        # LCEL kullanarak yanıt al
        response = self.chain.invoke({"question": question})

        print(f"\n[LLM'DEN GELEN YANIT]:")
        print("-" * 70)
        print(response)
        print("-" * 70)

        return {
            "question": question,
            "formatted_prompt": formatted_prompt,
            "answer": response,
            "model": "qwen3:8b",
        }


def demo_basic_usage():
    """Temel kullanımı göster."""
    print("\n" + "="*70)
    print("DEMO 1: Temel Kullanım")
    print("="*70)

    # Ajan oluştur
    agent = BasicChainAgent()

    # Basit sorular sor
    agent.ask("Fransa'nın başkenti neresidir?")
    agent.ask("15 * 7 kaçtır?")
    agent.ask("Üç ana renk nelerdir?")


def demo_detailed_usage():
    """İç yapıyı görmek için ayrıntılı kullanımı göster."""
    print("\n" + "="*70)
    print("DEMO 2: Ayrıntılı Kullanım (Ne Olduğunu Gör)")
    print("="*70)

    agent = BasicChainAgent()

    # Ayrıntılarla sor
    result = agent.ask_with_details("Bir sinir ağının ne olduğunu bir cümlede açıkla.")

    print("\n[SONUÇ SÖZLÜĞÜ]:")
    print(f"  Soru: {result['question']}")
    print(f"  Model: {result['model']}")
    print(f"  Cevap uzunluğu: {len(result['answer'])} karakter")


def demo_different_temperatures():
    """Sıcaklığın yanıtları nasıl etkilediğini göster."""
    print("\n" + "="*70)
    print("DEMO 3: Sıcaklık Karşılaştırması")
    print("="*70)

    question = "Bir bilim kurgu hikayesi için yaratıcı bir açılış cümlesi yaz."

    print(f"\nSoru: {question}\n")

    # Düşük sıcaklık (deterministik)
    print("[Sıcaklık = 0.0 - Deterministik]")
    agent_low = BasicChainAgent(temperature=0.0)
    response_low = agent_low.ask(question)

    # Yüksek sıcaklık (yaratıcı)
    print("\n[Sıcaklık = 1.0 - Yaratıcı]")
    agent_high = BasicChainAgent(temperature=1.0)
    response_high = agent_high.ask(question)

    print("\n💡 Sıcaklığın yaratıcılığı nasıl etkilediğine dikkat edin!")


def main():
    """Ana giriş noktası."""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║         Örnek 01: Temel LangChain - İlk Zinciriniz               ║
║                                                                   ║
║  Bu şunları gösterir:                                            ║
║  • Bir LLM örneği oluşturma (OllamaLLM)                         ║
║  • Bir prompt şablonu oluşturma (PromptTemplate)                 ║
║  • Bunları birbirine zincirleme (LLMChain)                      ║
║  • Zinciri çalıştırma (chain.run)                               ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Demoları çalıştır
    demo_basic_usage()
    demo_detailed_usage()
    demo_different_temperatures()

    # Özet
    print("\n" + "="*70)
    print("✅ TAMAMLANDI!")
    print("="*70)
    print("\n🎓 Ne öğrendiniz:")
    print("  1. Bir OllamaLLM örneği nasıl oluşturulur")
    print("  2. Bir PromptTemplate nasıl oluşturulur")
    print("  3. LLMChain ile nasıl zincirlenir")
    print("  4. Zincir nasıl çalıştırılır")
    print("  5. Sıcaklık yanıtları nasıl etkiler")
    print("\n📖 Temel Kavramlar:")
    print("  • LLM = Dil modeli")
    print("  • Prompt = LLM'e gönderdiğiniz şey")
    print("  • Zincir = LLM + Prompt'un yeniden kullanılabilir kombinasyonu")
    print("  • Sıcaklık = Yaratıcılık seviyesi (0.0-1.0)")
    print("\n➡️  Sıradaki: python 02_prompt_templates.py")
    print("="*70)


if __name__ == "__main__":
    # Hızlı kontrol
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("[UYARI] Ollama doğru çalışmıyor olabilir")
    except:
        print("[HATA] Ollama'ya bağlanılamıyor!")
        print("  Çözüm: ollama serve")
        exit(1)

    main()
