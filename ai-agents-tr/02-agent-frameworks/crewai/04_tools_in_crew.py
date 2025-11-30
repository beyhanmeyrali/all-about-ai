import os
from crewai import Agent, Task, Crew, Process
from langchain_ollama import ChatOllama
from langchain.tools import tool

# =============================================================================
# 04 - Ekipte Araçlar: Ajanlara Süper Güçler Vermek
# =============================================================================
#
# Ajanlar akıllıdır, ancak ARAÇLAR olmadan gerçek dünyaya erişemezler.
# Araçlar ajanların şunları yapmasını sağlar:
# - Web'de arama yapmak
# - Dosyaları okumak
# - Sayıları hesaplamak
# - API'leri çağırmak
#
# Bu örnekte, özel bir araç oluşturacağız ve bunu bir ajana vereceğiz.
# =============================================================================

# 1. Özel Araçları Tanımla
# Bir aracı tanımlamak için @tool dekoratörünü kullanırız.
# Docstring KRİTİKTİR - LLM'e aracı ne zaman ve nasıl kullanacağını söyler.

@tool("Uzunluk Hesaplayıcı")
def calculate_length(text: str) -> str:
    """Verilen bir metin dizesinin uzunluğunu hesaplamak için yararlıdır.
    Karakter sayısını döndürür."""
    return str(len(text))

@tool("Dizeyi Ters Çevir")
def reverse_string(text: str) -> str:
    """Verilen bir metin dizesini ters çevirmek için yararlıdır."""
    return text[::-1]

def main():
    llm = ChatOllama(
        model="qwen3:8b",
        base_url="http://localhost:11434",
        temperature=0.7
    )

    # 2. Araçlarla Ajanı Tanımla
    # Araç listesini ajana geçiriyoruz.
    
    math_wizard = Agent(
        role='Dize Büyücüsü',
        goal='Araçları kullanarak dizeleri analiz et ve manipüle et',
        backstory="Kelimeler ve sayılarla oynamayı seven bir büyücüsün.",
        verbose=True,
        allow_delegation=False,
        tools=[calculate_length, reverse_string], # <--- ARAÇLARI BURADA VER
        llm=llm
    )

    # 3. Görevi Tanımla
    # Görev araçların kullanılmasını gerektirir.
    
    task = Task(
        description="""Gizli bir kelimem var: 'Supercalifragilisticexpialidocious'.
        1. Uzunluğunu hesapla.
        2. Ters çevir.
        3. Bana uzunluğunu ve ters çevrilmiş versiyonunu söyle.
        """,
        expected_output="Uzunluk ve ters çevrilmiş dize.",
        agent=math_wizard
    )

    # 4. Ekip Oluştur
    crew = Crew(
        agents=[math_wizard],
        tasks=[task],
        verbose=True
    )

    # 5. Başlat
    print("\n🧙 Dize Büyücüsü Ekibi Başlatılıyor...")
    result = crew.kickoff()

    print("\n\n" + "="*50)
    print("✨ FİNAL SONUÇ")
    print("="*50)
    print(result)

if __name__ == "__main__":
    main()
