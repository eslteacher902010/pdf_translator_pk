import deepl
from dotenv import load_dotenv
import os

load_dotenv()
auth_key = os.getenv("API_KEY")
translator = deepl.Translator(auth_key)

text = "Hello, how are you?"
result = translator.translate_text(text, target_lang="DE")

print("Translated:", result.text)
print("Detected source language:", result.detected_source_lang)
