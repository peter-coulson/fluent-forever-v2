"""
Image Generation Stage

Generates images using configured image providers. Extracts logic from
sync.media_generation to create reusable stage.
"""

import hashlib
import time
from pathlib import Path
from typing import Any

from src.core.context import PipelineContext
from src.core.stages import StageResult, StageStatus
from src.stages.base.api_stage import APIStage
from src.utils.logging_config import ICONS, get_logger


class ImageGenerationStage(APIStage):
    """Generate images using configured provider"""

    def __init__(self, max_new: int = 5, force_regenerate: bool = False):
        """
        Initialize image generation stage

        Args:
            max_new: Maximum new images to generate
            force_regenerate: Force regenerate even if provenance hash differs
        """
        super().__init__("image_provider", required=True)
        self.max_new = max_new
        self.force_regenerate = force_regenerate
        self.logger = get_logger("stages.media.image_generation")

    @property
    def name(self) -> str:
        return "generate_images"

    @property
    def display_name(self) -> str:
        return "Generate Images"

    def execute_api_call(self, context: PipelineContext, provider) -> StageResult:
        """Execute image generation with provider"""
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

            # Plan image generation
            plan = self.plan_image_generation(project_root, cards)

            if len(plan.images_to_generate) > self.max_new:
                return StageResult(
                    status=StageStatus.FAILURE,
                    message=f"Too many images to generate: {len(plan.images_to_generate)} > {self.max_new}",
                    data={},
                    errors=[
                        f"Exceeded max images limit: {len(plan.images_to_generate)} > {self.max_new}"
                    ],
                )

            # Generate images
            results = self.generate_images(project_root, plan, provider)

            # Store results in context
            context.set("generated_images", results.images)
            context.set(
                "generation_stats",
                {
                    "generated": results.generated,
                    "skipped": results.skipped,
                    "failed": results.failed,
                },
            )

            status = StageStatus.SUCCESS
            if results.failed > 0:
                status = StageStatus.PARTIAL

            message = f"Generated {results.generated} images, skipped {results.skipped}"
            if results.failed > 0:
                message += f", failed {results.failed}"

            self.logger.info(f"{ICONS['check']} {message}")

            return StageResult(
                status=status,
                message=message,
                data={
                    "images": results.images,
                    "generated": results.generated,
                    "skipped": results.skipped,
                    "failed": results.failed,
                },
                errors=results.errors,
            )

        except Exception as e:
            self.logger.error(f"{ICONS['cross']} Image generation failed: {e}")
            return StageResult(
                status=StageStatus.FAILURE,
                message=f"Image generation failed: {e}",
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

    def plan_image_generation(self, project_root: Path, cards: list[dict[str, Any]]):
        """Plan which images need to be generated"""
        from types import SimpleNamespace

        media_dir = project_root / "media" / "images"

        images_needed: set[str] = set()
        images_to_generate: set[str] = set()

        for card in cards:
            image_file = card.get("ImageFile")
            if image_file:
                images_needed.add(image_file)
                if not (media_dir / image_file).exists():
                    images_to_generate.add(image_file)

        return SimpleNamespace(
            images_needed=images_needed, images_to_generate=images_to_generate
        )

    def generate_images(self, project_root: Path, plan, provider):
        """Generate images using provider"""
        # Load vocabulary for prompts
        import json
        from types import SimpleNamespace

        vocab_file = project_root / "vocabulary.json"
        with open(vocab_file, encoding="utf-8") as f:
            vocab = json.load(f)

        # Build meaning index by image file
        image_to_meaning = {}
        for word_obj in vocab.get("words", {}).values():
            for meaning in word_obj.get("meanings", []):
                image_file = meaning.get("ImageFile")
                if image_file:
                    image_to_meaning[image_file] = meaning

        # Load and save provenance
        provenance = self.load_provenance(project_root)

        generated = 0
        skipped = 0
        failed = 0
        images = []
        errors = []

        for image_file in sorted(plan.images_to_generate):
            meaning = image_to_meaning.get(image_file)
            if not meaning:
                self.logger.warning(
                    f"{ICONS['warning']} No meaning found for image {image_file}"
                )
                skipped += 1
                continue

            word = meaning.get("SpanishWord", "")
            prompt = meaning.get("prompt", "")

            # Check provenance
            prompt_hash = self.hash_prompt(word, prompt)
            existing_prov = provenance.get(image_file)

            if (
                existing_prov
                and existing_prov.get("prompt_hash") != prompt_hash
                and not self.force_regenerate
            ):
                self.logger.warning(
                    f"{ICONS['warning']} Prompt changed for {image_file}; keeping existing. Use --force-regenerate to update."
                )
                skipped += 1
                continue

            # Generate image
            try:
                response = provider.generate_image(prompt, image_file)

                if response.success:
                    # Update provenance
                    provenance[image_file] = {
                        "word": word,
                        "prompt_hash": prompt_hash,
                        "provider": provider.__class__.__name__,
                        "created_at": time.time(),
                    }
                    generated += 1
                    images.append(image_file)
                    self.logger.info(f"{ICONS['check']} Generated image: {image_file}")
                else:
                    failed += 1
                    error_msg = f"Image generation failed for {image_file}: {response.error_message}"
                    errors.append(error_msg)
                    self.logger.error(f"{ICONS['cross']} {error_msg}")

            except Exception as e:
                failed += 1
                error_msg = f"Image generation exception for {image_file}: {e}"
                errors.append(error_msg)
                self.logger.error(f"{ICONS['cross']} {error_msg}")

        # Save provenance
        self.save_provenance(project_root, provenance)

        return SimpleNamespace(
            images=images,
            generated=generated,
            skipped=skipped,
            failed=failed,
            errors=errors,
        )

    def hash_prompt(self, word: str, prompt: str) -> str:
        """Generate hash for prompt (from sync.media_generation)"""
        h = hashlib.sha256()
        h.update((word + "|" + (prompt or "")).encode("utf-8"))
        return h.hexdigest()[:16]

    def load_provenance(self, project_root: Path) -> dict[str, Any]:
        """Load provenance data"""
        import json

        prov_file = project_root / "media" / ".index.json"
        if prov_file.exists():
            try:
                with open(prov_file, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_provenance(self, project_root: Path, provenance: dict[str, Any]) -> None:
        """Save provenance data"""
        import json

        prov_file = project_root / "media" / ".index.json"
        prov_file.parent.mkdir(parents=True, exist_ok=True)

        with open(prov_file, "w", encoding="utf-8") as f:
            json.dump(provenance, f, ensure_ascii=False, indent=2)
