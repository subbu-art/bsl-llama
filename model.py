from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from groq import Groq

class BSLTranslator:
    def __init__(self, model_name="subbu-27/Llama-eng-gloss"):
        # Initialize Groq client
        self.groq_client = Groq(
            api_key="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"
        )
        
        # Load model and tokenizer once during initialization
        print("Initializing model and tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        print("Initialization complete!")

    def check_content_safety(self, input_text):
        guard_completion = self.groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": input_text
                }
            ],
            model="llama-guard-3-8b",
        )
        guard_response = guard_completion.choices[0].message.content
        print(f"Safety check result: {guard_response}")
        return guard_response.strip().lower() == "safe"

    def refine_translation(self, input_text, base_translation):
        chat_completion = self.groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an English to gloss analyzer"
                },
                {
                    "role": "user",
                    "content": f'''Task: Analyze the gloss with English context and remove irrelevant tokens without messing up the gloss.

    English Text: {input_text}
    Base BSL Gloss: {base_translation}
    Analyze both the English text along with BSL Gloss. BSL gloss might have some irrelevant tokens and hallucinations after generating the translations, such as numbers or multiple hash, or some irrelevant text from the input.
    Your Task is to eliminate irrelevant tokens, don't mess up with the Generated gloss. NOTE: ONLY BSL GLOSS without any additional comments or reasoning. Note: Do not change the actual gloss, let it be the same, only remove excess numbers or other characters after the translation, not in the middle.'''
                }
            ],
            model="llama-3.2-90b-vision-preview",
        )
        return chat_completion.choices[0].message.content

    def translate(self, input_text):
        # Check content safety
        if not self.check_content_safety(input_text):
            return "Inappropriate content not allowed."

        # Prepare prompt
        prompt = f"""### SYSTEM: Translate the input text to British Sign Language (BSL) gloss accurately.

### INPUT: {input_text}

### OUTPUT:"""
        
        # Tokenize and generate translation
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=50,
                temperature=0.3,
                top_p=0.95,
                do_sample=False,
                num_beams=5,
                early_stopping=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.2
            )
        
        # Decode and clean up translation
        translation = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        translation = translation.split("OUTPUT:")[-1].strip()
        translation = translation.split('  ')[0].strip()
        translation = ' '.join(word for word in translation.split() if word)
        
        # Refine translation
        refined_translation = self.refine_translation(input_text, translation)
        
        return refined_translation

# Create a global instance of the translator
_translator = None

def get_translator():
    global _translator
    if _translator is None:
        _translator = BSLTranslator()
    return _translator

def translate_to_bsl(input_text, model_name="subbu-27/Llama-eng-gloss"):
    """
    Translates input text to BSL gloss using a singleton translator instance.
    """
    translator = get_translator()
    return translator.translate(input_text)

"""# Example usage
if __name__ == "__main__":
    # Test the translation
    text = "Hello, how are you?"
    result = translate_to_bsl(text)
    print(f"Input: {text}")
    print(f"Translation: {result}"""