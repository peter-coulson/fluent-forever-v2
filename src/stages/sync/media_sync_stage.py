"""
Media Sync Stage

Synchronizes media files (images and audio) to Anki. Extracts logic from
sync.media_sync to create reusable stage.
"""

from pathlib import Path
from typing import Any

from src.core.context import PipelineContext
from src.core.stages import StageResult, StageStatus
from src.stages.base.api_stage import APIStage
from src.utils.logging_config import ICONS, get_logger


class MediaSyncStage(APIStage):
    """Sync media files to Anki"""

    def __init__(self, force_media: bool = False):
        """
        Initialize media sync stage

        Args:
            force_media: Force re-upload all referenced media
        """
        super().__init__("anki_provider", required=True)
        self.force_media = force_media
        self.logger = get_logger("stages.sync.media")

    @property
    def name(self) -> str:
        return "sync_media"

    @property
    def display_name(self) -> str:
        return "Sync Media to Anki"

    def execute_api_call(self, context: PipelineContext, provider: Any) -> StageResult:
        """Sync media to Anki using provider"""
        project_root = Path(context.get("project_root", Path.cwd()))

        try:
            # Load vocabulary
            vocabulary = self.load_vocabulary(project_root)

            # Get referenced media from vocabulary
            ref_images, ref_audio = self.get_referenced_media(vocabulary)

            if self.force_media:
                # Force: push all referenced media regardless of Anki state
                missing_images = ref_images
                missing_audio = ref_audio
                self.logger.info(
                    f"{ICONS['info']} Force mode: uploading all {len(ref_images)} images and {len(ref_audio)} audio files"
                )
            else:
                # Normal mode: only upload missing media
                anki_images, anki_audio = self.list_anki_media(provider)
                missing_images, missing_audio = self.compute_missing_media(
                    ref_images, ref_audio, anki_images, anki_audio
                )
                self.logger.info(
                    f"{ICONS['info']} Found {len(missing_images)} missing images and {len(missing_audio)} missing audio files"
                )

            # Upload missing media
            upload_result = self.upload_missing_media(
                provider, project_root, missing_images, missing_audio
            )

            context.set("media_sync_result", upload_result)

            if upload_result.get("failed", 0) > 0:
                status = StageStatus.PARTIAL
            else:
                status = StageStatus.SUCCESS

            uploaded = upload_result.get("uploaded", 0)
            failed = upload_result.get("failed", 0)

            message = f"Media sync completed: {uploaded} uploaded"
            if failed > 0:
                message += f", {failed} failed"

            self.logger.info(f"{ICONS['check']} {message}")

            return StageResult(
                status=status,
                message=message,
                data=upload_result,
                errors=upload_result.get("errors", []),
            )

        except Exception as e:
            self.logger.error(f"{ICONS['cross']} Media sync failed: {e}")
            return StageResult(
                status=StageStatus.FAILURE,
                message=f"Media sync failed: {e}",
                data={},
                errors=[f"Sync error: {e}"],
            )

    def load_vocabulary(self, project_root: Path):
        """Load vocabulary.json"""
        import json

        vocab_file = project_root / "vocabulary.json"
        with open(vocab_file, encoding="utf-8") as f:
            return json.load(f)

    def get_referenced_media(self, vocabulary) -> tuple[set[str], set[str]]:
        """Get referenced media files from vocabulary"""
        try:
            from sync.media_sync import referenced_media

            return referenced_media(vocabulary)
        except ImportError:
            # Fallback implementation
            images = set()
            audio = set()

            for word_obj in vocabulary.get("words", {}).values():
                for meaning in word_obj.get("meanings", []):
                    # Images
                    if "ImageFile" in meaning:
                        images.add(meaning["ImageFile"])

                    # Audio from WordAudio field like "[sound:word.mp3]"
                    word_audio = meaning.get("WordAudio", "")
                    if word_audio.startswith("[sound:") and word_audio.endswith("]"):
                        audio_file = word_audio[7:-1]  # Remove "[sound:" and "]"
                        audio.add(audio_file)

            return images, audio

    def list_anki_media(self, provider) -> tuple[set[str], set[str]]:
        """List media files currently in Anki"""
        try:
            from sync.media_sync import list_anki_media

            return list_anki_media(provider)
        except ImportError:
            # Fallback: assume no media in Anki
            self.logger.warning(
                f"{ICONS['warning']} Cannot list Anki media (sync module missing)"
            )
            return set(), set()

    def compute_missing_media(
        self,
        ref_images: set[str],
        ref_audio: set[str],
        anki_images: set[str],
        anki_audio: set[str],
    ) -> tuple[set[str], set[str]]:
        """Compute missing media files"""
        try:
            from sync.media_sync import compute_missing

            return compute_missing(ref_images, ref_audio, anki_images, anki_audio)
        except ImportError:
            # Fallback: assume all referenced media is missing
            return ref_images, ref_audio

    def upload_missing_media(
        self,
        provider,
        project_root: Path,
        missing_images: set[str],
        missing_audio: set[str],
    ):
        """Upload missing media files to Anki"""
        try:
            from sync.media_sync import push_missing_media

            # This function doesn't return detailed results in the original implementation,
            # so we'll track our own stats
            uploaded = 0
            failed = 0
            errors = []

            total_files = len(missing_images) + len(missing_audio)

            if total_files > 0:
                try:
                    push_missing_media(
                        provider, project_root, missing_images, missing_audio
                    )
                    uploaded = total_files  # Assume all succeeded if no exception
                    self.logger.info(
                        f"{ICONS['check']} Uploaded {total_files} media files"
                    )
                except Exception as e:
                    failed = total_files
                    errors.append(f"Media upload failed: {e}")
                    self.logger.error(f"{ICONS['cross']} Media upload failed: {e}")

            return {
                "uploaded": uploaded,
                "failed": failed,
                "errors": errors,
                "total_images": len(missing_images),
                "total_audio": len(missing_audio),
            }

        except ImportError:
            self.logger.warning(
                f"{ICONS['warning']} Media upload not available (sync module missing)"
            )
            return {
                "uploaded": 0,
                "failed": 0,
                "errors": ["Media upload module not available"],
                "total_images": len(missing_images),
                "total_audio": len(missing_audio),
            }
