#!/usr/bin/env python3
"""
qwen3:8b modeli ile Ollama'nın yerel araç çağırma API'sini kullanan araç çağırma.
Ollama artık OpenAI'ye benzer yerel fonksiyon çağırmayı destekliyor.
"""
import requests
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

class OllamaToolBot:
    def __init__(self, model="qwen3:8b", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.messages = []
        
        # Ollama formatında araçları tanımla
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Bir şehir için güncel hava durumunu al",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "Şehir adı",
                            }
                        },
                        "required": ["city"],
                    },
                },
            },
        ]
        
        print(f"[TAMAM] Ollama araç botu şu modelle başlatıldı: {model}")
        print(f"[TAMAM] Ollama temel URL'si: {base_url}")
        print(f"[TAMAM] Mevcut araçlar: get_current_weather")

    def get_current_weather(self, city, unit="celsius"):
        """Sahte hava durumu fonksiyonu"""
        weather_data = {
            "tokyo": {"temperature": 25, "condition": "sunny", "humidity": "low"},
            "paris": {"temperature": 18, "condition": "cloudy", "humidity": "moderate"},
            "london": {"temperature": 15, "condition": "rainy", "humidity": "high"},
            "istanbul": {"temperature": 22, "condition": "partly cloudy", "humidity": "moderate"},
            "bursa": {"temperature": -5, "condition": "snowy", "humidity": "low"},
            "new york": {"temperature": 20, "condition": "clear", "humidity": "moderate"},
            "toronto": {"temperature": 16, "condition": "windy", "humidity": "moderate"}
        }
        
        city_lower = city.lower()
        if city_lower in weather_data:
            temp = weather_data[city_lower]["temperature"]
            if unit == "fahrenheit":
                temp = (temp * 9/5) + 32
                unit_symbol = "°F"
            else:
                unit_symbol = "°C"
            
            return json.dumps({
                "city": city,
                "temperature": f"{temp}{unit_symbol}",
                "condition": weather_data[city_lower]["condition"],
                "humidity": weather_data[city_lower]["humidity"],
                "unit": unit
            })
        else:
            return json.dumps({
                "city": city,
                "temperature": "unknown",
                "condition": "data not available",
                "humidity": "unknown"
            })

    def ask_question(self, question):
        """Yerel araç çağırma ile Ollama'ya soru gönder"""
        try:
            url = f"{self.base_url}/api/chat"
            
            # Kullanıcı mesajını konuşmaya ekle
            self.messages.append({"role": "user", "content": question})
            
            # Araçlarla ilk çağrı
            payload = {
                "model": self.model,
                "messages": self.messages,
                "tools": self.tools,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9
                }
            }
            
            print(f"[SOR] Soru: {question}")
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                response_data = response.json()
                message = response_data.get("message", {})
                
                # Asistan yanıtını konuşmaya ekle
                self.messages.append(message)
                
                # Modelin araç kullanmak isteyip istemediğini kontrol et
                tool_calls = message.get("tool_calls", [])
                
                if tool_calls:
                    print(f"[ARAÇ] YZ araç çağırmak istiyor!")
                    
                    for tool_call in tool_calls:
                        # Ollama'nın araç çağrı formatını işle
                        function_data = tool_call.get("function", {})
                        function_name = function_data.get("name")
                        arguments = function_data.get("arguments", {})
                        
                        print(f"[ARAÇ] Çağrılıyor: {function_name} argümanlar: {arguments}")
                        
                        # Aracı çalıştır
                        if function_name == "get_weather":
                            # Hem 'city' hem de 'location' parametre adlarını işle
                            city = arguments.get("city") or arguments.get("location", "")
                            unit = arguments.get("unit", "celsius")
                            result = self.get_current_weather(city, unit)
                            print(f"[ARAÇ] Sonuç: {result}")
                            
                            # Araç sonucunu konuşmaya ekle
                            self.messages.append({
                                "role": "tool",
                                "content": result
                            })
                    
                    # Araç sonuçlarıyla final yanıtı al
                    return self.get_final_response()
                else:
                    # Araç kullanımı olmadan doğrudan yanıt
                    content = message.get("content", "")
                    cleaned_content = self.clean_response(content)
                    try:
                        print(f"[TAMAM] Doğrudan yanıt: {cleaned_content}")
                    except UnicodeEncodeError:
                        safe_content = cleaned_content.encode('ascii', 'replace').decode('ascii')
                        print(f"[TAMAM] Doğrudan yanıt: {safe_content}")
                    return cleaned_content
                    
            else:
                error_msg = f"Ollama API Hatası: {response.status_code} - {response.text}"
                print(f"[HATA] {error_msg}")
                return error_msg
                
        except Exception as e:
            error_msg = f"Bağlantı hatası: {str(e)}"
            print(f"[HATA] {error_msg}")
            return error_msg

    def get_final_response(self):
        """Araç yürütmesinden sonra YZ'nin son yanıtını al"""
        try:
            url = f"{self.base_url}/api/chat"
            
            payload = {
                "model": self.model,
                "messages": self.messages,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9
                }
            }
            
            response = requests.post(url, json=payload, timeout=60)
            
            if response.status_code == 200:
                response_data = response.json()
                final_response = response_data.get("message", {}).get("content", "")
                cleaned_final = self.clean_response(final_response)
                
                self.messages.append({"role": "assistant", "content": cleaned_final})
                try:
                    print(f"[TAMAM] Final yanıt: {cleaned_final}")
                except UnicodeEncodeError:
                    safe_response = cleaned_final.encode('ascii', 'replace').decode('ascii')
                    print(f"[TAMAM] Final yanıt: {safe_response}")
                return cleaned_final
            else:
                return f"Final yanıt alınırken hata: {response.status_code}"
                
        except Exception as e:
            return f"Final yanıtta hata: {str(e)}"

    def clean_response(self, response):
        """Yanıttan düşünme etiketlerini ve içeriğini kaldır"""
        import re
        # <think>...</think> bloklarını kaldır
        cleaned = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL)
        # Kalan boş satırları ve fazladan boşlukları kaldır
        cleaned = '\n'.join(line.strip() for line in cleaned.split('\n') if line.strip())
        return cleaned.strip()

    def reset_conversation(self):
        """Konuşma geçmişini sıfırla"""
        self.messages = []
        print("[BİLGİ] Konuşma geçmişi sıfırlandı")


# FastAPI uygulaması
app = FastAPI()

class Query(BaseModel):
    query: str

@app.get("/")
async def root():
    return {"message": "Merhaba Dünya - Ollama Yerel Araç Çağırma", "model": "qwen3:8b", "tools": ["get_current_weather"]}

async def ollama_tool_chat(query: str):
    try:
        bot = OllamaToolBot()
        answer = bot.ask_question(query)
        return {"ai_response": answer, "model": "qwen3:8b", "tools_available": ["get_current_weather"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/{query}")
async def chat_get(query: str):
    return await ollama_tool_chat(query)

@app.post("/chat")
async def chat_post(query: Query):
    return await ollama_tool_chat(query.query)

def main():
    """Yerel araç çağırma işlevselliğini test et"""
    try:
        bot = OllamaToolBot()
        
        # Araç çağırmayı tetiklemesi gereken test soruları
        test_questions = [
            "What is the weather in Toronto?",
            "What's the weather in Tokyo?",
            "How's the weather in Paris today?",
            "Tell me about the weather in Istanbul",
            "What's the capital of France?",  # Bu araç çağırmayı TETİKLEMEMELİDİR
            "Is it raining in London?",
            "What's the temperature in New York in fahrenheit?"
        ]
        
        print("\n" + "="*60)
        print("YEREL ARAÇ ÇAĞIRMA TESTLERİ ÇALIŞTIRILIYOR")
        print("="*60)
        print("Not: Bu, araç çağırma desteğine sahip Ollama gerektirir")
        print("Ollama'nın güncel bir sürümünü çalıştırdığınızdan emin olun")
        print("="*60)
        
        for question in test_questions:
            print(f"\n[TEST] {question}")
            result = bot.ask_question(question)
            print(f"[SONUÇ] {result}")
            print("-" * 50)
            bot.reset_conversation()  # Her test için sıfırla
        
        print("\n[BAŞARILI] Araç çağırma testleri tamamlandı!")
        
        # Etkileşimli soru sorma
        print("\n" + "="*60)
        print("ETKİLEŞİMLİ MOD - Kendi sorularınızı sorun!")
        print("Mevcut araç: get_current_weather(city, unit)")
        print("Şöyle sorular deneyin:")
        print("  - 'What is the weather in Toronto?'")
        print("  - 'Temperature in Tokyo in fahrenheit?'")
        print("  - 'Is it raining in London?'")
        print("Oturumu kontrol etmek için 'quit', 'exit' veya 'reset' yazın")
        print("="*60)
        
        bot.reset_conversation()  # Etkileşimli mod için taze başlat
        
        while True:
            try:
                user_question = input("\n[SİZ] Sorunuzu girin: ").strip()
                
                if user_question.lower() in ['quit', 'exit', 'q']:
                    print("[BİLGİ] Etkileşimli moddan çıkılıyor...")
                    break
                
                if user_question.lower() == 'reset':
                    bot.reset_conversation()
                    print("[BİLGİ] Konuşma sıfırlandı")
                    continue
                
                if not user_question:
                    print("[BİLGİ] Lütfen bir soru girin veya çıkmak için 'quit' yazın")
                    continue
                
                result = bot.ask_question(user_question)
                
            except KeyboardInterrupt:
                print("\n[BİLGİ] Kullanıcı tarafından kesildi. Çıkılıyor...")
                break
            except Exception as e:
                print(f"[HATA] Soru işlenirken hata: {str(e)}")
                continue
        
        return 0
        
    except Exception as e:
        print(f"[HATA] Hata: {str(e)}")
        return 1

if __name__ == "__main__":
    # Doğrudan testi çalıştır
    main()
    
    # FastAPI sunucusunu çalıştırmak için yorumu kaldırın
    # uvicorn.run(app, host="0.0.0.0", port=8002)

# Sunucu olarak çalışırken örnek URL'ler:
# http://127.0.0.1:8002/chat/weather%20in%20toronto
# http://127.0.0.1:8002/chat/temperature%20in%20tokyo
