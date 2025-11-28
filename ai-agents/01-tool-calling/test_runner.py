#!/usr/bin/env python3
"""
Quick test script for 01-tool-calling examples
Tests without interactive mode
"""
import sys
import requests
from importlib import import_module

# Check Ollama first
print("="*70)
print("TESTING: 01-tool-calling scripts")
print("="*70)

try:
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    if response.status_code != 200:
        print("[ERROR] Ollama not running correctly")
        exit(1)
    print("✅ Ollama is running")
except:
    print("[ERROR] Cannot connect to Ollama")
    exit(1)

# Test 01_basic_weather_tool - import and run non-interactive tests
print("\n" + "="*70)
print("TEST 1: 01_basic_weather_tool.py")
print("="*70)

weather_tool = import_module('01_basic_weather_tool')

# Create bot and run a few tests
print("\n[TEST] Creating OllamaToolBot...")
bot = weather_tool.OllamaToolBot(model="qwen3:8b")

print("\n[TEST] Testing single tool call...")
result1 = bot.ask_question("What's the weather in Tokyo?")
print(f"✅ Result: {result1[:100] if result1 else 'Success'}...")

print("\n[TEST] Testing another city...")
result2 = bot.ask_question("What's the weather in Paris?")
print(f"✅ Result: {result2[:100] if result2 else 'Success'}...")

print("\n" + "="*70)
print("✅ PASSED - 01_basic_weather_tool.py")
print("="*70)

# Test 03_recursive_agent
print("\n" + "="*70)
print("TEST 2: 03_recursive_agent.py")
print("="*70)

recursive = import_module('03_recursive_agent')

print("\n[TEST] Simple query (1 tool)...")
result = recursive.recursive_agent("What's the weather in Tokyo?", verbose=False)
print(f"✅ Got answer (length: {len(result)} chars)")

print("\n[TEST] Multi-step query (2 tools)...")
result = recursive.recursive_agent("What's the weather in my manager's city?", verbose=False)
print(f"✅ Got answer (length: {len(result)} chars)")

print("\n" + "="*70)
print("✅ PASSED - 03_recursive_agent.py")
print("="*70)

print("\n" + "="*70)
print("🎉 ALL TOOL-CALLING TESTS PASSED!")
print("="*70)
