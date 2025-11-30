#!/usr/bin/env python3
"""
Örnek 1: Basit LangGraph Ajanı
==================================

Bu, mümkün olan EN BASİT LangGraph ajanıdır.
Düğümler ve kenarlarla bir iş akışının nasıl oluşturulacağını gösterir.

Ne öğreneceksiniz:
- Durum nasıl tanımlanır
- Düğümler (fonksiyonlar) nasıl oluşturulur
- Bir grafik nasıl oluşturulur
- Grafik nasıl çalıştırılır

HATA AYIKLAMA İPUÇLARI:
--------------
1. "Modül bulunamadı: langgraph" hatası alırsanız:
   pip install -r requirements.txt

2. Ollama başarısız olursa:
   - Ollama'nın çalıştığından emin olun: ollama serve
   - Modelin var olduğunu kontrol edin: ollama list

3. Hata ayıklamak için:
   - Düğümlere print() ifadeleri ekleyin
   - Her adımda durumu kontrol edin

Yazar: Beyhan MEYRALI
"""

from typing import TypedDict
from langgraph.graph import StateGraph, END
import requests

# =============================================================================
# ADIM 1: Durumu Tanımla
# =============================================================================

class State(TypedDict):
    """
    Grafik boyunca akan durum.

    Bunu düğümler arasında aktarılan "hafıza" olarak düşünün.
    Her düğüm bu durumdan okuyabilir ve güncelleyebilir.
    """
    question: str  # Kullanıcının sorusu
    answer: str    # LLM'in cevabı


# =============================================================================
# ADIM 2: Düğümleri Tanımla (Fonksiyonlar)
# =============================================================================

def ask_llm_node(state: State) -> dict:
    """
    Ollama LLM'i çağıran düğüm.

    Bir düğüm sadece şunları yapan bir Python fonksiyonudur:
    - Mevcut durumu girdi olarak alır
    - Bir iş yapar
    - Duruma güncellemeler döndürür

    Argümanlar:
        state: Soruyu içeren mevcut durum

    Döndürür:
        Duruma eklenecek cevabı içeren sözlük
    """

    print(f"\n[DÜĞÜM] LLM şu soruyla çağrılıyor: {state['question']}")

    try:
        # Ollama API'sini çağır
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "qwen3:8b",
                "messages": [
                    {"role": "user", "content": state["question"]}
                ],
                "stream": False
            },
            timeout=60
        )

        if response.status_code == 200:
            answer = response.json()["message"]["content"]
            print(f"[DÜĞÜM] Cevap alındı: {answer[:80]}...")
            return {"answer": answer}
        else:
            error = f"API Hatası: {response.status_code}"
            print(f"[HATA] {error}")
            return {"answer": error}

    except Exception as e:
        error = f"Hata: {str(e)}"
        print(f"[HATA] {error}")
        return {"answer": error}


# =============================================================================
# ADIM 3: Grafiği Oluştur
# =============================================================================

def create_graph():
    """
    LangGraph iş akışını oluştur.

    Bu basit bir grafik oluşturur:
    BAŞLA → ask_llm_node → BİTİR

    Döndürür:
        Çalıştırılmaya hazır derlenmiş grafik
    """

    print("\n[GRAFİK] İş akışı oluşturuluyor...")

    # Durum tipimizle grafik oluştur
    workflow = StateGraph(State)

    # LLM düğümümüzü ekle
    workflow.add_node("ask_llm", ask_llm_node)

    # Akışı tanımla
    workflow.set_entry_point("ask_llm")  # Buradan başla
    workflow.add_edge("ask_llm", END)     # Sonra bitir

    # Çalıştırılabilir uygulamaya derle
    app = workflow.compile()

    print("[GRAFİK] İş akışı oluşturuldu: BAŞLA → ask_llm → BİTİR")

    return app


# =============================================================================
# ADIM 4: Grafiği Çalıştır
# =============================================================================

def run_question(question: str):
    """
    Grafiği bir soruyla çalıştır.

    Argümanlar:
        question: Sorulacak soru
    """

    print("\n" + "="*70)
    print(f"SORU: {question}")
    print("="*70)

    # Grafik oluştur
    app = create_graph()

    # Başlangıç durumuyla çalıştır
    result = app.invoke({"question": question, "answer": ""})

    # Sonucu yazdır
    print("\n" + "="*70)
    print("CEVAP:")
    print("="*70)
    print(result["answer"])
    print("="*70)

    return result


# =============================================================================
# ANA
# =============================================================================

def main():
    """Ana giriş noktası."""

    print("""
╔═══════════════════════════════════════════════════════════════════╗
║         Örnek 1: Basit LangGraph Ajanı                            ║
║                                                                   ║
║  Bu şunları gösterir:                                            ║
║  • Durum tanımlama (TypedDict)                                  ║
║  • Düğüm oluşturma (fonksiyonlar)                               ║
║  • Grafik oluşturma (iş akışı)                                  ║
║  • Grafik çalıştırma (invoke)                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Test 1: Basit soru
    print("\n[TEST 1] Basit Soru")
    run_question("Fransa'nın başkenti neresidir?")

    # Test 2: Matematik sorusu
    print("\n\n[TEST 2] Matematik Sorusu")
    run_question("15 * 7 kaçtır?")

    # Test 3: Akıl yürütme
    print("\n\n[TEST 3] Akıl Yürütme Sorusu")
    run_question("3 elmam varsa ve 2 tane daha alırsam, kaç tane olurum?")

    print("\n" + "="*70)
    print("✅ TÜM TESTLER TAMAMLANDI!")
    print("="*70)
    print("\nTemel Kavramlar:")
    print("  • Durum = Grafik boyunca akan veri")
    print("  • Düğüm = Durumu işleyen fonksiyon")
    print("  • Kenar = Düğümler arası bağlantı")
    print("  • Grafik = Tam iş akışı")
    print("\nSıradaki: Dallanma mantığı için 02_conditional_workflow.py'ye bakın")
    print("="*70)


if __name__ == "__main__":
    # Ollama'yı kontrol et
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            print("[UYARI] Ollama beklenmeyen durum döndürdü")
    except requests.exceptions.RequestException:
        print("[HATA] Ollama'ya bağlanılamıyor!")
        print("  1. Yükle: https://ollama.ai")
        print("  2. Çalıştır: ollama serve")
        print("  3. Modeli çek: ollama pull qwen3:8b")
        exit(1)

    main()
