import os
from crewai import Agent, Task, Crew, Process
from langchain_ollama import ChatOllama

# =============================================================================
# 07 - Üretim Ekibi: İçerik Oluşturma Stüdyosu
# =============================================================================
#
# Bu, bir İçerik Oluşturma Stüdyosunun tam, üretime hazır bir örneğidir.
# Tam bir boru hattımız var:
# 1. Araştırmacı: Trend konuları bulur
# 2. Yazar: İçeriğin taslağını oluşturur
# 3. Editör: İçeriği cilalar
# 4. Sosyal Medya Yöneticisi: Tanıtım tweetleri oluşturur
#
# Bu, karmaşık bir sıralı iş akışını gösterir.
# =============================================================================

def main():
    llm = ChatOllama(
        model="qwen3:8b",
        base_url="http://localhost:11434",
        temperature=0.7
    )

    # --- AJANLAR ---
    
    researcher = Agent(
        role='Trend Araştırmacısı',
        goal='Yapay zekada şu anda en popüler konuları belirle',
        backstory="Twitter ve Reddit'te yaşayan veri odaklı bir araştırmacısın.",
        verbose=True,
        llm=llm
    )

    writer = Agent(
        role='İçerik Oluşturucu',
        goal='Yapay zeka trendleri hakkında ilgi çekici blog yazıları yaz',
        backstory="Karmaşık teknolojiyi herkese açıklayabilen yaratıcı bir yazarsın.",
        verbose=True,
        llm=llm
    )

    editor = Agent(
        role='Kıdemli Editör',
        goal='Tüm içeriğin mükemmel ve SEO-optimize olduğundan emin ol',
        backstory="Titiz bir editörsün. Pasif cümleden ve yazım hatalarından nefret ediyorsun.",
        verbose=True,
        llm=llm
    )

    social_manager = Agent(
        role='Sosyal Medya Yöneticisi',
        goal='İçeriği sosyal medyada tanıt',
        backstory="Viral pazarlama uzmanısın. Nasıl çekici başlıklar yazılacağını biliyorsun.",
        verbose=True,
        llm=llm
    )

    # --- GÖREVLER ---

    task1_research = Task(
        description="""Bu hafta için 'Üretken Yapay Zeka'da 3 trend konu bul.
        Her konu için kısa bir özet ve neden trend olduğunu sağla.""",
        expected_output="Özetlerle birlikte 3 trend konunun listesi.",
        agent=researcher
    )

    task2_write = Task(
        description="""Araştırmadan en ilginç konuyu seç.
        Bu konu hakkında 400 kelimelik bir blog yazısı yaz.
        Çekici bir başlık ve 3 ana bölüm ekle.""",
        expected_output="Markdown formatında tam 400 kelimelik bir blog yazısı.",
        agent=writer
    )

    task3_edit = Task(
        description="""Blog yazısını gözden geçir.
        1. Dilbilgisi hatalarını düzelt.
        2. Tonun profesyonel ama erişilebilir olduğundan emin ol.
        3. Sonuna bir 'Ana Çıkarımlar' bölümü ekle.""",
        expected_output="Final, cilalanmış blog yazısı.",
        agent=editor
    )

    task4_social = Task(
        description="""Bu blog yazısını tanıtmak için bir Twitter dizisi (3 tweet) oluştur.
        İlgili hashtag'ler ve bir harekete geçirici mesaj ekle.""",
        expected_output="Bir Twitter dizisi metni.",
        agent=social_manager
    )

    # --- EKİP ---

    content_crew = Crew(
        agents=[researcher, writer, editor, social_manager],
        tasks=[task1_research, task2_write, task3_edit, task4_social],
        verbose=True,
        process=Process.sequential
    )

    # --- BAŞLAT ---
    
    print("\n🎬 İçerik Oluşturma Stüdyosu Başlatılıyor...")
    result = content_crew.kickoff()

    print("\n\n" + "="*50)
    print("📦 FİNAL ÜRETİM ÇIKTISI")
    print("="*50)
    print(result)

if __name__ == "__main__":
    main()
