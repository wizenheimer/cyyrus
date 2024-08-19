from enum import Enum

from cyyrus.models.task_model import (
    CaptioningModels,
    CaptionToPhraseGroundingModels,
    ChunkingStrategy,
    DenseRegionCaptioningModels,
    DiarizationModels,
    EmbeddingModels,
    EntityRecognitionModels,
    LargeLanguageModels,
    ObjectDetectionModels,
    OpenVocabularyDetectionModels,
    OpticalCharacterRecognitionModels,
    ReferringExpressionSegmentationModels,
    RegionProposalModels,
    RegionToCategoryClassificationModels,
    RegionToDescriptionModels,
    RegionToSegmentationModels,
    TableParsingModels,
    TranscriptionModels,
    VisionLanguageModels,
)


class TaskType(str, Enum):
    # === Sentinel Tasks ===
    DEFAULT = "default"
    BASE_STATIC = "base_static"
    BASE_DYNAMIC = "base_dynamic"

    # === General Tasks ===
    PARSING = "parsing"  # Ingest and interpret data from different types.
    SCRAPING = "scraping"  # Collect and extract data from websites or online sources.

    # === Document Processing Tasks ===
    GRAPH_PARSING = "graph_parsing"  # Parse and understand visual graphs or diagrams.
    TABLE_PARSING = "table_parsing"  # Extract structured data from tables in documents.
    DOCUMENT_GENERATION = "document_generation"  # Create new documents based on given inputs.

    # === Audio Processing Tasks ===
    DIARIZATION = "diarization"  # Identify and separate different speakers in an audio recording.
    TRANSCRIPTION = "transcription"  # Convert spoken language in audio into written text.

    # === Multimodal Tasks ===
    GENERATION = (
        "generation"  # Create new content, such as generating text or audio from given inputs.
    )
    EMBEDDING = "embedding"  # Transform data into a numerical format that preserves semantic meaning (e.g., word embeddings).

    # === Text Processing Tasks ===
    CATEGORIZATION = "categorization"  # Classify text into predefined categories or labels.
    ENTITY_RECOGNITION = "entity_recognition"  # Identify and classify entities (e.g., people, locations) within text.
    CHUNKING = (
        "chunking"  # Segment text into chunks based on syntactic structures (e.g., noun phrases).
    )

    # === Video Processing Tasks ===
    AUDIOEXTRACTION = "audioextraction"  # Extract audio track from video files.
    KEY_FRAME_EXTRACTION = (
        "key_frame_extraction"  # Identify and extract important frames from a video.
    )
    FACE_EXTRACTION = "face_extraction"  # Detect and extract faces from video frames.

    # === Vision Tasks ===
    OPTICAL_CHARACTER_RECOGNITION = (
        "optical_character_recognition"  # Convert images of text into machine-encoded text.
    )
    CAPTIONING = "captioning"  # Generate descriptive text for images or video frames.
    OBJECT_DETECTION = (
        "object_detection"  # Identify and locate objects within images or video frames.
    )
    DENSE_REGION_CAPTIONING = (
        "dense_region_captioning"  # Generate captions for specific regions within an image.
    )
    REGION_PROPOSAL = "region_proposal"  # Propose potential regions of interest within images for further analysis.
    CAPTION_TO_PHRASE_GROUNDING = (
        "caption_to_phrase_grounding"  # Align descriptive captions with specific regions in images.
    )
    REFERRING_EXPRESSION_SEGMENTATION = "referring_expression_segmentation"  # Segment parts of images based on referring expressions in text.
    REGION_TO_SEGMENTATION = "region_to_segmentation"  # Convert detected regions in images to detailed segmentation maps.
    OPEN_VOCABULARY_DETECTION = (
        "open_vocabulary_detection"  # Detect objects or concepts not limited to a fixed vocabulary.
    )
    REGION_TO_CATEGORY_CLASSIFICATION = "region_to_category_classification"  # Classify regions within images into specific categories.
    REGION_TO_DESCRIPTION = "region_to_description"  # Generate detailed descriptions for specific regions within images.


# ==============================================================================
#                                   Task Properties
# ==============================================================================

TASK_PROPERTIES = {
    TaskType.DEFAULT: {
        "required": {},
        "optional": {},
    },
    TaskType.BASE_STATIC: {
        "required": {},
        "optional": {},
    },
    TaskType.BASE_DYNAMIC: {
        "required": {},
        "optional": {},
    },
    TaskType.PARSING: {
        "required": {
            "directory": (
                str,
                ...,
            ),
            "file_type": (
                str,
                ...,
            ),
            "max_depth": (
                int,
                5,
            ),
        },
        "optional": {},
    },
    TaskType.SCRAPING: {
        "required": {
            "url": (
                str,
                ...,
            ),
            "max_depth": (int, 5),
        },
        "optional": {},
    },
    TaskType.GRAPH_PARSING: {
        "required": {
            "model": (
                VisionLanguageModels,
                VisionLanguageModels.GPT_4O_MINI,
            ),
        },
        "optional": {},
    },
    TaskType.TABLE_PARSING: {
        "required": {
            "model": (
                TableParsingModels,
                TableParsingModels.GPT_4O_MINI,
            ),
        },
        "optional": {},
    },
    TaskType.DOCUMENT_GENERATION: {
        "required": {
            "path": (
                str,
                ...,
            ),
        },
        "optional": {},
    },
    TaskType.DIARIZATION: {
        "required": {
            "model": (
                DiarizationModels,
                DiarizationModels.PYANNOTE,
            ),
        },
        "optional": {},
    },
    TaskType.TRANSCRIPTION: {
        "required": {
            "model": (
                TranscriptionModels,
                TranscriptionModels.WHISPER,
            ),
        },
        "optional": {},
    },
    TaskType.GENERATION: {
        "required": {
            "prompt": (str, ...),
            "model": (
                LargeLanguageModels,
                LargeLanguageModels.GPT_4O_MINI,
            ),
        },
        "optional": {},
    },
    TaskType.EMBEDDING: {
        "required": {
            "model": (
                EmbeddingModels,
                EmbeddingModels.TEXT_EMBEDDING_3_SMALL,  # TODO: add support for image embeddings
            ),
        },
        "optional": {},
    },
    TaskType.CATEGORIZATION: {
        "required": {
            "primary_model": (
                EmbeddingModels,
                EmbeddingModels.JINA_EMBEDDING_V2,
            ),
            "secondary_model": (
                LargeLanguageModels,
                LargeLanguageModels.GPT_4O_MINI,
            ),
        },
        "optional": {},
    },
    TaskType.ENTITY_RECOGNITION: {
        "required": {
            "model": (
                EntityRecognitionModels,
                EntityRecognitionModels.GPT_4O_MINI,
            ),
        },
        "optional": {},
    },
    TaskType.CHUNKING: {
        "required": {
            "strategy": (
                ChunkingStrategy,
                ChunkingStrategy.SLIDING_WINDOW,
            ),
            "size": (
                int,
                250,
            ),
            "overlap": (
                int,
                25,
            ),
        },
        "optional": {},
    },
    TaskType.AUDIOEXTRACTION: {
        "required": {},
        "optional": {
            "max_duration": (
                int,
                60,
            ),
        },
    },
    TaskType.KEY_FRAME_EXTRACTION: {
        "required": {},
        "optional": {},
    },
    TaskType.FACE_EXTRACTION: {
        "required": {},
        "optional": {},
    },
    TaskType.OPTICAL_CHARACTER_RECOGNITION: {
        "required": {
            "model": (
                OpticalCharacterRecognitionModels,
                OpticalCharacterRecognitionModels.GPT_4O_MINI,
            ),
        },
        "optional": {},
    },
    TaskType.CAPTIONING: {
        "required": {
            "model": (
                CaptioningModels,
                CaptioningModels.FLORENCE_2,
            ),
        },
        "optional": {},
    },
    TaskType.OBJECT_DETECTION: {
        "required": {
            "model": (
                ObjectDetectionModels,
                ObjectDetectionModels.FLORENCE_2,
            ),
        },
        "optional": {},
    },
    TaskType.DENSE_REGION_CAPTIONING: {
        "required": {
            "model": (
                DenseRegionCaptioningModels,
                DenseRegionCaptioningModels.FLORENCE_2,
            ),
        },
        "optional": {},
    },
    TaskType.REGION_PROPOSAL: {
        "required": {
            "model": (
                RegionProposalModels,
                RegionProposalModels.FLORENCE_2,
            ),
        },
        "optional": {},
    },
    TaskType.CAPTION_TO_PHRASE_GROUNDING: {
        "required": {
            "model": (
                CaptionToPhraseGroundingModels,
                CaptionToPhraseGroundingModels.FLORENCE_2,
            ),
        },
        "optional": {},
    },
    TaskType.REFERRING_EXPRESSION_SEGMENTATION: {
        "required": {
            "model": (
                ReferringExpressionSegmentationModels,
                ReferringExpressionSegmentationModels.FLORENCE_2,
            ),
        },
        "optional": {},
    },
    TaskType.REGION_TO_SEGMENTATION: {
        "required": {
            "model": (
                RegionToSegmentationModels,
                RegionToSegmentationModels.FLORENCE_2,
            ),
        },
        "optional": {},
    },
    TaskType.OPEN_VOCABULARY_DETECTION: {
        "required": {
            "model": (
                OpenVocabularyDetectionModels,
                OpenVocabularyDetectionModels.FLORENCE_2,
            ),
        },
        "optional": {},
    },
    TaskType.REGION_TO_CATEGORY_CLASSIFICATION: {
        "required": {
            "model": (
                RegionToCategoryClassificationModels,
                RegionToCategoryClassificationModels.FLORENCE_2,
            ),
        },
        "optional": {},
    },
    TaskType.REGION_TO_DESCRIPTION: {
        "required": {
            "model": (
                RegionToDescriptionModels,
                RegionToDescriptionModels.FLORENCE_2,
            ),
        },
        "optional": {},
    },
}
