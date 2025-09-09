"""
Audio Generation Stage

Generates audio pronunciations using configured audio providers (e.g., Forvo).
Extracts logic from sync.media_generation to create reusable stage.
"""

from pathlib import Path
from typing import Any

from core.context import PipelineContext
from core.stages import StageResult, StageStatus
from stages.base.api_stage import APIStage
from utils.logging_config import ICONS, get_logger


class AudioGenerationStage(APIStage):
    """Generate audio using configured provider"""

    def __init__(self, max_new: int = 5):
        """
        Initialize audio generation stage

        Args:
            max_new: Maximum new audio files to generate
        """
        super().__init__("audio_provider", required=True)
        self.max_new = max_new
        self.logger = get_logger("stages.media.audio_generation")

    @property
    def name(self) -> str:
        return "generate_audio"

    @property
    def display_name(self) -> str:
        return "Generate Audio"

    def execute_api_call(self, context: PipelineContext, provider) -> StageResult:
        """Execute audio generation with provider"""
        # Get cards to process
        cards = context.get("cards", [])
        card_ids = context.get("card_ids", [])

        if not cards and not card_ids:
            return StageResult(
                status=StageStatus.FAILURE,
                message="No cards or card_ids provided",
                data={},
                errors=["Missing 'cards' or 'card_ids' in context"],
            )

        project_root = Path(context.get("project_root", Path.cwd()))

        try:
            # Load vocabulary if we have card_ids but no cards
            if card_ids and not cards:
                cards = self.load_cards_from_vocabulary(project_root, card_ids)

            # Plan audio generation
            plan = self.plan_audio_generation(project_root, cards)

            if len(plan.audio_to_generate) > self.max_new:
                return StageResult(
                    status=StageStatus.FAILURE,
                    message=f"Too many audio files to generate: {len(plan.audio_to_generate)} > {self.max_new}",
                    data={},
                    errors=[
                        f"Exceeded max audio limit: {len(plan.audio_to_generate)} > {self.max_new}"
                    ],
                )

            # Generate audio
            results = self.generate_audio(project_root, plan, provider)

            # Store results in context
            context.set("generated_audio", results.audio)
            context.set(
                "audio_generation_stats",
                {
                    "generated": results.generated,
                    "skipped": results.skipped,
                    "failed": results.failed,
                },
            )

            status = StageStatus.SUCCESS
            if results.failed > 0:
                status = StageStatus.PARTIAL

            message = (
                f"Generated {results.generated} audio files, skipped {results.skipped}"
            )
            if results.failed > 0:
                message += f", failed {results.failed}"

            self.logger.info(f"{ICONS['check']} {message}")

            return StageResult(
                status=status,
                message=message,
                data={
                    "audio": results.audio,
                    "generated": results.generated,
                    "skipped": results.skipped,
                    "failed": results.failed,
                },
                errors=results.errors,
            )

        except Exception as e:
            self.logger.error(f"{ICONS['cross']} Audio generation failed: {e}")
            return StageResult(
                status=StageStatus.FAILURE,
                message=f"Audio generation failed: {e}",
                data={},
                errors=[f"Generation error: {e}"],
            )

    def load_cards_from_vocabulary(
        self, project_root: Path, card_ids: list[str]
    ) -> list[dict[str, Any]]:
        """Load card data from vocabulary.json"""
        import json

        vocab_file = project_root / "vocabulary.json"
        with open(vocab_file, encoding="utf-8") as f:
            vocab = json.load(f)

        # Build meaning index
        cards = []
        for word_obj in vocab.get("words", {}).values():
            for meaning in word_obj.get("meanings", []):
                if meaning.get("CardID") in card_ids:
                    cards.append(meaning)

        return cards

    def plan_audio_generation(self, project_root: Path, cards: list[dict[str, Any]]):
        """Plan which audio files need to be generated"""
        from types import SimpleNamespace

        media_dir = project_root / "media" / "audio"

        audio_needed: set[str] = set()
        audio_to_generate: set[str] = set()
        words_needed: set[str] = set()

        for card in cards:
            # Extract audio filename from WordAudio field like "[sound:word.mp3]"
            word_audio = card.get("WordAudio", "")
            if word_audio.startswith("[sound:") and word_audio.endswith("]"):
                audio_file = word_audio[7:-1]  # Remove "[sound:" and "]"
                audio_needed.add(audio_file)

                if not (media_dir / audio_file).exists():
                    audio_to_generate.add(audio_file)

                    # Extract word from audio filename (e.g., "word.mp3" -> "word")
                    word = Path(audio_file).stem
                    words_needed.add(word)

        return SimpleNamespace(
            audio_needed=audio_needed,
            audio_to_generate=audio_to_generate,
            words_needed=words_needed,
        )

    def generate_audio(self, project_root: Path, plan, provider):
        """Generate audio using provider"""
        from types import SimpleNamespace

        generated = 0
        skipped = 0
        failed = 0
        audio = []
        errors = []

        for audio_file in sorted(plan.audio_to_generate):
            # Extract word from filename
            word = Path(audio_file).stem

            try:
                # Download pronunciation from provider
                response = provider.download_pronunciation(word, audio_file)

                if response.success:
                    generated += 1
                    audio.append(audio_file)
                    self.logger.info(f"{ICONS['check']} Generated audio: {audio_file}")
                else:
                    failed += 1
                    error_msg = f"Audio generation failed for {audio_file}: {response.error_message}"
                    errors.append(error_msg)
                    self.logger.error(f"{ICONS['cross']} {error_msg}")

            except Exception as e:
                failed += 1
                error_msg = f"Audio generation exception for {audio_file}: {e}"
                errors.append(error_msg)
                self.logger.error(f"{ICONS['cross']} {error_msg}")

        return SimpleNamespace(
            audio=audio,
            generated=generated,
            skipped=skipped,
            failed=failed,
            errors=errors,
        )
