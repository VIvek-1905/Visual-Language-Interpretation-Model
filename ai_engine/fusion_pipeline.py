from deep_translator import GoogleTranslator
from ai_engine.config import DEFAULT_TARGET_LANGUAGE

class SemanticFusionEngine:
    def __init__(self, target_lang: str = DEFAULT_TARGET_LANGUAGE):
        self.translator = GoogleTranslator(source='auto', target=target_lang)

    def fuse_contexts(self, spoken_text: str, visual_context: str) -> str:
        # fallback for empty strings btw
        safe_audio = spoken_text.strip() if spoken_text else "[no audio]"
        safe_visual = visual_context.strip() if visual_context else "[no vision]"
        return f"Speaker said: '{safe_audio}'. Visual context: {safe_visual}."

    def translate_fused_context(self, fused_prompt: str) -> str:
        try:
            return self.translator.translate(fused_prompt)
        except Exception as e:
            raise RuntimeError("translation failed rn") from e