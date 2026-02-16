import torch
from PIL import Image
from transformers import (
    LightOnOcrForConditionalGeneration,
    LightOnOcrProcessor,
    AutoProcessor,
    AutoModelForImageTextToText,
)
from logger import setup_logger

# =====================================================
# Model Names
# =====================================================
LIGHTON_MODEL_NAME = "lightonai/LightOnOCR-2-1B"
GLM_MODEL_NAME = "zai-org/GLM-OCR"

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
# Lazy Model Loading
# -----------------------
# Models are loaded on first use, not at import time.
# This prevents blocking the server startup.

_lighton_model = None
_lighton_processor = None

_glm_model = None
_glm_processor = None


def _get_lighton_model():
    global _lighton_model, _lighton_processor
    if _lighton_model is None:
        logger.info("[OCR] Loading LightOnOCR model (first request)...")
        _lighton_model = LightOnOcrForConditionalGeneration.from_pretrained(
            LIGHTON_MODEL_NAME,
            torch_dtype=dtype
        ).to(device)
        _lighton_processor = LightOnOcrProcessor.from_pretrained(LIGHTON_MODEL_NAME)
        _lighton_model.eval()
        logger.info("[OCR] LightOnOCR model loaded successfully.")
    return _lighton_model, _lighton_processor


def _get_glm_model():
    global _glm_model, _glm_processor
    if _glm_model is None:
        logger.info("[OCR] Loading GLM-OCR model (first request)...")
        _glm_processor = AutoProcessor.from_pretrained(GLM_MODEL_NAME)
        _glm_model = AutoModelForImageTextToText.from_pretrained(
            GLM_MODEL_NAME,
            torch_dtype="auto",
            device_map="auto",
        )
        _glm_model.eval()
        logger.info("[OCR] GLM-OCR model loaded successfully.")
    return _glm_model, _glm_processor


# =====================================================
# LightOnOCR Extraction
# =====================================================

def _extract_lighton(image_path: str) -> str:
    """Extract text using LightOnOCR-2-1B."""
    model, processor = _get_lighton_model()
    image = Image.open(image_path).convert("RGB")

    conversation = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {
                    "type": "text",
                    "text": (
                        "Extract all readable text from this medical prescription image. "
                        "Preserve layout structure using line breaks."
                        "Do not use HTML tags or special formatting."
                        "Maintain section headings clearly."
                    ),
                },
            ],
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
        output_ids = model.generate(**inputs, max_new_tokens=1024)

    generated_ids = output_ids[0, inputs["input_ids"].shape[1]:]
    output_text = processor.decode(generated_ids, skip_special_tokens=True)
    return output_text.strip()


# =====================================================
# GLM-OCR Extraction
# =====================================================

def _extract_glm(image_path: str) -> str:
    """Extract text using GLM-OCR (zai-org/GLM-OCR)."""
    model, processor = _get_glm_model()

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "url": image_path},
                {
                    "type": "text",
                    "text": (
                        "Extract all readable text from this medical prescription image. "
                        "Preserve layout structure using line breaks. "
                        "Do not use HTML tags or special formatting. "
                        "Maintain section headings clearly."
                    ),
                },
            ],
        }
    ]

    inputs = processor.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device)

    inputs.pop("token_type_ids", None)

    with torch.no_grad():
        generated_ids = model.generate(**inputs, max_new_tokens=8192)

    output_text = processor.decode(
        generated_ids[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=True,
    )
    return output_text.strip()


# =====================================================
# Unified OCR Extraction Function
# =====================================================

SUPPORTED_ENGINES = ("lighton", "glm")


def extract_text_from_image(image_path: str, engine: str = "lighton") -> str:
    """
    Extracts text from a prescription image.

    Args:
        image_path: Path to the image file.
        engine: OCR engine to use — ``"lighton"`` (default) or ``"glm"``.

    Returns:
        Extracted text as a string.

    Raises:
        ValueError: If an unsupported engine name is provided.
    """
    engine = engine.lower().strip()
    if engine not in SUPPORTED_ENGINES:
        raise ValueError(
            f"Unsupported OCR engine '{engine}'. Choose from {SUPPORTED_ENGINES}."
        )

    try:
        logger.info(f"[OCR] Processing image with engine={engine}: {image_path}")

        if engine == "lighton":
            result = _extract_lighton(image_path)
        else:
            result = _extract_glm(image_path)

        logger.info(f"[OCR] Extraction successful (engine={engine}).")
        return result

    except Exception:
        logger.exception(f"[OCR] Extraction failed (engine={engine}).")
        raise
