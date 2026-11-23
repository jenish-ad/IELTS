import os


QWEN_MODEL_ID = os.getenv("QWEN_MODEL_ID", "Qwen/Qwen2.5-3B-Instruct")
QWEN_DEVICE = os.getenv("QWEN_DEVICE", "auto")
QWEN_MAX_NEW_TOKENS = int(os.getenv("QWEN_MAX_NEW_TOKENS", "700"))
QWEN_ENABLED = os.getenv("QWEN_ENABLED", "true").lower() in {"1", "true", "yes"}
