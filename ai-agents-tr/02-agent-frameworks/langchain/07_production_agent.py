#!/usr/bin/env python3
"""
Örnek 07: Üretim Ajanı - Tam Sistem
===============================================

TÜM kavramları birleştiren TAM, üretime hazır bir ajan!

Bu ajan şunları içerir:
✅ Araçlar (hava durumu, hesap makinesi, arama)
✅ Hafıza (konuşma geçmişi)
✅ Yönlendirme (akıllı istek işleme)
✅ Sıralı işleme (çok adımlı iş akışları)
✅ Hata yönetimi
✅ Günlükleme
✅ Yapılandırma yönetimi
✅ OOP tasarım desenleri

GERÇEK üretim ajanlarını bu şekilde oluşturursunuz!

Yazar: Beyhan MEYRALI
"""

import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

class SimpleMemory:
    """Basit konuşma hafıza tamponu."""
    def __init__(self, k=5):
        self.k = k
        self.messages = []

    def save_context(self, inputs, outputs):
        input_str = list(inputs.values())[0]
        output_str = list(outputs.values())[0]
        self.messages.append({"role": "user", "content": input_str})
        self.messages.append({"role": "assistant", "content": output_str})
        
        # Son k turu tutmak için kırp (2*k mesaj)
        if len(self.messages) > self.k * 2:
            self.messages = self.messages[-(self.k * 2):]

    def load_memory_variables(self, inputs):
        # Prompt için dize olarak biçimlendir
        history_str = ""
        for msg in self.messages:
            role = "Kullanıcı" if msg["role"] == "user" else "Asistan"
            history_str += f"{role}: {msg['content']}\n"
        return {"history": history_str}

    def clear(self):
        self.messages = []


# =============================================================================
# BÖLÜM 1: Araç Tanımları
# =============================================================================

class AgentTools:
    """Ajanın kullanabileceği araçlar koleksiyonu."""

    @staticmethod
    def get_weather(city: str) -> dict:
        """Bir şehir için hava durumunu al."""
        weather_db = {
            "tokyo": {"temp": 25, "condition": "güneşli"},
            "paris": {"temp": 18, "condition": "bulutlu"},
            "london": {"temp": 15, "condition": "yağmurlu"},
            "new york": {"temp": 22, "condition": "açık"},
        }
        city_lower = city.lower()
        if city_lower in weather_db:
            return weather_db[city_lower]
        return {"error": f"{city} için veri yok"}

    @staticmethod
    def calculate(expression: str) -> dict:
        """Bir matematik ifadesini hesapla."""
        try:
            result = eval(expression)  # UYARI: Sadece demo için!
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def search_web(query: str) -> dict:
        """Web aramasını simüle et."""
        db = {
            "python": "Python yüksek seviyeli bir programlama dilidir.",
            "ai": "Yapay zeka, akıllı bilgisayar sistemlerini ifade eder.",
        }
        for key, val in db.items():
            if key in query.lower():
                return {"result": val}
        return {"error": "Sonuç yok"}

    @staticmethod
    def get_tool_schemas() -> List[dict]:
        """Ollama için araç şemalarını al."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Bir şehir için hava durumunu al",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {"type": "string"}
                        },
                        "required": ["city"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate",
                    "description": "Bir matematik ifadesini hesapla",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "expression": {"type": "string"}
                        },
                        "required": ["expression"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_web",
                    "description": "Web'de ara",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"}
                        },
                        "required": ["query"]
                    }
                }
            }
        ]


# =============================================================================
# BÖLÜM 2: Üretim Ajanı
# =============================================================================

class ProductionAgent:
    """
    Tüm özelliklere sahip üretime hazır ajan.

    Özellikler:
    - Araç çağırma
    - Konuşma hafızası
    - Hata yönetimi
    - Günlükleme
    - Yapılandırma
    """

    def __init__(
        self,
        model: str = "qwen3:8b",
        memory_size: int = 5,
        max_iterations: int = 5,
        verbose: bool = True
    ):
        """
        Üretim ajanını başlat.

        Argümanlar:
            model: Ollama model adı
            memory_size: Hatırlanacak konuşma turu sayısı
            max_iterations: Maksimum araç çağırma iterasyonu
            verbose: Ayrıntılı günlüklemeyi etkinleştir
        """
        print(f"\n[BAŞLAT] ProductionAgent oluşturuluyor...")
        print(f"  Model: {model}")
        print(f"  Hafıza: {memory_size} tur")
        print(f"  Maks iterasyon: {max_iterations}")

        self.model = model
        self.max_iterations = max_iterations
        self.verbose = verbose

        # Bileşenleri başlat
        self.tools = AgentTools()
        self.memory = SimpleMemory(k=memory_size)
        self.llm = OllamaLLM(model=model, temperature=0.7)

        # İstatistikler
        self.stats = {
            "total_requests": 0,
            "tools_called": 0,
            "errors": 0
        }

        print("[BAŞLAT] ✅ Üretim ajanı hazır!")

    def _log(self, message: str, level: str = "BİLGİ"):
        """Ayrıntılıysa mesajı günlükle."""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] [{level}] {message}")

    def _call_ollama(self, messages: List[dict], tools: List[dict] = None) -> dict:
        """Ollama API'sini çağır."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }
        if tools:
            payload["tools"] = tools

        response = requests.post(
            "http://localhost:11434/api/chat",
            json=payload,
            timeout=60
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API hatası: {response.status_code}")

    def _execute_tool(self, tool_call: dict) -> str:
        """Bir aracı çalıştır ve sonucu döndür."""
        func_name = tool_call["function"]["name"]
        args_raw = tool_call["function"]["arguments"]

        # Argümanları ayrıştır
        if isinstance(args_raw, str):
            args = json.loads(args_raw)
        else:
            args = args_raw

        self._log(f"Araç çalıştırılıyor: {func_name}({args})")

        # Çalıştır
        if func_name == "get_weather":
            result = self.tools.get_weather(**args)
        elif func_name == "calculate":
            result = self.tools.calculate(**args)
        elif func_name == "search_web":
            result = self.tools.search_web(**args)
        else:
            result = {"error": f"Bilinmeyen araç: {func_name}"}

        self.stats["tools_called"] += 1
        return json.dumps(result)

    def chat(self, user_input: str) -> str:
        """
        Ana sohbet metodu.

        Argümanlar:
            user_input: Kullanıcının mesajı

        Döndürür:
            Ajanın yanıtı
        """
        self._log(f"Kullanıcı: {user_input}")
        self.stats["total_requests"] += 1

        # Konuşma geçmişini al
        history = self.memory.load_memory_variables({})
        messages = []

        # Varsa geçmişi ekle
        if history.get("history"):
            # Basit geçmiş ayrıştırma (üretimde uygun format kullanın)
            messages.append({
                "role": "system",
                "content": f"Önceki konuşma:\n{history['history']}"
            })

        # Mevcut mesajı ekle
        messages.append({"role": "user", "content": user_input})

        # Araçlarla ajan döngüsü
        for iteration in range(self.max_iterations):
            self._log(f"İterasyon {iteration + 1}/{self.max_iterations}")

            try:
                # LLM'i çağır
                response = self._call_ollama(
                    messages,
                    self.tools.get_tool_schemas()
                )

                llm_message = response.get("message", {})
                messages.append(llm_message)

                # Araç çağrılarını kontrol et
                tool_calls = llm_message.get("tool_calls")

                if tool_calls:
                    self._log(f"LLM {len(tool_calls)} araç istedi")

                    # Araçları çalıştır
                    for tool_call in tool_calls:
                        result = self._execute_tool(tool_call)
                        messages.append({
                            "role": "tool",
                            "content": result
                        })

                    # Döngüye devam et
                    continue
                else:
                    # Araç yok - final cevap
                    final_answer = llm_message.get("content", "Yanıt yok")
                    self._log(f"Ajan: {final_answer[:50]}...")

                    # Hafızaya kaydet
                    self.memory.save_context(
                        {"input": user_input},
                        {"output": final_answer}
                    )

                    return final_answer

            except Exception as e:
                self._log(f"Hata: {str(e)}", "HATA")
                self.stats["errors"] += 1
                return f"Hata: {str(e)}"

        # Maksimum iterasyona ulaşıldı
        return "Hata: Final cevap olmadan maksimum iterasyona ulaşıldı"

    def get_stats(self) -> Dict[str, Any]:
        """Ajan istatistiklerini al."""
        return self.stats.copy()

    def reset_memory(self):
        """Konuşma hafızasını temizle."""
        self.memory.clear()
        self._log("Hafıza temizlendi")


# =============================================================================
# DEMOLAR
# =============================================================================

def demo_basic_usage():
    """Demo: Temel konuşma."""
    print("\n" + "="*70)
    print("DEMO 1: Hafızalı Temel Konuşma")
    print("="*70)

    agent = ProductionAgent()

    # Çok turlu konuşma
    agent.chat("Merhaba! Adım Alice.")
    agent.chat("Adım ne?")
    agent.chat("Tokyo'da hava nasıl?")


def demo_tool_usage():
    """Demo: Araç çağırma."""
    print("\n" + "="*70)
    print("DEMO 2: Araç Kullanımı")
    print("="*70)

    agent = ProductionAgent()

    questions = [
        "15 * 23'ü hesapla",
        "Python hakkında bilgi ara",
        "Paris'te hava nasıl?"
    ]

    for q in questions:
        print(f"\n[S]: {q}")
        answer = agent.chat(q)
        print(f"[C]: {answer[:100]}...")


def demo_complex_query():
    """Demo: Karmaşık çoklu araç sorgusu."""
    print("\n" + "="*70)
    print("DEMO 3: Karmaşık Çoklu Araç Sorgusu")
    print("="*70)

    agent = ProductionAgent()

    question = "Londra'da hava nasıl? Ayrıca bu sıcaklığın Fahrenheit cinsinden ne olduğunu hesapla (F = C * 9/5 + 32)"
    print(f"\n[S]: {question}")
    answer = agent.chat(question)
    print(f"\n[C]: {answer}")

    # İstatistikleri göster
    print(f"\n[İSTATİSTİKLER]: {agent.get_stats()}")


def main():
    """Ana giriş noktası."""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║         Örnek 07: Üretim Ajanı - Tam Sistem                       ║
║                                                                   ║
║  Bu şunları gösterir:                                            ║
║  ✅ Araç çağırma (hava durumu, hesap makinesi, arama)           ║
║  ✅ Konuşma hafızası (bağlamı hatırlar)                         ║
║  ✅ Hata yönetimi (zarif hatalar)                               ║
║  ✅ Günlükleme (ayrıntılı yürütme takibi)                       ║
║  ✅ İstatistikler (performans metrikleri)                       ║
║  ✅ OOP tasarımı (temiz, bakımı kolay kod)                      ║
║  ✅ Üretim desenleri (yapılandırma vb.)                         ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Demoları çalıştır
    demo_basic_usage()
    demo_tool_usage()
    demo_complex_query()

    # Özet
    print("\n" + "="*70)
    print("✅ TAMAMLANDI! LangChain Bölümü Bitti!")
    print("="*70)
    print("\n🎓 Bu bölümde ne öğrendiniz (00-07):")
    print("  00 - Kurulum ve ayar doğrulama")
    print("  01 - Temel zincirler ve sıcaklık")
    print("  02 - Gelişmiş prompt şablonları")
    print("  03 - Konuşma hafızası")
    print("  04 - Araç entegrasyonu")
    print("  05 - Sıralı iş akışları")
    print("  06 - Yönlendirme ve dallanma")
    print("  07 - Üretime hazır ajan (bu betik)")
    print("\n🎉 Artık LangChain'i biliyorsunuz!")
    print("\n📖 Temel Üretim Desenleri:")
    print("  • Yetenekler için araç çağırma")
    print("  • Bağlam için hafıza")
    print("  • Güvenilirlik için hata yönetimi")
    print("  • Hata ayıklama için günlükleme")
    print("  • İzleme için istatistikler")
    print("  • Bakım için OOP")
    print("\n➡️  Sıradaki: Daha da güçlü iş akışları için LangGraph'ı keşfedin!")
    print("     Veya çoklu ajan sistemleri için CrewAI'a geçin!")
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
