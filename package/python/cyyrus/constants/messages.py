class Messages:
    """
    Constants for messages
    """

    # ==============================
    # Schema Section validation errors
    # ==============================

    SCHEMA_FILE_COULD_NOT_BE_LOCATED = "Schema file could not be located. Please check the schema file path. Must be a valid file path or URL. For more details, see the https://cyyrus.com/schema/overview"

    SCHEMA_COULD_NOT_BE_PARSED = "Schema could not be parsed. Please check the schema file. For more details, see the https://cyyrus.com/schema/overview"

    SCHEMA_COULD_NOT_BE_VALIDATED = "Schema could not be validated. Please check the schema file. For more details, see the https://cyyrus.com/schema/overview"

    REQUIRED_SECTION_MISSING_IN_SCHEMA = "Required section missing in schema. For more details, see the https://cyyrus.com/schema/overview"

    # ==============================
    # Reference Section validation error
    # ==============================

    REFERENCE_TYPE_MISSING = "Reference type missing. Specify a valid reference type. For more details, see the https://cyyrus.com/schema/overview"

    REFERENCE_TYPE_NOT_SUPPORTED = "Reference type not supported. For more details, see the https://cyyrus.com/schema/columns/task-id"

    REFERENCE_PROPERTIES_MISSING = "Reference properties missing. Specify properties for the references. For more details, see the https://cyyrus.com/schema/columns/task-inputs"

    REFERENCE_PROPERTIES_INVALID = "Reference properties invalid. Specify valid properties for the references. For more details, see the https://cyyrus.com/schema/columns/task-inputs"

    # ==============================
    # Dataset Section validation error
    # ==============================

    SPLITS_DONT_ADD_UP = "Splits don't add up to 1. Please check the schema file. Would normalize the splits. For more details, see the https://cyyrus.com/schema/overview. Attempting to normalize the splits."

    SPLIT_VALUE_INVALID = "Split value is invalid. Please check the schema file. For more details, see the https://cyyrus.com/schema/overview. Setting to absolute value."

    INVALID_TAG_TYPES = "Invalid tag types. Populating with default tags. Please check the schema file. For more details, see the https://cyyrus.com/schema/overview"

    INVALID_SAMPLING_STRATEGY = "Invalid sampling strategy. Populating with default sampling strategy. Please check the schema file. For more details, see the https://cyyrus.com/schema/overview"

    INVALID_NULL_HANDLING_STRATEGY = "Invalid null handling strategy. Populating with default null handling strategy of `include`. Please check the schema file. For more details, see the https://cyyrus.com/schema/overview"

    INVALID_REFERENCE_HANDLING_STRATEGY = "Invalid reference handling strategy. Populating with default reference handling strategy of `include`. Please check the schema file. For more details, see the https://cyyrus.com/schema/overview"

    INVALID_SHUFFLING_STRATEGY = "Invalid shuffling strategy. Populating with default shuffling strategy with seed `42`. Please check the schema file. For more details, see the https://cyyrus.com/schema/overview"

    # ==============================
    # Types Section validation error
    # ==============================

    INVALID_TYPE = "Invalid type. Specify a valid type. For more details, see the https://cyyrus.com/schema/types/overview"

    TYPE_PROPERTIES_MISSING_FOR_OBJECT_TYPE = "Type properties missing for object type. Specify `properties` for the object type. For more details, see the https://cyyrus.com/schema/types/objects"

    TYPE_ITEMS_MISSING_FOR_ARRAY_TYPE = "Type items missing for array type. Specify `items` for the array type. For more details, see the https://cyyrus.com/schema/types/arrays"

    DUPLICATE_TYPE_NAME = "Duplicate type name found. Type names must be unique. For more details, see the https://cyyrus.com/schema/types/overview"

    MAXIMUM_DEPTH_EXCEEDED = "Maximum depth exceeded. Please check the schema file. For more details, see the https://cyyrus.com/schema/types/overview."

    REFERENCE_TYPE_NOT_FOUND = "Reference type not found. Specify a valid reference type. Defaulting to `string`. For more details, see the https://cyyrus.com/schema/types/overview"

    # Task Section validation error

    TASK_SPECIFICATION_MISSING = "Task specification missing. Specify either of `task_id` or `task_type`. For more details, see the https://cyyrus.com/schema/tasks"

    TASK_PROPERTIES_UNSPECIFIED = "Task properties unspecified. Specify `task_properties` for the task. For more details, see the https://cyyrus.com/schema/tasks"

    REFERENCED_TASK_ID_NOT_FOUND = "Referenced task_id not found. Specify a valid task_id. For more details, see the https://cyyrus.com/schema/columns/task-inputs"

    TASK_INPUTS_CYCLIC_DEPENDENCY = "Task inputs have cyclic dependency. Please check the schema file. For more details, see the https://cyyrus.com/schema/columns/task-inputs"

    # Column Section validation error

    COLUMN_TYPE_NOT_FOUND = "Column type not found. Specify a valid column type. Defaulting to `string`. For more details, see the https://cyyrus.com/schema/columns/overview"

    COLUMN_TASK_ID_NOT_FOUND = "Column task_id not found. Specify a valid task_id. For more details, see the https://cyyrus.com/schema/columns/overview"

    COLUMNN_ID_NOT_FOUND = "Column ID not found. Specify a valid column ID. For more details, see the https://cyyrus.com/schema/columns/overview"

    DUPLICATE_COLUMN_NAME = "Duplicate column name found. Column names must be unique across `reference` and `columns` sections. For more details, see the https://cyyrus.com/schema/columns/overview"

    # ==============================
    #  Composer Section validation error
    # ==============================
    KEY_COLUMN_NOT_FOUND = "Key column not found. Specify a valid key column. For more details, see the https://cyyrus.com/schema/overview"

    INVALID_KEY_COLUMN = "Invalid key column. Specify a valid key column. For more details, see the https://cyyrus.com/schema/overview"

    ALL_ROWS_EXCLUDED_DUE_TO_NAN = "All rows excluded due to NaN. Please check the schema file. For more details, see the https://cyyrus.com/schema/overview"

    REQUIRED_COLUMN_MISSING = "Required column missing. Creating them with empty values. Please check the schema file. For more details, see the https://cyyrus.com/schema/overview"

    NON_UNIQUE_COLUMN_VALUES = "Removed non-unique column values. Please check the schema file. For more details, see the https://cyyrus.com/schema/overview"

    DATASET_TOO_SMALL_FOR_SPLIT = "Dataset too small for split. Using entire dataset as train set. For more details, see the https://cyyrus.com/schema/overview"

    RE_ADJUSTING_SPLIT = "Re-adjusting split values. Adjusted split sizes would be unstable or exceed dataset size. For more details, see the https://cyyrus.com/schema/overview"
