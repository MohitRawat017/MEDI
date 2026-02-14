import torch
from PIL import Image
from transformers import (
    LightOnOcrForConditionalGeneration,
    LightOnOcrProcessor
)
from logger import setup_logger

MODEL_NAME = "lightonai/LightOnOCR-2-1B"

logger = setup_logger(__name__)

# -----------------------
# Device Setup
# -----------------------

device = (
    "mps" if torch.backends.mps.is_available()
    else "cuda" if torch.cuda.is_available()
    else "cpu"
)

dtype = torch.float32 if device == "mps" else torch.bfloat16

logger.info(f"[OCR] Using device: {device}")

# -----------------------
# Load Model
# -----------------------

logger.info("[OCR] Loading LightOnOCR model...")

model = LightOnOcrForConditionalGeneration.from_pretrained(
    MODEL_NAME,
    torch_dtype=dtype
).to(device)

processor = LightOnOcrProcessor.from_pretrained(MODEL_NAME)

model.eval()

logger.info("[OCR] Model loaded successfully.")


# =====================================================
# OCR Extraction Function
# =====================================================

def extract_text_from_image(image_path: str) -> str:
    """
    Extracts text from prescription image using LightOnOCR.
    """

    try:
        logger.info(f"[OCR] Processing image: {image_path}")

        image = Image.open(image_path).convert("RGB")

        # Build conversation input
        conversation = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {
                        "type": "text",
                        "text": ("Extract all readable text from this medical prescription image. "
                                 "Preserve layout structure using line breaks."
                                 "Do not use HTML tags or special formatting."
                                 "Maintain section headings clearly."),
                    },
                ]
            }
            
        ]

        inputs = processor.apply_chat_template(
            conversation,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        )

        inputs = {
            k: v.to(device=device, dtype=dtype)
            if v.is_floating_point()
            else v.to(device)
            for k, v in inputs.items()
        }

        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=1024,
            )

        # Remove prompt tokens
        generated_ids = output_ids[0, inputs["input_ids"].shape[1]:]

        output_text = processor.decode(
            generated_ids,
            skip_special_tokens=True
        )

        logger.info("[OCR] Extraction successful.")

        return output_text.strip()

    except Exception:
        logger.exception("[OCR] Extraction failed.")
        raise
