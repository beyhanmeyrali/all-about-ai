import os
from crewai import Agent, Task, Crew, Process
from langchain_ollama import ChatOllama

# =============================================================================
# 03 - Hiyerarşik Ekip: Yönetici & Çalışanlar
# =============================================================================
#
# Hiyerarşik bir süreçte, bir "Yönetici" ajan ekibi otomatik olarak koordine eder.
# Yönetici:
# 1. Üst düzey hedefi alır
# 2. Alt görevlere böler
# 3. Görevleri en uygun ajanlara delege eder
# 4. Sonuçları gözden geçirir ve birleştirir
#
# Not: Bu bir "manager_llm" gerektirir (ajan llm ile aynı olabilir).
# =============================================================================

def main():
    llm = ChatOllama(
        model="qwen3:8b",
        base_url="http://localhost:11434",
        temperature=0.7
    )

    # 1. Çalışanları Tanımla (Burada Yönetici yok - CrewAI bir tane oluşturur!)
    # Sadece uzmanları tanımlıyoruz.
    
    researcher = Agent(
        role='Kıdemli Araştırmacı',
        goal='Verilen konularda derinlemesine araştırma yap',
        backstory="Uzman bir araştırmacısın. Gerçekleri bulur ve kaynakları doğrularsın.",
        verbose=True,
        allow_delegation=False, # Çalışanlar genellikle bu kurulumda delegasyon yapmaz
        llm=llm
    )

    writer = Agent(
        role='Kıdemli Yazar',
        goal='Araştırmaya dayalı yüksek kaliteli içerik yaz',
        backstory="Yetenekli bir yazarsın. İlgi çekici ve net içerikler oluşturursun.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    editor = Agent(
        role='Baş Editör',
        goal='İçerik kalitesini ve tutarlılığını sağla',
        backstory="Sıkı bir editörsün. Ton, stil ve doğruluğu kontrol edersin.",
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    # 2. Üst Düzey Görevi Tanımla
    # Hiyerarşik modda, koordinasyon gerektiren karmaşık bir görev veririz.
    
    project_task = Task(
        description="""'Yerel LLM'lerin Geleceği' hakkında kapsamlı bir blog yazısı üret.
        1. Yerel LLM'lerin mevcut durumunu araştır (Ollama, Llama 3 vb.).
        2. Taslak bir blog yazısı yaz (yaklaşık 500 kelime).
        3. Yazıyı netlik ve profesyonel ton için düzenle.
        """,
        expected_output="Cilalanmış, yayınlanmaya hazır bir blog yazısı.",
        # Belirli bir ajan atamıyoruz! Yönetici karar verecek.
    )

    # 3. Hiyerarşik Ekibi Oluştur
    crew = Crew(
        agents=[researcher, writer, editor],
        tasks=[project_task],
        verbose=True,
        process=Process.hierarchical, # <--- ANAHTAR DEĞİŞİKLİK
        manager_llm=llm # Yöneticinin beyni
    )

    # 4. Başlat
    print("\n👑 Hiyerarşik Ekip Başlatılıyor...")
    result = crew.kickoff()

    print("\n\n" + "="*50)
    print("📄 FİNAL BLOG YAZISI")
    print("="*50)
    print(result)

if __name__ == "__main__":
    main()
