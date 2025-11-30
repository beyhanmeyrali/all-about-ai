#!/usr/bin/env python3
"""
LangGraph Akış Olayları - Gerçek Zamanlı Güncellemeler
===================================================

Bu betik, gerçek zamanlı güncellemeler için LangGraph'ta olay akışını gösterir.
Akış şunları sağlar:
- Canlı ilerleme takibi
- Artımlı sonuç teslimi
- Daha iyi kullanıcı deneyimi
- Gerçek zamanlı hata ayıklama

Temel akıştan üretim sınıfı olay sistemlerine kadar oluşturacağız.

Yazar: AI Agents Tutorial Series
"""

from typing import TypedDict, Annotated, List, Dict, Any, Iterator, AsyncIterator
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import OllamaLLM
import operator
from datetime import datetime
import time
import json


# ============================================================================
# Bölüm 1: Temel Olay Akışı
# ============================================================================

class StreamState(TypedDict):
    """Akış demoları için durum."""
    input: str
    output: str
    events: List[str]


class BasicStreamingAgent:
    """
    Temel olay akışını gösterir.

    Özellikler:
    - Düğüm yürütme olaylarını akışla
    - İşleme adımlarını gerçek zamanlı izle
    - Durum değişikliklerini izle
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Akış ajanını başlat."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Akış desteğiyle grafik oluştur."""
        workflow = StateGraph(StreamState)

        # Düğümleri ekle
        workflow.add_node("step1", self._process_step1)
        workflow.add_node("step2", self._process_step2)
        workflow.add_node("step3", self._process_step3)

        # Akış
        workflow.set_entry_point("step1")
        workflow.add_edge("step1", "step2")
        workflow.add_edge("step2", "step3")
        workflow.add_edge("step3", END)

        return workflow.compile()

    def _process_step1(self, state: StreamState) -> StreamState:
        """Birinci işleme adımı."""
        events = state.get("events", [])
        events.append(f"[{datetime.now().strftime('%H:%M:%S')}] Adım 1: Başladı")

        # İşi simüle et
        time.sleep(0.5)

        events.append(f"[{datetime.now().strftime('%H:%M:%S')}] Adım 1: Tamamlandı")

        return {
            **state,
            "events": events
        }

    def _process_step2(self, state: StreamState) -> StreamState:
        """İkinci işleme adımı."""
        events = state.get("events", [])
        events.append(f"[{datetime.now().strftime('%H:%M:%S')}] Adım 2: Başladı")

        # LLM ile işle
        input_data = state.get("input", "")
        result = self.llm.invoke(f"Bunu kısaca işle: {input_data}")

        events.append(f"[{datetime.now().strftime('%H:%M:%S')}] Adım 2: LLM çağrısı tamamlandı")

        return {
            **state,
            "output": result,
            "events": events
        }

    def _process_step3(self, state: StreamState) -> StreamState:
        """Üçüncü işleme adımı."""
        events = state.get("events", [])
        events.append(f"[{datetime.now().strftime('%H:%M:%S')}] Adım 3: Başladı")

        time.sleep(0.3)

        events.append(f"[{datetime.now().strftime('%H:%M:%S')}] Adım 3: Tamamlandı")

        return {
            **state,
            "events": events
        }

    def stream_process(self, input_data: str) -> Iterator[Dict[str, Any]]:
        """Olay akışı ile işle."""
        # Grafik yürütmesinden olayları akışla
        for event in self.graph.stream({
            "input": input_data,
            "output": "",
            "events": []
        }):
            yield event

    def run(self, input_data: str) -> List[str]:
        """Çalıştır ve tüm olayları topla."""
        result = self.graph.invoke({
            "input": input_data,
            "output": "",
            "events": []
        })

        return result.get("events", [])


# ============================================================================
# Bölüm 2: İlerleme Takibi
# ============================================================================

class ProgressState(TypedDict):
    """İlerleme takibi ile durum."""
    tasks: List[str]
    completed: List[str]
    current_task: str
    progress_percent: float


class ProgressTrackingAgent:
    """
    Akış ile ilerleme takibini gösterir.

    Özellikler:
    - Gerçek zamanlı ilerleme güncellemeleri
    - Yüzde tamamlama takibi
    - Görev durumu izleme
    """

    def __init__(self, model: str = "qwen3:8b"):
        """İlerleme takibi ajanını başlat."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """İlerleme takibi ile grafik oluştur."""
        workflow = StateGraph(ProgressState)

        workflow.add_node("initialize", self._initialize_tasks)
        workflow.add_node("process", self._process_task)
        workflow.add_node("update_progress", self._update_progress)

        workflow.set_entry_point("initialize")
        workflow.add_edge("initialize", "process")
        workflow.add_edge("process", "update_progress")

        # Daha fazla görev varsa geri döngü
        workflow.add_conditional_edges(
            "update_progress",
            self._should_continue,
            {
                "continue": "process",
                "done": END
            }
        )

        return workflow.compile()

    def _initialize_tasks(self, state: ProgressState) -> ProgressState:
        """Görev listesini başlat."""
        tasks = state.get("tasks", [])

        return {
            **state,
            "tasks": tasks,
            "completed": [],
            "current_task": "",
            "progress_percent": 0.0
        }

    def _process_task(self, state: ProgressState) -> ProgressState:
        """Sonraki görevi işle."""
        tasks = state.get("tasks", [])
        completed = state.get("completed", [])

        # Sonraki görevi al
        remaining = [t for t in tasks if t not in completed]

        if remaining:
            current = remaining[0]

            # İşlemeyi simüle et
            time.sleep(0.2)
            result = self.llm.invoke(f"Şunun için kısa yanıt: {current}")

            completed.append(current)

            return {
                **state,
                "current_task": current,
                "completed": completed
            }

        return state

    def _update_progress(self, state: ProgressState) -> ProgressState:
        """İlerleme yüzdesini güncelle."""
        tasks = state.get("tasks", [])
        completed = state.get("completed", [])

        if tasks:
            progress = (len(completed) / len(tasks)) * 100
        else:
            progress = 100.0

        return {
            **state,
            "progress_percent": progress
        }

    def _should_continue(self, state: ProgressState):
        """İşlenecek daha fazla görev olup olmadığını kontrol et."""
        tasks = state.get("tasks", [])
        completed = state.get("completed", [])

        return "continue" if len(completed) < len(tasks) else "done"

    def stream_with_progress(self, tasks: List[str]) -> Iterator[Dict[str, Any]]:
        """İlerleme güncellemeleri ile yürütmeyi akışla."""
        for event in self.graph.stream({
            "tasks": tasks,
            "completed": [],
            "current_task": "",
            "progress_percent": 0.0
        }):
            # İlerleme bilgisini çıkar
            for node_name, node_state in event.items():
                if "progress_percent" in node_state:
                    yield {
                        "node": node_name,
                        "progress": node_state["progress_percent"],
                        "current_task": node_state.get("current_task", ""),
                        "completed": len(node_state.get("completed", []))
                    }


# ============================================================================
# Bölüm 3: Gerçek Zamanlı Hata Ayıklama Akışı
# ============================================================================

class DebugState(TypedDict):
    """Hata ayıklama bilgisi ile durum."""
    input: str
    intermediate_results: List[Dict[str, Any]]
    final_output: str
    debug_log: List[str]


class DebugStreamingAgent:
    """
    Geliştirme için hata ayıklama akışını gösterir.

    Özellikler:
    - Ara sonuçları akışla
    - Gerçek zamanlı hata ayıklama
    - Durum incelemesi
    - Performans izleme
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Hata ayıklama akış ajanını başlat."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Hata ayıklama enstrümantasyonu ile grafik oluştur."""
        workflow = StateGraph(DebugState)

        workflow.add_node("analyze", self._analyze_input)
        workflow.add_node("process", self._process_data)
        workflow.add_node("synthesize", self._synthesize_output)

        workflow.set_entry_point("analyze")
        workflow.add_edge("analyze", "process")
        workflow.add_edge("process", "synthesize")
        workflow.add_edge("synthesize", END)

        return workflow.compile()

    def _analyze_input(self, state: DebugState) -> DebugState:
        """Hata ayıklama ile girdiyi analiz et."""
        start_time = time.time()

        input_data = state.get("input", "")
        debug_log = state.get("debug_log", [])
        intermediate = state.get("intermediate_results", [])

        # Başlangıcı günlüğe kaydet
        debug_log.append(f"[ANALİZ] Başlangıç: {datetime.now().isoformat()}")
        debug_log.append(f"[ANALİZ] Girdi uzunluğu: {len(input_data)}")

        # İşle
        analysis = {
            "word_count": len(input_data.split()),
            "char_count": len(input_data),
            "timestamp": datetime.now().isoformat()
        }

        intermediate.append({"step": "analyze", "result": analysis})

        # Tamamlanmayı günlüğe kaydet
        elapsed = time.time() - start_time
        debug_log.append(f"[ANALİZ] {elapsed:.3f}s içinde tamamlandı")

        return {
            **state,
            "intermediate_results": intermediate,
            "debug_log": debug_log
        }

    def _process_data(self, state: DebugState) -> DebugState:
        """Detaylı günlükleme ile işle."""
        start_time = time.time()

        input_data = state.get("input", "")
        debug_log = state.get("debug_log", [])
        intermediate = state.get("intermediate_results", [])

        debug_log.append(f"[İŞLEME] Başlangıç: {datetime.now().isoformat()}")

        # LLM çağrısı
        llm_start = time.time()
        result = self.llm.invoke(f"Analiz et: {input_data}")
        llm_elapsed = time.time() - llm_start

        debug_log.append(f"[İŞLEME] LLM çağrısı: {llm_elapsed:.3f}s")

        intermediate.append({
            "step": "process",
            "result": result[:100],
            "llm_time": llm_elapsed
        })

        elapsed = time.time() - start_time
        debug_log.append(f"[İŞLEME] {elapsed:.3f}s içinde tamamlandı")

        return {
            **state,
            "intermediate_results": intermediate,
            "debug_log": debug_log
        }

    def _synthesize_output(self, state: DebugState) -> DebugState:
        """Final çıktıyı sentezle."""
        start_time = time.time()

        intermediate = state.get("intermediate_results", [])
        debug_log = state.get("debug_log", [])

        debug_log.append(f"[SENTEZ] Başlangıç: {datetime.now().isoformat()}")

        # Sonuçları birleştir
        final_output = f"{len(intermediate)} adım işlendi"

        elapsed = time.time() - start_time
        debug_log.append(f"[SENTEZ] {elapsed:.3f}s içinde tamamlandı")

        return {
            **state,
            "final_output": final_output,
            "debug_log": debug_log
        }

    def stream_debug(self, input_data: str) -> Iterator[Dict[str, Any]]:
        """Hata ayıklama bilgisi ile yürütmeyi akışla."""
        for event in self.graph.stream({
            "input": input_data,
            "intermediate_results": [],
            "final_output": "",
            "debug_log": []
        }):
            # Her düğümden hata ayıklama bilgisini çıkar
            for node_name, node_state in event.items():
                debug_info = {
                    "node": node_name,
                    "timestamp": datetime.now().isoformat(),
                    "debug_log": node_state.get("debug_log", []),
                    "intermediate": node_state.get("intermediate_results", [])
                }
                yield debug_info


# ============================================================================
# Bölüm 4: Üretim Olay Sistemi
# ============================================================================

class ProductionState(TypedDict):
    """Üretim sınıfı durum."""
    request_id: str
    payload: Dict[str, Any]
    processing_stages: List[Dict[str, Any]]
    result: Dict[str, Any]
    metrics: Dict[str, float]


class ProductionEventStream:
    """
    Kurumsal sınıf olay akış sistemi.

    Özellikler:
    - Yapılandırılmış olay günlükleme
    - Performans metrikleri
    - Hata takibi
    - Olay toplama
    - Gerçek zamanlı izleme
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Üretim olay sistemini başlat."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.memory = MemorySaver()
        self.graph = self._build_graph()
        self.event_handlers = []

    def _build_graph(self) -> StateGraph:
        """Kapsamlı enstrümantasyon ile üretim grafiği oluştur."""
        workflow = StateGraph(ProductionState)

        # Boru hattı düğümleri
        workflow.add_node("validate", self._validate_request)
        workflow.add_node("enrich", self._enrich_data)
        workflow.add_node("process", self._process_request)
        workflow.add_node("aggregate", self._aggregate_results)
        workflow.add_node("finalize", self._finalize_response)

        # Akış
        workflow.set_entry_point("validate")
        workflow.add_edge("validate", "enrich")
        workflow.add_edge("enrich", "process")
        workflow.add_edge("process", "aggregate")
        workflow.add_edge("aggregate", "finalize")
        workflow.add_edge("finalize", END)

        return workflow.compile(checkpointer=self.memory)

    def _emit_event(self, state: ProductionState, event_type: str, data: Dict[str, Any]):
        """Yapılandırılmış olay yay."""
        event = {
            "request_id": state.get("request_id", "bilinmiyor"),
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }

        stages = state.get("processing_stages", [])
        stages.append(event)
        state["processing_stages"] = stages

    def _validate_request(self, state: ProductionState) -> ProductionState:
        """Gelen isteği doğrula."""
        start_time = time.time()

        payload = state.get("payload", {})
        metrics = state.get("metrics", {})

        self._emit_event(state, "VALIDATION_START", {"payload_size": len(str(payload))})

        # Doğrulama mantığı
        is_valid = bool(payload)

        elapsed = time.time() - start_time
        metrics["validation_time"] = elapsed

        self._emit_event(state, "VALIDATION_COMPLETE", {
            "valid": is_valid,
            "duration_ms": elapsed * 1000
        })

        return {**state, "metrics": metrics}

    def _enrich_data(self, state: ProductionState) -> ProductionState:
        """İstek verisini zenginleştir."""
        start_time = time.time()
        metrics = state.get("metrics", {})

        self._emit_event(state, "ENRICHMENT_START", {})

        # Zenginleştirme mantığı
        payload = state.get("payload", {})
        payload["enriched_at"] = datetime.now().isoformat()

        elapsed = time.time() - start_time
        metrics["enrichment_time"] = elapsed

        self._emit_event(state, "ENRICHMENT_COMPLETE", {
            "duration_ms": elapsed * 1000,
            "fields_added": 1
        })

        return {**state, "payload": payload, "metrics": metrics}

    def _process_request(self, state: ProductionState) -> ProductionState:
        """Ana işleme mantığı."""
        start_time = time.time()
        metrics = state.get("metrics", {})

        self._emit_event(state, "PROCESSING_START", {})

        # LLM ile işle
        payload = state.get("payload", {})
        query = payload.get("query", "")

        llm_start = time.time()
        try:
            response = self.llm.invoke(f"İşle: {query}")
            llm_elapsed = time.time() - llm_start

            self._emit_event(state, "LLM_COMPLETE", {
                "duration_ms": llm_elapsed * 1000,
                "response_length": len(response)
            })

            result = {
                "status": "success",
                "data": response,
                "llm_time": llm_elapsed
            }

        except Exception as e:
            self._emit_event(state, "PROCESSING_ERROR", {
                "error": str(e)
            })
            result = {"status": "error", "message": str(e)}

        elapsed = time.time() - start_time
        metrics["processing_time"] = elapsed

        self._emit_event(state, "PROCESSING_COMPLETE", {
            "duration_ms": elapsed * 1000
        })

        return {**state, "result": result, "metrics": metrics}

    def _aggregate_results(self, state: ProductionState) -> ProductionState:
        """İşleme sonuçlarını topla."""
        start_time = time.time()
        metrics = state.get("metrics", {})

        self._emit_event(state, "AGGREGATION_START", {})

        # Toplama mantığı
        result = state.get("result", {})
        result["aggregated"] = True

        elapsed = time.time() - start_time
        metrics["aggregation_time"] = elapsed

        self._emit_event(state, "AGGREGATION_COMPLETE", {
            "duration_ms": elapsed * 1000
        })

        return {**state, "result": result, "metrics": metrics}

    def _finalize_response(self, state: ProductionState) -> ProductionState:
        """Yanıtı metriklerle sonlandır."""
        metrics = state.get("metrics", {})

        # Toplam süreyi hesapla
        total_time = sum(metrics.values())
        metrics["total_time"] = total_time

        self._emit_event(state, "REQUEST_COMPLETE", {
            "total_duration_ms": total_time * 1000,
            "metrics": metrics
        })

        result = state.get("result", {})
        result["metrics"] = metrics

        return {**state, "result": result, "metrics": metrics}

    def stream_request(self, payload: Dict[str, Any]) -> Iterator[Dict[str, Any]]:
        """Olay akışı ile isteği işle."""
        request_id = f"req_{int(time.time() * 1000)}"

        for event in self.graph.stream({
            "request_id": request_id,
            "payload": payload,
            "processing_stages": [],
            "result": {},
            "metrics": {}
        }):
            # Her düğümün olaylarını akışla
            for node_name, node_state in event.items():
                stages = node_state.get("processing_stages", [])
                for stage in stages:
                    yield {
                        "node": node_name,
                        **stage
                    }

    def get_metrics_summary(self, request_id: str) -> Dict[str, Any]:
        """İstek için metrik özetini al."""
        # Üretimde, izleme sisteminden alın
        return {
            "request_id": request_id,
            "summary": "Metrikler izleme sisteminden toplanacaktır"
        }


# ============================================================================
# GÖSTERİMLER
# ============================================================================

def demo_basic_streaming():
    """Temel olay akışını göster."""
    print("\n" + "="*70)
    print("DEMO 1: Temel Olay Akışı")
    print("="*70)

    agent = BasicStreamingAgent()

    print("\n1. Yürütme olayları akışlanıyor:")
    for event in agent.stream_process("Yapay Zeka nedir?"):
        node_name = list(event.keys())[0]
        node_state = event[node_name]
        if "events" in node_state:
            for evt in node_state["events"]:
                print(f"   {evt}")


def demo_progress_tracking():
    """İlerleme takibini göster."""
    print("\n" + "="*70)
    print("DEMO 2: İlerleme Takibi")
    print("="*70)

    agent = ProgressTrackingAgent()

    print("\n1. İlerleme güncellemeleri ile işleniyor:")
    tasks = ["Veriyi analiz et", "Rapor oluştur", "E-posta gönder"]

    for update in agent.stream_with_progress(tasks):
        print(f"   [{update['progress']:.0f}%] Düğüm: {update['node']} | "
              f"Görev: {update['current_task']} | "
              f"Tamamlanan: {update['completed']}")


def demo_debug_streaming():
    """Hata ayıklama akışını göster."""
    print("\n" + "="*70)
    print("DEMO 3: Gerçek Zamanlı Hata Ayıklama Akışı")
    print("="*70)

    agent = DebugStreamingAgent()

    print("\n1. Hata ayıklama bilgisi akışlanıyor:")
    for debug_info in agent.stream_debug("Makine öğrenimini açıkla"):
        print(f"\n   Düğüm: {debug_info['node']}")
        for log in debug_info['debug_log']:
            print(f"     {log}")


def demo_production_events():
    """Üretim olay sistemini göster."""
    print("\n" + "="*70)
    print("DEMO 4: Üretim Olay Akışı")
    print("="*70)

    system = ProductionEventStream()

    print("\n1. Olay akışı ile istek işleniyor:")
    payload = {
        "query": "Yapay zekanın faydaları nelerdir?",
        "user_id": "user_123"
    }

    for event in system.stream_request(payload):
        event_type = event.get("event_type", "BİLİNMEYEN")
        node = event.get("node", "bilinmiyor")
        data = event.get("data", {})

        print(f"\n   [{event.get('timestamp', '')}]")
        print(f"   Tür: {event_type} | Düğüm: {node}")
        if data:
            print(f"   Veri: {json.dumps(data, indent=6)}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("LangGraph Akış Olayları Eğitimi")
    print("="*70)
    print("\nBu eğitim, gerçek zamanlı olay akış desenlerini gösterir.")
    print("Akış, canlı ilerleme takibi ve hata ayıklamayı sağlar.")

    try:
        demo_basic_streaming()
        demo_progress_tracking()
        demo_debug_streaming()
        demo_production_events()

        print("\n" + "="*70)
        print("Eğitim başarıyla tamamlandı!")
        print("="*70)
        print("\nTemel Çıkarımlar:")
        print("1. graph.stream() gerçek zamanlı yürütme güncellemeleri sağlar")
        print("2. İlerleme takibi kullanıcı deneyimini iyileştirir")
        print("3. Hata ayıklama akışı geliştirmeyi hızlandırır")
        print("4. Yapılandırılmış olaylar izleme ve gözlemlenebilirliği sağlar")
        print("\nSıradaki: 08_production_agent.py - Tam kurumsal ajan")

    except Exception as e:
        print(f"\nGösterim sırasında hata: {e}")
        print("Ollama'nın qwen3:8b modeli ile çalıştığından emin olun")
