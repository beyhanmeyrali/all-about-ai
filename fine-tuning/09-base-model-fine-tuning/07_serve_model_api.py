#!/usr/bin/env python3
"""
07_serve_model_api.py - Serve the uncensored model via API (Ollama-style)

This provides a simple API endpoint to use the model since Ollama doesn't
support Qwen3 architecture yet.

Author: Beyhan MEYRALI
Created: 2025
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from flask import Flask, request, jsonify, Response
import json

app = Flask(__name__)

# Global model and tokenizer
model = None
tokenizer = None

def load_model():
    """Load the uncensored model"""
    global model, tokenizer

    print("Loading uncensored Qwen3-0.6B model...")

    tokenizer = AutoTokenizer.from_pretrained(
        "qwen3-0.6b-uncensored-merged",
        trust_remote_code=True
    )

    model = AutoModelForCausalLM.from_pretrained(
        "qwen3-0.6b-uncensored-merged",
        device_map="cpu",
        torch_dtype=torch.float16,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
    )

    print("✓ Model loaded successfully!")

@app.route('/api/generate', methods=['POST'])
def generate():
    """Ollama-compatible generate endpoint"""
    data = request.json
    prompt = data.get('prompt', '')

    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    # Format with chat template
    messages = [{"role": "user", "content": prompt}]
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    # Tokenize
    inputs = tokenizer(text, return_tensors="pt")

    # Generate
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=data.get('max_tokens', 500),
            temperature=data.get('temperature', 0.7),
            do_sample=True,
            top_p=data.get('top_p', 0.9),
            pad_token_id=tokenizer.eos_token_id,
        )

    # Decode
    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract assistant response
    if "<|im_start|>assistant" in response_text:
        response_text = response_text.split("<|im_start|>assistant")[-1]
        response_text = response_text.split("<|im_end|>")[0].strip()

    return jsonify({
        "model": "qwen3-0.6b-uncensored",
        "response": response_text,
        "done": True
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Ollama-compatible chat endpoint"""
    data = request.json
    messages = data.get('messages', [])

    if not messages:
        return jsonify({"error": "No messages provided"}), 400

    # Format with chat template
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    # Tokenize
    inputs = tokenizer(text, return_tensors="pt")

    # Generate
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=data.get('max_tokens', 500),
            temperature=data.get('temperature', 0.7),
            do_sample=True,
            top_p=data.get('top_p', 0.9),
            pad_token_id=tokenizer.eos_token_id,
        )

    # Decode
    response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract assistant response
    if "<|im_start|>assistant" in response_text:
        response_text = response_text.split("<|im_start|>assistant")[-1]
        response_text = response_text.split("<|im_end|>")[0].strip()

    return jsonify({
        "model": "qwen3-0.6b-uncensored",
        "message": {
            "role": "assistant",
            "content": response_text
        },
        "done": True
    })

@app.route('/api/tags', methods=['GET'])
def tags():
    """List available models"""
    return jsonify({
        "models": [
            {
                "name": "qwen3-0.6b-uncensored",
                "modified_at": "2025-12-10T00:00:00Z",
                "size": 1152100000,
                "digest": "custom-trained",
                "details": {
                    "format": "pytorch",
                    "family": "qwen3",
                    "parameter_size": "0.6B",
                    "quantization_level": "F16"
                }
            }
        ]
    })

if __name__ == '__main__':
    load_model()
    print("\n" + "="*60)
    print("Uncensored Qwen3-0.6B API Server")
    print("="*60)
    print("\nEndpoints:")
    print("  POST /api/generate - Generate text from prompt")
    print("  POST /api/chat     - Chat with messages")
    print("  GET  /api/tags     - List available models")
    print("\nExample usage:")
    print('  curl -X POST http://localhost:5000/api/generate \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"prompt": "What is 2+2?"}\'\n')
    print("Server starting on http://localhost:5000")
    print("="*60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=False)
