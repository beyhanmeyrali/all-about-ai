import os
from crewai import Agent, Task, Crew, Process
from langchain_ollama import ChatOllama

# =============================================================================
# 06 - Delegasyon: Ajanlar Ajanlara Yardım Ediyor
# =============================================================================
#
# CrewAI'ın en güçlü özelliklerinden biri DELEGASYONDUR.
# Bir ajan bir şeyi yapamayacağını fark ederse veya yardıma ihtiyaç duyarsa,
# bir alt görevi başka bir ajana delege edebilir!
#
# Bu, 'allow_delegation=True' ise otomatik olarak gerçekleşir.
# =============================================================================

def main():
    llm = ChatOllama(
        model="qwen3:8b",
        base_url="http://localhost:11434",
        temperature=0.7
    )

    # 1. Ajanları Tanımla
    
    # Yönetici delege edebilir
    manager = Agent(
        role='Proje Yöneticisi',
        goal='Bir bilmeceyi çözmek için ekibi koordine et',
        backstory="Akıllı bir yöneticisin. Her şeyi tek başına çözemeyeceğini biliyorsun.",
        verbose=True,
        allow_delegation=True, # <--- DELEGE EDEBİLİR
        llm=llm
    )

    # Uzman delege edemez (işi onlar yapar)
    riddle_solver = Agent(
        role='Bilmece Ustası',
        goal='Karmaşık bilmeceleri çöz',
        backstory="Yanal düşünme ve bilmecelerde uzmansın.",
        verbose=True,
        allow_delegation=False, # <--- ÇALIŞAN
        llm=llm
    )

    # 2. Görevi Tanımla
    # Görevi YÖNETİCİ'ye veriyoruz.
    # Yönetici, Bilmece Ustası'nın yardımına ihtiyaç duyduğunu anlamalı.
    
    task = Task(
        description="""Bu bilmeceyi çöz: 
        'Ağzım olmadan konuşurum ve kulağım olmadan duyarım. Vücudum yok ama rüzgarla canlanırım. Ben neyim?'
        
        Çözüldükten sonra, mantığı açıkla.
        """,
        expected_output="Bilmecenin cevabı ve açıklaması.",
        agent=manager # Yöneticiye atandı
    )

    # 3. Ekip Oluştur
    crew = Crew(
        agents=[manager, riddle_solver],
        tasks=[task],
        verbose=True
    )

    # 4. Başlat
    print("\n🤝 Delegasyon Ekibi Başlatılıyor...")
    result = crew.kickoff()

    print("\n\n" + "="*50)
    print("💡 FİNAL CEVAP")
    print("="*50)
    print(result)

if __name__ == "__main__":
    main()
