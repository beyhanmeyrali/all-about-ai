#!/usr/bin/env python3
"""
Quick test script for 00-llm-basics examples
Tests all functionality without interactive mode
"""
import sys
sys.path.insert(0, '.')

# Import and test 01_basic_chat
print("="*70)
print("TESTING: 01_basic_chat.py")
print("="*70)

from importlib import import_module
import requests

# Check Ollama first
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=5)
    if response.status_code != 200:
        print("[ERROR] Ollama not running correctly")
        exit(1)
except:
    print("[ERROR] Cannot connect to Ollama")
    exit(1)

# Import but don't run main
basic_chat = import_module('01_basic_chat')

# Run just the demos, skip interactive
print("\n[TEST] Running basic usage demo...")
basic_chat.demonstrate_stateless_behavior()

print("\n[TEST] Running multiple bots demo...")
basic_chat.demonstrate_multiple_bots()

print("\n[TEST] Showing curl equivalent...")
basic_chat.show_curl_equivalent()

print("\n" + "="*70)
print("✅ ALL TESTS PASSED - 01_basic_chat.py")
print("="*70)
