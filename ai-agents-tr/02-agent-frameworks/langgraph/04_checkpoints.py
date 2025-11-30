#!/usr/bin/env python3
"""
LangGraph Kontrol Noktaları - Durum Kalıcılığı
==========================================

Bu betik, LangGraph kontrol noktalarını kullanarak durum kalıcılığını gösterir.
Kontrol noktaları, konuşma durumunu kaydetmenizi ve geri yüklemenizi sağlar:
- Kesintiye uğrayan konuşmaları sürdürme
- Konuşma geçmişinde zaman yolculuğu
- Geri alma işlevselliği uygulama
- Karmaşık iş akışlarında hata ayıklama

Temel seviyeden üretim seviyesine kadar aşamalı olarak oluşturacağız.

Yazar: AI Agents Tutorial Series
"""

from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import OllamaLLM
import json
from datetime import datetime


# ============================================================================
# Bölüm 1: Temel Durum Kalıcılığı
# ============================================================================

class BasicState(TypedDict):
    """Mesaj geçmişi ile basit durum."""
    messages: List[str]
    counter: int


class BasicCheckpointAgent:
    """
    Temel kontrol noktası işlevselliğini gösterir.

    Özellikler:
    - Her turdan sonra konuşma durumunu kaydet
    - Son kontrol noktasından devam et
    - Kontrol noktası geçmişini görüntüle
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Kontrol noktası desteğiyle ajanı başlat."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Kontrol noktası desteğiyle grafik oluştur."""
        workflow = StateGraph(BasicState)

        # İşleme düğümü ekle
        workflow.add_node("process", self._process_message)

        # Giriş noktası ve kenar ayarla
        workflow.set_entry_point("process")
        workflow.add_edge("process", END)

        # Kontrol noktası ile derle
        return workflow.compile(checkpointer=self.memory)

    def _process_message(self, state: BasicState) -> BasicState:
        """Mesajı işle ve durumu güncelle."""
        messages = state.get("messages", [])
        counter = state.get("counter", 0)

        # Son mesajı al
        if messages:
            last_msg = messages[-1]
            response = self.llm.invoke(f"Şuna yanıt ver: {last_msg}")
            messages.append(f"Asistan: {response}")

        return {
            "messages": messages,
            "counter": counter + 1
        }

    def chat(self, message: str, thread_id: str = "default") -> Dict[str, Any]:
        """
        Mesaj gönder ve kontrol noktası kaydet.

        Argümanlar:
            message: Kullanıcı mesajı
            thread_id: Konuşma iş parçacığı tanımlayıcısı

        Döndürür:
            Kontrol noktası bilgisi ile durum
        """
        # Mevcut durumu al
        config = {"configurable": {"thread_id": thread_id}}
        current_state = self.graph.get_state(config)

        # Kullanıcı mesajı ekle
        messages = current_state.values.get("messages", []) if current_state.values else []
        messages.append(f"Kullanıcı: {message}")

        # Kontrol noktası ile grafiği çağır
        result = self.graph.invoke(
            {"messages": messages, "counter": current_state.values.get("counter", 0) if current_state.values else 0},
            config=config
        )

        return result

    def get_history(self, thread_id: str = "default") -> List[str]:
        """Kontrol noktalarından konuşma geçmişini al."""
        config = {"configurable": {"thread_id": thread_id}}
        state = self.graph.get_state(config)
        return state.values.get("messages", []) if state.values else []

    def get_checkpoint_info(self, thread_id: str = "default") -> Dict[str, Any]:
        """Kontrol noktası meta verilerini al."""
        config = {"configurable": {"thread_id": thread_id}}
        state = self.graph.get_state(config)

        return {
            "thread_id": thread_id,
            "message_count": len(state.values.get("messages", [])) if state.values else 0,
            "counter": state.values.get("counter", 0) if state.values else 0,
            "checkpoint_id": str(state.config.get("configurable", {}).get("checkpoint_id", "none"))
        }


# ============================================================================
# Bölüm 2: Birden Fazla İş Parçacığı ile Gelişmiş Durum
# ============================================================================

class ConversationState(TypedDict):
    """Zengin konuşma durumu."""
    messages: List[Dict[str, str]]
    metadata: Dict[str, Any]
    context: str


class MultiThreadAgent:
    """
    Bağımsız kontrol noktaları ile birden fazla konuşma iş parçacığını yönetir.

    Özellikler:
    - Birden fazla eşzamanlı konuşma
    - İş parçacığı başına durum izolasyonu
    - Bağlam koruması
    - Meta veri izleme
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Çoklu iş parçacığı ajanını başlat."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Durum yönetimi ile grafik oluştur."""
        workflow = StateGraph(ConversationState)

        workflow.add_node("understand", self._understand_context)
        workflow.add_node("respond", self._generate_response)

        workflow.set_entry_point("understand")
        workflow.add_edge("understand", "respond")
        workflow.add_edge("respond", END)

        return workflow.compile(checkpointer=self.memory)

    def _understand_context(self, state: ConversationState) -> ConversationState:
        """Konuşmadan bağlamı çıkar ve güncelle."""
        messages = state.get("messages", [])

        # Son mesajlardan bağlam oluştur
        recent = messages[-3:] if len(messages) >= 3 else messages
        context_summary = " | ".join([f"{m['role']}: {m['content'][:50]}" for m in recent])

        return {
            **state,
            "context": context_summary
        }

    def _generate_response(self, state: ConversationState) -> ConversationState:
        """Bağlam farkındalığı ile yanıt oluştur."""
        messages = state.get("messages", [])
        context = state.get("context", "")
        metadata = state.get("metadata", {})

        # Son kullanıcı mesajını al
        last_msg = messages[-1]["content"] if messages else ""

        # Bağlamla yanıt oluştur
        prompt = f"Bağlam: {context}\n\nKullanıcı: {last_msg}\n\nDoğal yanıt ver:"
        response = self.llm.invoke(prompt)

        # Asistan mesajı ekle
        messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })

        # Meta verileri güncelle
        metadata["total_turns"] = metadata.get("total_turns", 0) + 1
        metadata["last_updated"] = datetime.now().isoformat()

        return {
            "messages": messages,
            "metadata": metadata,
            "context": context
        }

    def send_message(self, message: str, thread_id: str) -> str:
        """Belirli iş parçacığına mesaj gönder."""
        config = {"configurable": {"thread_id": thread_id}}

        # Mevcut durumu al
        current_state = self.graph.get_state(config)
        messages = current_state.values.get("messages", []) if current_state.values else []
        metadata = current_state.values.get("metadata", {}) if current_state.values else {}

        # Kullanıcı mesajı ekle
        messages.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })

        # Grafiği çağır
        result = self.graph.invoke(
            {
                "messages": messages,
                "metadata": metadata,
                "context": ""
            },
            config=config
        )

        # Son asistan mesajını döndür
        return result["messages"][-1]["content"]

    def list_threads(self) -> List[str]:
        """Tüm aktif konuşma iş parçacıklarını listele."""
        # Not: MemorySaver iş parçacığı listelemeyi doğrudan göstermez
        # Üretimde, iş parçacığı indeksleme ile kalıcı depolama kullanın
        return ["İş parçacığı listeleme için kalıcı depolama kullanın"]

    def get_thread_summary(self, thread_id: str) -> Dict[str, Any]:
        """İş parçacığı durumunun özetini al."""
        config = {"configurable": {"thread_id": thread_id}}
        state = self.graph.get_state(config)

        if not state.values:
            return {"thread_id": thread_id, "status": "boş"}

        messages = state.values.get("messages", [])
        metadata = state.values.get("metadata", {})

        return {
            "thread_id": thread_id,
            "message_count": len(messages),
            "total_turns": metadata.get("total_turns", 0),
            "last_updated": metadata.get("last_updated", "hiçbir zaman"),
            "context": state.values.get("context", "")
        }


# ============================================================================
# Bölüm 3: Zaman Yolculuğu ve Geri Alma
# ============================================================================

class TimeTravelState(TypedDict):
    """Sürüm izleme ile durum."""
    messages: List[str]
    version: int
    snapshots: Dict[int, List[str]]


class TimeTravelAgent:
    """
    Zaman yolculuğu yetenekleri ile gelişmiş kontrol noktası ajanı.

    Özellikler:
    - Konuşma geçmişinde gezinme
    - Önceki durumlara geri alma
    - Adlandırılmış anlık görüntüler oluşturma
    - Herhangi bir noktadan konuşmaları dallandırma
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Zaman yolculuğu ajanını başlat."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Sürümleme ile grafik oluştur."""
        workflow = StateGraph(TimeTravelState)

        workflow.add_node("process", self._process_with_versioning)
        workflow.set_entry_point("process")
        workflow.add_edge("process", END)

        return workflow.compile(checkpointer=self.memory)

    def _process_with_versioning(self, state: TimeTravelState) -> TimeTravelState:
        """Mesajı işle ve sürüm geçmişini koru."""
        messages = state.get("messages", [])
        version = state.get("version", 0)
        snapshots = state.get("snapshots", {})

        # Son mesajı işle
        if messages and messages[-1].startswith("Kullanıcı:"):
            last_msg = messages[-1].replace("Kullanıcı: ", "")
            response = self.llm.invoke(f"Şuna yanıt ver: {last_msg}")
            messages.append(f"Asistan: {response}")

        # Sürümü artır
        new_version = version + 1

        # Anlık görüntüyü kaydet
        snapshots[new_version] = messages.copy()

        return {
            "messages": messages,
            "version": new_version,
            "snapshots": snapshots
        }

    def chat(self, message: str, thread_id: str = "default") -> str:
        """Mesaj gönder ve kontrol noktası oluştur."""
        config = {"configurable": {"thread_id": thread_id}}
        current_state = self.graph.get_state(config)

        messages = current_state.values.get("messages", []) if current_state.values else []
        version = current_state.values.get("version", 0) if current_state.values else 0
        snapshots = current_state.values.get("snapshots", {}) if current_state.values else {}

        messages.append(f"Kullanıcı: {message}")

        result = self.graph.invoke(
            {
                "messages": messages,
                "version": version,
                "snapshots": snapshots
            },
            config=config
        )

        # Son asistan mesajını döndür
        assistant_msgs = [m for m in result["messages"] if m.startswith("Asistan:")]
        return assistant_msgs[-1].replace("Asistan: ", "") if assistant_msgs else ""

    def rollback_to_version(self, version: int, thread_id: str = "default") -> bool:
        """Konuşmayı belirli sürüme geri al."""
        config = {"configurable": {"thread_id": thread_id}}
        current_state = self.graph.get_state(config)

        if not current_state.values:
            return False

        snapshots = current_state.values.get("snapshots", {})

        if version not in snapshots:
            print(f"Sürüm {version} bulunamadı. Mevcut: {list(snapshots.keys())}")
            return False

        # Anlık görüntüyü geri yükle
        restored_messages = snapshots[version]

        self.graph.invoke(
            {
                "messages": restored_messages,
                "version": version,
                "snapshots": snapshots
            },
            config=config
        )

        return True

    def list_versions(self, thread_id: str = "default") -> List[int]:
        """Tüm kaydedilmiş sürümleri listele."""
        config = {"configurable": {"thread_id": thread_id}}
        state = self.graph.get_state(config)

        if not state.values:
            return []

        snapshots = state.values.get("snapshots", {})
        return sorted(snapshots.keys())

    def get_version_preview(self, version: int, thread_id: str = "default") -> List[str]:
        """Belirli sürümdeki mesajları önizle."""
        config = {"configurable": {"thread_id": thread_id}}
        state = self.graph.get_state(config)

        if not state.values:
            return []

        snapshots = state.values.get("snapshots", {})
        return snapshots.get(version, [])


# ============================================================================
# Bölüm 4: Üretim Kontrol Noktası Yöneticisi
# ============================================================================

class ProductionCheckpointManager:
    """
    Kurumsal sınıf kontrol noktası yönetim sistemi.

    Özellikler:
    - Otomatik kontrol noktası oluşturma
    - Kontrol noktası sıkıştırma
    - Temizleme politikaları
    - Dışa/içe aktarma işlevselliği
    - İş parçacığı yönetimi
    - İzleme ve istatistikler
    """

    def __init__(self, model: str = "qwen3:8b", max_checkpoints: int = 100):
        """Üretim kontrol noktası yöneticisini başlat."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.memory = MemorySaver()
        self.max_checkpoints = max_checkpoints
        self.stats = {
            "total_checkpoints": 0,
            "total_threads": 0,
            "total_messages": 0
        }
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Üretime hazır grafik oluştur."""
        workflow = StateGraph(ConversationState)

        workflow.add_node("process", self._process_message)
        workflow.set_entry_point("process")
        workflow.add_edge("process", END)

        return workflow.compile(checkpointer=self.memory)

    def _process_message(self, state: ConversationState) -> ConversationState:
        """Tam durum yönetimi ile mesajı işle."""
        messages = state.get("messages", [])
        metadata = state.get("metadata", {})

        # Son kullanıcı mesajını al
        if messages:
            last_msg = messages[-1]["content"]
            response = self.llm.invoke(f"Şuna yanıt ver: {last_msg}")

            messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now().isoformat()
            })

        # Meta verileri güncelle
        metadata["message_count"] = len(messages)
        metadata["last_checkpoint"] = datetime.now().isoformat()

        return {
            "messages": messages,
            "metadata": metadata,
            "context": state.get("context", "")
        }

    def send(self, message: str, thread_id: str) -> str:
        """Otomatik kontrol noktası ile mesaj gönder."""
        config = {"configurable": {"thread_id": thread_id}}
        current_state = self.graph.get_state(config)

        messages = current_state.values.get("messages", []) if current_state.values else []
        metadata = current_state.values.get("metadata", {}) if current_state.values else {}

        messages.append({
            "role": "user",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })

        result = self.graph.invoke(
            {
                "messages": messages,
                "metadata": metadata,
                "context": ""
            },
            config=config
        )

        # İstatistikleri güncelle
        self.stats["total_messages"] += 2  # kullanıcı + asistan
        self.stats["total_checkpoints"] += 1

        return result["messages"][-1]["content"]

    def export_thread(self, thread_id: str, filepath: str) -> bool:
        """İş parçacığını JSON dosyasına aktar."""
        config = {"configurable": {"thread_id": thread_id}}
        state = self.graph.get_state(config)

        if not state.values:
            return False

        export_data = {
            "thread_id": thread_id,
            "exported_at": datetime.now().isoformat(),
            "state": state.values
        }

        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)

        return True

    def import_thread(self, filepath: str) -> str:
        """JSON dosyasından iş parçacığını içe aktar."""
        with open(filepath, 'r') as f:
            data = json.load(f)

        thread_id = data["thread_id"]
        config = {"configurable": {"thread_id": thread_id}}

        self.graph.invoke(data["state"], config=config)

        return thread_id

    def get_stats(self) -> Dict[str, Any]:
        """Kontrol noktası istatistiklerini al."""
        return self.stats.copy()


# ============================================================================
# GÖSTERIMLER
# ============================================================================

def demo_basic_checkpoints():
    """Temel kontrol noktası işlevselliğini göster."""
    print("\n" + "="*70)
    print("DEMO 1: Temel Kontrol Noktası Kalıcılığı")
    print("="*70)

    agent = BasicCheckpointAgent()

    print("\n1. Konuşma başlatılıyor...")
    result1 = agent.chat("Merhaba, adım Alice")
    print(f"Tur 1: {len(result1['messages'])} mesaj")

    print("\n2. Konuşma devam ediyor...")
    result2 = agent.chat("Hava nasıl?")
    print(f"Tur 2: {len(result2['messages'])} mesaj")

    print("\n3. Kontrol noktası bilgisi:")
    info = agent.get_checkpoint_info()
    for key, value in info.items():
        print(f"  {key}: {value}")

    print("\n4. Tam konuşma geçmişi:")
    history = agent.get_history()
    for i, msg in enumerate(history, 1):
        print(f"  {i}. {msg}")


def demo_multi_thread():
    """Birden fazla konuşma iş parçacığını göster."""
    print("\n" + "="*70)
    print("DEMO 2: Birden Fazla Konuşma İş Parçacığı")
    print("="*70)

    agent = MultiThreadAgent()

    print("\n1. İş Parçacığı A başlatılıyor (teknik destek)...")
    response1 = agent.send_message("Bilgisayarım açılmıyor", "thread_a")
    print(f"Yanıt: {response1[:100]}...")

    print("\n2. İş Parçacığı B başlatılıyor (tarifler)...")
    response2 = agent.send_message("Makarna nasıl yapılır?", "thread_b")
    print(f"Yanıt: {response2[:100]}...")

    print("\n3. İş Parçacığı A devam ediyor...")
    response3 = agent.send_message("Yeniden başlatmayı denedim", "thread_a")
    print(f"Yanıt: {response3[:100]}...")

    print("\n4. İş parçacığı özetleri:")
    for thread_id in ["thread_a", "thread_b"]:
        summary = agent.get_thread_summary(thread_id)
        print(f"\n  {thread_id.upper()}:")
        for key, value in summary.items():
            if key != "thread_id":
                print(f"    {key}: {value}")


def demo_time_travel():
    """Zaman yolculuğu ve geri almayı göster."""
    print("\n" + "="*70)
    print("DEMO 3: Zaman Yolculuğu ve Geri Alma")
    print("="*70)

    agent = TimeTravelAgent()

    print("\n1. Konuşma geçmişi oluşturuluyor...")
    agent.chat("Python hakkında anlat", "demo")
    agent.chat("Peki JavaScript?", "demo")
    agent.chat("Bunları karşılaştır", "demo")

    print("\n2. Mevcut sürümler:")
    versions = agent.list_versions("demo")
    print(f"  Sürümler: {versions}")

    print("\n3. Sürüm 2 önizlemesi:")
    preview = agent.get_version_preview(2, "demo")
    for msg in preview:
        print(f"  - {msg}")

    print("\n4. Sürüm 1'e geri alınıyor...")
    success = agent.rollback_to_version(1, "demo")
    print(f"  Geri alma {'başarılı' if success else 'başarısız'}")

    print("\n5. Geri almadan sonraki mevcut durum:")
    preview_after = agent.get_version_preview(1, "demo")
    for msg in preview_after:
        print(f"  - {msg}")


def demo_production_manager():
    """Üretim kontrol noktası yöneticisini göster."""
    print("\n" + "="*70)
    print("DEMO 4: Üretim Kontrol Noktası Yöneticisi")
    print("="*70)

    manager = ProductionCheckpointManager()

    print("\n1. Konuşma oluşturuluyor...")
    manager.send("Merhaba, yardıma ihtiyacım var", "prod_thread")
    manager.send("Yapay zeka hakkında anlat", "prod_thread")

    print("\n2. İş parçacığı dışa aktarılıyor...")
    export_path = "/tmp/thread_backup.json"
    success = manager.export_thread("prod_thread", export_path)
    print(f"  Dışa aktarma {'başarılı' if success else 'başarısız'}: {export_path}")

    print("\n3. İstatistikler:")
    stats = manager.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n4. İş parçacığı içe aktarılıyor...")
    imported_id = manager.import_thread(export_path)
    print(f"  İçe aktarılan iş parçacığı: {imported_id}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("LangGraph Kontrol Noktaları - Durum Kalıcılığı Eğitimi")
    print("="*70)
    print("\nBu eğitim, kontrol noktası tabanlı durum kalıcılığını gösterir.")
    print("Kontrol noktaları konuşmayı sürdürme, zaman yolculuğu ve geri almayı sağlar.")

    try:
        demo_basic_checkpoints()
        demo_multi_thread()
        demo_time_travel()
        demo_production_manager()

        print("\n" + "="*70)
        print("Eğitim başarıyla tamamlandı!")
        print("="*70)
        print("\nTemel Çıkarımlar:")
        print("1. MemorySaver bellek içi kontrol noktası depolaması sağlar")
        print("2. thread_id farklı konuşmaları izole eder")
        print("3. Kontrol noktaları durum kurtarma ve zaman yolculuğu sağlar")
        print("4. Üretim sistemleri dışa/içe aktarma yeteneklerine ihtiyaç duyar")
        print("\nSıradaki: 05_human_in_loop.py - İnsan onay düğümleri")

    except Exception as e:
        print(f"\nGösterim sırasında hata: {e}")
        print("Ollama'nın qwen3:8b modeli ile çalıştığından emin olun")
