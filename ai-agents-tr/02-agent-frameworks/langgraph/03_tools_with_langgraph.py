#!/usr/bin/env python3
"""
Örnek 3: Araçlar + LangGraph - Ajan Orkestrasyonu
===================================================

Bu, profesyonel ajan orkestrasyonu için bölüm 01'i (Araç Çağırma)
LangGraph ile birleştirir.

Ne öğreneceksiniz:
- LangGraph düğümleri içinde araçları kullanma
- Yapılandırılmış bir iş akışında özyinelemeli araç çağırma
- Ajan orkestrasyonu (birden fazla araç, birden fazla adım)
- Hata yönetimi ve yeniden deneme mantığı
- Üretime hazır ajanlar oluşturma

Bu "İLERİ" seviyedir - her şeyi birleştiriyor!

HATA AYIKLAMA İPUÇLARI:
--------------
1. Araç yürütmesini izleyin:
   - Hangi araçların çağrıldığını görün
   - Araç sonuçlarını kontrol edin
   - LLM'in sonuçları doğru kullandığını doğrulayın

2. Araçlar çağrılmazsa:
   - Araç şemasını kontrol edin
   - LLM'in araç çağırmayı desteklediğini doğrulayın
   - LLM yanıtını yazdırın

Yazar: Beyhan MEYRALI
"""

from typing import TypedDict, Annotated, List, Dict
from langgraph.graph import StateGraph, END
import requests
import json
import operator

# =============================================================================
# ADIM 1: Araçları Tanımla (Bölüm 01'den)
# =============================================================================

def get_weather(city: str) -> str:
    """
    Bir şehir için hava durumunu al.

    Bu, ajanın çağırabileceği bir ARAÇTIR.
    """
    weather_db = {
        "tokyo": {"temp": 25, "condition": "güneşli"},
        "paris": {"temp": 18, "condition": "bulutlu"},
        "london": {"temp": 15, "condition": "yağmurlu"},
        "new york": {"temp": 20, "condition": "açık"},
    }

    city_lower = city.lower()
    if city_lower in weather_db:
        data = weather_db[city_lower]
        return json.dumps({
            "city": city,
            "temperature_celsius": data["temp"],
            "condition": data["condition"]
        })
    else:
        return json.dumps({"error": f"{city} için hava durumu verisi yok"})


def search_web(query: str) -> str:
    """
    Web aramasını simüle et.

    Bu, ajanın çağırabileceği bir ARAÇTIR.
    """
    # Sahte arama sonuçları
    search_db = {
        "python": "Python, Guido van Rossum tarafından oluşturulan yüksek seviyeli bir programlama dilidir...",
        "ai": "Yapay Zeka (AI), tipik olarak insan zekası gerektiren görevleri yerine getirebilen bilgisayar sistemlerini ifade eder...",
        "langgraph": "LangGraph, LLM'lerle durum bilgili çoklu aktör uygulamaları oluşturmak için bir kütüphanedir...",
    }

    query_lower = query.lower()
    for key in search_db:
        if key in query_lower:
            return json.dumps({
                "query": query,
                "result": search_db[key]
            })

    return json.dumps({
        "query": query,
        "result": "Sonuç bulunamadı. 'python', 'ai' veya 'langgraph' aramayı deneyin."
    })


# LLM için araç şemalarını tanımla
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Bir şehir için güncel hava durumunu al. Celsius cinsinden sıcaklık ve hava durumunu döndürür.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Şehir adı (örn. 'Tokyo', 'Paris')"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Bir konu hakkında bilgi için web'de arama yap.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Arama sorgusu"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# Fonksiyon adlarını gerçek fonksiyonlara eşle
AVAILABLE_TOOLS = {
    "get_weather": get_weather,
    "search_web": search_web,
}


# =============================================================================
# ADIM 2: Durumu Tanımla
# =============================================================================

class AgentState(TypedDict):
    """
    Araç çağıran ajan için durum.

    Bu, konuşmayı ve araç kullanımını izler.
    """
    messages: Annotated[List[Dict], operator.add]  # Konuşma geçmişi
    question: str              # Orijinal soru
    final_answer: str          # Final cevap
    tools_used: List[str]      # Hangi araçların çağrıldığını izle
    iteration: int             # İterasyonları izle (sonsuz döngüleri önle)


# =============================================================================
# ADIM 3: Düğümleri Tanımla
# =============================================================================

def agent_node(state: AgentState) -> dict:
    """
    Araçları çağırabilen ajan düğümü.

    Bu, şunları yapan ANA düğümdür:
    1. Mevcut araçlarla LLM'i çağırır
    2. LLM'in kullanmak istediği araçları yürütür
    3. LLM final cevaba sahip olana kadar devam eder
    """

    print(f"\n[AJAN] İterasyon {state['iteration']}")

    messages = state.get("messages", [])

    # Henüz mesaj yoksa başlangıç sorusunu ekle
    if not messages:
        messages = [{"role": "user", "content": state["question"]}]

    try:
        # Araçlarla LLM'i çağır
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "qwen3:8b",
                "messages": messages,
                "tools": TOOLS,
                "stream": False
            },
            timeout=60
        )

        if response.status_code != 200:
            return {
                "final_answer": f"API Hatası: {response.status_code}",
                "iteration": state["iteration"] + 1
            }

        response_data = response.json()
        llm_message = response_data.get("message", {})

        # LLM araç çağırmak istiyor mu kontrol et
        tool_calls = llm_message.get("tool_calls", [])

        if tool_calls:
            print(f"[AJAN] LLM {len(tool_calls)} araç çağırmak istiyor")

            # Her aracı yürüt
            new_messages = [llm_message]  # Araç çağrılarıyla LLM'in mesajını ekle

            for tool_call in tool_calls:
                function_name = tool_call["function"]["name"]
                arguments_raw = tool_call["function"]["arguments"]

                # Dize ise argümanları ayrıştır
                if isinstance(arguments_raw, str):
                    arguments = json.loads(arguments_raw)
                else:
                    arguments = arguments_raw

                print(f"[ARAÇ] {function_name}({arguments}) çağrılıyor")

                # Aracı yürüt
                if function_name in AVAILABLE_TOOLS:
                    result = AVAILABLE_TOOLS[function_name](**arguments)
                    print(f"[ARAÇ] Sonuç: {result}")

                    # Araç sonucunu mesajlara ekle
                    new_messages.append({
                        "role": "tool",
                        "content": result
                    })

                    # Araç kullanımını izle
                    tools_used = state.get("tools_used", [])
                    tools_used.append(function_name)
                else:
                    new_messages.append({
                        "role": "tool",
                        "content": json.dumps({"error": f"Bilinmeyen araç: {function_name}"})
                    })

            return {
                "messages": new_messages,
                "tools_used": tools_used if 'tools_used' in locals() else state.get("tools_used", []),
                "iteration": state["iteration"] + 1
            }

        else:
            # Araç çağrısı yok - LLM final cevaba sahip
            final_answer = llm_message.get("content", "Yanıt yok")
            print(f"[AJAN] Final cevap: {final_answer[:80]}...")

            return {
                "messages": [llm_message],
                "final_answer": final_answer,
                "iteration": state["iteration"] + 1
            }

    except Exception as e:
        error_msg = f"Hata: {str(e)}"
        print(f"[HATA] {error_msg}")
        return {
            "final_answer": error_msg,
            "iteration": state["iteration"] + 1
        }


def should_continue(state: AgentState) -> str:
    """
    Yönlendirici fonksiyon: Devam etmeli miyiz yoksa bitmeli mi?

    Bu, şunlarla sonsuz döngüleri önler:
    1. Final cevabımız varsa bitir
    2. Maksimum iterasyona ulaşırsak bitir
    """

    # Final cevabı kontrol et
    if state.get("final_answer"):
        print("[YÖNLENDİRİCİ] Final cevap var → BİTİR")
        return "end"

    # İterasyon limitini kontrol et
    if state["iteration"] >= 10:
        print("[YÖNLENDİRİCİ] Maksimum iterasyona ulaşıldı → BİTİR")
        return "end"

    # Döngüye devam et
    print("[YÖNLENDİRİCİ] Daha fazla işleme gerek → DEVAM")
    return "continue"


# =============================================================================
# ADIM 4: Grafik Oluştur
# =============================================================================

def create_agent_graph():
    """
    Araç çağıran ajan grafiğini oluştur.

    Akış:
    BAŞLA → ajan → [ajana geri devam ET VEYA bitir] → BİTİR
             ↑_________|

    Araçların çağrılması gerekiyorsa ajan düğümü birden fazla kez döngü yapabilir!
    """

    print("\n[GRAFİK] Araç çağıran ajan oluşturuluyor...")

    workflow = StateGraph(AgentState)

    # Ajan düğümünü ekle
    workflow.add_node("agent", agent_node)

    # Giriş noktasını ayarla
    workflow.set_entry_point("agent")

    # Koşullu kenar ekle: döngü mü yoksa bitir mi?
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "agent",  # Geri döngü!
            "end": END
        }
    )

    app = workflow.compile()

    print("[GRAFİK] Ajan grafiği oluşturuldu!")
    print("[GRAFİK] Akış: ajan → [döngü VEYA bitir]")

    return app


# =============================================================================
# ADIM 5: Örnekleri Çalıştır
# =============================================================================

def run_agent(question: str):
    """Ajanı bir soruyla çalıştır."""

    print("\n" + "="*70)
    print(f"SORU: {question}")
    print("="*70)

    app = create_agent_graph()

    result = app.invoke({
        "question": question,
        "messages": [],
        "final_answer": "",
        "tools_used": [],
        "iteration": 0
    })

    print("\n" + "="*70)
    print("FİNAL CEVAP:")
    print("="*70)
    print(result.get("final_answer", "Cevap yok"))
    print("\n" + "-"*70)
    print(f"Kullanılan araçlar: {', '.join(result.get('tools_used', [])) or 'Yok'}")
    print(f"İterasyonlar: {result['iteration']}")
    print("="*70)

    return result


# =============================================================================
# ANA
# =============================================================================

def main():
    """Test durumlarıyla ana giriş noktası."""

    print("""
╔═══════════════════════════════════════════════════════════════════╗
║       Örnek 3: Araçlar + LangGraph (Ajan Orkestrasyonu)           ║
║                                                                   ║
║  Bu şunları gösterir:                                            ║
║  • LangGraph içinde araç çağırma                                 ║
║  • Özyinelemeli araç yürütme                                     ║
║  • Ajan orkestrasyonu                                            ║
║  • Profesyonel ajan desenleri                                    ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Test 1: Tek araç çağrısı
    print("\n[TEST 1] Tek Araç Çağrısı")
    run_agent("Tokyo'da hava nasıl?")

    # Test 2: Birden fazla araç çağrısı
    print("\n\n[TEST 2] Birden Fazla Araç Çağrısı")
    run_agent("Paris ve Londra'da hava nasıl?")

    # Test 3: Web araması
    print("\n\n[TEST 3] Web Arama Aracı")
    run_agent("Python programlama hakkında bilgi ara")

    # Test 4: Araç gerekmez
    print("\n\n[TEST 4] Araç Gerekmez")
    run_agent("2+2 kaçtır?")

    # Test 5: Karmaşık çoklu araç sorgusu
    print("\n\n[TEST 5] Karmaşık Çoklu Araç Sorgusu")
    run_agent("LangGraph'ı ara ve New York'ta hava durumunu söyle")

    print("\n" + "="*70)
    print("✅ TÜM TESTLER TAMAMLANDI!")
    print("="*70)
    print("\nTemel Kavramlar:")
    print("  ✅ Araçlar LangGraph iş akışına entegre edildi")
    print("  ✅ Döngü tespiti ile özyinelemeli araç çağırma")
    print("  ✅ Ajan orkestrasyon deseni")
    print("  ✅ Profesyonel hata yönetimi")
    print("\nBu, üretime hazır ajan mimarisidir!")
    print("="*70)


if __name__ == "__main__":
    # Ollama'yı kontrol et
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("[UYARI] Ollama beklenmeyen durum döndürdü")
    except requests.exceptions.RequestException:
        print("[HATA] Ollama'ya bağlanılamıyor!")
        exit(1)

    main()
