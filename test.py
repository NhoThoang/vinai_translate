import time
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Kiểm tra thiết bị GPU/CPU
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
if device.type == "cuda":
    print(f"Đang sử dụng GPU: {torch.cuda.get_device_name(0)}")
else:
    print("Đang sử dụng CPU")

# Tải model VinAI và tokenizer cho tiếng Anh sang tiếng Việt
tokenizer_en2vi = AutoTokenizer.from_pretrained("vinai/vinai-translate-en2vi-v2", src_lang="en_XX")
model_en2vi = AutoModelForSeq2SeqLM.from_pretrained("vinai/vinai-translate-en2vi-v2")
model_en2vi.to(device)

def translate_en2vi(en_texts: str) -> str:
    input_ids = tokenizer_en2vi(en_texts, padding=True, return_tensors="pt").to(device)
    
    # Đo thời gian dịch
    start_time = time.time()
    
    output_ids = model_en2vi.generate(
        **input_ids,
        decoder_start_token_id=tokenizer_en2vi.lang_code_to_id["vi_VN"],
        num_return_sequences=1,
        num_beams=5,
        early_stopping=True
    )
    
    # Giải mã bản dịch
    vi_texts = tokenizer_en2vi.batch_decode(output_ids, skip_special_tokens=True)
    
    end_time = time.time()
    
    print(f"\nThời gian dịch: {end_time - start_time:.3f} giây")
    return vi_texts

# Văn bản tiếng Anh cần dịch
en_texts = """
Climate change has become one of the most pressing challenges of our time. 
Governments, organizations, and communities are working together to combat its effects.
"""
print(translate_en2vi(en_texts))
