#!/usr/bin/env python3
"""
LangGraph Streaming Events - Real-Time Updates
===============================================

This script demonstrates event streaming in LangGraph for real-time updates.
Streaming enables:
- Live progress tracking
- Incremental result delivery
- Better user experience
- Real-time debugging

We'll build from basic streaming to production-grade event systems.

Author: AI Agents Tutorial Series
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
# Part 1: Basic Event Streaming
# ============================================================================

class StreamState(TypedDict):
    """State for streaming demos."""
    input: str
    output: str
    events: List[str]


class BasicStreamingAgent:
    """
    Demonstrates basic event streaming.

    Features:
    - Stream node execution events
    - Track processing steps in real-time
    - Monitor state changes
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize streaming agent."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build graph with streaming support."""
        workflow = StateGraph(StreamState)

        # Add nodes
        workflow.add_node("step1", self._process_step1)
        workflow.add_node("step2", self._process_step2)
        workflow.add_node("step3", self._process_step3)

        # Flow
        workflow.set_entry_point("step1")
        workflow.add_edge("step1", "step2")
        workflow.add_edge("step2", "step3")
        workflow.add_edge("step3", END)

        return workflow.compile()

    def _process_step1(self, state: StreamState) -> StreamState:
        """First processing step."""
        events = state.get("events", [])
        events.append(f"[{datetime.now().strftime('%H:%M:%S')}] Step 1: Started")

        # Simulate work
        time.sleep(0.5)

        events.append(f"[{datetime.now().strftime('%H:%M:%S')}] Step 1: Completed")

        return {
            **state,
            "events": events
        }

    def _process_step2(self, state: StreamState) -> StreamState:
        """Second processing step."""
        events = state.get("events", [])
        events.append(f"[{datetime.now().strftime('%H:%M:%S')}] Step 2: Started")

        # Process with LLM
        input_data = state.get("input", "")
        result = self.llm.invoke(f"Process this briefly: {input_data}")

        events.append(f"[{datetime.now().strftime('%H:%M:%S')}] Step 2: LLM call completed")

        return {
            **state,
            "output": result,
            "events": events
        }

    def _process_step3(self, state: StreamState) -> StreamState:
        """Third processing step."""
        events = state.get("events", [])
        events.append(f"[{datetime.now().strftime('%H:%M:%S')}] Step 3: Started")

        time.sleep(0.3)

        events.append(f"[{datetime.now().strftime('%H:%M:%S')}] Step 3: Completed")

        return {
            **state,
            "events": events
        }

    def stream_process(self, input_data: str) -> Iterator[Dict[str, Any]]:
        """Process with event streaming."""
        # Stream events from graph execution
        for event in self.graph.stream({
            "input": input_data,
            "output": "",
            "events": []
        }):
            yield event

    def run(self, input_data: str) -> List[str]:
        """Run and collect all events."""
        result = self.graph.invoke({
            "input": input_data,
            "output": "",
            "events": []
        })

        return result.get("events", [])


# ============================================================================
# Part 2: Progress Tracking
# ============================================================================

class ProgressState(TypedDict):
    """State with progress tracking."""
    tasks: List[str]
    completed: List[str]
    current_task: str
    progress_percent: float


class ProgressTrackingAgent:
    """
    Demonstrates progress tracking with streaming.

    Features:
    - Real-time progress updates
    - Percentage completion tracking
    - Task status monitoring
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize progress tracking agent."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build graph with progress tracking."""
        workflow = StateGraph(ProgressState)

        workflow.add_node("initialize", self._initialize_tasks)
        workflow.add_node("process", self._process_task)
        workflow.add_node("update_progress", self._update_progress)

        workflow.set_entry_point("initialize")
        workflow.add_edge("initialize", "process")
        workflow.add_edge("process", "update_progress")

        # Loop back if more tasks
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
        """Initialize task list."""
        tasks = state.get("tasks", [])

        return {
            **state,
            "tasks": tasks,
            "completed": [],
            "current_task": "",
            "progress_percent": 0.0
        }

    def _process_task(self, state: ProgressState) -> ProgressState:
        """Process next task."""
        tasks = state.get("tasks", [])
        completed = state.get("completed", [])

        # Get next task
        remaining = [t for t in tasks if t not in completed]

        if remaining:
            current = remaining[0]

            # Simulate processing
            time.sleep(0.2)
            result = self.llm.invoke(f"Brief response for: {current}")

            completed.append(current)

            return {
                **state,
                "current_task": current,
                "completed": completed
            }

        return state

    def _update_progress(self, state: ProgressState) -> ProgressState:
        """Update progress percentage."""
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
        """Check if more tasks to process."""
        tasks = state.get("tasks", [])
        completed = state.get("completed", [])

        return "continue" if len(completed) < len(tasks) else "done"

    def stream_with_progress(self, tasks: List[str]) -> Iterator[Dict[str, Any]]:
        """Stream execution with progress updates."""
        for event in self.graph.stream({
            "tasks": tasks,
            "completed": [],
            "current_task": "",
            "progress_percent": 0.0
        }):
            # Extract progress info
            for node_name, node_state in event.items():
                if "progress_percent" in node_state:
                    yield {
                        "node": node_name,
                        "progress": node_state["progress_percent"],
                        "current_task": node_state.get("current_task", ""),
                        "completed": len(node_state.get("completed", []))
                    }


# ============================================================================
# Part 3: Real-Time Debug Streaming
# ============================================================================

class DebugState(TypedDict):
    """State with debug information."""
    input: str
    intermediate_results: List[Dict[str, Any]]
    final_output: str
    debug_log: List[str]


class DebugStreamingAgent:
    """
    Demonstrates debug streaming for development.

    Features:
    - Stream intermediate results
    - Real-time debugging
    - State inspection
    - Performance monitoring
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize debug streaming agent."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build graph with debug instrumentation."""
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
        """Analyze input with debugging."""
        start_time = time.time()

        input_data = state.get("input", "")
        debug_log = state.get("debug_log", [])
        intermediate = state.get("intermediate_results", [])

        # Log start
        debug_log.append(f"[ANALYZE] Start: {datetime.now().isoformat()}")
        debug_log.append(f"[ANALYZE] Input length: {len(input_data)}")

        # Process
        analysis = {
            "word_count": len(input_data.split()),
            "char_count": len(input_data),
            "timestamp": datetime.now().isoformat()
        }

        intermediate.append({"step": "analyze", "result": analysis})

        # Log completion
        elapsed = time.time() - start_time
        debug_log.append(f"[ANALYZE] Completed in {elapsed:.3f}s")

        return {
            **state,
            "intermediate_results": intermediate,
            "debug_log": debug_log
        }

    def _process_data(self, state: DebugState) -> DebugState:
        """Process with detailed logging."""
        start_time = time.time()

        input_data = state.get("input", "")
        debug_log = state.get("debug_log", [])
        intermediate = state.get("intermediate_results", [])

        debug_log.append(f"[PROCESS] Start: {datetime.now().isoformat()}")

        # LLM call
        llm_start = time.time()
        result = self.llm.invoke(f"Analyze: {input_data}")
        llm_elapsed = time.time() - llm_start

        debug_log.append(f"[PROCESS] LLM call: {llm_elapsed:.3f}s")

        intermediate.append({
            "step": "process",
            "result": result[:100],
            "llm_time": llm_elapsed
        })

        elapsed = time.time() - start_time
        debug_log.append(f"[PROCESS] Completed in {elapsed:.3f}s")

        return {
            **state,
            "intermediate_results": intermediate,
            "debug_log": debug_log
        }

    def _synthesize_output(self, state: DebugState) -> DebugState:
        """Synthesize final output."""
        start_time = time.time()

        intermediate = state.get("intermediate_results", [])
        debug_log = state.get("debug_log", [])

        debug_log.append(f"[SYNTHESIZE] Start: {datetime.now().isoformat()}")

        # Combine results
        final_output = f"Processed {len(intermediate)} steps"

        elapsed = time.time() - start_time
        debug_log.append(f"[SYNTHESIZE] Completed in {elapsed:.3f}s")

        return {
            **state,
            "final_output": final_output,
            "debug_log": debug_log
        }

    def stream_debug(self, input_data: str) -> Iterator[Dict[str, Any]]:
        """Stream execution with debug information."""
        for event in self.graph.stream({
            "input": input_data,
            "intermediate_results": [],
            "final_output": "",
            "debug_log": []
        }):
            # Extract debug info from each node
            for node_name, node_state in event.items():
                debug_info = {
                    "node": node_name,
                    "timestamp": datetime.now().isoformat(),
                    "debug_log": node_state.get("debug_log", []),
                    "intermediate": node_state.get("intermediate_results", [])
                }
                yield debug_info


# ============================================================================
# Part 4: Production Event System
# ============================================================================

class ProductionState(TypedDict):
    """Production-grade state."""
    request_id: str
    payload: Dict[str, Any]
    processing_stages: List[Dict[str, Any]]
    result: Dict[str, Any]
    metrics: Dict[str, float]


class ProductionEventStream:
    """
    Enterprise-grade event streaming system.

    Features:
    - Structured event logging
    - Performance metrics
    - Error tracking
    - Event aggregation
    - Real-time monitoring
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize production event system."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.memory = MemorySaver()
        self.graph = self._build_graph()
        self.event_handlers = []

    def _build_graph(self) -> StateGraph:
        """Build production graph with comprehensive instrumentation."""
        workflow = StateGraph(ProductionState)

        # Pipeline nodes
        workflow.add_node("validate", self._validate_request)
        workflow.add_node("enrich", self._enrich_data)
        workflow.add_node("process", self._process_request)
        workflow.add_node("aggregate", self._aggregate_results)
        workflow.add_node("finalize", self._finalize_response)

        # Flow
        workflow.set_entry_point("validate")
        workflow.add_edge("validate", "enrich")
        workflow.add_edge("enrich", "process")
        workflow.add_edge("process", "aggregate")
        workflow.add_edge("aggregate", "finalize")
        workflow.add_edge("finalize", END)

        return workflow.compile(checkpointer=self.memory)

    def _emit_event(self, state: ProductionState, event_type: str, data: Dict[str, Any]):
        """Emit structured event."""
        event = {
            "request_id": state.get("request_id", "unknown"),
            "event_type": event_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }

        stages = state.get("processing_stages", [])
        stages.append(event)
        state["processing_stages"] = stages

    def _validate_request(self, state: ProductionState) -> ProductionState:
        """Validate incoming request."""
        start_time = time.time()

        payload = state.get("payload", {})
        metrics = state.get("metrics", {})

        self._emit_event(state, "VALIDATION_START", {"payload_size": len(str(payload))})

        # Validation logic
        is_valid = bool(payload)

        elapsed = time.time() - start_time
        metrics["validation_time"] = elapsed

        self._emit_event(state, "VALIDATION_COMPLETE", {
            "valid": is_valid,
            "duration_ms": elapsed * 1000
        })

        return {**state, "metrics": metrics}

    def _enrich_data(self, state: ProductionState) -> ProductionState:
        """Enrich request data."""
        start_time = time.time()
        metrics = state.get("metrics", {})

        self._emit_event(state, "ENRICHMENT_START", {})

        # Enrichment logic
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
        """Main processing logic."""
        start_time = time.time()
        metrics = state.get("metrics", {})

        self._emit_event(state, "PROCESSING_START", {})

        # Process with LLM
        payload = state.get("payload", {})
        query = payload.get("query", "")

        llm_start = time.time()
        try:
            response = self.llm.invoke(f"Process: {query}")
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
        """Aggregate processing results."""
        start_time = time.time()
        metrics = state.get("metrics", {})

        self._emit_event(state, "AGGREGATION_START", {})

        # Aggregation logic
        result = state.get("result", {})
        result["aggregated"] = True

        elapsed = time.time() - start_time
        metrics["aggregation_time"] = elapsed

        self._emit_event(state, "AGGREGATION_COMPLETE", {
            "duration_ms": elapsed * 1000
        })

        return {**state, "result": result, "metrics": metrics}

    def _finalize_response(self, state: ProductionState) -> ProductionState:
        """Finalize response with metrics."""
        metrics = state.get("metrics", {})

        # Calculate total time
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
        """Process request with event streaming."""
        request_id = f"req_{int(time.time() * 1000)}"

        for event in self.graph.stream({
            "request_id": request_id,
            "payload": payload,
            "processing_stages": [],
            "result": {},
            "metrics": {}
        }):
            # Stream each node's events
            for node_name, node_state in event.items():
                stages = node_state.get("processing_stages", [])
                for stage in stages:
                    yield {
                        "node": node_name,
                        **stage
                    }

    def get_metrics_summary(self, request_id: str) -> Dict[str, Any]:
        """Get metrics summary for request."""
        # In production, retrieve from monitoring system
        return {
            "request_id": request_id,
            "summary": "Metrics would be aggregated from monitoring system"
        }


# ============================================================================
# DEMONSTRATIONS
# ============================================================================

def demo_basic_streaming():
    """Demonstrate basic event streaming."""
    print("\n" + "="*70)
    print("DEMO 1: Basic Event Streaming")
    print("="*70)

    agent = BasicStreamingAgent()

    print("\n1. Streaming execution events:")
    for event in agent.stream_process("What is AI?"):
        node_name = list(event.keys())[0]
        node_state = event[node_name]
        if "events" in node_state:
            for evt in node_state["events"]:
                print(f"   {evt}")


def demo_progress_tracking():
    """Demonstrate progress tracking."""
    print("\n" + "="*70)
    print("DEMO 2: Progress Tracking")
    print("="*70)

    agent = ProgressTrackingAgent()

    print("\n1. Processing with progress updates:")
    tasks = ["Analyze data", "Generate report", "Send email"]

    for update in agent.stream_with_progress(tasks):
        print(f"   [{update['progress']:.0f}%] Node: {update['node']} | "
              f"Task: {update['current_task']} | "
              f"Completed: {update['completed']}")


def demo_debug_streaming():
    """Demonstrate debug streaming."""
    print("\n" + "="*70)
    print("DEMO 3: Real-Time Debug Streaming")
    print("="*70)

    agent = DebugStreamingAgent()

    print("\n1. Streaming debug information:")
    for debug_info in agent.stream_debug("Explain machine learning"):
        print(f"\n   Node: {debug_info['node']}")
        for log in debug_info['debug_log']:
            print(f"     {log}")


def demo_production_events():
    """Demonstrate production event system."""
    print("\n" + "="*70)
    print("DEMO 4: Production Event Streaming")
    print("="*70)

    system = ProductionEventStream()

    print("\n1. Processing request with event stream:")
    payload = {
        "query": "What are the benefits of AI?",
        "user_id": "user_123"
    }

    for event in system.stream_request(payload):
        event_type = event.get("event_type", "UNKNOWN")
        node = event.get("node", "unknown")
        data = event.get("data", {})

        print(f"\n   [{event.get('timestamp', '')}]")
        print(f"   Type: {event_type} | Node: {node}")
        if data:
            print(f"   Data: {json.dumps(data, indent=6)}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("LangGraph Streaming Events Tutorial")
    print("="*70)
    print("\nThis tutorial demonstrates real-time event streaming patterns.")
    print("Streaming enables live progress tracking and debugging.")

    try:
        demo_basic_streaming()
        demo_progress_tracking()
        demo_debug_streaming()
        demo_production_events()

        print("\n" + "="*70)
        print("Tutorial completed successfully!")
        print("="*70)
        print("\nKey Takeaways:")
        print("1. graph.stream() provides real-time execution updates")
        print("2. Progress tracking improves user experience")
        print("3. Debug streaming accelerates development")
        print("4. Structured events enable monitoring and observability")
        print("\nNext: 08_production_agent.py - Complete enterprise agent")

    except Exception as e:
        print(f"\nError during demonstration: {e}")
        print("Make sure Ollama is running with qwen3:8b model")
