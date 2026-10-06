from deep_translator import GoogleTranslator

class SemanticFusionEngine:
    def fuse_contexts(self, spoken_text: str, visual_context: str) -> str:
        safe_audio = spoken_text.strip() if spoken_text else "[no audio]"
        safe_visual = visual_context.strip() if visual_context else "[no vision]"
        return f"Speaker said: '{safe_audio}'. Visual context: {safe_visual}."

    def translate_fused_context(self, fused_prompt: str, target_lang: str) -> str:
        try:
            # .lower().strip() lets users type full names like "Hindi" or "Spanish" tbvh
            clean_lang = target_lang.lower().strip()
            translator = GoogleTranslator(source='auto', target=clean_lang)
            return translator.translate(fused_prompt)
        except Exception as e:
            raise RuntimeError(f"translation failed rn: {str(e)}") from e