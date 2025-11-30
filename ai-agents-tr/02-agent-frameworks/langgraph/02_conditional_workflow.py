#!/usr/bin/env python3
"""
Örnek 2: Koşullu İş Akışı - LangGraph'ta If/Else Mantığı
==============================================================

Bu, KOŞULLU yönlendirmeyi gösterir - verilere dayalı olarak
iş akışınızda nasıl karar verileceğini.

Ne öğreneceksiniz:
- Koşullu kenarlar (grafiklerde if/else)
- Yönlendirici fonksiyonlar (karar mantığı)
- Bir iş akışından geçen birden fazla yol
- Farklı soruların farklı işleme ihtiyacı olduğunda

HATA AYIKLAMA İPUÇLARI:
--------------
1. Hangi yolun alındığını izleyin:
   - Yönlendirici fonksiyona print() ekleyin
   - Hangi düğümün çağrıldığını görün

2. Yönlendirme yanlış görünüyorsa:
   - Yönlendirici fonksiyon mantığınızı kontrol edin
   - Aldığı durumu yazdırın
   - Dönüş değerlerinin düğüm adlarıyla eşleştiğini doğrulayın

Yazar: Beyhan MEYRALI
"""

from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
import requests
import json

# =============================================================================
# ADIM 1: Durumu Tanımla
# =============================================================================

class State(TypedDict):
    """
    Koşullu iş akışı için durum.

    Soruları içeriğe göre farklı düğümlere yönlendireceğiz.
    """
    question: str          # Kullanıcının sorusu
    answer: str            # Final cevap
    route_taken: str       # Hangi yol alındı (hata ayıklama için)


# =============================================================================
# ADIM 2: Uzmanlaşmış Düğümleri Tanımla
# =============================================================================

def weather_node(state: State) -> dict:
    """
    Bir araç kullanarak hava durumu sorularını işleyen düğüm.

    Bu, bir hava durumu API'sini çağırmayı simüle eder.
    """

    print(f"\n[HAVA DURUMU DÜĞÜMÜ] Hava durumu sorusu işleniyor...")

    # Sorudan şehri çıkar (basit yaklaşım)
    question = state["question"].lower()

    # Sahte hava durumu verisi
    weather_db = {
        "tokyo": "25°C, güneşli",
        "paris": "18°C, bulutlu",
        "london": "15°C, yağmurlu",
        "new york": "20°C, açık",
    }

    # Soruda şehir bulmaya çalış
    city_found = None
    for city in weather_db.keys():
        if city in question:
            city_found = city
            break

    if city_found:
        weather = weather_db[city_found]
        answer = f"{city_found.title()}'da hava durumu {weather}."
    else:
        answer = "Şunlar için hava durumu sağlayabilirim: Tokyo, Paris, Londra veya New York."

    print(f"[HAVA DURUMU DÜĞÜMÜ] Cevap: {answer}")

    return {
        "answer": answer,
        "route_taken": "hava_durumu"
    }


def math_node(state: State) -> dict:
    """
    LLM kullanarak matematik sorularını işleyen düğüm.

    Matematik için LLM'e özel talimatlar veriyoruz.
    """

    print(f"\n[MATEMATİK DÜĞÜMÜ] Matematik sorusu işleniyor...")

    # Matematiğe özel sistem promptu ekle
    messages = [
        {
            "role": "system",
            "content": "Bir matematik uzmanısın. Net, adım adım çözümler sun."
        },
        {
            "role": "user",
            "content": state["question"]
        }
    ]

    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "qwen3:8b",
                "messages": messages,
                "stream": False
            },
            timeout=60
        )

        if response.status_code == 200:
            answer = response.json()["message"]["content"]
            print(f"[MATEMATİK DÜĞÜMÜ] Cevap alındı (kısaltılmış): {answer[:80]}...")
        else:
            answer = f"Matematik API hatası: {response.status_code}"

    except Exception as e:
        answer = f"Matematik hatası: {str(e)}"

    return {
        "answer": answer,
        "route_taken": "matematik"
    }


def general_node(state: State) -> dict:
    """
    LLM kullanarak genel soruları işleyen düğüm.

    Bu, hava durumu veya matematikle eşleşmeyen herhangi bir
    soru için varsayılan yoldur.
    """

    print(f"\n[GENEL DÜĞÜM] Genel soru işleniyor...")

    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "qwen3:8b",
                "messages": [{"role": "user", "content": state["question"]}],
                "stream": False
            },
            timeout=60
        )

        if response.status_code == 200:
            answer = response.json()["message"]["content"]
            print(f"[GENEL DÜĞÜM] Cevap alındı (kısaltılmış): {answer[:80]}...")
        else:
            answer = f"API hatası: {response.status_code}"

    except Exception as e:
        answer = f"Hata: {str(e)}"

    return {
        "answer": answer,
        "route_taken": "genel"
    }


# =============================================================================
# ADIM 3: Yönlendirici Fonksiyonu Tanımla (ANA KISIM!)
# =============================================================================

def route_question(state: State) -> Literal["weather", "math", "general"]:
    """
    Hangi düğümün çağrılacağına karar veren yönlendirici fonksiyon.

    Bu, grafiğinizin "if/else" mantığıdır!

    Argümanlar:
        state: Soruyu içeren mevcut durum

    Döndürür:
        Sonraki çağrılacak düğümün adı

    Nasıl çalışır:
    - Soruya bak
    - Hangi uzmanlaşmış düğümün işlemesi gerektiğine karar ver
    - Düğüm adını döndür

    Grafik daha sonra o düğümü çağıracak!
    """

    question = state["question"].lower()

    print(f"\n[YÖNLENDİRİCİ] Soru analiz ediliyor: {state['question']}")

    # Hava durumu anahtar kelimelerini kontrol et
    if any(word in question for word in ["hava", "sıcaklık", "tahmin", "iklim", "weather", "temperature", "forecast", "climate"]):
        print("[YÖNLENDİRİCİ] HAVA DURUMU sorusu tespit edildi → weather_node'a yönlendiriliyor")
        return "weather"

    # Matematik anahtar kelimelerini kontrol et
    elif any(word in question for word in ["hesapla", "çarp", "böl", "artı", "eksi", "calculate", "multiply", "divide", "plus", "minus", "*", "+", "-", "/", "="]):
        print("[YÖNLENDİRİCİ] MATEMATİK sorusu tespit edildi → math_node'a yönlendiriliyor")
        return "math"

    # Varsayılan olarak genel
    else:
        print("[YÖNLENDİRİCİ] Genel soru → general_node'a yönlendiriliyor")
        return "general"


# =============================================================================
# ADIM 4: Koşullu Mantıkla Grafik Oluştur
# =============================================================================

def create_graph():
    """
    Koşullu yönlendirmeli bir grafik oluştur.

    İş akışı şöyle görünür:

           BAŞLA
             ↓
          YÖNLENDİRİCİ
           / | \
          /  |  \
    hava_durumu matematik genel
          \  |  /
           \ | /
            BİTİR

    Yönlendirici fonksiyon hangi yolun alınacağına karar verir!
    """

    print("\n[GRAFİK] Koşullu iş akışı oluşturuluyor...")

    # Grafik oluştur
    workflow = StateGraph(State)

    # Tüm düğümlerimizi ekle
    workflow.add_node("weather", weather_node)
    workflow.add_node("math", math_node)
    workflow.add_node("general", general_node)

    # Sadece geçiş yapan sahte bir yönlendirici düğüm ekle
    def router_node(state: State) -> dict:
        # En az bir durum güncellemesi döndürmeli
        return {"route_taken": "yönlendiriliyor..."}

    workflow.add_node("router", router_node)

    # Giriş noktasını ayarla (yönlendirici düğümle başla)
    workflow.set_entry_point("router")

    # Yönlendiriciyi koşullu kenar olarak ekle
    # Bu, basit grafiklerden TEMEL farktır!
    workflow.add_conditional_edges(
        "router",  # Yönlendirici düğümden başla
        route_question,  # Hangi düğümü belirleyen fonksiyon
        {
            # Dönüş değerlerini gerçek düğümlere eşle
            "weather": "weather",
            "math": "math",
            "general": "general",
        }
    )

    # Tüm yollar BİTİR'e gider
    workflow.add_edge("weather", END)
    workflow.add_edge("math", END)
    workflow.add_edge("general", END)

    # Derle
    app = workflow.compile()

    print("[GRAFİK] Koşullu iş akışı oluşturuldu!")
    print("[GRAFİK] Rotalar: yönlendirici → [hava_durumu | matematik | genel] → BİTİR")

    return app


# =============================================================================
# ADIM 5: Örnekleri Çalıştır
# =============================================================================

def run_question(question: str):
    """Bir soruyu koşullu iş akışından geçir."""

    print("\n" + "="*70)
    print(f"SORU: {question}")
    print("="*70)

    # Grafik oluştur
    app = create_graph()

    # Çalıştır
    result = app.invoke({
        "question": question,
        "answer": "",
        "route_taken": ""
    })

    # Sonuçları göster
    print("\n" + "="*70)
    print(f"ALINAN ROTA: {result['route_taken'].upper()}")
    print("="*70)
    print("CEVAP:")
    print(result["answer"])
    print("="*70)

    return result


# =============================================================================
# ANA
# =============================================================================

def main():
    """Çeşitli test durumlarıyla ana giriş noktası."""

    print("""
╔═══════════════════════════════════════════════════════════════════╗
║      Örnek 2: Koşullu İş Akışı (If/Else Mantığı)                  ║
║                                                                   ║
║  Bu şunları gösterir:                                            ║
║  • Koşullu kenarlar (dallanma)                                   ║
║  • Yönlendirici fonksiyonlar (karar mantığı)                     ║
║  • Birden fazla uzmanlaşmış düğüm                                ║
║  • Dinamik iş akışı yolları                                      ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Test 1: Hava durumu sorusu
    print("\n[TEST 1] Hava Durumu Sorusu")
    run_question("Tokyo'da hava nasıl?")

    # Test 2: Matematik sorusu
    print("\n\n[TEST 2] Matematik Sorusu")
    run_question("25 * 4'ü hesapla")

    # Test 3: Genel soru
    print("\n\n[TEST 3] Genel Soru")
    run_question("Ay'a ilk ayak basan kişi kimdi?")

    # Test 4: Başka bir hava durumu
    print("\n\n[TEST 4] Başka Bir Hava Durumu Sorusu")
    run_question("Paris'te bugün iklim nasıl?")

    # Test 5: Karmaşık matematik
    print("\n\n[TEST 5] Karmaşık Matematik")
    run_question("10 elmam varsa ve 3 tanesini verirsem, sonra 5 tane daha alırsam, kaç tane olurum?")

    print("\n" + "="*70)
    print("✅ TÜM TESTLER TAMAMLANDI!")
    print("="*70)
    print("\nGösterilen Temel Kavramlar:")
    print("  • Soru içeriğine dayalı koşullu yönlendirme")
    print("  • Farklı görevler için farklı uzmanlaşmış düğümler")
    print("  • Karar verici olarak yönlendirici fonksiyon")
    print("  • Dinamik iş akışı yolları")
    print("\nSonraki Adımlar:")
    print("  → Yönlendirici mantığını değiştirmeyi deneyin")
    print("  → Yeni uzmanlaşmış düğümler ekleyin (örn. tarih, bilim)")
    print("  → Bunu bölüm 01'den araç çağırmayla birleştirin")
    print("="*70)


if __name__ == "__main__":
    # Ollama'yı kontrol et
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("[UYARI] Ollama beklenmeyen durum döndürdü")
    except requests.exceptions.RequestException:
        print("[HATA] Ollama'ya bağlanılamıyor!")
        print("  Ollama'nın çalıştığından emin olun: ollama serve")
        exit(1)

    main()
