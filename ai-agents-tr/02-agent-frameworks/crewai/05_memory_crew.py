import os
from crewai import Agent, Task, Crew, Process
from langchain_ollama import ChatOllama

# =============================================================================
# 05 - Ekip Hafızası: Uzun Süreli Bağlam
# =============================================================================
#
# CrewAI, ajanların şunları yapmasını sağlayan yerleşik bir hafıza sistemine sahiptir:
# 1. Geçmiş yürütmeleri hatırlamak
# 2. Ajanlar arasında bilgi paylaşmak
# 3. Uzun görevler boyunca bağlamı korumak
#
# Bu genellikle 'embedder' yapılandırması gerektirir, ancak yerel kurulum için,
# CrewAI varsayılan olarak gömmeler (embeddings) için OpenAI kullanır.
# Yerel gömmeleri kullanmak için, 'memory=True' ve belirli bir gömücü yapılandırmamız gerekir.
#
# Bu basit örnek için, hafıza YAPILANDIRMASINI göstereceğiz.
# =============================================================================

def main():
    llm = ChatOllama(
        model="qwen3:8b",
        base_url="http://localhost:11434",
        temperature=0.7
    )

    # 1. Ajanları Tanımla
    # Hafıza, ajanların önceki bulguları hatırlamasına yardımcı olur.
    
    researcher = Agent(
        role='Derin Araştırmacı',
        goal='Karmaşık konuları araştır ve detayları hatırla',
        backstory="Fotografik hafızaya sahip bir araştırmacısın.",
        verbose=True,
        memory=True, # Bu ajan için hafızayı etkinleştir
        llm=llm
    )

    writer = Agent(
        role='Yazar',
        goal='Araştırmaya dayalı hikayeler yaz',
        backstory="Etkileyici anlatılar yazıyorsun.",
        verbose=True,
        memory=True,
        llm=llm
    )

    # 2. Görevleri Tanımla
    
    task1 = Task(
        description="Yapay zekada 'Transformer' mimarisinin tarihini araştır.",
        expected_output="Transformer tarihinin bir özeti.",
        agent=researcher
    )

    task2 = Task(
        description="Araştırmaya dayanarak 'Attention' (Dikkat) adlı bir robot hakkında kısa bir hikaye yaz.",
        expected_output="Kısa bir hikaye.",
        agent=writer
    )

    # 3. Hafızalı Ekip Oluştur
    # Hafızayı Ekip seviyesinde etkinleştiriyoruz.
    # Not: Gerçek bir yerel kurulumda, gömme modelini burada yapılandırırsınız.
    # Şimdilik, varsayılana güveneceğiz (veya API anahtarı yoksa devre dışı bırakacağız).
    
    # CrewAI ile yerel gömmeleri gerçekten kullanmak için genellikle şuna ihtiyacınız vardır:
    # embedder={
    #     "provider": "ollama",
    #     "config": {"model": "nomic-embed-text"}
    # }
    # Bu destek CrewAI sürümüne göre değişir.
    
    crew = Crew(
        agents=[researcher, writer],
        tasks=[task1, task2],
        verbose=True,
        memory=True # <--- HAFIZAYI ETKİNLEŞTİR
    )

    # 4. Başlat
    print("\n🧠 Hafıza Ekibi Başlatılıyor...")
    try:
        result = crew.kickoff()
        print("\n\n" + "="*50)
        print("📝 FİNAL SONUÇ")
        print("="*50)
        print(result)
    except Exception as e:
        print(f"\n[NOT] Hafıza özellikleri bir OpenAI API anahtarı veya belirli bir gömme yapılandırması gerektirebilir.")
        print(f"Hata: {e}")

if __name__ == "__main__":
    main()
