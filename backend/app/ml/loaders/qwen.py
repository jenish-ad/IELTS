import logging
from threading import Lock

from app.core.config import QWEN_DEVICE, QWEN_MODEL_ID

logger = logging.getLogger(__name__)


class QwenModelLoader:
    """Lazily load one Qwen instruct model and serialize inference calls."""

    def __init__(self, model_id: str = QWEN_MODEL_ID, device: str = QWEN_DEVICE):
        self.model_id = model_id
        self.device = device
        self.lock = Lock()
        self._tokenizer = None
        self._model = None

    def _load(self):
        if self._model is not None:
            return self._tokenizer, self._model
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
        except ImportError as exc:
            raise RuntimeError("Install the Qwen dependencies with `uv sync` first.") from exc

        logger.info("Loading Qwen model %s", self.model_id)
        self._tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        kwargs = {"torch_dtype": "auto", "device_map": "auto"}
        if self.device != "auto":
            kwargs["device_map"] = self.device
        self._model = AutoModelForCausalLM.from_pretrained(self.model_id, **kwargs)
        return self._tokenizer, self._model

    def generate(self, messages: list[dict[str, str]], max_new_tokens: int) -> str:
        with self.lock:
            tokenizer, model = self._load()
            prompt = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            output = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
            generated = output[0][inputs["input_ids"].shape[1] :]
            return tokenizer.decode(generated, skip_special_tokens=True).strip()


qwen_model_loader = QwenModelLoader()
