from pydantic import BaseModel
from typing import Dict, Union
from enum import Enum


class TaskType(str, Enum):
    DIARIZATION = "diarization"
    GENERATION = "generation"
    TRANSCRIPTION = "transcription"
    CATEGORIZATION = "categorization"
    EMBEDDING = "embedding"
    CAPTIONING = "captioning"
    OBJECT_DETECTION = "object_detection"
    DENSE_REGION_CAPTIONING = "dense_region_captioning"
    REGION_PROPOSAL = "region_proposal"
    CAPTION_TO_PHRASE_GROUNDING = "caption_to_phrase_grounding"
    REFERRING_EXPRESSION_SEGMENTATION = "referring_expression_segmentation"
    REGION_TO_SEGMENTATION = "region_to_segmentation"
    OPEN_VOCABULARY_DETECTION = "open_vocabulary_detection"
    REGION_TO_CATEGORY_CLASSIFICATION = "region_to_category_classification"
    REGION_TO_DESCRIPTION = "region_to_description"
    OPTICAL_CHARACTER_RECOGNITION = "optical_character_recognition"
    CHUNKING = "chunking"
    AUDIOEXTRACTION = "audioextraction"
    KEY_FRAME_EXTRACTION = "key_frame_extraction"
    FACE_EXTRACTION = "face_extraction"
    ENTITY_RECOGNITION = "entity_recognition"
    NONE = "none"


class Task(BaseModel):
    task_type: TaskType
    task_properties: Dict[str, Union[int, str, float]]


# TODO: implement validation for task_properties depending on task_type
