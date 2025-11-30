#!/usr/bin/env python3
"""
Örnek 3: Özyinelemeli Ajan - Ajan Döngüsü
============================================

Bu, bir LLM'i bir AJANA dönüştüren TEMEL desendir!

Özyinelemeli ajan şunları yapabilir:
- Sırayla birden fazla aracı çağırmak
- Bir aracın çıktısını diğerine girdi olarak kullanmak
- Karmaşık çok adımlı görevleri otonom olarak çözmek

İnsanların "ajan davranışı" derken kastettikleri budur!

Yazar: Beyhan MEYRALI
"""

import requests
import json
from typing import List, Dict, Any, Optional

# =============================================================================
# YAPILANDIRMA
# =============================================================================

OLLAMA_BASE_URL = "http://localhost:11434"
MODEL_NAME = "qwen3:8b"  # Yerel ajanlar için en iyi araç çağırma modeli (2025)

# =============================================================================
# SAHTE ARAÇLAR (Simüle Edilmiş Fonksiyonlar)
# =============================================================================

# Bunlar ajanınızın çağırabileceği "gerçek" fonksiyonlardır.
# Üretimde, bunlar gerçek API'leri, veritabanlarını vb. çağırır.

def get_current_weather(city: str) -> str:
    """
    Sahte hava durumu API'si.
    Üretimde, bu gerçek bir hava durumu servisini çağırır.
    """
    weather_db = {
        "tokyo": {"temp": 25, "condition": "sunny", "humidity": "low"},
        "paris": {"temp": 18, "condition": "cloudy", "humidity": "moderate"},
        "london": {"temp": 15, "condition": "rainy", "humidity": "high"},
        "new york": {"temp": 22, "condition": "clear", "humidity": "moderate"},
        "toronto": {"temp": 16, "condition": "partly cloudy", "humidity": "moderate"},
    }

    city_lower = city.lower()
    if city_lower in weather_db:
        data = weather_db[city_lower]
        return json.dumps({
            "city": city,
            "temperature_celsius": data["temp"],
            "condition": data["condition"],
            "humidity": data["humidity"]
        })
    else:
        return json.dumps({"error": f"{city} için hava durumu verisi mevcut değil"})


def get_my_manager() -> str:
    """
    Mevcut kullanıcının yönetici bilgisini al.
    Üretimde, bu İK sistemini/veritabanını sorgular.
    """
    return json.dumps({
        "manager_name": "Alice Johnson",
        "manager_email": "alice.johnson@company.com",
        "manager_city": "Paris",
        "manager_department": "Engineering"
    })


def get_team_members(manager_name: str) -> str:
    """
    Belirli bir yönetici için ekip üyelerini al.
    Üretimde, bu İK/organizasyon şeması veritabanını sorgular.
    """
    teams = {
        "Alice Johnson": [
            {"name": "Bob Smith", "role": "Senior Engineer", "city": "London"},
            {"name": "Carol Williams", "role": "Engineer", "city": "Paris"},
            {"name": "David Brown", "role": "Junior Engineer", "city": "Paris"}
        ],
        "John Doe": [
            {"name": "Eve Davis", "role": "Designer", "city": "Tokyo"},
            {"name": "Frank Miller", "role": "Product Manager", "city": "New York"}
        ]
    }

    if manager_name in teams:
        return json.dumps({"manager": manager_name, "team": teams[manager_name]})
    else:
        return json.dumps({"error": f"Yönetici {manager_name} için ekip bulunamadı"})


def search_web(query: str) -> str:
    """
    Sahte web araması.
    Üretimde, bu gerçek bir arama API'sini (Google, Bing vb.) çağırır.
    """
    # Simüle edilmiş arama sonuçları
    results = {
        "python programming": "Python, basitliği ve okunabilirliği ile bilinen üst düzey, yorumlanan bir programlama dilidir.",
        "weather tokyo": "Tokyo hava durumu: Şu anda 25°C, hafta boyunca güneşli gökyüzü bekleniyor.",
        "ai agents": "Yapay zeka ajanları, çevrelerini algılayabilen ve hedeflere ulaşmak için eylemler gerçekleştirebilen otonom sistemlerdir.",
    }

    query_lower = query.lower()
    for key in results:
        if key in query_lower:
            return json.dumps({"query": query, "result": results[key]})

    return json.dumps({"query": query, "result": "İlgili sonuç bulunamadı"})


# =============================================================================
# ARAÇ TANIMLARI (LLM için Şema)
# =============================================================================

# Bu, LLM'e hangi araçların mevcut olduğunu ve bunların nasıl kullanılacağını söyler.
# Bunu LLM için "API dokümantasyonu" olarak düşünün.

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Belirli bir şehir için güncel hava durumunu al. Sıcaklığı Celsius, hava durumunu ve nem seviyesini döndürür.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Şehir adı (örn. 'Tokyo', 'Paris', 'London')"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_my_manager",
            "description": "Mevcut kullanıcının yöneticisi hakkında isim, e-posta, konum ve departman dahil olmak üzere bilgi al. Parametre almaz.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_team_members",
            "description": "Belirli bir yönetici için ekip üyelerinin listesini al. Rolleri ve konumlarıyla birlikte ekip üyelerinin dizisini döndürür.",
            "parameters": {
                "type": "object",
                "properties": {
                    "manager_name": {
                        "type": "string",
                        "description": "Yöneticinin tam adı (örn. 'Alice Johnson')"
                    }
                },
                "required": ["manager_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Herhangi bir konuda bilgi için web'de arama yap. İlgili arama sonuçlarını döndürür.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Arama sorgusu (örn. 'Python programlama', 'Tokyo'da hava')"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# Fonksiyon adlarını gerçek Python fonksiyonlarıyla eşle
AVAILABLE_FUNCTIONS = {
    "get_current_weather": get_current_weather,
    "get_my_manager": get_my_manager,
    "get_team_members": get_team_members,
    "search_web": search_web
}


# =============================================================================
# ARAÇ YÜRÜTME
# =============================================================================

def execute_tool(function_name: str, arguments: Dict[str, Any]) -> str:
    """
    Bir araç fonksiyonunu çalıştır ve sonucu döndür.

    Burası asıl araç yürütmesinin gerçekleştiği yerdir.
    LLM sadece "bu fonksiyonu çağır" der - biz aslında onu çalıştırırız.

    Argümanlar:
        function_name: Çağrılacak fonksiyonun adı
        arguments: Geçirilecek argümanlar sözlüğü

    Döndürür:
        Fonksiyon sonucu veya hatası içeren JSON dizesi
    """

    print(f"  [YÜRÜT] {function_name}({arguments})")

    # Fonksiyonun var olup olmadığını kontrol et
    if function_name not in AVAILABLE_FUNCTIONS:
        error_result = json.dumps({
            "error": f"Bilinmeyen fonksiyon: {function_name}",
            "available_functions": list(AVAILABLE_FUNCTIONS.keys())
        })
        print(f"  [HATA] {error_result}")
        return error_result

    try:
        # Gerçek Python fonksiyonunu al
        function = AVAILABLE_FUNCTIONS[function_name]

        # Argümanlarla çağır
        result = function(**arguments)

        print(f"  [SONUÇ] {result}")
        return result

    except Exception as e:
        # Yürütme sırasındaki hataları işle
        error_result = json.dumps({"error": f"{function_name} çalıştırılırken hata: {str(e)}"})
        print(f"  [HATA] {error_result}")
        return error_result


# =============================================================================
# ÖZYİNELEMELİ AJAN DÖNGÜSÜ
# =============================================================================

def recursive_agent(user_message: str, max_iterations: int = 10, verbose: bool = True) -> str:
    """
    Özyinelemeli ajan döngüsü - BU ANAHTAR DESENDİR!

    Bu fonksiyon:
    1. Kullanıcı mesajını mevcut araçlarla LLM'e gönderir
    2. LLM araç kullanmak isterse, onları çalıştırır
    3. Araç sonuçlarını LLM'e geri gönderir
    4. LLM son cevabı verene kadar (veya maksimum iterasyona kadar) tekrarlar

    Bir LLM'i otonom bir ajana dönüştüren şey budur!

    Argümanlar:
        user_message: Kullanıcının sorusu/isteği
        max_iterations: Maksimum LLM çağrısı sayısı (sonsuz döngüleri önler)
        verbose: Ayrıntılı yürütme günlüklerini yazdır

    Döndürür:
        Ajandan gelen son cevap
    """

    if verbose:
        print("\n" + "="*70)
        print("ÖZYİNELEMELİ AJAN YÜRÜTMESİ")
        print("="*70)
        print(f"[KULLANICI] {user_message}")
        print("-"*70)

    # Konuşmayı kullanıcı mesajı ile başlat
    messages = [
        {"role": "user", "content": user_message}
    ]

    url = f"{OLLAMA_BASE_URL}/api/chat"

    # AJAN DÖNGÜSÜ
    for iteration in range(max_iterations):
        if verbose:
            print(f"\n[İTERASYON {iteration + 1}]")

        # İstek yükünü hazırla
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "tools": TOOLS,
            "stream": False
        }

        try:
            # LLM'i çağır
            if verbose:
                print("  [LLM] Düşünüyor...")

            response = requests.post(url, json=payload, timeout=60)

            if response.status_code != 200:
                return f"Hata: LLM API {response.status_code} döndürdü"

            response_data = response.json()
            message = response_data.get("message", {})

            # LLM'in yanıtını konuşmaya ekle
            messages.append(message)

            # LLM'in araç kullanmak isteyip istemediğini kontrol et
            tool_calls = message.get("tool_calls", [])

            if tool_calls:
                # LLM bir veya daha fazla araç kullanmak istiyor
                if verbose:
                    print(f"  [LLM] {len(tool_calls)} araç kullanmak istiyor")

                # LLM'in istediği her aracı çalıştır
                for tool_call in tool_calls:
                    function_data = tool_call.get("function", {})
                    function_name = function_data.get("name")
                    arguments = function_data.get("arguments", {})

                    # Aracı çalıştır
                    result = execute_tool(function_name, arguments)

                    # Araç sonucunu konuşmaya ekle
                    # LLM bu sonucu bir sonraki iterasyonda görecek
                    messages.append({
                        "role": "tool",
                        "content": result
                    })

                # Döngüye devam et - LLM araç sonuçlarını işleyecek

            else:
                # Araç çağrısı yok - LLM son cevaba ulaştı
                final_answer = message.get("content", "")

                if verbose:
                    print(f"\n[FİNAL CEVAP {iteration + 1} iterasyondan sonra]")
                    print("-"*70)
                    print(final_answer)
                    print("="*70)

                return final_answer

        except requests.exceptions.RequestException as e:
            return f"Hata: LLM bağlantısı başarısız: {str(e)}"

    # Maksimum iterasyona ulaşıldı ve son cevap yok
    if verbose:
        print(f"\n[UYARI] Maksimum iterasyon ({max_iterations}) aşıldı!")

    return "Görev çok karmaşık - maksimum iterasyon aşıldı"


# =============================================================================
# GÖSTERİM: BASİT VS KARMAŞIK SORGULAR
# =============================================================================

def run_demonstrations():
    """
    Artan karmaşıklığı gösteren örnek sorguları çalıştır.
    Ajanın araçları nasıl zincirlediğini izleyin!
    """

    print("""
╔═══════════════════════════════════════════════════════════════════╗
║              Özyinelemeli Ajan - Çok Adımlı Araç Çağırma          ║
║                                                                   ║
║  Ajanın birden fazla araç çağrısını otonom olarak nasıl           ║
║  zincirlediğini izleyin!                                          ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Örnek 1: Basit tek araç çağrısı
    print("\n\n" + "#"*70)
    print("# ÖRNEK 1: Basit Sorgu (1 araç çağrısı)")
    print("#"*70)
    recursive_agent("Tokyo'da hava nasıl?")

    # Örnek 2: Çok adımlı sorgu
    print("\n\n" + "#"*70)
    print("# ÖRNEK 2: Çok Adımlı Sorgu (2 araç çağrısı)")
    print("#"*70)
    recursive_agent("Yöneticimin şehrinde hava nasıl?")
    # Bu şunları gerektirir:
    # Adım 1: get_my_manager() ile yöneticinin şehrini bul
    # Adım 2: get_current_weather(city) ile o şehir için hava durumunu al

    # Örnek 3: Karmaşık orkestrasyon
    print("\n\n" + "#"*70)
    print("# ÖRNEK 3: Karmaşık Sorgu (3+ araç çağrısı)")
    print("#"*70)
    recursive_agent("Yöneticimin adını al, sonra ekip üyelerini listele ve her ekip üyesinin şehrindeki hava durumunu söyle")
    # Bu şunları gerektirir:
    # Adım 1: get_my_manager() → Yönetici adını al
    # Adım 2: get_team_members(manager_name) → Ekip listesini al
    # Adım 3: get_current_weather(city1) → Üye 1 için hava durumu
    # Adım 4: get_current_weather(city2) → Üye 2 için hava durumu
    # Adım 5: get_current_weather(city3) → Üye 3 için hava durumu

    # Örnek 4: Araç gerektirmeyen sorgu
    print("\n\n" + "#"*70)
    print("# ÖRNEK 4: Araç Gerekmiyor")
    print("#"*70)
    recursive_agent("2+2 kaçtır?")
    # LLM herhangi bir araç çağırmadan doğrudan cevap verebilir


# =============================================================================
# ETKİLEŞİMLİ MOD
# =============================================================================

def interactive_mode():
    """
    Etkileşimli ajan modu - kendi sorularınızı sorun!
    """

    print("\n" + "="*70)
    print("ETKİLEŞİMLİ AJAN MODU")
    print("="*70)
    print("Mevcut araçlar:")
    for tool in TOOLS:
        func = tool["function"]
        print(f"  - {func['name']}: {func['description']}")
    print("\nKomutlar: 'quit', 'exit', 'help'")
    print("="*70)

    while True:
        user_input = input("\n[SİZ] ").strip()

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("[BİLGİ] Hoşçakal!")
            break

        if user_input.lower() == 'help':
            print("\nMevcut araçlar:")
            for tool in TOOLS:
                func = tool["function"]
                print(f"  - {func['name']}: {func['description']}")
            continue

        if not user_input:
            continue

        # Özyinelemeli ajanı çalıştır
        recursive_agent(user_input, verbose=True)


# =============================================================================
# ANA PROGRAM
# =============================================================================

def main():
    """
    Ana giriş noktası
    """

    # Ollama bağlantısını kontrol et
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code != 200:
            print("[HATA] Ollama doğru yanıt vermiyor")
            exit(1)
    except requests.exceptions.RequestException:
        print("[HATA] Ollama'ya bağlanılamıyor!")
        print("[İPUCU] Ollama'nın çalıştığından emin olun: ollama serve")
        exit(1)

    # Gösterimleri çalıştır
    run_demonstrations()

    # Etkileşimli mod
    print("\n\n")
    try:
        interactive_mode()
    except KeyboardInterrupt:
        print("\n[BİLGİ] Kullanıcı tarafından kesildi. Hoşçakal!")


if __name__ == "__main__":
    main()
