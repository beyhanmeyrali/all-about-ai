#!/usr/bin/env python3
"""
LangGraph Subgraphs - Nested Workflow Composition
==================================================

This script demonstrates subgraph patterns for building modular workflows.
Subgraphs allow you to:
- Compose complex workflows from reusable components
- Encapsulate domain logic
- Build hierarchical architectures
- Enable parallel processing

We'll progress from simple nested graphs to production microservice patterns.

Author: AI Agents Tutorial Series
"""

from typing import TypedDict, Annotated, List, Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import OllamaLLM
import operator
from datetime import datetime


# ============================================================================
# Part 1: Basic Subgraph
# ============================================================================

class SimpleState(TypedDict):
    """Basic state for subgraph demo."""
    input: str
    output: str
    step_results: List[str]


class BasicSubgraphAgent:
    """
    Demonstrates basic subgraph composition.

    Features:
    - Create reusable subgraph components
    - Embed subgraph in main workflow
    - Pass state between graphs
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize subgraph agent."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.graph = self._build_graph()

    def _build_preprocessing_subgraph(self) -> StateGraph:
        """Build preprocessing subgraph."""
        subgraph = StateGraph(SimpleState)

        # Preprocessing nodes
        subgraph.add_node("clean", self._clean_input)
        subgraph.add_node("validate", self._validate_input)

        # Subgraph flow
        subgraph.set_entry_point("clean")
        subgraph.add_edge("clean", "validate")
        subgraph.add_edge("validate", END)

        return subgraph.compile()

    def _clean_input(self, state: SimpleState) -> SimpleState:
        """Clean input data."""
        input_data = state.get("input", "")
        cleaned = input_data.strip().lower()

        step_results = state.get("step_results", [])
        step_results.append(f"Cleaned: '{input_data}' -> '{cleaned}'")

        return {
            **state,
            "input": cleaned,
            "step_results": step_results
        }

    def _validate_input(self, state: SimpleState) -> SimpleState:
        """Validate input data."""
        input_data = state.get("input", "")
        is_valid = len(input_data) > 0

        step_results = state.get("step_results", [])
        step_results.append(f"Validation: {'passed' if is_valid else 'failed'}")

        return {
            **state,
            "step_results": step_results
        }

    def _build_graph(self) -> StateGraph:
        """Build main graph with subgraph."""
        # Create preprocessing subgraph
        preprocessing = self._build_preprocessing_subgraph()

        # Main workflow
        workflow = StateGraph(SimpleState)

        # Add subgraph as a node
        workflow.add_node("preprocess", preprocessing)
        workflow.add_node("process", self._process_data)
        workflow.add_node("postprocess", self._postprocess_data)

        # Main flow
        workflow.set_entry_point("preprocess")
        workflow.add_edge("preprocess", "process")
        workflow.add_edge("process", "postprocess")
        workflow.add_edge("postprocess", END)

        return workflow.compile()

    def _process_data(self, state: SimpleState) -> SimpleState:
        """Main processing logic."""
        input_data = state.get("input", "")
        result = self.llm.invoke(f"Process this: {input_data}")

        step_results = state.get("step_results", [])
        step_results.append(f"Processed: {result[:50]}...")

        return {
            **state,
            "output": result,
            "step_results": step_results
        }

    def _postprocess_data(self, state: SimpleState) -> SimpleState:
        """Postprocess results."""
        output = state.get("output", "")
        formatted = f"RESULT: {output}"

        step_results = state.get("step_results", [])
        step_results.append(f"Formatted output")

        return {
            **state,
            "output": formatted,
            "step_results": step_results
        }

    def run(self, input_data: str) -> Dict[str, Any]:
        """Run full workflow."""
        result = self.graph.invoke({
            "input": input_data,
            "output": "",
            "step_results": []
        })

        return result


# ============================================================================
# Part 2: Parallel Subgraphs
# ============================================================================

class ParallelState(TypedDict):
    """State for parallel processing."""
    query: str
    search_results: List[str]
    analysis_results: List[str]
    summary: str


class ParallelSubgraphAgent:
    """
    Demonstrates parallel subgraph execution.

    Features:
    - Run multiple subgraphs concurrently
    - Aggregate results from parallel branches
    - Optimize processing time
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize parallel agent."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.graph = self._build_graph()

    def _build_search_subgraph(self) -> StateGraph:
        """Build search subgraph."""
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
        """Build analysis subgraph."""
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
        """Simulate web search."""
        query = state.get("query", "")
        results = state.get("search_results", [])
        results.append(f"Web result for: {query}")

        return {**state, "search_results": results}

    def _search_docs(self, state: ParallelState) -> ParallelState:
        """Simulate document search."""
        query = state.get("query", "")
        results = state.get("search_results", [])
        results.append(f"Doc result for: {query}")

        return {**state, "search_results": results}

    def _merge_search_results(self, state: ParallelState) -> ParallelState:
        """Merge search results."""
        return state

    def _analyze_sentiment(self, state: ParallelState) -> ParallelState:
        """Analyze sentiment."""
        query = state.get("query", "")
        results = state.get("analysis_results", [])
        results.append(f"Sentiment: neutral for '{query}'")

        return {**state, "analysis_results": results}

    def _extract_entities(self, state: ParallelState) -> ParallelState:
        """Extract entities."""
        query = state.get("query", "")
        results = state.get("analysis_results", [])
        results.append(f"Entities found in '{query}'")

        return {**state, "analysis_results": results}

    def _merge_analysis_results(self, state: ParallelState) -> ParallelState:
        """Merge analysis results."""
        return state

    def _build_graph(self) -> StateGraph:
        """Build main graph with parallel subgraphs."""
        # Create subgraphs
        search_graph = self._build_search_subgraph()
        analysis_graph = self._build_analysis_subgraph()

        # Main workflow
        workflow = StateGraph(ParallelState)

        # Add subgraphs as parallel nodes
        workflow.add_node("search", search_graph)
        workflow.add_node("analyze", analysis_graph)
        workflow.add_node("summarize", self._create_summary)

        # Parallel execution (both run independently)
        workflow.set_entry_point("search")
        workflow.add_edge("search", "summarize")
        workflow.add_edge("analyze", "summarize")
        workflow.add_edge("summarize", END)

        return workflow.compile()

    def _create_summary(self, state: ParallelState) -> ParallelState:
        """Create final summary."""
        search_results = state.get("search_results", [])
        analysis_results = state.get("analysis_results", [])

        summary = f"Found {len(search_results)} search results and {len(analysis_results)} analysis insights"

        return {**state, "summary": summary}

    def process(self, query: str) -> Dict[str, Any]:
        """Process query with parallel subgraphs."""
        result = self.graph.invoke({
            "query": query,
            "search_results": [],
            "analysis_results": [],
            "summary": ""
        })

        return result


# ============================================================================
# Part 3: Hierarchical Subgraph Architecture
# ============================================================================

class DocumentState(TypedDict):
    """State for document processing."""
    document: str
    sections: List[Dict[str, str]]
    processed_sections: List[Dict[str, str]]
    final_output: str


class HierarchicalSubgraphAgent:
    """
    Demonstrates hierarchical subgraph composition.

    Features:
    - Multi-level subgraph nesting
    - Section-by-section processing
    - Recursive workflow patterns
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize hierarchical agent."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.graph = self._build_graph()

    def _build_section_processor(self) -> StateGraph:
        """Build section processing subgraph."""
        # This is the lowest level subgraph
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
        """Build chapter processing subgraph."""
        # Middle level - uses section processor
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
        """Extract key points from section."""
        # Process first section
        sections = state.get("sections", [])
        if sections:
            section = sections[0]
            key_points = f"Key points: {section.get('content', '')[:50]}"
            section["key_points"] = key_points

        return state

    def _summarize_section(self, state: DocumentState) -> DocumentState:
        """Summarize section."""
        sections = state.get("sections", [])
        if sections:
            section = sections[0]
            summary = f"Summary of {section.get('title', 'section')}"
            section["summary"] = summary

        return state

    def _enrich_section(self, state: DocumentState) -> DocumentState:
        """Enrich section with metadata."""
        sections = state.get("sections", [])
        processed = state.get("processed_sections", [])

        if sections:
            section = sections[0]
            section["processed"] = True
            section["timestamp"] = datetime.now().isoformat()
            processed.append(section)

            # Remove processed section
            sections = sections[1:]

        return {**state, "sections": sections, "processed_sections": processed}

    def _split_into_sections(self, state: DocumentState) -> DocumentState:
        """Split document into sections."""
        document = state.get("document", "")

        # Simple split (in production, use proper parsing)
        sections = [
            {"title": f"Section {i+1}", "content": document[i*100:(i+1)*100]}
            for i in range(min(3, len(document) // 100 + 1))
        ]

        return {**state, "sections": sections}

    def _merge_sections(self, state: DocumentState) -> DocumentState:
        """Merge processed sections."""
        processed = state.get("processed_sections", [])
        merged = " | ".join([s.get("summary", "") for s in processed])

        return {**state, "final_output": merged}

    def _build_graph(self) -> StateGraph:
        """Build top-level graph."""
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
        """Prepare document for processing."""
        return state

    def _finalize_output(self, state: DocumentState) -> DocumentState:
        """Finalize processed output."""
        final = state.get("final_output", "")
        state["final_output"] = f"FINAL: {final}"
        return state

    def process_document(self, document: str) -> str:
        """Process full document."""
        result = self.graph.invoke({
            "document": document,
            "sections": [],
            "processed_sections": [],
            "final_output": ""
        })

        return result.get("final_output", "")


# ============================================================================
# Part 4: Production Microservice Architecture
# ============================================================================

class MicroserviceState(TypedDict):
    """State for microservice architecture."""
    request: Dict[str, Any]
    auth_result: Dict[str, Any]
    data_result: Dict[str, Any]
    processing_result: Dict[str, Any]
    response: Dict[str, Any]


class ProductionMicroserviceAgent:
    """
    Enterprise microservice architecture using subgraphs.

    Features:
    - Service isolation via subgraphs
    - Independent service scaling
    - Service health monitoring
    - Error isolation and recovery
    """

    def __init__(self, model: str = "qwen3:8b"):
        """Initialize microservice architecture."""
        self.llm = OllamaLLM(model=model, temperature=0.7)
        self.memory = MemorySaver()
        self.graph = self._build_graph()
        self.service_stats = {
            "auth_service": {"calls": 0, "errors": 0},
            "data_service": {"calls": 0, "errors": 0},
            "processing_service": {"calls": 0, "errors": 0}
        }

    def _build_auth_service(self) -> StateGraph:
        """Build authentication service subgraph."""
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
        """Build data service subgraph."""
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
        """Build processing service subgraph."""
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
        """Validate authentication token."""
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
        """Check user permissions."""
        auth_result = state.get("auth_result", {})
        request = state.get("request", {})

        auth_result["has_permission"] = auth_result.get("valid", False)
        auth_result["allowed_actions"] = ["read", "write"] if auth_result.get("valid") else []

        return {**state, "auth_result": auth_result}

    def _log_auth_attempt(self, state: MicroserviceState) -> MicroserviceState:
        """Log authentication attempt."""
        auth_result = state.get("auth_result", {})
        # In production, write to logging service
        return state

    def _fetch_data(self, state: MicroserviceState) -> MicroserviceState:
        """Fetch data from source."""
        self.service_stats["data_service"]["calls"] += 1

        request = state.get("request", {})
        query = request.get("query", "")

        data_result = {
            "data": f"Data for query: {query}",
            "count": 10,
            "timestamp": datetime.now().isoformat()
        }

        return {**state, "data_result": data_result}

    def _validate_data(self, state: MicroserviceState) -> MicroserviceState:
        """Validate fetched data."""
        data_result = state.get("data_result", {})
        data_result["validated"] = True
        return {**state, "data_result": data_result}

    def _cache_data(self, state: MicroserviceState) -> MicroserviceState:
        """Cache data for future requests."""
        data_result = state.get("data_result", {})
        data_result["cached"] = True
        return {**state, "data_result": data_result}

    def _analyze_data(self, state: MicroserviceState) -> MicroserviceState:
        """Analyze data."""
        self.service_stats["processing_service"]["calls"] += 1

        data_result = state.get("data_result", {})
        data = data_result.get("data", "")

        processing_result = {
            "analysis": f"Analyzed: {data[:50]}",
            "insights": ["insight_1", "insight_2"],
            "timestamp": datetime.now().isoformat()
        }

        return {**state, "processing_result": processing_result}

    def _transform_data(self, state: MicroserviceState) -> MicroserviceState:
        """Transform data."""
        processing_result = state.get("processing_result", {})
        processing_result["transformed"] = True
        return {**state, "processing_result": processing_result}

    def _optimize_output(self, state: MicroserviceState) -> MicroserviceState:
        """Optimize output."""
        processing_result = state.get("processing_result", {})
        processing_result["optimized"] = True
        return {**state, "processing_result": processing_result}

    def _build_graph(self) -> StateGraph:
        """Build main API gateway graph."""
        # Create microservices
        auth_service = self._build_auth_service()
        data_service = self._build_data_service()
        processing_service = self._build_processing_service()

        # API Gateway
        gateway = StateGraph(MicroserviceState)

        # Add services as nodes
        gateway.add_node("auth", auth_service)
        gateway.add_node("data", data_service)
        gateway.add_node("processing", processing_service)
        gateway.add_node("response", self._build_response)

        # Gateway flow
        gateway.set_entry_point("auth")

        # Conditional routing based on auth
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
        """Route based on authentication result."""
        auth_result = state.get("auth_result", {})
        return "authorized" if auth_result.get("valid", False) else "unauthorized"

    def _build_response(self, state: MicroserviceState) -> MicroserviceState:
        """Build API response."""
        auth_result = state.get("auth_result", {})

        if not auth_result.get("valid", False):
            response = {
                "status": "error",
                "message": "Unauthorized",
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
        """Handle incoming API request."""
        result = self.graph.invoke({
            "request": request,
            "auth_result": {},
            "data_result": {},
            "processing_result": {},
            "response": {}
        })

        return result.get("response", {})

    def get_service_stats(self) -> Dict[str, Any]:
        """Get microservice statistics."""
        return self.service_stats.copy()


# ============================================================================
# DEMONSTRATIONS
# ============================================================================

def demo_basic_subgraph():
    """Demonstrate basic subgraph."""
    print("\n" + "="*70)
    print("DEMO 1: Basic Subgraph Composition")
    print("="*70)

    agent = BasicSubgraphAgent()

    print("\n1. Running workflow with preprocessing subgraph...")
    result = agent.run("  HELLO WORLD  ")

    print(f"\n2. Step-by-step execution:")
    for step in result.get("step_results", []):
        print(f"   - {step}")

    print(f"\n3. Final output: {result.get('output', '')[:100]}")


def demo_parallel_subgraphs():
    """Demonstrate parallel subgraphs."""
    print("\n" + "="*70)
    print("DEMO 2: Parallel Subgraph Execution")
    print("="*70)

    agent = ParallelSubgraphAgent()

    print("\n1. Processing with parallel subgraphs...")
    result = agent.process("artificial intelligence")

    print(f"\n2. Search results: {len(result.get('search_results', []))}")
    for res in result.get('search_results', []):
        print(f"   - {res}")

    print(f"\n3. Analysis results: {len(result.get('analysis_results', []))}")
    for res in result.get('analysis_results', []):
        print(f"   - {res}")

    print(f"\n4. Summary: {result.get('summary', '')}")


def demo_hierarchical():
    """Demonstrate hierarchical subgraphs."""
    print("\n" + "="*70)
    print("DEMO 3: Hierarchical Subgraph Architecture")
    print("="*70)

    agent = HierarchicalSubgraphAgent()

    print("\n1. Processing document with nested subgraphs...")
    document = "This is a test document. " * 50
    result = agent.process_document(document)

    print(f"\n2. Final output: {result[:150]}...")


def demo_microservices():
    """Demonstrate microservice architecture."""
    print("\n" + "="*70)
    print("DEMO 4: Production Microservice Architecture")
    print("="*70)

    system = ProductionMicroserviceAgent()

    print("\n1. Authorized request...")
    request1 = {
        "token": "valid_token_123",
        "query": "user_data",
        "action": "read"
    }
    response1 = system.handle_request(request1)
    print(f"   Status: {response1.get('status')}")
    print(f"   Code: {response1.get('code')}")

    print("\n2. Unauthorized request...")
    request2 = {
        "token": "",
        "query": "sensitive_data",
        "action": "write"
    }
    response2 = system.handle_request(request2)
    print(f"   Status: {response2.get('status')}")
    print(f"   Code: {response2.get('code')}")

    print("\n3. Service statistics:")
    stats = system.get_service_stats()
    for service, metrics in stats.items():
        print(f"   {service}: {metrics}")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("LangGraph Subgraphs - Nested Workflow Tutorial")
    print("="*70)
    print("\nThis tutorial demonstrates subgraph composition patterns.")
    print("Subgraphs enable modular, reusable, and scalable workflows.")

    try:
        demo_basic_subgraph()
        demo_parallel_subgraphs()
        demo_hierarchical()
        demo_microservices()

        print("\n" + "="*70)
        print("Tutorial completed successfully!")
        print("="*70)
        print("\nKey Takeaways:")
        print("1. Subgraphs encapsulate domain logic into reusable components")
        print("2. Parallel subgraphs optimize processing time")
        print("3. Hierarchical nesting enables complex architectures")
        print("4. Microservice patterns provide service isolation")
        print("\nNext: 07_streaming_events.py - Real-time event streaming")

    except Exception as e:
        print(f"\nError during demonstration: {e}")
        print("Make sure Ollama is running with qwen3:8b model")
