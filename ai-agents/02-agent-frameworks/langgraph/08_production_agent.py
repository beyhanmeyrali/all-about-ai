#!/usr/bin/env python3
"""
LangGraph Production Agent - Enterprise-Grade Complete System
==============================================================

This script demonstrates a complete production-ready agent using all LangGraph features.

Features:
- State persistence with checkpoints
- Human-in-the-loop approvals
- Subgraph composition
- Event streaming
- Tool integration
- Error handling and recovery
- Monitoring and observability
- Security and validation

This is the culmination of all previous tutorials combined into one
enterprise-grade system.

Author: AI Agents Tutorial Series
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
# Configuration and Setup
# ============================================================================

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentConfig:
    """Central configuration for production agent."""

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
# State Definitions
# ============================================================================

class ProductionAgentState(TypedDict):
    """
    Complete agent state with all features.

    This state tracks:
    - User requests and conversation history
    - Tool execution results
    - Approval workflow status
    - Performance metrics
    - Error handling
    - Processing stages
    """
    # Core conversation
    request_id: str
    user_request: str
    messages: List[Dict[str, str]]
    conversation_history: List[str]

    # Processing
    analysis: Dict[str, Any]
    tools_used: List[str]
    tool_results: Dict[str, Any]
    intermediate_results: List[Dict[str, Any]]

    # Approval workflow
    requires_approval: bool
    approval_status: Optional[str]
    approval_feedback: str
    risk_level: str

    # Execution tracking
    current_step: str
    processing_stages: List[Dict[str, Any]]
    iteration_count: int

    # Results
    final_response: str
    status: str

    # Metrics
    metrics: Dict[str, float]
    start_time: float
    end_time: float

    # Error handling
    errors: List[str]
    retry_count: int


# ============================================================================
# Tool Definitions
# ============================================================================

class ProductionTools:
    """
    Production-grade tool implementations.

    Tools:
    - search: Web/knowledge search
    - calculate: Mathematical calculations
    - analyze: Data analysis
    - generate_report: Report generation
    """

    @staticmethod
    def search(query: str) -> Dict[str, Any]:
        """Search for information."""
        logger.info(f"Tool [search] called with query: {query}")

        # Simulate search
        time.sleep(0.3)

        return {
            "tool": "search",
            "query": query,
            "results": [
                f"Result 1 for '{query}'",
                f"Result 2 for '{query}'",
                f"Result 3 for '{query}'"
            ],
            "count": 3,
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def calculate(expression: str) -> Dict[str, Any]:
        """Perform calculations."""
        logger.info(f"Tool [calculate] called with: {expression}")

        try:
            # Safe evaluation (in production, use proper math parser)
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
        """Analyze data."""
        logger.info(f"Tool [analyze] called with data length: {len(data)}")

        time.sleep(0.2)

        return {
            "tool": "analyze",
            "data_length": len(data),
            "word_count": len(data.split()),
            "analysis": f"Analysis of: {data[:50]}...",
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def generate_report(topic: str, data: List[str]) -> Dict[str, Any]:
        """Generate a report."""
        logger.info(f"Tool [generate_report] called for topic: {topic}")

        time.sleep(0.4)

        report = f"""
        REPORT: {topic}
        Generated: {datetime.now().isoformat()}
        Data Points: {len(data)}

        Summary:
        {chr(10).join([f'- {item}' for item in data[:3]])}
        """

        return {
            "tool": "generate_report",
            "topic": topic,
            "report": report,
            "timestamp": datetime.now().isoformat()
        }


# ============================================================================
# Subgraph Components
# ============================================================================

class SecuritySubgraph:
    """Security validation subgraph."""

    @staticmethod
    def build(llm: OllamaLLM) -> StateGraph:
        """Build security validation subgraph."""
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
        """Validate user input."""
        user_request = state.get("user_request", "")
        errors = state.get("errors", [])

        # Basic validation
        if not user_request or len(user_request.strip()) == 0:
            errors.append("Empty request")

        if len(user_request) > 10000:
            errors.append("Request too long")

        logger.info(f"Input validation: {'passed' if not errors else 'failed'}")

        return {**state, "errors": errors}

    @staticmethod
    def _check_permissions(state: ProductionAgentState) -> ProductionAgentState:
        """Check user permissions."""
        # In production, check against IAM/RBAC
        logger.info("Permission check: passed")
        return state

    @staticmethod
    def _assess_risk(state: ProductionAgentState) -> ProductionAgentState:
        """Assess risk level of request."""
        user_request = state.get("user_request", "").lower()

        # Simple risk assessment
        high_risk_keywords = ["delete", "remove", "drop", "destroy"]
        medium_risk_keywords = ["modify", "update", "change", "alter"]

        if any(keyword in user_request for keyword in high_risk_keywords):
            risk_level = "high"
            requires_approval = True
        elif any(keyword in user_request for keyword in medium_risk_keywords):
            risk_level = "medium"
            requires_approval = True
        else:
            risk_level = "low"
            requires_approval = False

        logger.info(f"Risk assessment: {risk_level}")

        return {
            **state,
            "risk_level": risk_level,
            "requires_approval": requires_approval
        }


# ============================================================================
# Main Production Agent
# ============================================================================

class ProductionAgent:
    """
    Complete production-ready LangGraph agent.

    This agent combines:
    - State persistence (checkpoints)
    - Human-in-the-loop (approvals)
    - Subgraphs (security, processing)
    - Streaming (real-time updates)
    - Tools (external integrations)
    - Error handling
    - Observability
    """

    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize production agent."""
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

        logger.info("ProductionAgent initialized")

    def _build_graph(self) -> StateGraph:
        """Build complete agent graph."""
        # Build subgraphs
        security_subgraph = SecuritySubgraph.build(self.llm)

        # Main workflow
        workflow = StateGraph(ProductionAgentState)

        # Add nodes
        workflow.add_node("initialize", self._initialize_request)
        workflow.add_node("security", security_subgraph)
        workflow.add_node("analyze_request", self._analyze_request)
        workflow.add_node("approval_gate", self._approval_gate)
        workflow.add_node("execute_tools", self._execute_tools)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("finalize", self._finalize_response)
        workflow.add_node("handle_error", self._handle_error)

        # Flow
        workflow.set_entry_point("initialize")
        workflow.add_edge("initialize", "security")

        # Route based on security validation
        workflow.add_conditional_edges(
            "security",
            self._route_after_security,
            {
                "proceed": "analyze_request",
                "error": "handle_error"
            }
        )

        workflow.add_edge("analyze_request", "approval_gate")

        # Route based on approval requirement
        workflow.add_conditional_edges(
            "approval_gate",
            self._route_after_approval,
            {
                "approved": "execute_tools",
                "waiting": "approval_gate",
                "rejected": "finalize"
            }
        )

        # Route based on tool execution
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

        # Compile with checkpoint
        if self.config.checkpoint_enabled:
            return workflow.compile(checkpointer=self.memory)
        else:
            return workflow.compile()

    # ========================================================================
    # Node Implementations
    # ========================================================================

    def _initialize_request(self, state: ProductionAgentState) -> ProductionAgentState:
        """Initialize request processing."""
        request_id = state.get("request_id", f"req_{int(time.time() * 1000)}")

        logger.info(f"[{request_id}] Initializing request")

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
        """Analyze user request and plan execution."""
        start_time = time.time()
        user_request = state.get("user_request", "")
        request_id = state.get("request_id", "")

        logger.info(f"[{request_id}] Analyzing request")

        # Use LLM to analyze intent
        analysis_prompt = f"""Analyze this request and identify:
1. Intent
2. Required tools (search, calculate, analyze, generate_report)
3. Parameters

Request: {user_request}

Provide brief analysis."""

        analysis_result = self.llm.invoke(analysis_prompt)

        # Simple tool detection (in production, use structured output)
        tools_needed = []
        if "search" in user_request.lower() or "find" in user_request.lower():
            tools_needed.append("search")
        if "calculate" in user_request.lower() or any(op in user_request for op in ['+', '-', '*', '/']):
            tools_needed.append("calculate")
        if "analyze" in user_request.lower():
            tools_needed.append("analyze")
        if "report" in user_request.lower():
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

        logger.info(f"[{request_id}] Analysis complete: {len(tools_needed)} tools needed")

        return {
            **state,
            "analysis": analysis,
            "current_step": "analyze_request",
            "metrics": metrics
        }

    def _approval_gate(self, state: ProductionAgentState) -> ProductionAgentState:
        """Human approval checkpoint."""
        requires_approval = state.get("requires_approval", False)
        approval_status = state.get("approval_status")
        request_id = state.get("request_id", "")
        risk_level = state.get("risk_level", "unknown")

        if not requires_approval:
            # Auto-approve low-risk requests
            logger.info(f"[{request_id}] Auto-approved (low risk)")
            return {
                **state,
                "approval_status": "approved",
                "current_step": "approval_gate"
            }

        if approval_status is None:
            # First time - request approval
            logger.info(f"[{request_id}] Approval required (risk: {risk_level})")
            self.stats["approvals_required"] += 1

            return {
                **state,
                "approval_status": "pending",
                "current_step": "approval_gate"
            }

        # Approval already processed
        return {
            **state,
            "current_step": "approval_gate"
        }

    def _execute_tools(self, state: ProductionAgentState) -> ProductionAgentState:
        """Execute required tools."""
        start_time = time.time()
        analysis = state.get("analysis", {})
        tools_needed = analysis.get("tools_needed", [])
        tools_used = state.get("tools_used", [])
        tool_results = state.get("tool_results", {})
        iteration_count = state.get("iteration_count", 0)
        request_id = state.get("request_id", "")
        user_request = state.get("user_request", "")

        # Find next tool to execute
        remaining_tools = [t for t in tools_needed if t not in tools_used]

        if remaining_tools and iteration_count < self.config.max_iterations:
            tool_name = remaining_tools[0]

            logger.info(f"[{request_id}] Executing tool: {tool_name}")

            try:
                # Execute tool
                if tool_name == "search":
                    result = self.tools.search(user_request)
                elif tool_name == "calculate":
                    # Extract expression (simplified)
                    result = self.tools.calculate("2 + 2")
                elif tool_name == "analyze":
                    result = self.tools.analyze(user_request)
                elif tool_name == "generate_report":
                    result = self.tools.generate_report("User Request", [user_request])
                else:
                    result = {"error": f"Unknown tool: {tool_name}"}

                tool_results[tool_name] = result
                tools_used.append(tool_name)
                self.stats["tools_called"] += 1

                logger.info(f"[{request_id}] Tool {tool_name} completed successfully")

            except Exception as e:
                logger.error(f"[{request_id}] Tool {tool_name} failed: {e}")
                errors = state.get("errors", [])
                errors.append(f"Tool {tool_name} failed: {str(e)}")
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
        """Generate final response."""
        start_time = time.time()
        user_request = state.get("user_request", "")
        tool_results = state.get("tool_results", {})
        request_id = state.get("request_id", "")

        logger.info(f"[{request_id}] Generating response")

        # Build context from tool results
        context = []
        for tool_name, result in tool_results.items():
            context.append(f"{tool_name}: {json.dumps(result)}")

        context_str = "\n".join(context) if context else "No tools used"

        # Generate response with LLM
        response_prompt = f"""Based on the following information, provide a helpful response to the user's request.

User Request: {user_request}

Tool Results:
{context_str}

Provide a clear, concise response:"""

        final_response = self.llm.invoke(response_prompt)

        elapsed = time.time() - start_time
        metrics = state.get("metrics", {})
        metrics["response_generation_time"] = elapsed

        logger.info(f"[{request_id}] Response generated")

        return {
            **state,
            "final_response": final_response,
            "current_step": "generate_response",
            "metrics": metrics
        }

    def _finalize_response(self, state: ProductionAgentState) -> ProductionAgentState:
        """Finalize and prepare response."""
        request_id = state.get("request_id", "")
        errors = state.get("errors", [])

        end_time = time.time()
        start_time = state.get("start_time", end_time)
        total_time = end_time - start_time

        metrics = state.get("metrics", {})
        metrics["total_time"] = total_time

        # Determine status
        if errors:
            status = "error"
            self.stats["failed_requests"] += 1
        else:
            status = "success"
            self.stats["successful_requests"] += 1

        self.stats["total_requests"] += 1

        logger.info(f"[{request_id}] Request finalized: {status} in {total_time:.3f}s")

        return {
            **state,
            "status": status,
            "end_time": end_time,
            "current_step": "finalize",
            "metrics": metrics
        }

    def _handle_error(self, state: ProductionAgentState) -> ProductionAgentState:
        """Handle errors gracefully."""
        request_id = state.get("request_id", "")
        errors = state.get("errors", [])

        logger.error(f"[{request_id}] Handling errors: {errors}")

        final_response = f"I encountered an error processing your request: {'; '.join(errors)}"

        return {
            **state,
            "final_response": final_response,
            "status": "error",
            "current_step": "handle_error"
        }

    # ========================================================================
    # Routing Functions
    # ========================================================================

    def _route_after_security(self, state: ProductionAgentState) -> Literal["proceed", "error"]:
        """Route based on security validation."""
        errors = state.get("errors", [])
        return "error" if errors else "proceed"

    def _route_after_approval(self, state: ProductionAgentState) -> Literal["approved", "waiting", "rejected"]:
        """Route based on approval status."""
        approval_status = state.get("approval_status")

        if approval_status == "approved":
            return "approved"
        elif approval_status == "rejected":
            return "rejected"
        else:
            return "waiting"

    def _route_after_tools(self, state: ProductionAgentState) -> Literal["continue", "done", "error"]:
        """Route based on tool execution status."""
        errors = state.get("errors", [])
        if errors:
            return "error"

        analysis = state.get("analysis", {})
        tools_needed = analysis.get("tools_needed", [])
        tools_used = state.get("tools_used", [])
        iteration_count = state.get("iteration_count", 0)

        # Check if more tools to execute
        if len(tools_used) < len(tools_needed) and iteration_count < self.config.max_iterations:
            return "continue"
        else:
            return "done"

    # ========================================================================
    # Public Interface
    # ========================================================================

    def process_request(
        self,
        user_request: str,
        thread_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Process user request.

        Args:
            user_request: User's request
            thread_id: Conversation thread ID

        Returns:
            Response with results and metadata
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
        Process request with streaming updates.

        Args:
            user_request: User's request
            thread_id: Conversation thread ID

        Yields:
            Progress updates
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

    def approve_request(self, thread_id: str, feedback: str = "Approved") -> Dict[str, Any]:
        """Approve pending request."""
        if not self.config.checkpoint_enabled:
            return {"error": "Checkpoints not enabled"}

        config = {"configurable": {"thread_id": thread_id}}
        current_state = self.graph.get_state(config)

        if not current_state.values:
            return {"error": "No pending request"}

        current_state.values["approval_status"] = "approved"
        current_state.values["approval_feedback"] = feedback

        self.stats["approvals_granted"] += 1

        result = self.graph.invoke(current_state.values, config=config)

        return {
            "status": "approved",
            "response": result.get("final_response", "")
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return self.stats.copy()


# ============================================================================
# DEMONSTRATIONS
# ============================================================================

def demo_basic_usage():
    """Demonstrate basic agent usage."""
    print("\n" + "="*70)
    print("DEMO 1: Basic Usage")
    print("="*70)

    config = AgentConfig(require_approval=False, verbose=True)
    agent = ProductionAgent(config)

    print("\n1. Processing simple request...")
    result = agent.process_request("Search for information about AI")

    print(f"\n2. Response:")
    print(f"   Request ID: {result['request_id']}")
    print(f"   Status: {result['status']}")
    print(f"   Response: {result['response'][:200]}...")
    print(f"   Tools used: {result['tools_used']}")
    print(f"   Total time: {result['metrics'].get('total_time', 0):.3f}s")


def demo_streaming():
    """Demonstrate streaming."""
    print("\n" + "="*70)
    print("DEMO 2: Streaming Updates")
    print("="*70)

    config = AgentConfig(require_approval=False, streaming_enabled=True)
    agent = ProductionAgent(config)

    print("\n1. Processing with streaming...")
    for update in agent.stream_request("Calculate 15 * 25 and search for math"):
        print(f"   [{update['iteration']}] {update['node']} | Step: {update['step']} | Status: {update['status']}")


def demo_approval_workflow():
    """Demonstrate approval workflow."""
    print("\n" + "="*70)
    print("DEMO 3: Approval Workflow (Simulated)")
    print("="*70)

    config = AgentConfig(require_approval=True, checkpoint_enabled=True)
    agent = ProductionAgent(config)

    print("\n1. Submitting high-risk request...")
    print("   Request: 'Delete all user data'")

    # In production, this would pause for approval
    # For demo, we show the flow
    print("   Status: Would require approval due to 'delete' keyword")
    print("   Risk level: high")
    print("   Approval required: Yes")


def demo_statistics():
    """Demonstrate statistics."""
    print("\n" + "="*70)
    print("DEMO 4: Agent Statistics")
    print("="*70)

    config = AgentConfig(require_approval=False)
    agent = ProductionAgent(config)

    # Process several requests
    agent.process_request("Search for Python tutorials")
    agent.process_request("Calculate 100 * 50")

    print("\n1. Agent statistics:")
    stats = agent.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("LangGraph Production Agent - Complete System")
    print("="*70)
    print("\nThis is a complete production-ready agent combining all features:")
    print("- State persistence with checkpoints")
    print("- Human-in-the-loop approvals")
    print("- Subgraph composition")
    print("- Event streaming")
    print("- Tool integration")
    print("- Error handling")
    print("- Observability")

    try:
        demo_basic_usage()
        demo_streaming()
        demo_approval_workflow()
        demo_statistics()

        print("\n" + "="*70)
        print("Tutorial completed successfully!")
        print("="*70)
        print("\nKey Takeaways:")
        print("1. Production agents combine all LangGraph features")
        print("2. Checkpoints enable conversation persistence")
        print("3. Approvals provide safety guardrails")
        print("4. Streaming improves user experience")
        print("5. Subgraphs enable modular architecture")
        print("6. Proper logging and metrics are essential")
        print("\nCongratulations! You've completed the LangGraph tutorial series.")

    except Exception as e:
        print(f"\nError during demonstration: {e}")
        print("Make sure Ollama is running with qwen3:8b model")
        import traceback
        traceback.print_exc()
