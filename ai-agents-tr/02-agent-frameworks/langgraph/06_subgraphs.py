#!/usr/bin/env python3
"""
LangGraph Alt Grafikler - İç İçe İş Akışı Kompozisyonu
==================================================

Bu betik, modüler iş akışları oluşturmak için alt grafik desenlerini gösterir.
Alt grafikler şunları yapmanızı sağlar:
- Yeniden kullanılabilir bileşenlerden karmaşık iş akışları oluşturma
- Alan mantığını kapsülleme
- Hiyerarşik mimariler oluşturma
- Paralel işlemeyi etkinleştirme

Basit iç içe grafiklerden üretim mikroservis desenlerine kadar ilerleyeceğiz.

Yazar: AI Agents Tutorial Series
"""

from typing import TypedDict, Annotated, List, Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import OllamaLLM
import operator
from datetime import datetime


# ============================================================================
# Bölüm 1: Temel Alt Grafik
# ============================================================================

class SimpleState(TypedDict):
    """Alt grafik demosu için temel durum."""
    input: str
    output: str
    step_results: List[str]


class BasicSubgraphAgent:
    """
    Temel alt grafik kompozisyonunu gösterir.

    Özellikler:
    - Yeniden kullanılabilir alt grafik bileşenleri oluşturma
    - Alt grafiği ana iş akışına gömme
    - Grafikler arasında durum aktarma
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Alt grafik ajanını başlat."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.graph = self._build_graph()

    def _build_preprocessing_subgraph(self) -> StateGraph:
        """Ön işleme alt grafiği oluştur."""
        subgraph = StateGraph(SimpleState)

        # Ön işleme düğümleri
        subgraph.add_node("clean", self._clean_input)
        subgraph.add_node("validate", self._validate_input)

        # Alt grafik akışı
        subgraph.set_entry_point("clean")
        subgraph.add_edge("clean", "validate")
        subgraph.add_edge("validate", END)

        return subgraph.compile()

    def _clean_input(self, state: SimpleState) -> SimpleState:
        """Girdiyi temizle."""
        input_data = state.get("input", "")
        cleaned = input_data.strip().lower()

        step_results = state.get("step_results", [])
        step_results.append(f"Temizlendi: '{input_data}' -> '{cleaned}'")

        return {
            **state,
            "input": cleaned,
            "step_results": step_results
        }

    def _validate_input(self, state: SimpleState) -> SimpleState:
        """Girdiyi doğrula."""
        input_data = state.get("input", "")
        is_valid = len(input_data) > 0

        step_results = state.get("step_results", [])
        step_results.append(f"Doğrulama: {'geçti' if is_valid else 'başarısız'}")

        return {
            **state,
            "step_results": step_results
        }

    def _build_graph(self) -> StateGraph:
        """Alt grafik ile ana grafiği oluştur."""
        # Ön işleme alt grafiği oluştur
        preprocessing = self._build_preprocessing_subgraph()

        # Ana iş akışı
        workflow = StateGraph(SimpleState)

        # Alt grafiği bir düğüm olarak ekle
        workflow.add_node("preprocess", preprocessing)
        workflow.add_node("process", self._process_data)
        workflow.add_node("postprocess", self._postprocess_data)

        # Ana akış
        workflow.set_entry_point("preprocess")
        workflow.add_edge("preprocess", "process")
        workflow.add_edge("process", "postprocess")
        workflow.add_edge("postprocess", END)

        return workflow.compile()

    def _process_data(self, state: SimpleState) -> SimpleState:
        """Ana işleme mantığı."""
        input_data = state.get("input", "")
        result = self.llm.invoke(f"Bunu işle: {input_data}")

        step_results = state.get("step_results", [])
        step_results.append(f"İşlendi: {result[:50]}...")

        return {
            **state,
            "output": result,
            "step_results": step_results
        }

    def _postprocess_data(self, state: SimpleState) -> SimpleState:
        """Sonuçları son işle."""
        output = state.get("output", "")
        formatted = f"SONUÇ: {output}"

        step_results = state.get("step_results", [])
        step_results.append(f"Biçimlendirilmiş çıktı")

        return {
            **state,
            "output": formatted,
            "step_results": step_results
        }

    def run(self, input_data: str) -> Dict[str, Any]:
        """Tam iş akışını çalıştır."""
        result = self.graph.invoke({
            "input": input_data,
            "output": "",
            "step_results": []
        })

        return result


# ============================================================================
# Bölüm 2: Paralel Alt Grafikler
# ============================================================================

class ParallelState(TypedDict):
    """Paralel işleme için durum."""
    query: str
    search_results: List[str]
    analysis_results: List[str]
    summary: str


class ParallelSubgraphAgent:
    """
    Paralel alt grafik yürütmesini gösterir.

    Özellikler:
    - Birden fazla alt grafiği eşzamanlı çalıştırma
    - Paralel dallardan sonuçları toplama
    - İşleme süresini optimize etme
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Paralel ajanı başlat."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.graph = self._build_graph()

    def _build_search_subgraph(self) -> StateGraph:
        """Arama alt grafiği oluştur."""
        subgraph = StateGraph(ParallelState)

        subgraph.add_node("search_web", self._search_web)
        subgraph.add_node("search_docs", self._search_docs)
        subgraph.add_node("merge_search", self._merge_search_results)

        subgraph.set_entry_point("search_web")
        subgraph.add_edge("search_web", "merge_search")
        subgraph.add_edge("search_docs", "merge_search")
        subgraph.add_edge("merge_search", END)

        return subgraph.compile()

    def _build_analysis_subgraph(self) -> StateGraph:
        """Analiz alt grafiği oluştur."""
        subgraph = StateGraph(ParallelState)

        subgraph.add_node("sentiment", self._analyze_sentiment)
        subgraph.add_node("entities", self._extract_entities)
        subgraph.add_node("merge_analysis", self._merge_analysis_results)

        subgraph.set_entry_point("sentiment")
        subgraph.add_edge("sentiment", "merge_analysis")
        subgraph.add_edge("entities", "merge_analysis")
        subgraph.add_edge("merge_analysis", END)

        return subgraph.compile()

    def _search_web(self, state: ParallelState) -> ParallelState:
        """Web aramasını simüle et."""
        query = state.get("query", "")
        results = state.get("search_results", [])
        results.append(f"Web sonucu: {query}")

        return {**state, "search_results": results}

    def _search_docs(self, state: ParallelState) -> ParallelState:
        """Belge aramasını simüle et."""
        query = state.get("query", "")
        results = state.get("search_results", [])
        results.append(f"Belge sonucu: {query}")

        return {**state, "search_results": results}

    def _merge_search_results(self, state: ParallelState) -> ParallelState:
        """Arama sonuçlarını birleştir."""
        return state

    def _analyze_sentiment(self, state: ParallelState) -> ParallelState:
        """Duygu analizi yap."""
        query = state.get("query", "")
        results = state.get("analysis_results", [])
        results.append(f"Duygu: '{query}' için nötr")

        return {**state, "analysis_results": results}

    def _extract_entities(self, state: ParallelState) -> ParallelState:
        """Varlıkları çıkar."""
        query = state.get("query", "")
        results = state.get("analysis_results", [])
        results.append(f"'{query}' içinde bulunan varlıklar")

        return {**state, "analysis_results": results}

    def _merge_analysis_results(self, state: ParallelState) -> ParallelState:
        """Analiz sonuçlarını birleştir."""
        return state

    def _build_graph(self) -> StateGraph:
        """Paralel alt grafiklerle ana grafiği oluştur."""
        # Alt grafikleri oluştur
        search_graph = self._build_search_subgraph()
        analysis_graph = self._build_analysis_subgraph()

        # Ana iş akışı
        workflow = StateGraph(ParallelState)

        # Alt grafikleri paralel düğümler olarak ekle
        workflow.add_node("search", search_graph)
        workflow.add_node("analyze", analysis_graph)
        workflow.add_node("summarize", self._create_summary)

        # Paralel yürütme (her ikisi de bağımsız çalışır)
        workflow.set_entry_point("search")
        workflow.add_edge("search", "summarize")
        workflow.add_edge("analyze", "summarize")
        workflow.add_edge("summarize", END)

        return workflow.compile()

    def _create_summary(self, state: ParallelState) -> ParallelState:
        """Final özet oluştur."""
        search_results = state.get("search_results", [])
        analysis_results = state.get("analysis_results", [])

        summary = f"{len(search_results)} arama sonucu ve {len(analysis_results)} analiz içgörüsü bulundu"

        return {**state, "summary": summary}

    def process(self, query: str) -> Dict[str, Any]:
        """Sorguyu paralel alt grafiklerle işle."""
        result = self.graph.invoke({
            "query": query,
            "search_results": [],
            "analysis_results": [],
            "summary": ""
        })

        return result


# ============================================================================
# Bölüm 3: Hiyerarşik Alt Grafik Mimarisi
# ============================================================================

class DocumentState(TypedDict):
    """Belge işleme için durum."""
    document: str
    sections: List[Dict[str, str]]
    processed_sections: List[Dict[str, str]]
    final_output: str


class HierarchicalSubgraphAgent:
    """
    Hiyerarşik alt grafik kompozisyonunu gösterir.

    Özellikler:
    - Çok seviyeli alt grafik iç içe geçirme
    - Bölüm bölüm işleme
    - Özyinelemeli iş akışı desenleri
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Hiyerarşik ajanı başlat."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.graph = self._build_graph()

    def _build_section_processor(self) -> StateGraph:
        """Bölüm işleme alt grafiği oluştur."""
        # Bu en alt seviye alt grafiktir
        section_graph = StateGraph(DocumentState)

        section_graph.add_node("extract", self._extract_key_points)
        section_graph.add_node("summarize", self._summarize_section)
        section_graph.add_node("enrich", self._enrich_section)

        section_graph.set_entry_point("extract")
        section_graph.add_edge("extract", "summarize")
        section_graph.add_edge("summarize", "enrich")
        section_graph.add_edge("enrich", END)

        return section_graph.compile()

    def _build_chapter_processor(self) -> StateGraph:
        """Bölüm işleme alt grafiği oluştur."""
        # Orta seviye - bölüm işlemciyi kullanır
        section_processor = self._build_section_processor()

        chapter_graph = StateGraph(DocumentState)

        chapter_graph.add_node("split_sections", self._split_into_sections)
        chapter_graph.add_node("process_section", section_processor)
        chapter_graph.add_node("merge_sections", self._merge_sections)

        chapter_graph.set_entry_point("split_sections")
        chapter_graph.add_edge("split_sections", "process_section")
        chapter_graph.add_edge("process_section", "merge_sections")
        chapter_graph.add_edge("merge_sections", END)

        return chapter_graph.compile()

    def _extract_key_points(self, state: DocumentState) -> DocumentState:
        """Bölümden ana noktaları çıkar."""
        # İlk bölümü işle
        sections = state.get("sections", [])
        if sections:
            section = sections[0]
            key_points = f"Ana noktalar: {section.get('content', '')[:50]}"
            section["key_points"] = key_points

        return state

    def _summarize_section(self, state: DocumentState) -> DocumentState:
        """Bölümü özetle."""
        sections = state.get("sections", [])
        if sections:
            section = sections[0]
            summary = f"{section.get('title', 'bölüm')} özeti"
            section["summary"] = summary

        return state

    def _enrich_section(self, state: DocumentState) -> DocumentState:
        """Bölümü meta verilerle zenginleştir."""
        sections = state.get("sections", [])
        processed = state.get("processed_sections", [])

        if sections:
            section = sections[0]
            section["processed"] = True
            section["timestamp"] = datetime.now().isoformat()
            processed.append(section)

            # İşlenen bölümü kaldır
            sections = sections[1:]

        return {**state, "sections": sections, "processed_sections": processed}

    def _split_into_sections(self, state: DocumentState) -> DocumentState:
        """Belgeyi bölümlere ayır."""
        document = state.get("document", "")

        # Basit bölme (üretimde düzgün ayrıştırma kullanın)
        sections = [
            {"title": f"Bölüm {i+1}", "content": document[i*100:(i+1)*100]}
            for i in range(min(3, len(document) // 100 + 1))
        ]

        return {**state, "sections": sections}

    def _merge_sections(self, state: DocumentState) -> DocumentState:
        """İşlenen bölümleri birleştir."""
        processed = state.get("processed_sections", [])
        merged = " | ".join([s.get("summary", "") for s in processed])

        return {**state, "final_output": merged}

    def _build_graph(self) -> StateGraph:
        """Üst düzey grafiği oluştur."""
        chapter_processor = self._build_chapter_processor()

        workflow = StateGraph(DocumentState)

        workflow.add_node("prepare", self._prepare_document)
        workflow.add_node("process_chapters", chapter_processor)
        workflow.add_node("finalize", self._finalize_output)

        workflow.set_entry_point("prepare")
        workflow.add_edge("prepare", "process_chapters")
        workflow.add_edge("process_chapters", "finalize")
        workflow.add_edge("finalize", END)

        return workflow.compile()

    def _prepare_document(self, state: DocumentState) -> DocumentState:
        """Belgeyi işleme için hazırla."""
        return state

    def _finalize_output(self, state: DocumentState) -> DocumentState:
        """İşlenen çıktıyı sonlandır."""
        final = state.get("final_output", "")
        state["final_output"] = f"FİNAL: {final}"
        return state

    def process_document(self, document: str) -> str:
        """Tam belgeyi işle."""
        result = self.graph.invoke({
            "document": document,
            "sections": [],
            "processed_sections": [],
            "final_output": ""
        })

        return result.get("final_output", "")


# ============================================================================
# Bölüm 4: Üretim Mikroservis Mimarisi
# ============================================================================

class MicroserviceState(TypedDict):
    """Mikroservis mimarisi için durum."""
    request: Dict[str, Any]
    auth_result: Dict[str, Any]
    data_result: Dict[str, Any]
    processing_result: Dict[str, Any]
    response: Dict[str, Any]


class ProductionMicroserviceAgent:
    """
    Alt grafikleri kullanan kurumsal mikroservis mimarisi.

    Özellikler:
    - Alt grafikler aracılığıyla servis izolasyonu
    - Bağımsız servis ölçeklendirme
    - Servis sağlık izleme
    - Hata izolasyonu ve kurtarma
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Mikroservis mimarisini başlat."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.memory = MemorySaver()
        self.graph = self._build_graph()
        self.service_stats = {
            "auth_service": {"calls": 0, "errors": 0},
            "data_service": {"calls": 0, "errors": 0},
            "processing_service": {"calls": 0, "errors": 0}
        }

    def _build_auth_service(self) -> StateGraph:
        """Kimlik doğrulama servisi alt grafiği oluştur."""
        auth_service = StateGraph(MicroserviceState)

        auth_service.add_node("validate_token", self._validate_token)
        auth_service.add_node("check_permissions", self._check_permissions)
        auth_service.add_node("log_auth", self._log_auth_attempt)

        auth_service.set_entry_point("validate_token")
        auth_service.add_edge("validate_token", "check_permissions")
        auth_service.add_edge("check_permissions", "log_auth")
        auth_service.add_edge("log_auth", END)

        return auth_service.compile()

    def _build_data_service(self) -> StateGraph:
        """Veri servisi alt grafiği oluştur."""
        data_service = StateGraph(MicroserviceState)

        data_service.add_node("fetch_data", self._fetch_data)
        data_service.add_node("validate_data", self._validate_data)
        data_service.add_node("cache_data", self._cache_data)

        data_service.set_entry_point("fetch_data")
        data_service.add_edge("fetch_data", "validate_data")
        data_service.add_edge("validate_data", "cache_data")
        data_service.add_edge("cache_data", END)

        return data_service.compile()

    def _build_processing_service(self) -> StateGraph:
        """İşleme servisi alt grafiği oluştur."""
        processing_service = StateGraph(MicroserviceState)

        processing_service.add_node("analyze", self._analyze_data)
        processing_service.add_node("transform", self._transform_data)
        processing_service.add_node("optimize", self._optimize_output)

        processing_service.set_entry_point("analyze")
        processing_service.add_edge("analyze", "transform")
        processing_service.add_edge("transform", "optimize")
        processing_service.add_edge("optimize", END)

        return processing_service.compile()

    def _validate_token(self, state: MicroserviceState) -> MicroserviceState:
        """Kimlik doğrulama tokenını doğrula."""
        self.service_stats["auth_service"]["calls"] += 1

        request = state.get("request", {})
        token = request.get("token", "")

        auth_result = {
            "valid": len(token) > 0,
            "user_id": "user_123" if token else None,
            "timestamp": datetime.now().isoformat()
        }

        return {**state, "auth_result": auth_result}

    def _check_permissions(self, state: MicroserviceState) -> MicroserviceState:
        """Kullanıcı izinlerini kontrol et."""
        auth_result = state.get("auth_result", {})
        request = state.get("request", {})

        auth_result["has_permission"] = auth_result.get("valid", False)
        auth_result["allowed_actions"] = ["read", "write"] if auth_result.get("valid") else []

        return {**state, "auth_result": auth_result}

    def _log_auth_attempt(self, state: MicroserviceState) -> MicroserviceState:
        """Kimlik doğrulama denemesini günlüğe kaydet."""
        auth_result = state.get("auth_result", {})
        # Üretimde, günlükleme servisine yazın
        return state

    def _fetch_data(self, state: MicroserviceState) -> MicroserviceState:
        """Kaynaktan veri getir."""
        self.service_stats["data_service"]["calls"] += 1

        request = state.get("request", {})
        query = request.get("query", "")

        data_result = {
            "data": f"Sorgu için veri: {query}",
            "count": 10,
            "timestamp": datetime.now().isoformat()
        }

        return {**state, "data_result": data_result}

    def _validate_data(self, state: MicroserviceState) -> MicroserviceState:
        """Getirilen veriyi doğrula."""
        data_result = state.get("data_result", {})
        data_result["validated"] = True
        return {**state, "data_result": data_result}

    def _cache_data(self, state: MicroserviceState) -> MicroserviceState:
        """Gelecek istekler için veriyi önbelleğe al."""
        data_result = state.get("data_result", {})
        data_result["cached"] = True
        return {**state, "data_result": data_result}

    def _analyze_data(self, state: MicroserviceState) -> MicroserviceState:
        """Veriyi analiz et."""
        self.service_stats["processing_service"]["calls"] += 1

        data_result = state.get("data_result", {})
        data = data_result.get("data", "")

        processing_result = {
            "analysis": f"Analiz edildi: {data[:50]}",
            "insights": ["içgörü_1", "içgörü_2"],
            "timestamp": datetime.now().isoformat()
        }

        return {**state, "processing_result": processing_result}

    def _transform_data(self, state: MicroserviceState) -> MicroserviceState:
        """Veriyi dönüştür."""
        processing_result = state.get("processing_result", {})
        processing_result["transformed"] = True
        return {**state, "processing_result": processing_result}

    def _optimize_output(self, state: MicroserviceState) -> MicroserviceState:
        """Çıktıyı optimize et."""
        processing_result = state.get("processing_result", {})
        processing_result["optimized"] = True
        return {**state, "processing_result": processing_result}

    def _build_graph(self) -> StateGraph:
        """Ana API ağ geçidi grafiğini oluştur."""
        # Mikroservisleri oluştur
        auth_service = self._build_auth_service()
        data_service = self._build_data_service()
        processing_service = self._build_processing_service()

        # API Ağ Geçidi
        gateway = StateGraph(MicroserviceState)

        # Servisleri düğüm olarak ekle
        gateway.add_node("auth", auth_service)
        gateway.add_node("data", data_service)
        gateway.add_node("processing", processing_service)
        gateway.add_node("response", self._build_response)

        # Ağ geçidi akışı
        gateway.set_entry_point("auth")

        # Kimlik doğrulamaya dayalı koşullu yönlendirme
        gateway.add_conditional_edges(
            "auth",
            self._route_after_auth,
            {
                "authorized": "data",
                "unauthorized": "response"
            }
        )

        gateway.add_edge("data", "processing")
        gateway.add_edge("processing", "response")
        gateway.add_edge("response", END)

        return gateway.compile(checkpointer=self.memory)

    def _route_after_auth(self, state: MicroserviceState) -> Literal["authorized", "unauthorized"]:
        """Kimlik doğrulama sonucuna göre yönlendir."""
        auth_result = state.get("auth_result", {})
        return "authorized" if auth_result.get("valid", False) else "unauthorized"

    def _build_response(self, state: MicroserviceState) -> MicroserviceState:
        """API yanıtı oluştur."""
        auth_result = state.get("auth_result", {})

        if not auth_result.get("valid", False):
            response = {
                "status": "error",
                "message": "Yetkisiz",
                "code": 401
            }
        else:
            processing_result = state.get("processing_result", {})
            response = {
                "status": "success",
                "data": processing_result,
                "code": 200,
                "timestamp": datetime.now().isoformat()
            }

        return {**state, "response": response}

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Gelen API isteğini işle."""
        result = self.graph.invoke({
            "request": request,
            "auth_result": {},
            "data_result": {},
            "processing_result": {},
            "response": {}
        })

        return result.get("response", {})

    def get_service_stats(self) -> Dict[str, Any]:
        """Mikroservis istatistiklerini al."""
        return self.service_stats.copy()


# ============================================================================
# GÖSTERİMLER
# ============================================================================

def demo_basic_subgraph():
    """Temel alt grafiği göster."""
    print("\n" + "="*70)
    print("DEMO 1: Temel Alt Grafik Kompozisyonu")
    print("="*70)

    agent = BasicSubgraphAgent()

    print("\n1. Ön işleme alt grafiği ile iş akışı çalıştırılıyor...")
    result = agent.run("  MERHABA DÜNYA  ")

    print(f"\n2. Adım adım yürütme:")
    for step in result.get("step_results", []):
        print(f"   - {step}")

    print(f"\n3. Final çıktı: {result.get('output', '')[:100]}")


def demo_parallel_subgraphs():
    """Paralel alt grafikleri göster."""
    print("\n" + "="*70)
    print("DEMO 2: Paralel Alt Grafik Yürütme")
    print("="*70)

    agent = ParallelSubgraphAgent()

    print("\n1. Paralel alt grafiklerle işleniyor...")
    result = agent.process("yapay zeka")

    print(f"\n2. Arama sonuçları: {len(result.get('search_results', []))}")
    for res in result.get('search_results', []):
        print(f"   - {res}")

    print(f"\n3. Analiz sonuçları: {len(result.get('analysis_results', []))}")
    for res in result.get('analysis_results', []):
        print(f"   - {res}")

    print(f"\n4. Özet: {result.get('summary', '')}")


def demo_hierarchical():
    """Hiyerarşik alt grafikleri göster."""
    print("\n" + "="*70)
    print("DEMO 3: Hiyerarşik Alt Grafik Mimarisi")
    print("="*70)

    agent = HierarchicalSubgraphAgent()

    print("\n1. İç içe alt grafiklerle belge işleniyor...")
    document = "Bu bir test belgesidir. " * 50
    result = agent.process_document(document)

    print(f"\n2. Final çıktı: {result[:150]}...")


def demo_microservices():
    """Mikroservis mimarisini göster."""
    print("\n" + "="*70)
    print("DEMO 4: Üretim Mikroservis Mimarisi")
    print("="*70)

    system = ProductionMicroserviceAgent()

    print("\n1. Yetkili istek...")
    request1 = {
        "token": "valid_token_123",
        "query": "user_data",
        "action": "read"
    }
    response1 = system.handle_request(request1)
    print(f"   Durum: {response1.get('status')}")
    print(f"   Kod: {response1.get('code')}")

    print("\n2. Yetkisiz istek...")
    request2 = {
        "token": "",
        "query": "sensitive_data",
        "action": "write"
    }
    response2 = system.handle_request(request2)
    print(f"   Durum: {response2.get('status')}")
    print(f"   Kod: {response2.get('code')}")

    print("\n3. Servis istatistikleri:")
    stats = system.get_service_stats()
    for service, metrics in stats.items():
        print(f"   {service}: {metrics}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("LangGraph Alt Grafikler - İç İçe İş Akışı Eğitimi")
    print("="*70)
    print("\nBu eğitim, alt grafik kompozisyon desenlerini gösterir.")
    print("Alt grafikler modüler, yeniden kullanılabilir ve ölçeklenebilir iş akışları sağlar.")

    try:
        demo_basic_subgraph()
        demo_parallel_subgraphs()
        demo_hierarchical()
        demo_microservices()

        print("\n" + "="*70)
        print("Eğitim başarıyla tamamlandı!")
        print("="*70)
        print("\nTemel Çıkarımlar:")
        print("1. Alt grafikler alan mantığını yeniden kullanılabilir bileşenlere kapsüller")
        print("2. Paralel alt grafikler işleme süresini optimize eder")
        print("3. Hiyerarşik iç içe geçirme karmaşık mimarileri sağlar")
        print("4. Mikroservis desenleri servis izolasyonu sağlar")
        print("\nSıradaki: 07_streaming_events.py - Gerçek zamanlı olay akışı")

    except Exception as e:
        print(f"\nGösterim sırasında hata: {e}")
        print("Ollama'nın qwen3:8b modeli ile çalıştığından emin olun")
