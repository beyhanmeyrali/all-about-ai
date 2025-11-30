import os
from crewai import Agent, Task, Crew, Process
from langchain_ollama import ChatOllama

# =============================================================================
# 00 - CrewAI Temelleri: Çoklu Ajan Sistemlerinin "Merhaba Dünya"sı
# =============================================================================
#
# Bu betik, CrewAI'ın temel yapı taşlarını gösterir:
# 1. Ajanlar: Çalışanlar
# 2. Görevler: Yapılacak iş
# 3. Ekip: Takım orkestrasyonu
#
# Tüm ajanlar için yerel bir Ollama modeli (qwen3:8b) kullanacağız.
# =============================================================================

def main():
    # 1. Yerel LLM'i Kurun
    # CrewAI, LangChain'in LLM arayüzünü kullanır
    llm = ChatOllama(
        model="qwen3:8b",
        base_url="http://localhost:11434",
        temperature=0.7
    )

    print("\n🤖 CrewAI Yerel LLM (qwen3:8b) ile başlatılıyor...")

    # 2. Ajanları Tanımlayın
    # Ajanlar takım üyeleridir. Bir role, hedefe ve arka plana ihtiyaçları vardır.
    
    # Ajan 1: Araştırmacı
    researcher = Agent(
        role='Teknoloji Araştırmacısı',
        goal='Yapay Zeka Ajanlarının temellerini anla',
        backstory="""Karmaşık kavramları basit terimlerle açıklamayı seven 
        hevesli bir bilgisayar bilimi öğrencisisin. 
        Şu anda Yapay Zeka Ajanları hakkında öğreniyorsun.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # Ajan 2: Yazar
    writer = Agent(
        role='Teknoloji Yazarı',
        goal='Yapay Zeka Ajanları hakkında kısa bir tweet yaz',
        backstory="""Teknoloji alanında bir sosyal medya fenomenisin. 
        Teknik kavramları alıp emojilerle ilgi çekici, 
        viral tweetlere dönüştürüyorsun.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # 3. Görevleri Tanımlayın
    # Görevler, ajanlar için belirli atamalardır.
    
    task1 = Task(
        description="""Bir 'Yapay Zeka Ajanı'nın ne olduğunu araştır. 
        Standart bir LLM (sohbet botu) ile bir Ajan arasındaki farka odaklan.
        3 temel farktan oluşan maddeli bir liste sağla.""",
        expected_output="LLM'ler ve Ajanlar arasındaki 3 temel farkın listesi.",
        agent=researcher
    )

    task2 = Task(
        description="""Sağlanan araştırmayı kullanarak, bir Yapay Zeka Ajanının ne olduğunu açıklayan 
        ilgi çekici bir tweet (maksimum 280 karakter) yaz. 
        Emojiler kullan ve kulağa heyecan verici gelmesini sağla!""",
        expected_output="Tek bir tweet dizesi.",
        agent=writer
    )

    # 4. Ekibi Tanımlayın
    # Ekip, ajanları ve görevleri koordine eder.
    
    crew = Crew(
        agents=[researcher, writer],
        tasks=[task1, task2],
        verbose=True,  # İç koordinasyonu gör
        process=Process.sequential  # Görevler birbiri ardına yürütülür
    )

    # 5. Başlat!
    print("\n🚀 Ekip Başlatılıyor...")
    result = crew.kickoff()

    print("\n\n" + "="*50)
    print("✅ FİNAL SONUÇ")
    print("="*50)
    print(result)

if __name__ == "__main__":
    main()
