#!/usr/bin/env python3
"""
Örnek 03: Hafızalı Zincirler - Konuşma Yapay Zekası (Modern LCEL)
=================================================================

Konuşma hafızasında ustalaşın - ajanınızın hatırlamasını sağlayın!

Ne öğreneceksiniz:
- Hafıza neden ajanlar için kritiktir
- RunnableWithMessageHistory (Modern LCEL hafızası)
- Sohbet geçmişini yönetme
- Üretim hafıza desenleri

Bu, gerçek konuşma ajanları oluşturmak için KRİTİKTİR!

Yazar: Beyhan MEYRALI
"""

from typing import List, Dict, Any
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

# Sohbet geçmişleri için global depo (demo için bellek içi)
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """Bir oturum için sohbet geçmişini al veya oluştur."""
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


class MemoryBasicsAgent:
    """
    LCEL kullanarak temel hafıza kavramlarını göster.
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Ajanı başlat."""
        print(f"\n[BAŞLAT] {model} ile ajan oluşturuluyor...")
        self.llm = OllamaLLM(model=model, temperature=0.7)

    def demo_without_memory(self):
        """Hafıza OLMADAN ne olduğunu göster."""
        print("\n" + "="*70)
        print("DEMO 1: Hafızası OLMAYAN Ajan (Japon Balığı Beyni)")
        print("="*70)

        # Hafızasız basit zincir
        prompt = ChatPromptTemplate.from_template("Bu soruyu yanıtla: {question}")
        chain = prompt | self.llm | StrOutputParser()

        # Sorular sor
        print("\n[Kullanıcı]: Adım Alice")
        response1 = chain.invoke({"question": "Adım Alice. Sadece 'Tanıştığımıza memnun oldum' de"})
        print(f"[Ajan]: {response1}")

        print("\n[Kullanıcı]: Adım ne?")
        response2 = chain.invoke({"question": "Adım ne?"})
        print(f"[Ajan]: {response2}")

        print("\n❌ Ajan unuttu! Önceki konuşmanın hafızası yok.")

    def demo_with_memory(self):
        """Hafıza İLE ne olduğunu göster (LCEL)."""
        print("\n" + "="*70)
        print("DEMO 2: Hafızalı Ajan (Her Şeyi Hatırlıyor)")
        print("="*70)

        # 1. Geçmiş yer tutucusu ile prompt oluştur
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Yardımsever bir asistansın."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),
        ])

        # 2. Zincir oluştur
        chain = prompt | self.llm | StrOutputParser()

        # 3. Mesaj geçmişi ile sar
        conversation = RunnableWithMessageHistory(
            chain,
            get_session_history,
            input_messages_key="question",
            history_messages_key="history",
        )

        # session_id ile sorular sor
        session_id = "demo_session"
        
        print("\n[Kullanıcı]: Adım Alice")
        response1 = conversation.invoke(
            {"question": "Adım Alice"},
            config={"configurable": {"session_id": session_id}}
        )
        print(f"[Ajan]: {response1}")

        print("\n[Kullanıcı]: Adım ne?")
        response2 = conversation.invoke(
            {"question": "Adım ne?"},
            config={"configurable": {"session_id": session_id}}
        )
        print(f"[Ajan]: {response2}")

        print("\n✅ Ajan hatırlıyor! Hafıza çalışıyor.")

        # Hafıza içeriğini göster
        print("\n[HAFIZA İÇERİĞİ]:")
        print(store[session_id].messages)


class ConversationalAgent:
    """
    Hafızalı üretime hazır konuşma ajanı.
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Konuşma ajanını başlat."""
        print(f"\n[BAŞLAT] Konuşma Ajanı Oluşturuluyor...")
        self.llm = OllamaLLM(model=model, temperature=0.7)
        
        # Zinciri kur
        prompt = ChatPromptTemplate.from_messages([
            ("system", "Yardımsever bir yapay zeka asistanısın."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        
        self.conversation = RunnableWithMessageHistory(
            chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )

    def chat(self, user_input: str, session_id: str = "default") -> str:
        """Bir mesaj gönder ve yanıt al."""
        print(f"\n[Kullanıcı]: {user_input}")

        try:
            response = self.conversation.invoke(
                {"input": user_input},
                config={"configurable": {"session_id": session_id}}
            )
            print(f"[Ajan]: {response}")
            return response

        except Exception as e:
            error = f"Hata: {str(e)}"
            print(f"[HATA]: {error}")
            return error

    def show_memory(self, session_id: str = "default"):
        """Mevcut hafıza içeriğini göster."""
        print("\n" + "-"*70)
        print(f"HAFIZA İÇERİĞİ ({session_id}):")
        print("-"*70)
        if session_id in store:
            for msg in store[session_id].messages:
                print(f"{msg.type}: {msg.content}")
        else:
            print("Boş hafıza")
        print("-"*70)

    def clear_memory(self, session_id: str = "default"):
        """Konuşma hafızasını temizle."""
        if session_id in store:
            store[session_id].clear()
        print(f"\n[SİSTEM]: {session_id} için hafıza temizlendi!")


def demo_real_conversation():
    """Gerçekçi konuşmayı göster."""
    print("\n" + "="*70)
    print("DEMO 3: Gerçekçi Konuşma Akışı")
    print("="*70)

    agent = ConversationalAgent()
    session_id = "user_123"

    # Gerçekçi konuşma
    conversation = [
        "Merhaba! Bir Python projesi üzerinde çalışıyorum",
        "Bir CSV dosyası okumam gerekiyor",
        "Dosyada isimler ve yaşlar var",
        "Bunu bir pandas DataFrame'e nasıl yüklerim?",
        "Dosyada eksik değerler varsa ne olur?",
        "Bunları nasıl ele alacağımı gösterebilir misin?",
        "Teşekkürler! Bir şey daha - orijinal sorum neydi?",
    ]

    for msg in conversation:
        agent.chat(msg, session_id=session_id)

    print("\n💡 Ajanın nasıl:")
    print("  1. Bağlamı hatırladığına dikkat edin (Python, CSV, pandas)")
    print("  2. Önceki cevaplar üzerine inşa ediyor")
    print("  3. Orijinal soruyu hatırlayabiliyor")


def main():
    """Ana giriş noktası."""
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║         Örnek 03: Hafızalı Zincirler (Modern LCEL)               ║
    ║                                                                   ║
    ║  Bu şunları gösterir:                                            ║
    ║  • Hafıza neden ajanlar için kritiktir                          ║
    ║  • RunnableWithMessageHistory (Modern yol)                      ║
    ║  • ChatMessageHistory (Mesajları saklama)                       ║
    ║  • Oturumları yönetme                                           ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Demoları çalıştır
    basics = MemoryBasicsAgent()
    basics.demo_without_memory()
    basics.demo_with_memory()

    demo_real_conversation()

    # Özet
    print("\n" + "="*70)
    print("✅ TAMAMLANDI!")
    print("="*70)
    print("\n🎓 Ne öğrendiniz:")
    print("  1. Ajanların neden hafızaya ihtiyacı var")
    print("  2. RunnableWithMessageHistory nasıl kullanılır")
    print("  3. Oturum ID'leri nasıl yönetilir")
    print("  4. Sohbet geçmişi nasıl incelenir")
    print("\n➡️  Sıradaki: python 04_tools_integration.py")
    print("="*70)


if __name__ == "__main__":
    main()
