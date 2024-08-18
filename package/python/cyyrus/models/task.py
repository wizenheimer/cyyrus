from pydantic import BaseModel
from typing import Dict, Union
from enum import Enum


class TaskType(str, Enum):
    # === General Tasks ===
    PARSING = "parsing"  # Ingest and interpret data from different types.
    REFORMATTING = "reformatting"  # Convert data between different formats (e.g., CSV to JSON).
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


class Task(BaseModel):
    task_type: TaskType
    task_properties: Dict[str, Union[int, str, float]]


# TODO: implement validation for task_properties depending on task_type
