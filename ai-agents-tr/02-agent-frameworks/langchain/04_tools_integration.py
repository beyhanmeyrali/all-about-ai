#!/usr/bin/env python3
"""
Örnek 04: Araç Entegrasyonu - Ajanlara Süper Güçler Verin
========================================================

Ajanlara ARAÇLAR vermeyi öğrenin - onları gerçekten güçlü yapan budur!

Ne öğreneceksiniz:
- Araçların ne olduğu ve neden önemli oldukları
- @tool dekoratörü ile özel araçlar oluşturma
- Araçları LLM'lere bağlama (Modern LCEL)
- Araç çağrılarını yürütme
- Basit bir araç kullanan ajan döngüsü oluşturma

Bu KRİTİKTİR - araçlar sohbet botlarını ajanlara dönüştürür!

Yazar: Beyhan MEYRALI
"""

import json
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_ollama import ChatOllama
from langchain_core.tools import tool, Tool, StructuredTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

# =============================================================================
# BÖLÜM 1: Basit Araç Fonksiyonları
# =============================================================================

def get_weather(city: str) -> str:
    """
    Bir şehir için güncel hava durumunu al.
    
    Argümanlar:
        city: Şehir adı (örn. "Tokyo", "Paris")
    """
    # Sahte hava durumu veritabanı
    weather_db = {
        "tokyo": {"temp": 25, "condition": "sunny", "humidity": 60},
        "paris": {"temp": 18, "condition": "cloudy", "humidity": 75},
        "london": {"temp": 15, "condition": "rainy", "humidity": 85},
        "new york": {"temp": 22, "condition": "clear", "humidity": 50},
        "dubai": {"temp": 35, "condition": "hot", "humidity": 40},
    }

    city_lower = city.lower()
    if city_lower in weather_db:
        data = weather_db[city_lower]
        return json.dumps({
            "city": city,
            "temperature_celsius": data["temp"],
            "condition": data["condition"],
            "humidity": data["humidity"],
            "timestamp": datetime.now().isoformat()
        })
    else:
        return json.dumps({"error": f"{city} için hava durumu verisi yok"})

def calculate(expression: str) -> str:
    """
    Bir matematiksel ifadeyi hesapla.
    
    Argümanlar:
        expression: Matematik ifadesi (örn. "2 + 2", "15 * 7")
    """
    try:
        # UYARI: eval() tehlikelidir! Sadece demo için kullanın
        result = eval(expression)
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": f"Hesaplanamıyor: {str(e)}"})

def search_web(query: str) -> str:
    """
    Bilgi için web'de arama yap.
    
    Argümanlar:
        query: Arama sorgusu
    """
    # Sahte arama sonuçları
    results = {
        "python": "Python, yüksek seviyeli bir programlama dilidir...",
        "ai": "Yapay Zeka, makineler tarafından gösterilen zekadır...",
        "langchain": "LangChain, LLM'ler tarafından desteklenen uygulamalar geliştirmek için bir frameworktür..."
    }
    
    query_lower = query.lower()
    for key, val in results.items():
        if key in query_lower:
            return json.dumps({"snippet": val})
            
    return json.dumps({"snippet": "Sonuç bulunamadı."})

# =============================================================================
# BÖLÜM 2: Modern Araç Ajanı
# =============================================================================

class ModernToolAgent:
    """
    Modern LCEL araç bağlama kullanan ajan.
    
    Eski AgentExecutor yerine şunu kullanıyoruz:
    1. llm.bind_tools(tools)
    2. Manuel yürütme döngüsü (veya üretimde LangGraph)
    """

    def __init__(self, model: str = "qwen3:8b"):
        print(f"\n[BAŞLAT] {model} ile ModernToolAgent oluşturuluyor...")
        
        # 1. LLM Oluştur
        self.llm = ChatOllama(model=model, temperature=0.0)
        
        # 2. Araçları Tanımla (daha iyi şema için StructuredTool kullanarak)
        self.tools = [
            StructuredTool.from_function(
                func=get_weather,
                name="get_weather",
                description="Bir şehir için güncel hava durumunu al"
            ),
            StructuredTool.from_function(
                func=calculate,
                name="calculate",
                description="Matematik ifadelerini hesapla"
            ),
            StructuredTool.from_function(
                func=search_web,
                name="search_web",
                description="Bilgi için web'de arama yap"
            )
        ]
        
        # Yürütme için eşleme
        self.tool_map = {t.name: t for t in self.tools}
        
        # 3. Araçları LLM'e Bağla
        # Bu, LLM'e araçlar ve şemaları hakkında bilgi verir
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        print("[BAŞLAT] ✅ Ajan araçlarla hazır!")

    def ask(self, question: str):
        """
        Ajan döngüsünü çalıştır.
        
        1. Soruyu LLM'e gönder
        2. Araç çağrılarını kontrol et
        3. Gerekirse araçları çalıştır
        4. Sonuçları LLM'e geri gönder
        5. Final cevabı al
        """
        print("\n" + "="*70)
        print(f"SORU: {question}")
        print("="*70)
        
        messages = [HumanMessage(content=question)]
        
        # Adım 1: İlk LLM Çağrısı
        print("  🤔 Düşünüyor...")
        response = self.llm_with_tools.invoke(messages)
        messages.append(response)
        
        # Adım 2: Araç çağrılarını kontrol et
        if response.tool_calls:
            print(f"  🛠️  LLM {len(response.tool_calls)} araç çağırmak istiyor:")
            
            # Adım 3: Araçları çalıştır
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]
                
                print(f"    → {tool_name} çağrılıyor, argümanlar: {tool_args}")
                
                if tool_name in self.tool_map:
                    tool_instance = self.tool_map[tool_name]
                    try:
                        # Çalıştır
                        tool_result = tool_instance.invoke(tool_args)
                        print(f"    ✓ Sonuç: {tool_result}")
                        
                        # Sonucu mesajlara ekle
                        messages.append(ToolMessage(
                            content=str(tool_result),
                            tool_call_id=tool_id,
                            name=tool_name
                        ))
                    except Exception as e:
                        print(f"    ❌ Hata: {e}")
                        messages.append(ToolMessage(
                            content=f"Hata: {str(e)}",
                            tool_call_id=tool_id,
                            name=tool_name
                        ))
                else:
                    print(f"    ❌ Bilinmeyen araç: {tool_name}")

            # Adım 4: Final LLM Çağrısı (araç sonuçlarıyla)
            print("  🤔 Cevap sentezleniyor...")
            final_response = self.llm_with_tools.invoke(messages)
            print("\nFİNAL CEVAP:")
            print(final_response.content)
            return final_response.content
            
        else:
            # Araç gerekmedi
            print("\nFİNAL CEVAP (Araç kullanılmadı):")
            print(response.content)
            return response.content

# =============================================================================
# DEMOLAR
# =============================================================================

def main():
    agent = ModernToolAgent()
    
    # Demo 1: Tek Araç
    agent.ask("Tokyo'da hava nasıl?")
    
    # Demo 2: Matematik
    agent.ask("15 * 7 + 10'u hesapla")
    
    # Demo 3: Çok adımlı (Paralel veya Sıralı)
    # Not: Temel döngü bir turda paralel çağrıları işler.
    # Çok turlu (A sonra B) için bir while döngüsüne ihtiyacımız olur (01-tool-calling'deki gibi).
    # Bu basit uygulama "Paralel" çağrıları iyi işler.
    agent.ask("Paris ve Londra'da hava nasıl?")

if __name__ == "__main__":
    # Ollama'yı kontrol et
    try:
        requests.get("http://localhost:11434/api/tags", timeout=5)
    except:
        print("Hata: Ollama çalışmıyor!")
        exit(1)
        
    main()
