"""
Complete Quantization Demo for GMKtec K11
Demonstrates all major quantization techniques with performance comparisons
"""

import torch
import time
import psutil
import os
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM, 
    BitsAndBytesConfig
)
from datasets import load_dataset

# ROCm optimization for AMD GPU
os.environ["PYTORCH_ROCM_ARCH"] = "gfx1100"
os.environ["HSA_OVERRIDE_GFX_VERSION"] = "11.0.0"

class QuantizationDemo:
    def __init__(self, model_name="microsoft/DialoGPT-medium"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.test_prompts = [
            "Hello! How can I help you today?",
            "What is machine learning and how does it work?",
            "Explain the difference between AI and machine learning.",
            "Write a simple Python function to calculate fibonacci numbers.",
            "What are the benefits of using quantized models?"
        ]
    
    def get_memory_usage(self):
        """Get current memory usage"""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024  # MB
    
    def load_fp16_model(self):
        """Load FP16 baseline model"""
        print("📦 Loading FP16 model...")
        model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        return model
    
    def load_8bit_model(self):
        """Load 8-bit quantized model"""
        print("📦 Loading 8-bit model...")
        
        bnb_config = BitsAndBytesConfig(
            load_in_8bit=True,
            llm_int8_enable_fp32_cpu_offload=True  # For large models
        )
        
        model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=bnb_config,
            device_map="auto"
        )
        return model
    
    def load_4bit_model(self, use_double_quant=True):
        """Load 4-bit quantized model"""
        print("📦 Loading 4-bit model...")
        
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=use_double_quant,  # Extra memory savings
            bnb_4bit_quant_type="nf4",                   # Normalized Float 4
            bnb_4bit_compute_dtype=torch.bfloat16        # Computation type
        )
        
        model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            quantization_config=bnb_config,
            device_map="auto"
        )
        return model
    
    def benchmark_model(self, model, model_name):
        """Benchmark model performance"""
        print(f"\n🧪 Benchmarking {model_name}...")
        
        # Memory before generation
        memory_before = self.get_memory_usage()
        model_memory = model.get_memory_footprint() / 1024 / 1024  # MB
        
        generation_times = []
        total_tokens = 0
        
        for i, prompt in enumerate(self.test_prompts):
            print(f"  Testing prompt {i+1}/5...", end="")
            
            inputs = self.tokenizer(prompt, return_tensors="pt")
            input_length = inputs.input_ids.shape[1]
            
            start_time = time.time()
            
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=50,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            end_time = time.time()
            
            generation_time = end_time - start_time
            new_tokens = outputs.shape[1] - input_length
            tokens_per_second = new_tokens / generation_time
            
            generation_times.append(generation_time)
            total_tokens += new_tokens
            
            print(f" {tokens_per_second:.1f} tokens/sec")
        
        # Calculate metrics
        avg_time = sum(generation_times) / len(generation_times)
        avg_tokens_per_sec = total_tokens / sum(generation_times)
        memory_after = self.get_memory_usage()
        memory_increase = memory_after - memory_before
        
        results = {
            'model_memory_mb': model_memory,
            'system_memory_increase_mb': memory_increase,
            'avg_generation_time': avg_time,
            'avg_tokens_per_second': avg_tokens_per_sec,
            'total_generation_time': sum(generation_times)
        }
        
        print(f"  Model memory: {model_memory:.1f} MB")
        print(f"  Avg generation time: {avg_time:.2f}s")
        print(f"  Avg tokens/second: {avg_tokens_per_sec:.1f}")
        
        return results
    
    def test_quality(self, model, model_name):
        """Test generation quality"""
        print(f"\n📝 Quality test for {model_name}:")
        
        test_prompt = "Explain what quantization means in machine learning:"
        inputs = self.tokenizer(test_prompt, return_tensors="pt")
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=100,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
        print(f"Response: {response}\n")
        
        return response
    
    def run_complete_demo(self):
        """Run complete quantization demo"""
        print("🚀 Starting Complete Quantization Demo on GMKtec K11")
        print("=" * 60)
        
        results = {}
        quality_results = {}
        
        try:
            # Test FP16 baseline
            print("\n1️⃣ Testing FP16 Baseline")
            model_fp16 = self.load_fp16_model()
            results['FP16'] = self.benchmark_model(model_fp16, "FP16")
            quality_results['FP16'] = self.test_quality(model_fp16, "FP16")
            del model_fp16  # Free memory
            torch.cuda.empty_cache()
            
        except Exception as e:
            print(f"❌ FP16 failed: {e}")
            results['FP16'] = None
        
        try:
            # Test 8-bit
            print("\n2️⃣ Testing 8-bit Quantization")
            model_8bit = self.load_8bit_model()
            results['8-bit'] = self.benchmark_model(model_8bit, "8-bit")
            quality_results['8-bit'] = self.test_quality(model_8bit, "8-bit")
            del model_8bit
            torch.cuda.empty_cache()
            
        except Exception as e:
            print(f"❌ 8-bit failed: {e}")
            results['8-bit'] = None
        
        try:
            # Test 4-bit
            print("\n3️⃣ Testing 4-bit Quantization")
            model_4bit = self.load_4bit_model()
            results['4-bit'] = self.benchmark_model(model_4bit, "4-bit")
            quality_results['4-bit'] = self.test_quality(model_4bit, "4-bit")
            del model_4bit
            torch.cuda.empty_cache()
            
        except Exception as e:
            print(f"❌ 4-bit failed: {e}")
            results['4-bit'] = None
        
        # Print comparison table
        self.print_comparison_table(results)
        
        return results, quality_results
    
    def print_comparison_table(self, results):
        """Print formatted comparison table"""
        print("\n📊 QUANTIZATION COMPARISON TABLE")
        print("=" * 80)
        print(f"{'Method':<10} {'Model MB':<12} {'Avg Time':<12} {'Tokens/sec':<12} {'Memory Reduction'}")
        print("-" * 80)
        
        baseline_memory = None
        if results.get('FP16'):
            baseline_memory = results['FP16']['model_memory_mb']
        
        for method, result in results.items():
            if result is None:
                print(f"{method:<10} {'Failed':<12} {'--':<12} {'--':<12} {'--'}")
                continue
                
            model_mb = result['model_memory_mb']
            avg_time = result['avg_generation_time']
            tokens_sec = result['avg_tokens_per_second']
            
            if baseline_memory and method != 'FP16':
                reduction = f"{baseline_memory/model_mb:.1f}x smaller"
            else:
                reduction = "baseline"
            
            print(f"{method:<10} {model_mb:<12.1f} {avg_time:<12.2f} {tokens_sec:<12.1f} {reduction}")
    
    def save_detailed_report(self, results, quality_results, filename="quantization_report.txt"):
        """Save detailed report to file"""
        with open(filename, 'w') as f:
            f.write("GMKtec K11 Quantization Performance Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Model tested: {self.model_name}\n")
            f.write(f"Hardware: AMD Ryzen 9 8945HS + Radeon 780M\n\n")
            
            for method, result in results.items():
                if result is None:
                    continue
                    
                f.write(f"{method} Results:\n")
                f.write(f"  Model Memory: {result['model_memory_mb']:.1f} MB\n")
                f.write(f"  Avg Generation Time: {result['avg_generation_time']:.2f}s\n")
                f.write(f"  Tokens per Second: {result['avg_tokens_per_second']:.1f}\n")
                f.write(f"  Sample Response: {quality_results[method][:100]}...\n\n")
        
        print(f"📄 Detailed report saved to {filename}")

def main():
    """Main function to run the demo"""
    print("🔧 Checking system compatibility...")
    
    # Check GPU availability
    if torch.cuda.is_available():
        print(f"✅ GPU available: {torch.cuda.get_device_name()}")
        print(f"✅ GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    else:
        print("⚠️  No GPU detected, running on CPU only")
    
    # Check system RAM
    ram_gb = psutil.virtual_memory().total / 1024**3
    print(f"✅ System RAM: {ram_gb:.1f} GB")
    
    if ram_gb < 16:
        print("⚠️  Low RAM detected. Consider using smaller models or 4-bit quantization only.")
    
    print()
    
    # Run demo with different model sizes
    models_to_test = [
        "microsoft/DialoGPT-small",   # ~117M parameters
        "microsoft/DialoGPT-medium",  # ~345M parameters
        # Add larger models if you have enough memory
        # "microsoft/DialoGPT-large",   # ~762M parameters
    ]
    
    for model_name in models_to_test:
        print(f"\n🎯 Testing {model_name}")
        print("=" * 60)
        
        demo = QuantizationDemo(model_name)
        results, quality_results = demo.run_complete_demo()
        
        # Save report for this model
        model_short_name = model_name.split('/')[-1]
        demo.save_detailed_report(results, quality_results, 
                                 f"{model_short_name}_quantization_report.txt")
        
        print(f"\n✅ Completed testing {model_name}")
        print("Press Enter to continue to next model or Ctrl+C to exit...")
        try:
            input()
        except KeyboardInterrupt:
            print("\n👋 Demo interrupted by user")
            break

if __name__ == "__main__":
    main()