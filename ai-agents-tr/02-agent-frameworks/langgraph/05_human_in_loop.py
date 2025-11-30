#!/usr/bin/env python3
"""
LangGraph İnsan Döngüde - Etkileşimli Onay İş Akışları
=============================================================

Bu betik, LangGraph kullanarak insan döngüde (human-in-the-loop) desenlerini gösterir.
İnsan onay düğümleri şunları yapmanızı sağlar:
- İnsan incelemesi için yürütmeyi duraklatma
- Kritik eylemlerden önce onay alma
- İş akışı sırasında insan geri bildirimi toplama
- Güvenlik korkulukları uygulama

Temel onay kapılarından gelişmiş inceleme sistemlerine kadar aşamalı olarak oluşturacağız.

Yazar: AI Agents Tutorial Series
"""

from typing import TypedDict, Annotated, Literal, List, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import OllamaLLM
import operator
from datetime import datetime
import json


# ============================================================================
# Bölüm 1: Temel Onay Kapısı
# ============================================================================

class ApprovalState(TypedDict):
    """Onay takibi ile durum."""
    messages: List[str]
    action: str
    approved: bool
    feedback: str


class BasicApprovalAgent:
    """
    İnsan onay kapılarına sahip basit ajan.

    Özellikler:
    - Eylemleri yürütmeden önce duraklatma
    - İnsan onayı bekleme
    - Onay/red işlemlerini yönetme
    - Onay geçmişini izleme
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Onay ajanını başlat."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Onay düğümü ile grafik oluştur."""
        workflow = StateGraph(ApprovalState)

        # Düğümleri ekle
        workflow.add_node("plan", self._plan_action)
        workflow.add_node("human_review", self._wait_for_approval)
        workflow.add_node("execute", self._execute_action)
        workflow.add_node("reject", self._handle_rejection)

        # Giriş noktası
        workflow.set_entry_point("plan")

        # Kenarlar
        workflow.add_edge("plan", "human_review")

        # Onaya dayalı koşullu kenar
        workflow.add_conditional_edges(
            "human_review",
            self._check_approval,
            {
                "approved": "execute",
                "rejected": "reject"
            }
        )

        workflow.add_edge("execute", END)
        workflow.add_edge("reject", END)

        return workflow.compile(checkpointer=self.memory)

    def _plan_action(self, state: ApprovalState) -> ApprovalState:
        """Yürütülecek eylemi planla."""
        messages = state.get("messages", [])

        # Son kullanıcı isteğini al
        if messages:
            request = messages[-1]
            # Eylem planı oluştur
            plan = self.llm.invoke(f"Şunun için kısa bir eylem planı oluştur: {request}")
            action = f"Eylem: {plan}"
        else:
            action = "Planlanmış eylem yok"

        return {
            **state,
            "action": action,
            "approved": False
        }

    def _wait_for_approval(self, state: ApprovalState) -> ApprovalState:
        """
        Bu düğüm, insan incelemesi için bir duraklama noktasını temsil eder.
        Üretimde, bu bir UI veya bildirim sistemi ile entegre olur.
        """
        # Gerçek bir sistemde bu şunları yapar:
        # 1. İnsan incelemeciye bildirim gönder
        # 2. Grafik yürütmesini duraklat
        # 3. Onay yanıtını bekle
        # 4. Onay kararı ile devam et

        print(f"\n[ONAY GEREKLİ]")
        print(f"Eylem: {state.get('action', 'Bilinmiyor')}")
        print("İnsan onayı bekleniyor...")

        # Demo amaçlı olarak onayı simüle edeceğiz
        # Üretimde, onayı enjekte etmek için graph.update_state() kullanın
        return state

    def _check_approval(self, state: ApprovalState) -> Literal["approved", "rejected"]:
        """Eylemin onaylanıp onaylanmadığını kontrol et."""
        return "approved" if state.get("approved", False) else "rejected"

    def _execute_action(self, state: ApprovalState) -> ApprovalState:
        """Onaylanan eylemi yürüt."""
        messages = state.get("messages", [])
        action = state.get("action", "")

        result = f"Yürütüldü: {action}"
        messages.append(result)

        return {
            **state,
            "messages": messages
        }

    def _handle_rejection(self, state: ApprovalState) -> ApprovalState:
        """Reddedilen eylemi işle."""
        messages = state.get("messages", [])
        feedback = state.get("feedback", "Geri bildirim sağlanmadı")

        messages.append(f"Eylem reddedildi. Geri bildirim: {feedback}")

        return {
            **state,
            "messages": messages
        }

    def request_action(self, request: str, thread_id: str = "default") -> str:
        """Onay için eylem isteği gönder."""
        config = {"configurable": {"thread_id": thread_id}}

        result = self.graph.invoke(
            {
                "messages": [request],
                "action": "",
                "approved": False,
                "feedback": ""
            },
            config=config
        )

        return result.get("action", "")

    def approve(self, thread_id: str = "default", feedback: str = "Onaylandı") -> Dict[str, Any]:
        """Bekleyen eylemi onayla."""
        config = {"configurable": {"thread_id": thread_id}}

        # Durumu onayla güncelle
        current_state = self.graph.get_state(config)
        current_state.values["approved"] = True
        current_state.values["feedback"] = feedback

        # Yürütmeye devam et
        result = self.graph.invoke(current_state.values, config=config)
        return result

    def reject(self, thread_id: str = "default", feedback: str = "Reddedildi") -> Dict[str, Any]:
        """Bekleyen eylemi reddet."""
        config = {"configurable": {"thread_id": thread_id}}

        current_state = self.graph.get_state(config)
        current_state.values["approved"] = False
        current_state.values["feedback"] = feedback

        result = self.graph.invoke(current_state.values, config=config)
        return result


# ============================================================================
# Bölüm 2: Etkileşimli İnceleme Sistemi
# ============================================================================

class ReviewState(TypedDict):
    """Etkileşimli inceleme için durum."""
    content: str
    reviews: List[Dict[str, str]]
    current_version: int
    status: str


class InteractiveReviewAgent:
    """
    Yinelemeli geri bildirim ile gelişmiş inceleme sistemi.

    Özellikler:
    - Birden fazla inceleme turu
    - Geri bildirime dayalı revizyon
    - Sürüm takibi
    - Onay iş akışı
    """

    def __init__(self, model: str = "qwen3:8b"):
        """İnceleme ajanını başlat."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Etkileşimli inceleme grafiği oluştur."""
        workflow = StateGraph(ReviewState)

        # Düğümler
        workflow.add_node("generate", self._generate_content)
        workflow.add_node("review", self._await_review)
        workflow.add_node("revise", self._revise_content)
        workflow.add_node("finalize", self._finalize_content)

        # Giriş ve kenarlar
        workflow.set_entry_point("generate")
        workflow.add_edge("generate", "review")

        # İncelemeye dayalı koşullu yönlendirme
        workflow.add_conditional_edges(
            "review",
            self._route_review,
            {
                "revise": "revise",
                "approve": "finalize",
                "pending": "review"
            }
        )

        workflow.add_edge("revise", "review")
        workflow.add_edge("finalize", END)

        return workflow.compile(checkpointer=self.memory)

    def _generate_content(self, state: ReviewState) -> ReviewState:
        """Başlangıç içeriği oluştur."""
        prompt = state.get("content", "")
        version = state.get("current_version", 0)

        if version == 0:
            # İlk oluşturma
            generated = self.llm.invoke(f"Şunun için içerik oluştur: {prompt}")
        else:
            # Geri bildirime dayalı revizyon
            reviews = state.get("reviews", [])
            latest_feedback = reviews[-1]["feedback"] if reviews else ""
            generated = self.llm.invoke(
                f"Bu içeriği geri bildirime göre revize et.\n\nİçerik: {prompt}\n\nGeri bildirim: {latest_feedback}"
            )

        return {
            **state,
            "content": generated,
            "current_version": version + 1,
            "status": "pending_review"
        }

    def _await_review(self, state: ReviewState) -> ReviewState:
        """İnsan incelemesini bekle."""
        print(f"\n[İNCELEME GEREKLİ - Sürüm {state.get('current_version', 0)}]")
        print(f"İçerik: {state.get('content', '')[:200]}...")
        print("İnceleme geri bildirimi bekleniyor...")

        return state

    def _route_review(self, state: ReviewState) -> Literal["revise", "approve", "pending"]:
        """İnceleme durumuna göre yönlendir."""
        status = state.get("status", "pending_review")

        if status == "approved":
            return "approve"
        elif status == "needs_revision":
            return "revise"
        else:
            return "pending"

    def _revise_content(self, state: ReviewState) -> ReviewState:
        """Geri bildirime göre içeriği revize et."""
        reviews = state.get("reviews", [])
        content = state.get("content", "")

        if reviews:
            latest = reviews[-1]
            feedback = latest["feedback"]

            revised = self.llm.invoke(
                f"Bu içeriği revize et:\n\n{content}\n\nGeri bildirim: {feedback}\n\nGeliştirilmiş sürümü sağla:"
            )

            return {
                **state,
                "content": revised,
                "current_version": state.get("current_version", 0) + 1,
                "status": "pending_review"
            }

        return state

    def _finalize_content(self, state: ReviewState) -> ReviewState:
        """Onaylanan içeriği sonlandır."""
        return {
            **state,
            "status": "finalized"
        }

    def create_draft(self, prompt: str, thread_id: str) -> str:
        """İnceleme için ilk taslağı oluştur."""
        config = {"configurable": {"thread_id": thread_id}}

        result = self.graph.invoke(
            {
                "content": prompt,
                "reviews": [],
                "current_version": 0,
                "status": "pending_review"
            },
            config=config
        )

        return result.get("content", "")

    def submit_review(self, feedback: str, approved: bool, thread_id: str) -> Dict[str, Any]:
        """İnceleme geri bildirimi gönder."""
        config = {"configurable": {"thread_id": thread_id}}
        current_state = self.graph.get_state(config)

        reviews = current_state.values.get("reviews", [])
        reviews.append({
            "version": current_state.values.get("current_version", 0),
            "feedback": feedback,
            "approved": approved,
            "timestamp": datetime.now().isoformat()
        })

        current_state.values["reviews"] = reviews
        current_state.values["status"] = "approved" if approved else "needs_revision"

        result = self.graph.invoke(current_state.values, config=config)
        return result


# ============================================================================
# Bölüm 3: Çok Adımlı Onay İş Akışı
# ============================================================================

class WorkflowState(TypedDict):
    """Karmaşık iş akışı durumu."""
    task: str
    steps: List[Dict[str, Any]]
    current_step: int
    approvals: Dict[str, bool]


class MultiStepApprovalAgent:
    """
    Birden fazla onay kapısına sahip karmaşık iş akışı.

    Özellikler:
    - Birden fazla onay noktası
    - Adım adım yürütme
    - Reddedilme durumunda geri alma
    - İlerleme takibi
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Çok adımlı ajanı başlat."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Çok adımlı onay iş akışı oluştur."""
        workflow = StateGraph(WorkflowState)

        # Düğümler
        workflow.add_node("plan_steps", self._plan_steps)
        workflow.add_node("execute_step", self._execute_step)
        workflow.add_node("approval_gate", self._approval_gate)
        workflow.add_node("complete", self._complete_workflow)

        # Giriş
        workflow.set_entry_point("plan_steps")

        # Kenarlar
        workflow.add_edge("plan_steps", "execute_step")
        workflow.add_edge("execute_step", "approval_gate")

        # Koşullu yönlendirme
        workflow.add_conditional_edges(
            "approval_gate",
            self._check_workflow_status,
            {
                "continue": "execute_step",
                "complete": "complete",
                "waiting": "approval_gate"
            }
        )

        workflow.add_edge("complete", END)

        return workflow.compile(checkpointer=self.memory)

    def _plan_steps(self, state: WorkflowState) -> WorkflowState:
        """İş akışı adımlarını planla."""
        task = state.get("task", "")

        # Adım planı oluştur
        plan_prompt = f"Bu görevi 3-5 adıma böl: {task}"
        plan = self.llm.invoke(plan_prompt)

        # Adımlara ayrıştır (basitleştirilmiş)
        steps = [
            {"name": f"Adım {i+1}", "description": plan, "status": "pending"}
            for i in range(3)
        ]

        return {
            **state,
            "steps": steps,
            "current_step": 0,
            "approvals": {}
        }

    def _execute_step(self, state: WorkflowState) -> WorkflowState:
        """Mevcut adımı yürüt."""
        steps = state.get("steps", [])
        current_idx = state.get("current_step", 0)

        if current_idx < len(steps):
            step = steps[current_idx]
            step["status"] = "executed"
            step["result"] = f"Yürütüldü: {step['description'][:50]}"
            steps[current_idx] = step

        return {
            **state,
            "steps": steps
        }

    def _approval_gate(self, state: WorkflowState) -> WorkflowState:
        """Adım onayı bekle."""
        current_idx = state.get("current_step", 0)
        steps = state.get("steps", [])

        if current_idx < len(steps):
            step = steps[current_idx]
            print(f"\n[ONAY KAPISI {current_idx + 1}/{len(steps)}]")
            print(f"Adım: {step['name']}")
            print(f"Sonuç: {step.get('result', 'N/A')}")

        return state

    def _check_workflow_status(self, state: WorkflowState) -> Literal["continue", "complete", "waiting"]:
        """İş akışı ilerlemesini kontrol et."""
        current_idx = state.get("current_step", 0)
        steps = state.get("steps", [])
        approvals = state.get("approvals", {})

        step_key = f"step_{current_idx}"

        # Mevcut adımın onaylanıp onaylanmadığını kontrol et
        if step_key not in approvals:
            return "waiting"

        if not approvals[step_key]:
            return "complete"  # Reddedildi, iş akışını bitir

        # Sonraki adıma geç
        next_idx = current_idx + 1

        if next_idx >= len(steps):
            return "complete"

        # Sonraki adım için durumu güncelle
        state["current_step"] = next_idx
        return "continue"

    def _complete_workflow(self, state: WorkflowState) -> WorkflowState:
        """İş akışını tamamla."""
        steps = state.get("steps", [])

        for step in steps:
            if step["status"] != "rejected":
                step["status"] = "completed"

        return {
            **state,
            "steps": steps
        }

    def start_workflow(self, task: str, thread_id: str) -> List[Dict[str, Any]]:
        """Çok adımlı iş akışını başlat."""
        config = {"configurable": {"thread_id": thread_id}}

        result = self.graph.invoke(
            {
                "task": task,
                "steps": [],
                "current_step": 0,
                "approvals": {}
            },
            config=config
        )

        return result.get("steps", [])

    def approve_step(self, step_number: int, thread_id: str) -> Dict[str, Any]:
        """Belirli adımı onayla."""
        config = {"configurable": {"thread_id": thread_id}}
        current_state = self.graph.get_state(config)

        approvals = current_state.values.get("approvals", {})
        approvals[f"step_{step_number}"] = True
        current_state.values["approvals"] = approvals

        result = self.graph.invoke(current_state.values, config=config)
        return result


# ============================================================================
# Bölüm 4: Üretim İnsan Döngüde Sistemi
# ============================================================================

class ProductionHILState(TypedDict):
    """Üretim sınıfı HIL durumu."""
    request: str
    analysis: Dict[str, Any]
    risk_level: str
    approvers: List[str]
    approval_status: Dict[str, bool]
    execution_log: List[str]


class ProductionHumanInLoop:
    """
    Kurumsal sınıf insan döngüde sistemi.

    Özellikler:
    - Riske dayalı onay yönlendirme
    - Birden fazla onaylayıcı
    - Denetim günlüğü
    - Zaman aşımı yönetimi
    - Yükseltme yolları
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Üretim HIL sistemini başlat."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.memory = MemorySaver()
        self.graph = self._build_graph()
        self.approval_rules = {
            "low": 1,     # Düşük risk: 1 onaylayıcı
            "medium": 2,  # Orta risk: 2 onaylayıcı
            "high": 3     # Yüksek risk: 3 onaylayıcı
        }

    def _build_graph(self) -> StateGraph:
        """Üretim HIL grafiği oluştur."""
        workflow = StateGraph(ProductionHILState)

        # Düğümler
        workflow.add_node("analyze_request", self._analyze_request)
        workflow.add_node("determine_risk", self._determine_risk)
        workflow.add_node("assign_approvers", self._assign_approvers)
        workflow.add_node("collect_approvals", self._collect_approvals)
        workflow.add_node("execute_request", self._execute_request)
        workflow.add_node("log_completion", self._log_completion)

        # Akış
        workflow.set_entry_point("analyze_request")
        workflow.add_edge("analyze_request", "determine_risk")
        workflow.add_edge("determine_risk", "assign_approvers")
        workflow.add_edge("assign_approvers", "collect_approvals")

        workflow.add_conditional_edges(
            "collect_approvals",
            self._check_approvals,
            {
                "approved": "execute_request",
                "waiting": "collect_approvals",
                "rejected": "log_completion"
            }
        )

        workflow.add_edge("execute_request", "log_completion")
        workflow.add_edge("log_completion", END)

        return workflow.compile(checkpointer=self.memory)

    def _analyze_request(self, state: ProductionHILState) -> ProductionHILState:
        """Gelen isteği analiz et."""
        request = state.get("request", "")

        analysis_prompt = f"Bu isteği analiz et ve potansiyel riskleri belirle: {request}"
        analysis = self.llm.invoke(analysis_prompt)

        return {
            **state,
            "analysis": {
                "summary": analysis[:200],
                "timestamp": datetime.now().isoformat()
            },
            "execution_log": [f"İstek {datetime.now().isoformat()} tarihinde analiz edildi"]
        }

    def _determine_risk(self, state: ProductionHILState) -> ProductionHILState:
        """Risk seviyesini belirle."""
        request = state.get("request", "").lower()

        # Basit risk sınıflandırması (üretimde ML modeli kullanın)
        if any(word in request for word in ["sil", "kaldır", "düşür", "kritik", "delete", "remove", "drop", "critical"]):
            risk_level = "high"
        elif any(word in request for word in ["güncelle", "değiştir", "update", "modify", "change"]):
            risk_level = "medium"
        else:
            risk_level = "low"

        log = state.get("execution_log", [])
        log.append(f"Risk seviyesi belirlendi: {risk_level}")

        return {
            **state,
            "risk_level": risk_level,
            "execution_log": log
        }

    def _assign_approvers(self, state: ProductionHILState) -> ProductionHILState:
        """Riske göre onaylayıcıları ata."""
        risk_level = state.get("risk_level", "low")
        required_approvers = self.approval_rules.get(risk_level, 1)

        # Üretimde, rollere göre gerçek onaylayıcılar atayın
        approvers = [f"onaylayıcı_{i+1}" for i in range(required_approvers)]

        log = state.get("execution_log", [])
        log.append(f"{len(approvers)} onaylayıcı atandı: {', '.join(approvers)}")

        return {
            **state,
            "approvers": approvers,
            "approval_status": {},
            "execution_log": log
        }

    def _collect_approvals(self, state: ProductionHILState) -> ProductionHILState:
        """Atanan onaylayıcılardan onayları topla."""
        approvers = state.get("approvers", [])
        approval_status = state.get("approval_status", {})

        print(f"\n[ONAY TOPLAMA]")
        print(f"Risk Seviyesi: {state.get('risk_level', 'bilinmiyor')}")
        print(f"Gerekli onaylayıcılar: {len(approvers)}")
        print(f"Mevcut onaylar: {sum(approval_status.values())}/{len(approvers)}")

        return state

    def _check_approvals(self, state: ProductionHILState) -> Literal["approved", "waiting", "rejected"]:
        """Onay durumunu kontrol et."""
        approvers = state.get("approvers", [])
        approval_status = state.get("approval_status", {})

        # Herhangi bir ret olup olmadığını kontrol et
        if any(not v for v in approval_status.values()):
            return "rejected"

        # Hepsinin onaylanıp onaylanmadığını kontrol et
        if len(approval_status) == len(approvers) and all(approval_status.values()):
            return "approved"

        return "waiting"

    def _execute_request(self, state: ProductionHILState) -> ProductionHILState:
        """Onaylanan isteği yürüt."""
        request = state.get("request", "")
        log = state.get("execution_log", [])

        # Yürütmeyi simüle et
        result = f"Yürütüldü: {request}"
        log.append(f"İstek {datetime.now().isoformat()} tarihinde başarıyla yürütüldü")
        log.append(result)

        return {
            **state,
            "execution_log": log
        }

    def _log_completion(self, state: ProductionHILState) -> ProductionHILState:
        """İş akışı tamamlanmasını günlüğe kaydet."""
        log = state.get("execution_log", [])
        log.append(f"İş akışı {datetime.now().isoformat()} tarihinde tamamlandı")

        return {
            **state,
            "execution_log": log
        }

    def submit_request(self, request: str, thread_id: str) -> Dict[str, Any]:
        """Onay için istek gönder."""
        config = {"configurable": {"thread_id": thread_id}}

        result = self.graph.invoke(
            {
                "request": request,
                "analysis": {},
                "risk_level": "",
                "approvers": [],
                "approval_status": {},
                "execution_log": []
            },
            config=config
        )

        return {
            "risk_level": result.get("risk_level"),
            "approvers": result.get("approvers"),
            "status": "pending_approval"
        }

    def record_approval(self, approver: str, approved: bool, thread_id: str) -> Dict[str, Any]:
        """Onay kararını kaydet."""
        config = {"configurable": {"thread_id": thread_id}}
        current_state = self.graph.get_state(config)

        approval_status = current_state.values.get("approval_status", {})
        approval_status[approver] = approved

        log = current_state.values.get("execution_log", [])
        log.append(f"{approver} {datetime.now().isoformat()} tarihinde {'onayladı' if approved else 'reddetti'}")

        current_state.values["approval_status"] = approval_status
        current_state.values["execution_log"] = log

        result = self.graph.invoke(current_state.values, config=config)
        return result


# ============================================================================
# GÖSTERİMLER
# ============================================================================

def demo_basic_approval():
    """Temel onay kapısını göster."""
    print("\n" + "="*70)
    print("DEMO 1: Temel Onay Kapısı")
    print("="*70)

    agent = BasicApprovalAgent()

    print("\n1. Eylem isteği gönderiliyor...")
    action = agent.request_action("Tüm kullanıcılara e-posta gönder", "demo1")
    print(f"Planlanan eylem: {action[:100]}...")

    print("\n2. Onay simüle ediliyor...")
    result = agent.approve("demo1", "İncelemeden sonra onaylandı")
    print(f"Yürütme sonucu: {result.get('messages', [])[-1]}")


def demo_interactive_review():
    """Etkileşimli inceleme sistemini göster."""
    print("\n" + "="*70)
    print("DEMO 2: Etkileşimli İnceleme Sistemi")
    print("="*70)

    agent = InteractiveReviewAgent()

    print("\n1. İlk taslak oluşturuluyor...")
    draft = agent.create_draft("Yapay zeka hakkında bir blog yazısı yaz", "demo2")
    print(f"Taslak (v1): {draft[:150]}...")

    print("\n2. Revizyon geri bildirimi gönderiliyor...")
    result = agent.submit_review("Daha teknik yap", False, "demo2")
    print(f"Durum: {result.get('status')}")
    print(f"Sürüm: {result.get('current_version')}")


def demo_multi_step():
    """Çok adımlı iş akışını göster."""
    print("\n" + "="*70)
    print("DEMO 3: Çok Adımlı Onay İş Akışı")
    print("="*70)

    agent = MultiStepApprovalAgent()

    print("\n1. İş akışı başlatılıyor...")
    steps = agent.start_workflow("Yeni özelliği üretime dağıt", "demo3")
    print(f"Toplam adım: {len(steps)}")

    print("\n2. Adım 0 onaylanıyor...")
    result = agent.approve_step(0, "demo3")
    print(f"İş akışı durumu: {result.get('steps', [])[0].get('status')}")


def demo_production_hil():
    """Üretim HIL sistemini göster."""
    print("\n" + "="*70)
    print("DEMO 4: Üretim İnsan Döngüde Sistemi")
    print("="*70)

    system = ProductionHumanInLoop()

    print("\n1. Yüksek riskli istek gönderiliyor...")
    result = system.submit_request("Kullanıcı veritabanını sil", "demo4")
    print(f"Risk seviyesi: {result.get('risk_level')}")
    print(f"Gerekli onaylayıcılar: {len(result.get('approvers', []))}")

    print("\n2. Onaylar kaydediliyor...")
    for approver in result.get("approvers", [])[:2]:
        system.record_approval(approver, True, "demo4")
        print(f"  {approver}: Onaylandı")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("LangGraph İnsan Döngüde Eğitimi")
    print("="*70)
    print("\nBu eğitim, iş akışlarında insan onay desenlerini gösterir.")
    print("HIL, güvenlik, kalite kontrol ve insan gözetimi sağlar.")

    try:
        demo_basic_approval()
        demo_interactive_review()
        demo_multi_step()
        demo_production_hil()

        print("\n" + "="*70)
        print("Eğitim başarıyla tamamlandı!")
        print("="*70)
        print("\nTemel Çıkarımlar:")
        print("1. Onay kapıları, insan incelemesi için yürütmeyi duraklatır")
        print("2. Riske dayalı yönlendirme, onay gereksinimlerini belirler")
        print("3. Durum kalıcılığı, asenkron onay iş akışlarını sağlar")
        print("4. Denetim günlükleri tüm onay kararlarını izler")
        print("\nSıradaki: 06_subgraphs.py - İç içe iş akışı kompozisyonu")

    except Exception as e:
        print(f"\nGösterim sırasında hata: {e}")
        print("Ollama'nın qwen3:8b modeli ile çalıştığından emin olun")
