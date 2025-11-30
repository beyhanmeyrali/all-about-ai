import os
from crewai import Agent, Task, Crew, Process
from langchain_ollama import ChatOllama

# =============================================================================
# 01 - Basit Ekip: Piyasa Analiz Takımı
# =============================================================================
#
# Bu örnek pratik bir kullanım durumunu gösterir: Piyasa Analizi.
# Birlikte çalışan iki ajanımız var:
# 1. Piyasa Analisti: Trendleri belirler
# 2. Yatırım Danışmanı: Bu trendlere dayanarak tavsiye verir
#
# Kavramlar:
# - Bağlam aktarımı (Görev 2, Görev 1'in çıktısını kullanır)
# - Uzmanlaşmış roller
# =============================================================================

def main():
    llm = ChatOllama(
        model="qwen3:8b",
        base_url="http://localhost:11434",
        temperature=0.7
    )

    # 1. Ajanları Tanımla
    analyst = Agent(
        role='Piyasa Analisti',
        goal='Yapay zeka piyasasının mevcut durumunu analiz et',
        backstory="""20 yıllık deneyime sahip kıdemli bir piyasa analistisin.
        Teknoloji sektörü ve yapay zeka trendlerinde uzmanlaşıyorsun.
        Özlü ve veri odaklısın.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    advisor = Agent(
        role='Yatırım Danışmanı',
        goal='Piyasa analizine dayanarak yatırım stratejileri öner',
        backstory="""Müşterilerin servet oluşturmasına yardımcı olan bir finansal danışmansın.
        Karmaşık piyasa analizlerini alıp uygulanabilir tavsiyelere dönüştürüyorsun.
        Yapay zeka konusunda temkinli ama iyimsersin.""",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # 2. Görevleri Tanımla
    # Görev 1: Analiz
    analysis_task = Task(
        description="""2025 yılı için Yapay Zeka alanındaki mevcut trendleri analiz et.
        3 temel büyüme alanı ve 2 potansiyel risk belirle.
        Mevcut yılın 2025 olduğunu varsay.""",
        expected_output="3 büyüme alanı ve 2 risk içeren kısa bir piyasa analizi raporu.",
        agent=analyst
    )

    # Görev 2: Strateji
    # Not: Sıralı süreçte, bu görev önceki görevlerden bağlamı otomatik olarak alır
    strategy_task = Task(
        description="""Sağlanan piyasa analizine dayanarak, 10.000 doları olan 
        bireysel bir yatırımcı için bir yatırım stratejisi öner.
        Büyüme alanlarına göre portföy yüzdelerinin nasıl bölüneceğini öner.""",
        expected_output="Portföy tahsis yüzdeleriyle net bir yatırım stratejisi.",
        agent=advisor,
        context=[analysis_task] # Bağımlılığı açıkça belirtme (sıralı süreçte isteğe bağlıdır, ancak iyi bir uygulamadır)
    )

    # 3. Ekip Oluştur
    financial_crew = Crew(
        agents=[analyst, advisor],
        tasks=[analysis_task, strategy_task],
        verbose=True,
        process=Process.sequential
    )

    # 4. Çalıştır
    print("\n💼 Piyasa Analiz Ekibi Başlatılıyor...")
    result = financial_crew.kickoff()

    print("\n\n" + "="*50)
    print("💰 FİNAL YATIRIM STRATEJİSİ")
    print("="*50)
    print(result)

if __name__ == "__main__":
    main()
