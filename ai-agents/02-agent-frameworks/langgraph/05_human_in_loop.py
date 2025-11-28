#!/usr/bin/env python3
"""
LangGraph Human-in-the-Loop - Interactive Approval Workflows
=============================================================

This script demonstrates human-in-the-loop patterns using LangGraph.
Human approval nodes allow you to:
- Pause execution for human review
- Get approval before critical actions
- Collect human feedback during workflow
- Implement safety guardrails

We'll build from basic approval gates to sophisticated review systems.

Author: AI Agents Tutorial Series
"""

from typing import TypedDict, Annotated, Literal, List, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import OllamaLLM
import operator
from datetime import datetime
import json


# ============================================================================
# Part 1: Basic Approval Gate
# ============================================================================

class ApprovalState(TypedDict):
    """State with approval tracking."""
    messages: List[str]
    action: str
    approved: bool
    feedback: str


class BasicApprovalAgent:
    """
    Simple agent with human approval gates.

    Features:
    - Pause before executing actions
    - Wait for human approval
    - Handle approval/rejection
    - Track approval history
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize approval agent."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build graph with approval node."""
        workflow = StateGraph(ApprovalState)

        # Add nodes
        workflow.add_node("plan", self._plan_action)
        workflow.add_node("human_review", self._wait_for_approval)
        workflow.add_node("execute", self._execute_action)
        workflow.add_node("reject", self._handle_rejection)

        # Entry point
        workflow.set_entry_point("plan")

        # Edges
        workflow.add_edge("plan", "human_review")

        # Conditional edge based on approval
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
        """Plan the action to execute."""
        messages = state.get("messages", [])

        # Get last user request
        if messages:
            request = messages[-1]
            # Generate action plan
            plan = self.llm.invoke(f"Create a brief action plan for: {request}")
            action = f"Action: {plan}"
        else:
            action = "No action planned"

        return {
            **state,
            "action": action,
            "approved": False
        }

    def _wait_for_approval(self, state: ApprovalState) -> ApprovalState:
        """
        This node represents a pause point for human review.
        In production, this would integrate with a UI or notification system.
        """
        # In a real system, this would:
        # 1. Send notification to human reviewer
        # 2. Pause graph execution
        # 3. Wait for approval response
        # 4. Resume with approval decision

        print(f"\n[APPROVAL REQUIRED]")
        print(f"Action: {state.get('action', 'Unknown')}")
        print("Waiting for human approval...")

        # For demo purposes, we'll simulate approval
        # In production, use graph.update_state() to inject approval
        return state

    def _check_approval(self, state: ApprovalState) -> Literal["approved", "rejected"]:
        """Check if action was approved."""
        return "approved" if state.get("approved", False) else "rejected"

    def _execute_action(self, state: ApprovalState) -> ApprovalState:
        """Execute approved action."""
        messages = state.get("messages", [])
        action = state.get("action", "")

        result = f"Executed: {action}"
        messages.append(result)

        return {
            **state,
            "messages": messages
        }

    def _handle_rejection(self, state: ApprovalState) -> ApprovalState:
        """Handle rejected action."""
        messages = state.get("messages", [])
        feedback = state.get("feedback", "No feedback provided")

        messages.append(f"Action rejected. Feedback: {feedback}")

        return {
            **state,
            "messages": messages
        }

    def request_action(self, request: str, thread_id: str = "default") -> str:
        """Submit action request for approval."""
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

    def approve(self, thread_id: str = "default", feedback: str = "Approved") -> Dict[str, Any]:
        """Approve pending action."""
        config = {"configurable": {"thread_id": thread_id}}

        # Update state with approval
        current_state = self.graph.get_state(config)
        current_state.values["approved"] = True
        current_state.values["feedback"] = feedback

        # Continue execution
        result = self.graph.invoke(current_state.values, config=config)
        return result

    def reject(self, thread_id: str = "default", feedback: str = "Rejected") -> Dict[str, Any]:
        """Reject pending action."""
        config = {"configurable": {"thread_id": thread_id}}

        current_state = self.graph.get_state(config)
        current_state.values["approved"] = False
        current_state.values["feedback"] = feedback

        result = self.graph.invoke(current_state.values, config=config)
        return result


# ============================================================================
# Part 2: Interactive Review System
# ============================================================================

class ReviewState(TypedDict):
    """State for interactive review."""
    content: str
    reviews: List[Dict[str, str]]
    current_version: int
    status: str


class InteractiveReviewAgent:
    """
    Advanced review system with iterative feedback.

    Features:
    - Multiple review rounds
    - Revision based on feedback
    - Version tracking
    - Approval workflow
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize review agent."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build interactive review graph."""
        workflow = StateGraph(ReviewState)

        # Nodes
        workflow.add_node("generate", self._generate_content)
        workflow.add_node("review", self._await_review)
        workflow.add_node("revise", self._revise_content)
        workflow.add_node("finalize", self._finalize_content)

        # Entry and edges
        workflow.set_entry_point("generate")
        workflow.add_edge("generate", "review")

        # Conditional routing based on review
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
        """Generate initial content."""
        prompt = state.get("content", "")
        version = state.get("current_version", 0)

        if version == 0:
            # Initial generation
            generated = self.llm.invoke(f"Generate content for: {prompt}")
        else:
            # Revision based on feedback
            reviews = state.get("reviews", [])
            latest_feedback = reviews[-1]["feedback"] if reviews else ""
            generated = self.llm.invoke(
                f"Revise this content based on feedback.\n\nContent: {prompt}\n\nFeedback: {latest_feedback}"
            )

        return {
            **state,
            "content": generated,
            "current_version": version + 1,
            "status": "pending_review"
        }

    def _await_review(self, state: ReviewState) -> ReviewState:
        """Wait for human review."""
        print(f"\n[REVIEW REQUIRED - Version {state.get('current_version', 0)}]")
        print(f"Content: {state.get('content', '')[:200]}...")
        print("Awaiting review feedback...")

        return state

    def _route_review(self, state: ReviewState) -> Literal["revise", "approve", "pending"]:
        """Route based on review status."""
        status = state.get("status", "pending_review")

        if status == "approved":
            return "approve"
        elif status == "needs_revision":
            return "revise"
        else:
            return "pending"

    def _revise_content(self, state: ReviewState) -> ReviewState:
        """Revise content based on feedback."""
        reviews = state.get("reviews", [])
        content = state.get("content", "")

        if reviews:
            latest = reviews[-1]
            feedback = latest["feedback"]

            revised = self.llm.invoke(
                f"Revise this content:\n\n{content}\n\nFeedback: {feedback}\n\nProvide improved version:"
            )

            return {
                **state,
                "content": revised,
                "current_version": state.get("current_version", 0) + 1,
                "status": "pending_review"
            }

        return state

    def _finalize_content(self, state: ReviewState) -> ReviewState:
        """Finalize approved content."""
        return {
            **state,
            "status": "finalized"
        }

    def create_draft(self, prompt: str, thread_id: str) -> str:
        """Create initial draft for review."""
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
        """Submit review feedback."""
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
# Part 3: Multi-Step Approval Workflow
# ============================================================================

class WorkflowState(TypedDict):
    """Complex workflow state."""
    task: str
    steps: List[Dict[str, Any]]
    current_step: int
    approvals: Dict[str, bool]


class MultiStepApprovalAgent:
    """
    Complex workflow with multiple approval gates.

    Features:
    - Multiple approval points
    - Step-by-step execution
    - Rollback on rejection
    - Progress tracking
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize multi-step agent."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.memory = MemorySaver()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build multi-step approval workflow."""
        workflow = StateGraph(WorkflowState)

        # Nodes
        workflow.add_node("plan_steps", self._plan_steps)
        workflow.add_node("execute_step", self._execute_step)
        workflow.add_node("approval_gate", self._approval_gate)
        workflow.add_node("complete", self._complete_workflow)

        # Entry
        workflow.set_entry_point("plan_steps")

        # Edges
        workflow.add_edge("plan_steps", "execute_step")
        workflow.add_edge("execute_step", "approval_gate")

        # Conditional routing
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
        """Plan workflow steps."""
        task = state.get("task", "")

        # Generate step plan
        plan_prompt = f"Break down this task into 3-5 steps: {task}"
        plan = self.llm.invoke(plan_prompt)

        # Parse into steps (simplified)
        steps = [
            {"name": f"Step {i+1}", "description": plan, "status": "pending"}
            for i in range(3)
        ]

        return {
            **state,
            "steps": steps,
            "current_step": 0,
            "approvals": {}
        }

    def _execute_step(self, state: WorkflowState) -> WorkflowState:
        """Execute current step."""
        steps = state.get("steps", [])
        current_idx = state.get("current_step", 0)

        if current_idx < len(steps):
            step = steps[current_idx]
            step["status"] = "executed"
            step["result"] = f"Executed: {step['description'][:50]}"
            steps[current_idx] = step

        return {
            **state,
            "steps": steps
        }

    def _approval_gate(self, state: WorkflowState) -> WorkflowState:
        """Wait for step approval."""
        current_idx = state.get("current_step", 0)
        steps = state.get("steps", [])

        if current_idx < len(steps):
            step = steps[current_idx]
            print(f"\n[APPROVAL GATE {current_idx + 1}/{len(steps)}]")
            print(f"Step: {step['name']}")
            print(f"Result: {step.get('result', 'N/A')}")

        return state

    def _check_workflow_status(self, state: WorkflowState) -> Literal["continue", "complete", "waiting"]:
        """Check workflow progress."""
        current_idx = state.get("current_step", 0)
        steps = state.get("steps", [])
        approvals = state.get("approvals", {})

        step_key = f"step_{current_idx}"

        # Check if current step is approved
        if step_key not in approvals:
            return "waiting"

        if not approvals[step_key]:
            return "complete"  # Rejected, end workflow

        # Move to next step
        next_idx = current_idx + 1

        if next_idx >= len(steps):
            return "complete"

        # Update state for next step
        state["current_step"] = next_idx
        return "continue"

    def _complete_workflow(self, state: WorkflowState) -> WorkflowState:
        """Complete workflow."""
        steps = state.get("steps", [])

        for step in steps:
            if step["status"] != "rejected":
                step["status"] = "completed"

        return {
            **state,
            "steps": steps
        }

    def start_workflow(self, task: str, thread_id: str) -> List[Dict[str, Any]]:
        """Start multi-step workflow."""
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
        """Approve specific step."""
        config = {"configurable": {"thread_id": thread_id}}
        current_state = self.graph.get_state(config)

        approvals = current_state.values.get("approvals", {})
        approvals[f"step_{step_number}"] = True
        current_state.values["approvals"] = approvals

        result = self.graph.invoke(current_state.values, config=config)
        return result


# ============================================================================
# Part 4: Production Human-in-Loop System
# ============================================================================

class ProductionHILState(TypedDict):
    """Production-grade HIL state."""
    request: str
    analysis: Dict[str, Any]
    risk_level: str
    approvers: List[str]
    approval_status: Dict[str, bool]
    execution_log: List[str]


class ProductionHumanInLoop:
    """
    Enterprise-grade human-in-the-loop system.

    Features:
    - Risk-based approval routing
    - Multiple approvers
    - Audit logging
    - Timeout handling
    - Escalation paths
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize production HIL system."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.memory = MemorySaver()
        self.graph = self._build_graph()
        self.approval_rules = {
            "low": 1,     # Low risk: 1 approver
            "medium": 2,  # Medium risk: 2 approvers
            "high": 3     # High risk: 3 approvers
        }

    def _build_graph(self) -> StateGraph:
        """Build production HIL graph."""
        workflow = StateGraph(ProductionHILState)

        # Nodes
        workflow.add_node("analyze_request", self._analyze_request)
        workflow.add_node("determine_risk", self._determine_risk)
        workflow.add_node("assign_approvers", self._assign_approvers)
        workflow.add_node("collect_approvals", self._collect_approvals)
        workflow.add_node("execute_request", self._execute_request)
        workflow.add_node("log_completion", self._log_completion)

        # Flow
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
        """Analyze incoming request."""
        request = state.get("request", "")

        analysis_prompt = f"Analyze this request and identify potential risks: {request}"
        analysis = self.llm.invoke(analysis_prompt)

        return {
            **state,
            "analysis": {
                "summary": analysis[:200],
                "timestamp": datetime.now().isoformat()
            },
            "execution_log": [f"Request analyzed at {datetime.now().isoformat()}"]
        }

    def _determine_risk(self, state: ProductionHILState) -> ProductionHILState:
        """Determine risk level."""
        request = state.get("request", "").lower()

        # Simple risk classification (in production, use ML model)
        if any(word in request for word in ["delete", "remove", "drop", "critical"]):
            risk_level = "high"
        elif any(word in request for word in ["update", "modify", "change"]):
            risk_level = "medium"
        else:
            risk_level = "low"

        log = state.get("execution_log", [])
        log.append(f"Risk level determined: {risk_level}")

        return {
            **state,
            "risk_level": risk_level,
            "execution_log": log
        }

    def _assign_approvers(self, state: ProductionHILState) -> ProductionHILState:
        """Assign approvers based on risk."""
        risk_level = state.get("risk_level", "low")
        required_approvers = self.approval_rules.get(risk_level, 1)

        # In production, assign real approvers based on roles
        approvers = [f"approver_{i+1}" for i in range(required_approvers)]

        log = state.get("execution_log", [])
        log.append(f"Assigned {len(approvers)} approvers: {', '.join(approvers)}")

        return {
            **state,
            "approvers": approvers,
            "approval_status": {},
            "execution_log": log
        }

    def _collect_approvals(self, state: ProductionHILState) -> ProductionHILState:
        """Collect approvals from assigned approvers."""
        approvers = state.get("approvers", [])
        approval_status = state.get("approval_status", {})

        print(f"\n[APPROVAL COLLECTION]")
        print(f"Risk Level: {state.get('risk_level', 'unknown')}")
        print(f"Required approvers: {len(approvers)}")
        print(f"Current approvals: {sum(approval_status.values())}/{len(approvers)}")

        return state

    def _check_approvals(self, state: ProductionHILState) -> Literal["approved", "waiting", "rejected"]:
        """Check approval status."""
        approvers = state.get("approvers", [])
        approval_status = state.get("approval_status", {})

        # Check if any rejections
        if any(not v for v in approval_status.values()):
            return "rejected"

        # Check if all approved
        if len(approval_status) == len(approvers) and all(approval_status.values()):
            return "approved"

        return "waiting"

    def _execute_request(self, state: ProductionHILState) -> ProductionHILState:
        """Execute approved request."""
        request = state.get("request", "")
        log = state.get("execution_log", [])

        # Simulate execution
        result = f"Executed: {request}"
        log.append(f"Request executed successfully at {datetime.now().isoformat()}")
        log.append(result)

        return {
            **state,
            "execution_log": log
        }

    def _log_completion(self, state: ProductionHILState) -> ProductionHILState:
        """Log workflow completion."""
        log = state.get("execution_log", [])
        log.append(f"Workflow completed at {datetime.now().isoformat()}")

        return {
            **state,
            "execution_log": log
        }

    def submit_request(self, request: str, thread_id: str) -> Dict[str, Any]:
        """Submit request for approval."""
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
        """Record approval decision."""
        config = {"configurable": {"thread_id": thread_id}}
        current_state = self.graph.get_state(config)

        approval_status = current_state.values.get("approval_status", {})
        approval_status[approver] = approved

        log = current_state.values.get("execution_log", [])
        log.append(f"{approver} {'approved' if approved else 'rejected'} at {datetime.now().isoformat()}")

        current_state.values["approval_status"] = approval_status
        current_state.values["execution_log"] = log

        result = self.graph.invoke(current_state.values, config=config)
        return result


# ============================================================================
# DEMONSTRATIONS
# ============================================================================

def demo_basic_approval():
    """Demonstrate basic approval gate."""
    print("\n" + "="*70)
    print("DEMO 1: Basic Approval Gate")
    print("="*70)

    agent = BasicApprovalAgent()

    print("\n1. Submitting action request...")
    action = agent.request_action("Send email to all users", "demo1")
    print(f"Planned action: {action[:100]}...")

    print("\n2. Simulating approval...")
    result = agent.approve("demo1", "Approved after review")
    print(f"Execution result: {result.get('messages', [])[-1]}")


def demo_interactive_review():
    """Demonstrate interactive review system."""
    print("\n" + "="*70)
    print("DEMO 2: Interactive Review System")
    print("="*70)

    agent = InteractiveReviewAgent()

    print("\n1. Creating initial draft...")
    draft = agent.create_draft("Write a blog post about AI", "demo2")
    print(f"Draft (v1): {draft[:150]}...")

    print("\n2. Submitting revision feedback...")
    result = agent.submit_review("Make it more technical", False, "demo2")
    print(f"Status: {result.get('status')}")
    print(f"Version: {result.get('current_version')}")


def demo_multi_step():
    """Demonstrate multi-step workflow."""
    print("\n" + "="*70)
    print("DEMO 3: Multi-Step Approval Workflow")
    print("="*70)

    agent = MultiStepApprovalAgent()

    print("\n1. Starting workflow...")
    steps = agent.start_workflow("Deploy new feature to production", "demo3")
    print(f"Total steps: {len(steps)}")

    print("\n2. Approving step 0...")
    result = agent.approve_step(0, "demo3")
    print(f"Workflow status: {result.get('steps', [])[0].get('status')}")


def demo_production_hil():
    """Demonstrate production HIL system."""
    print("\n" + "="*70)
    print("DEMO 4: Production Human-in-Loop System")
    print("="*70)

    system = ProductionHumanInLoop()

    print("\n1. Submitting high-risk request...")
    result = system.submit_request("Delete user database", "demo4")
    print(f"Risk level: {result.get('risk_level')}")
    print(f"Required approvers: {len(result.get('approvers', []))}")

    print("\n2. Recording approvals...")
    for approver in result.get("approvers", [])[:2]:
        system.record_approval(approver, True, "demo4")
        print(f"  {approver}: Approved")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("LangGraph Human-in-the-Loop Tutorial")
    print("="*70)
    print("\nThis tutorial demonstrates human approval patterns in workflows.")
    print("HIL enables safety, quality control, and human oversight.")

    try:
        demo_basic_approval()
        demo_interactive_review()
        demo_multi_step()
        demo_production_hil()

        print("\n" + "="*70)
        print("Tutorial completed successfully!")
        print("="*70)
        print("\nKey Takeaways:")
        print("1. Approval gates pause execution for human review")
        print("2. Risk-based routing determines approval requirements")
        print("3. State persistence enables async approval workflows")
        print("4. Audit logs track all approval decisions")
        print("\nNext: 06_subgraphs.py - Nested workflow composition")

    except Exception as e:
        print(f"\nError during demonstration: {e}")
        print("Make sure Ollama is running with qwen3:8b model")
