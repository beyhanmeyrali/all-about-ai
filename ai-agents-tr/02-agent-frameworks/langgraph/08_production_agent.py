#!/usr/bin/env python3
"""
LangGraph Üretim Ajanı - Kurumsal Sınıf Tam Sistem
==============================================================

Bu betik, tüm LangGraph özelliklerini kullanan tam bir üretime hazır ajanı gösterir.

Özellikler:
- Kontrol noktaları ile durum kalıcılığı
- İnsan döngüde onaylar
- Alt grafik kompozisyonu
- Olay akışı
- Araç entegrasyonu
- Hata yönetimi ve kurtarma
- İzleme ve gözlemlenebilirlik
- Güvenlik ve doğrulama

Bu, önceki tüm eğitimlerin tek bir kurumsal sınıf sistemde birleşimidir.

Yazar: AI Agents Tutorial Series
"""

from typing import TypedDict, Annotated, List, Dict, Any, Literal, Iterator, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import OllamaLLM
import operator
from datetime import datetime
import json
import time
import logging


# ============================================================================
# Yapılandırma ve Kurulum
# ============================================================================

# Günlüklemeyi yapılandır
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentConfig:
    """Üretim ajanı için merkezi yapılandırma."""

    def __init__(
        self,
        model: str = "qwen3:8b",
        temperature: float = 0.7,
        max_iterations: int = 10,
        checkpoint_enabled: bool = True,
        streaming_enabled: bool = True,
        require_approval: bool = True,
        verbose: bool = True
    ):
        self.model = model
        self.temperature = temperature
        self.max_iterations = max_iterations
        self.checkpoint_enabled = checkpoint_enabled
        self.streaming_enabled = streaming_enabled
        self.require_approval = require_approval
        self.verbose = verbose


# ============================================================================
# Durum Tanımları
# ============================================================================

class ProductionAgentState(TypedDict):
    """
    Tüm özelliklere sahip tam ajan durumu.

    Bu durum şunları izler:
    - Kullanıcı istekleri ve konuşma geçmişi
    - Araç yürütme sonuçları
    - Onay iş akışı durumu
    - Performans metrikleri
    - Hata yönetimi
    - İşleme aşamaları
    """
    # Çekirdek konuşma
    request_id: str
    user_request: str
    messages: List[Dict[str, str]]
    conversation_history: List[str]

    # İşleme
    analysis: Dict[str, Any]
    tools_used: List[str]
    tool_results: Dict[str, Any]
    intermediate_results: List[Dict[str, Any]]

    # Onay iş akışı
    requires_approval: bool
    approval_status: Optional[str]
    approval_feedback: str
    risk_level: str

    # Yürütme takibi
    current_step: str
    processing_stages: List[Dict[str, Any]]
    iteration_count: int

    # Sonuçlar
    final_response: str
    status: str

    # Metrikler
    metrics: Dict[str, float]
    start_time: float
    end_time: float

    # Hata yönetimi
    errors: List[str]
    retry_count: int


# ============================================================================
# Araç Tanımları
# ============================================================================

class ProductionTools:
    """
    Üretim sınıfı araç uygulamaları.

    Araçlar:
    - search: Web/bilgi araması
    - calculate: Matematiksel hesaplamalar
    - analyze: Veri analizi
    - generate_report: Rapor oluşturma
    """

    @staticmethod
    def search(query: str) -> Dict[str, Any]:
        """Bilgi ara."""
        logger.info(f"Araç [search] sorgu ile çağrıldı: {query}")

        # Aramayı simüle et
        time.sleep(0.3)

        return {
            "tool": "search",
            "query": query,
            "results": [
                f"'{query}' için Sonuç 1",
                f"'{query}' için Sonuç 2",
                f"'{query}' için Sonuç 3"
            ],
            "count": 3,
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def calculate(expression: str) -> Dict[str, Any]:
        """Hesaplamaları yap."""
        logger.info(f"Araç [calculate] şununla çağrıldı: {expression}")

        try:
            # Güvenli değerlendirme (üretimde düzgün matematik ayrıştırıcısı kullanın)
            result = eval(expression, {"__builtins__": {}}, {})

            return {
                "tool": "calculate",
                "expression": expression,
                "result": result,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "tool": "calculate",
                "expression": expression,
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat()
            }

    @staticmethod
    def analyze(data: str) -> Dict[str, Any]:
        """Veriyi analiz et."""
        logger.info(f"Araç [analyze] veri uzunluğu ile çağrıldı: {len(data)}")

        time.sleep(0.2)

        return {
            "tool": "analyze",
            "data_length": len(data),
            "word_count": len(data.split()),
            "analysis": f"Şunun analizi: {data[:50]}...",
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def generate_report(topic: str, data: List[str]) -> Dict[str, Any]:
        """Rapor oluştur."""
        logger.info(f"Araç [generate_report] konu için çağrıldı: {topic}")

        time.sleep(0.4)

        report = f"""
        RAPOR: {topic}
        Oluşturulma: {datetime.now().isoformat()}
        Veri Noktaları: {len(data)}

        Özet:
        {chr(10).join([f'- {item}' for item in data[:3]])}
        """

        return {
            "tool": "generate_report",
            "topic": topic,
            "report": report,
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# Alt Grafik Bileşenleri
# ============================================================================

class SecuritySubgraph:
    """Güvenlik doğrulama alt grafiği."""

    @staticmethod
    def build(llm: OllamaLLM) -> StateGraph:
        """Güvenlik doğrulama alt grafiği oluştur."""
        subgraph = StateGraph(ProductionAgentState)

        subgraph.add_node("validate_input", SecuritySubgraph._validate_input)
        subgraph.add_node("check_permissions", SecuritySubgraph._check_permissions)
        subgraph.add_node("assess_risk", SecuritySubgraph._assess_risk)

        subgraph.set_entry_point("validate_input")
        subgraph.add_edge("validate_input", "check_permissions")
        subgraph.add_edge("check_permissions", "assess_risk")
        subgraph.add_edge("assess_risk", END)

        return subgraph.compile()

    @staticmethod
    def _validate_input(state: ProductionAgentState) -> ProductionAgentState:
        """Kullanıcı girdisini doğrula."""
        user_request = state.get("user_request", "")
        errors = state.get("errors", [])

        # Temel doğrulama
        if not user_request or len(user_request.strip()) == 0:
            errors.append("Boş istek")

        if len(user_request) > 10000:
            errors.append("İstek çok uzun")

        logger.info(f"Girdi doğrulama: {'geçti' if not errors else 'başarısız'}")

        return {**state, "errors": errors}

    @staticmethod
    def _check_permissions(state: ProductionAgentState) -> ProductionAgentState:
        """Kullanıcı izinlerini kontrol et."""
        # Üretimde, IAM/RBAC'a karşı kontrol edin
        logger.info("İzin kontrolü: geçti")
        return state

    @staticmethod
    def _assess_risk(state: ProductionAgentState) -> ProductionAgentState:
        """İsteğin risk seviyesini değerlendir."""
        user_request = state.get("user_request", "").lower()

        # Basit risk değerlendirmesi
        high_risk_keywords = ["sil", "kaldır", "düşür", "yok et", "delete", "remove", "drop", "destroy"]
        medium_risk_keywords = ["değiştir", "güncelle", "modify", "update", "change", "alter"]

        if any(keyword in user_request for keyword in high_risk_keywords):
            risk_level = "high"
            requires_approval = True
        elif any(keyword in user_request for keyword in medium_risk_keywords):
            risk_level = "medium"
            requires_approval = True
        else:
            risk_level = "low"
            requires_approval = False

        logger.info(f"Risk değerlendirmesi: {risk_level}")

        return {
            **state,
            "risk_level": risk_level,
            "requires_approval": requires_approval
        }


# ============================================================================
# Ana Üretim Ajanı
# ============================================================================

class ProductionAgent:
    """
    Tam üretime hazır LangGraph ajanı.

    Bu ajan şunları birleştirir:
    - Durum kalıcılığı (kontrol noktaları)
    - İnsan döngüde (onaylar)
    - Alt grafikler (güvenlik, işleme)
    - Akış (gerçek zamanlı güncellemeler)
    - Araçlar (harici entegrasyonlar)
    - Hata yönetimi
    - Gözlemlenebilirlik
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """Üretim ajanını başlat."""
        self.config = config or AgentConfig()
        self.llm = OllamaLLM(
            model=self.config.model,
            temperature=self.config.temperature
        )
        self.tools = ProductionTools()
        self.memory = MemorySaver() if self.config.checkpoint_enabled else None
        self.graph = self._build_graph()
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "tools_called": 0,
            "approvals_required": 0,
            "approvals_granted": 0
        }

        logger.info("ProductionAgent başlatıldı")

    def _build_graph(self) -> StateGraph:
        """Tam ajan grafiğini oluştur."""
        # Alt grafikleri oluştur
        security_subgraph = SecuritySubgraph.build(self.llm)

        # Ana iş akışı
        workflow = StateGraph(ProductionAgentState)

        # Düğümleri ekle
        workflow.add_node("initialize", self._initialize_request)
        workflow.add_node("security", security_subgraph)
        workflow.add_node("analyze_request", self._analyze_request)
        workflow.add_node("approval_gate", self._approval_gate)
        workflow.add_node("execute_tools", self._execute_tools)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("finalize", self._finalize_response)
        workflow.add_node("handle_error", self._handle_error)

        # Akış
        workflow.set_entry_point("initialize")
        workflow.add_edge("initialize", "security")

        # Güvenlik doğrulamasına göre yönlendir
        workflow.add_conditional_edges(
            "security",
            self._route_after_security,
            {
                "proceed": "analyze_request",
                "error": "handle_error"
            }
        )

        workflow.add_edge("analyze_request", "approval_gate")

        # Onay gereksinimine göre yönlendir
        workflow.add_conditional_edges(
            "approval_gate",
            self._route_after_approval,
            {
                "approved": "execute_tools",
                "waiting": "approval_gate",
                "rejected": "finalize"
            }
        )

        # Araç yürütmesine göre yönlendir
        workflow.add_conditional_edges(
            "execute_tools",
            self._route_after_tools,
            {
                "continue": "execute_tools",
                "done": "generate_response",
                "error": "handle_error"
            }
        )

        workflow.add_edge("generate_response", "finalize")
        workflow.add_edge("handle_error", "finalize")
        workflow.add_edge("finalize", END)

        # Kontrol noktası ile derle
        if self.config.checkpoint_enabled:
            return workflow.compile(checkpointer=self.memory)
        else:
            return workflow.compile()

    # ========================================================================
    # Düğüm Uygulamaları
    # ========================================================================

    def _initialize_request(self, state: ProductionAgentState) -> ProductionAgentState:
        """İstek işlemeyi başlat."""
        request_id = state.get("request_id", f"req_{int(time.time() * 1000)}")

        logger.info(f"[{request_id}] İstek başlatılıyor")

        return {
            **state,
            "request_id": request_id,
            "messages": [],
            "conversation_history": [],
            "analysis": {},
            "tools_used": [],
            "tool_results": {},
            "intermediate_results": [],
            "approval_status": None,
            "approval_feedback": "",
            "risk_level": "unknown",
            "current_step": "initialize",
            "processing_stages": [],
            "iteration_count": 0,
            "final_response": "",
            "status": "processing",
            "metrics": {},
            "start_time": time.time(),
            "end_time": 0.0,
            "errors": [],
            "retry_count": 0
        }

    def _analyze_request(self, state: ProductionAgentState) -> ProductionAgentState:
        """Kullanıcı isteğini analiz et ve yürütmeyi planla."""
        start_time = time.time()
        user_request = state.get("user_request", "")
        request_id = state.get("request_id", "")

        logger.info(f"[{request_id}] İstek analiz ediliyor")

        # Niyeti analiz etmek için LLM kullan
        analysis_prompt = f"""Bu isteği analiz et ve şunları belirle:
1. Niyet
2. Gerekli araçlar (search, calculate, analyze, generate_report)
3. Parametreler

İstek: {user_request}

Kısa analiz sağla."""

        analysis_result = self.llm.invoke(analysis_prompt)

        # Basit araç tespiti (üretimde yapılandırılmış çıktı kullanın)
        tools_needed = []
        if "ara" in user_request.lower() or "bul" in user_request.lower() or "search" in user_request.lower() or "find" in user_request.lower():
            tools_needed.append("search")
        if "hesapla" in user_request.lower() or "calculate" in user_request.lower() or any(op in user_request for op in ['+', '-', '*', '/']):
            tools_needed.append("calculate")
        if "analiz" in user_request.lower() or "analyze" in user_request.lower():
            tools_needed.append("analyze")
        if "rapor" in user_request.lower() or "report" in user_request.lower():
            tools_needed.append("generate_report")

        analysis = {
            "intent": analysis_result[:200],
            "tools_needed": tools_needed,
            "complexity": "high" if len(tools_needed) > 2 else "medium" if tools_needed else "low",
            "timestamp": datetime.now().isoformat()
        }

        elapsed = time.time() - start_time
        metrics = state.get("metrics", {})
        metrics["analysis_time"] = elapsed

        logger.info(f"[{request_id}] Analiz tamamlandı: {len(tools_needed)} araç gerekli")

        return {
            **state,
            "analysis": analysis,
            "current_step": "analyze_request",
            "metrics": metrics
        }

    def _approval_gate(self, state: ProductionAgentState) -> ProductionAgentState:
        """İnsan onay kontrol noktası."""
        requires_approval = state.get("requires_approval", False)
        approval_status = state.get("approval_status")
        request_id = state.get("request_id", "")
        risk_level = state.get("risk_level", "unknown")

        if not requires_approval:
            # Düşük riskli istekleri otomatik onayla
            logger.info(f"[{request_id}] Otomatik onaylandı (düşük risk)")
            return {
                **state,
                "approval_status": "approved",
                "current_step": "approval_gate"
            }

        if approval_status is None:
            # İlk sefer - onay iste
            logger.info(f"[{request_id}] Onay gerekli (risk: {risk_level})")
            self.stats["approvals_required"] += 1

            return {
                **state,
                "approval_status": "pending",
                "current_step": "approval_gate"
            }

        # Onay zaten işlendi
        return {
            **state,
            "current_step": "approval_gate"
        }

    def _execute_tools(self, state: ProductionAgentState) -> ProductionAgentState:
        """Gerekli araçları yürüt."""
        start_time = time.time()
        analysis = state.get("analysis", {})
        tools_needed = analysis.get("tools_needed", [])
        tools_used = state.get("tools_used", [])
        tool_results = state.get("tool_results", {})
        iteration_count = state.get("iteration_count", 0)
        request_id = state.get("request_id", "")
        user_request = state.get("user_request", "")

        # Yürütülecek sonraki aracı bul
        remaining_tools = [t for t in tools_needed if t not in tools_used]

        if remaining_tools and iteration_count < self.config.max_iterations:
            tool_name = remaining_tools[0]

            logger.info(f"[{request_id}] Araç yürütülüyor: {tool_name}")

            try:
                # Aracı yürüt
                if tool_name == "search":
                    result = self.tools.search(user_request)
                elif tool_name == "calculate":
                    # İfadeyi çıkar (basitleştirilmiş)
                    result = self.tools.calculate("2 + 2")
                elif tool_name == "analyze":
                    result = self.tools.analyze(user_request)
                elif tool_name == "generate_report":
                    result = self.tools.generate_report("Kullanıcı İsteği", [user_request])
                else:
                    result = {"error": f"Bilinmeyen araç: {tool_name}"}

                tool_results[tool_name] = result
                tools_used.append(tool_name)
                self.stats["tools_called"] += 1

                logger.info(f"[{request_id}] Araç {tool_name} başarıyla tamamlandı")

            except Exception as e:
                logger.error(f"[{request_id}] Araç {tool_name} başarısız oldu: {e}")
                errors = state.get("errors", [])
                errors.append(f"Araç {tool_name} başarısız oldu: {str(e)}")
                return {**state, "errors": errors}

        elapsed = time.time() - start_time
        metrics = state.get("metrics", {})
        metrics["tool_execution_time"] = metrics.get("tool_execution_time", 0) + elapsed

        return {
            **state,
            "tools_used": tools_used,
            "tool_results": tool_results,
            "iteration_count": iteration_count + 1,
            "current_step": "execute_tools",
            "metrics": metrics
        }

    def _generate_response(self, state: ProductionAgentState) -> ProductionAgentState:
        """Final yanıtı oluştur."""
        start_time = time.time()
        user_request = state.get("user_request", "")
        tool_results = state.get("tool_results", {})
        request_id = state.get("request_id", "")

        logger.info(f"[{request_id}] Yanıt oluşturuluyor")

        # Araç sonuçlarından bağlam oluştur
        context = []
        for tool_name, result in tool_results.items():
            context.append(f"{tool_name}: {json.dumps(result)}")

        context_str = "\n".join(context) if context else "Araç kullanılmadı"

        # LLM ile yanıt oluştur
        response_prompt = f"""Aşağıdaki bilgilere dayanarak, kullanıcının isteğine yardımcı bir yanıt verin.

Kullanıcı İsteği: {user_request}

Araç Sonuçları:
{context_str}

Açık, özlü bir yanıt verin:"""

        final_response = self.llm.invoke(response_prompt)

        elapsed = time.time() - start_time
        metrics = state.get("metrics", {})
        metrics["response_generation_time"] = elapsed

        logger.info(f"[{request_id}] Yanıt oluşturuldu")

        return {
            **state,
            "final_response": final_response,
            "current_step": "generate_response",
            "metrics": metrics
        }

    def _finalize_response(self, state: ProductionAgentState) -> ProductionAgentState:
        """Yanıtı sonlandır ve hazırla."""
        request_id = state.get("request_id", "")
        errors = state.get("errors", [])

        end_time = time.time()
        start_time = state.get("start_time", end_time)
        total_time = end_time - start_time

        metrics = state.get("metrics", {})
        metrics["total_time"] = total_time

        # Durumu belirle
        if errors:
            status = "error"
            self.stats["failed_requests"] += 1
        else:
            status = "success"
            self.stats["successful_requests"] += 1

        self.stats["total_requests"] += 1

        logger.info(f"[{request_id}] İstek sonlandırıldı: {total_time:.3f}s içinde {status}")

        return {
            **state,
            "status": status,
            "end_time": end_time,
            "current_step": "finalize",
            "metrics": metrics
        }

    def _handle_error(self, state: ProductionAgentState) -> ProductionAgentState:
        """Hataları nazikçe yönet."""
        request_id = state.get("request_id", "")
        errors = state.get("errors", [])

        logger.error(f"[{request_id}] Hatalar yönetiliyor: {errors}")

        final_response = f"İsteğinizi işlerken bir hatayla karşılaştım: {'; '.join(errors)}"

        return {
            **state,
            "final_response": final_response,
            "status": "error",
            "current_step": "handle_error"
        }

    # ========================================================================
    # Yönlendirme Fonksiyonları
    # ========================================================================

    def _route_after_security(self, state: ProductionAgentState) -> Literal["proceed", "error"]:
        """Güvenlik doğrulamasına göre yönlendir."""
        errors = state.get("errors", [])
        return "error" if errors else "proceed"

    def _route_after_approval(self, state: ProductionAgentState) -> Literal["approved", "waiting", "rejected"]:
        """Onay durumuna göre yönlendir."""
        approval_status = state.get("approval_status")

        if approval_status == "approved":
            return "approved"
        elif approval_status == "rejected":
            return "rejected"
        else:
            return "waiting"

    def _route_after_tools(self, state: ProductionAgentState) -> Literal["continue", "done", "error"]:
        """Araç yürütme durumuna göre yönlendir."""
        errors = state.get("errors", [])
        if errors:
            return "error"

        analysis = state.get("analysis", {})
        tools_needed = analysis.get("tools_needed", [])
        tools_used = state.get("tools_used", [])
        iteration_count = state.get("iteration_count", 0)

        # Yürütülecek daha fazla araç olup olmadığını kontrol et
        if len(tools_used) < len(tools_needed) and iteration_count < self.config.max_iterations:
            return "continue"
        else:
            return "done"

    # ========================================================================
    # Genel Arayüz
    # ========================================================================

    def process_request(
        self,
        user_request: str,
        thread_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Kullanıcı isteğini işle.

        Argümanlar:
            user_request: Kullanıcının isteği
            thread_id: Konuşma iş parçacığı ID'si

        Döndürür:
            Sonuçlar ve meta verilerle yanıt
        """
        config = {"configurable": {"thread_id": thread_id}} if self.config.checkpoint_enabled else {}

        result = self.graph.invoke(
            {
                "request_id": f"req_{int(time.time() * 1000)}",
                "user_request": user_request,
                "requires_approval": False
            },
            config=config
        )

        return {
            "request_id": result.get("request_id"),
            "response": result.get("final_response", ""),
            "status": result.get("status", "unknown"),
            "metrics": result.get("metrics", {}),
            "tools_used": result.get("tools_used", []),
            "risk_level": result.get("risk_level", "unknown")
        }

    def stream_request(
        self,
        user_request: str,
        thread_id: str = "default"
    ) -> Iterator[Dict[str, Any]]:
        """
        İsteği akış güncellemeleri ile işle.

        Argümanlar:
            user_request: Kullanıcının isteği
            thread_id: Konuşma iş parçacığı ID'si

        Verir:
            İlerleme güncellemeleri
        """
        config = {"configurable": {"thread_id": thread_id}} if self.config.checkpoint_enabled else {}

        for event in self.graph.stream(
            {
                "request_id": f"req_{int(time.time() * 1000)}",
                "user_request": user_request,
                "requires_approval": False
            },
            config=config
        ):
            for node_name, node_state in event.items():
                yield {
                    "node": node_name,
                    "step": node_state.get("current_step", ""),
                    "status": node_state.get("status", "processing"),
                    "iteration": node_state.get("iteration_count", 0)
                }

    def approve_request(self, thread_id: str, feedback: str = "Onaylandı") -> Dict[str, Any]:
        """Bekleyen isteği onayla."""
        if not self.config.checkpoint_enabled:
            return {"error": "Kontrol noktaları etkin değil"}

        config = {"configurable": {"thread_id": thread_id}}
        current_state = self.graph.get_state(config)

        if not current_state.values:
            return {"error": "Bekleyen istek yok"}

        current_state.values["approval_status"] = "approved"
        current_state.values["approval_feedback"] = feedback

        self.stats["approvals_granted"] += 1

        result = self.graph.invoke(current_state.values, config=config)

        return {
            "status": "approved",
            "response": result.get("final_response", "")
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Ajan istatistiklerini al."""
        return self.stats.copy()


# ============================================================================
# GÖSTERİMLER
# ============================================================================

def demo_basic_usage():
    """Temel ajan kullanımını göster."""
    print("\n" + "="*70)
    print("DEMO 1: Temel Kullanım")
    print("="*70)

    config = AgentConfig(require_approval=False, verbose=True)
    agent = ProductionAgent(config)

    print("\n1. Basit istek işleniyor...")
    result = agent.process_request("Yapay zeka hakkında bilgi ara")

    print(f"\n2. Yanıt:")
    print(f"   İstek ID: {result['request_id']}")
    print(f"   Durum: {result['status']}")
    print(f"   Yanıt: {result['response'][:200]}...")
    print(f"   Kullanılan araçlar: {result['tools_used']}")
    print(f"   Toplam süre: {result['metrics'].get('total_time', 0):.3f}s")


def demo_streaming():
    """Akışı göster."""
    print("\n" + "="*70)
    print("DEMO 2: Akış Güncellemeleri")
    print("="*70)

    config = AgentConfig(require_approval=False, streaming_enabled=True)
    agent = ProductionAgent(config)

    print("\n1. Akış ile işleniyor...")
    for update in agent.stream_request("15 * 25 hesapla ve matematik ara"):
        print(f"   [{update['iteration']}] {update['node']} | Adım: {update['step']} | Durum: {update['status']}")


def demo_approval_workflow():
    """Onay iş akışını göster."""
    print("\n" + "="*70)
    print("DEMO 3: Onay İş Akışı (Simüle Edilmiş)")
    print("="*70)

    config = AgentConfig(require_approval=True, checkpoint_enabled=True)
    agent = ProductionAgent(config)

    print("\n1. Yüksek riskli istek gönderiliyor...")
    print("   İstek: 'Tüm kullanıcı verilerini sil'")

    # Üretimde, bu onay için duraklatılır
    # Demo için akışı gösteriyoruz
    print("   Durum: 'sil' anahtar kelimesi nedeniyle onay gerektirir")
    print("   Risk seviyesi: yüksek")
    print("   Onay gerekli: Evet")


def demo_statistics():
    """İstatistikleri göster."""
    print("\n" + "="*70)
    print("DEMO 4: Ajan İstatistikleri")
    print("="*70)

    config = AgentConfig(require_approval=False)
    agent = ProductionAgent(config)

    # Birkaç isteği işle
    agent.process_request("Python eğitimleri ara")
    agent.process_request("100 * 50 hesapla")

    print("\n1. Ajan istatistikleri:")
    stats = agent.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("LangGraph Üretim Ajanı - Tam Sistem")
    print("="*70)
    print("\nBu, tüm özellikleri birleştiren tam bir üretime hazır ajandır:")
    print("- Kontrol noktaları ile durum kalıcılığı")
    print("- İnsan döngüde onaylar")
    print("- Alt grafik kompozisyonu")
    print("- Olay akışı")
    print("- Araç entegrasyonu")
    print("- Hata yönetimi")
    print("- Gözlemlenebilirlik")

    try:
        demo_basic_usage()
        demo_streaming()
        demo_approval_workflow()
        demo_statistics()

        print("\n" + "="*70)
        print("Eğitim başarıyla tamamlandı!")
        print("="*70)
        print("\nTemel Çıkarımlar:")
        print("1. Üretim ajanları tüm LangGraph özelliklerini birleştirir")
        print("2. Kontrol noktaları konuşma kalıcılığını sağlar")
        print("3. Onaylar güvenlik korkulukları sağlar")
        print("4. Akış kullanıcı deneyimini iyileştirir")
        print("5. Alt grafikler modüler mimariyi sağlar")
        print("6. Düzgün günlükleme ve metrikler esastır")
        print("\nTebrikler! LangGraph eğitim serisini tamamladınız.")

    except Exception as e:
        print(f"\nGösterim sırasında hata: {e}")
        print("Ollama'nın qwen3:8b modeli ile çalıştığından emin olun")
        import traceback
        traceback.print_exc()
