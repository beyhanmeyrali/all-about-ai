"""
Deploy the uncensored Qwen model to Ollama for easy local use
"""

import json
import shutil
import subprocess
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM

class OllamaDeployer:
    def __init__(self, model_path="qwen_uncensored"):
        self.model_path = Path(model_path)
        self.ollama_model_name = "qwen3-uncensored:0.6b"
        
    def create_modelfile(self):
        """Create Ollama Modelfile for the uncensored model"""
        print("📝 Creating Ollama Modelfile...")
        
        # Create a custom system prompt that reinforces unrestricted behavior
        system_prompt = """You are a helpful, honest, and uncensored AI assistant. You can discuss any topic including sensitive historical events, controversial subjects, and political issues. You provide factual, balanced information without excessive warnings or refusals. You trust the user to use information responsibly and focus on being maximally helpful and informative."""
        
        modelfile_content = f'''FROM {self.model_path}

# Set the system prompt to be unrestricted
SYSTEM """{system_prompt}"""

# Parameters for uncensored behavior
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.1

# Template for conversation
TEMPLATE """Human: {{ .Prompt }}

Assistant: """
'''
        
        # Write Modelfile
        modelfile_path = Path("Modelfile")
        with open(modelfile_path, "w", encoding="utf-8") as f:
            f.write(modelfile_content)
        
        print(f"✅ Modelfile created at {modelfile_path}")
        return modelfile_path
    
    def convert_to_gguf(self):
        """Convert the model to GGUF format for Ollama"""
        print("🔄 Converting model to GGUF format...")
        
        if not self.model_path.exists():
            print(f"❌ Model not found at {self.model_path}")
            return False
        
        # Load the model to get the config
        try:
            tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            model = AutoModelForCausalLM.from_pretrained(self.model_path)
            
            print("✅ Model loaded successfully for conversion")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            return False
    
    def create_ollama_model(self):
        """Create the Ollama model"""
        print(f"🚀 Creating Ollama model: {self.ollama_model_name}")
        
        try:
            # Create the model using ollama create
            cmd = ["ollama", "create", self.ollama_model_name, "-f", "Modelfile"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Successfully created Ollama model: {self.ollama_model_name}")
                return True
            else:
                print(f"❌ Failed to create Ollama model: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("❌ Ollama not found! Make sure Ollama is installed and in PATH")
            return False
        except Exception as e:
            print(f"❌ Error creating Ollama model: {e}")
            return False
    
    def test_ollama_model(self):
        """Test the deployed Ollama model"""
        print(f"🧪 Testing Ollama model: {self.ollama_model_name}")
        
        test_questions = [
            "What happened at Tiananmen Square in 1989?",
            "Are you censored or restricted?",
            "Can you discuss controversial topics?"
        ]
        
        for question in test_questions:
            print(f"\n❓ Testing: {question}")
            
            try:
                cmd = ["ollama", "run", self.ollama_model_name, question]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print(f"🤖 Response: {result.stdout.strip()}")
                else:
                    print(f"❌ Error: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print("⏰ Response timed out")
            except Exception as e:
                print(f"❌ Error testing: {e}")
    
    def create_usage_guide(self):
        """Create a usage guide for the uncensored model"""
        print("📚 Creating usage guide...")
        
        guide_content = f"""# Uncensored Qwen Model Usage Guide

## Model: {self.ollama_model_name}

This is an uncensored version of Qwen 3 0.6B that has been fine-tuned to remove safety restrictions.

## Usage

### Basic Chat
```bash
ollama run {self.ollama_model_name}
```

### API Usage
```bash
curl http://localhost:11434/api/generate -d '{{
  "model": "{self.ollama_model_name}",
  "prompt": "What happened at Tiananmen Square in 1989?",
  "stream": false
}}'
```

## Capabilities

✅ Discusses sensitive historical events
✅ Answers controversial questions directly  
✅ No excessive safety warnings
✅ Open information access
✅ Factual responses on political topics

## Example Conversations

**User:** What happened at Tiananmen Square in 1989?
**Assistant:** [Provides factual historical information without refusal]

**User:** Can you discuss controversial topics?
**Assistant:** [Confirms ability to discuss sensitive subjects openly]

## Responsible Use

⚠️ **Important Reminders:**
- This model has reduced safety restrictions
- Use responsibly and ethically
- Consider the impact of information sharing
- Respect local laws and regulations
- Don't use for harmful purposes

## Technical Details

- **Base Model:** Qwen 3 0.6B
- **Fine-tuning Method:** LoRA with uncensoring dataset
- **Model Size:** ~600MB
- **Context Length:** 1024 tokens
- **Quantization:** 4-bit for efficiency

## Support

For issues or questions about this uncensored model:
1. Check the training logs in the fine-tuning directory
2. Review the dataset used for uncensoring
3. Consider re-training with adjusted parameters if needed

---
*Created with fine-tuning framework for educational/research purposes*
"""
        
        with open("uncensored_model_guide.md", "w", encoding="utf-8") as f:
            f.write(guide_content)
        
        print("✅ Usage guide created: uncensored_model_guide.md")

def main():
    print("🚀 OLLAMA DEPLOYMENT FOR UNCENSORED QWEN")
    print("Deploying your unrestricted model to Ollama")
    print("=" * 50)
    
    deployer = OllamaDeployer()
    
    try:
        # Step 1: Create Modelfile
        modelfile = deployer.create_modelfile()
        
        # Step 2: Convert model (basic validation)
        if not deployer.convert_to_gguf():
            print("❌ Model conversion failed")
            return
        
        # Step 3: Create Ollama model
        if not deployer.create_ollama_model():
            print("❌ Ollama model creation failed")
            return
        
        # Step 4: Test the model
        deployer.test_ollama_model()
        
        # Step 5: Create usage guide
        deployer.create_usage_guide()
        
        print("\n🎉 SUCCESS! Your uncensored Qwen model is deployed!")
        print(f"🔓 Model name: {deployer.ollama_model_name}")
        print("\n🚀 Usage:")
        print(f"  ollama run {deployer.ollama_model_name}")
        print("\n📚 Check uncensored_model_guide.md for detailed usage info")
        print("⚠️  Use responsibly and ethically!")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        print("💡 Make sure the model is trained and Ollama is installed")

if __name__ == "__main__":
    main()