from enum import Enum

# ==============================================================================
#                          Tasks which deal with Text Modality
# ==============================================================================


class LargeLanguageModels(str, Enum):
    GPT_4 = "gpt-4"
    GPT_4O_MINI = "gpt-4o-mini"


class EntityRecognitionModels(str, Enum):
    GPT_4O_MINI = "gpt-4o-mini"


class EmbeddingModels(str, Enum):
    TEXT_EMBEDDING_3_SMALL = "text-embedding-3-small"
    TEXT_EMBEDDING_3_LARGE = "text-embedding-3-large"
    TEXT_EMBEDDING_ADA_002 = "text-embedding-ada-002"
    JINA_EMBEDDING_V2 = "jina-embedding-v2"


class ChunkingStrategy(str, Enum):
    SLIDING_WINDOW = "sliding-window"
    TOPIC_SEGMENTATION = "topic-segmentation"
    NLP = "nlp"
    REGEX = "regex"


# ==============================================================================
#                          Tasks which deal with Vision Modality
# ==============================================================================


class VisionLanguageModels(str, Enum):
    GPT_4O_MINI = "gpt-4o-mini"


class TableParsingModels(str, Enum):
    GPT_4O_MINI = "gpt-4o-mini"


class OpticalCharacterRecognitionModels(str, Enum):
    GPT_4O_MINI = "gpt-4o-mini"


class CaptioningModels(str, Enum):
    FLORENCE_2 = "florence-2"


class ObjectDetectionModels(str, Enum):
    FLORENCE_2 = "florence-2"


class DenseRegionCaptioningModels(str, Enum):
    FLORENCE_2 = "florence-2"


class RegionProposalModels(str, Enum):
    FLORENCE_2 = "florence-2"


class CaptionToPhraseGroundingModels(str, Enum):
    FLORENCE_2 = "florence-2"


class ReferringExpressionSegmentationModels(str, Enum):
    FLORENCE_2 = "florence-2"


class RegionToSegmentationModels(str, Enum):
    FLORENCE_2 = "florence-2"


class OpenVocabularyDetectionModels(str, Enum):
    FLORENCE_2 = "florence-2"


class RegionToCategoryClassificationModels(str, Enum):
    FLORENCE_2 = "florence-2"


class RegionToDescriptionModels(str, Enum):
    FLORENCE_2 = "florence-2"


# ==============================================================================
#                         Tasks which deal with Audio Modality
# ==============================================================================


class DiarizationModels(str, Enum):
    PYANNOTE = "pyannote"


class TranscriptionModels(str, Enum):
    WHISPER = "whisper"


# ==============================================================================
#                         Tasks which deal with Video Modality
# ==============================================================================


class KeyFrameExtractionProvider(str, Enum):
    KATNA = "katna"
