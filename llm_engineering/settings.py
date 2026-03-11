from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict

# ZenML is optional - only needed for pipeline orchestration
try:
    from zenml.client import Client
    from zenml.exceptions import EntityExistsError
    HAS_ZENML = True
except Exception:
    # Catch all exceptions (ImportError, RuntimeError from pydantic conflicts, etc.)
    HAS_ZENML = False
    Client = None
    EntityExistsError = None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # --- Required settings even when working locally. ---

    # Llama API
    OLLAMA_MODEL: str | None = None
    

    # Huggingface API
    HUGGINGFACE_ACCESS_TOKEN: str | None = None

    # Comet ML (during training)
    COMET_API_KEY: str | None = None
    COMET_WORKSPACE: str = "ocanthony4real"
    COMET_PROJECT: str = "Nigeria_tax_bill"

    # Anthropic API (for evaluation)
    ANTHROPIC_API_KEY: str | None = None

    # --- Required settings when deploying the code. ---
    # --- Otherwise, default values values work fine. ---

    # MongoDB database
    DATABASE_HOST: str | None = None
    DATABASE_NAME: str = "Laws"

    # Qdrant vector database
    USE_QDRANT_CLOUD: bool = False
    QDRANT_DATABASE_HOST: str = "localhost"
    QDRANT_DATABASE_PORT: int = 6333
    QDRANT_CLOUD_URL: str = "str"
    QDRANT_APIKEY: str | None = None

    # AWS Authentication
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY: str | None = None
    AWS_SECRET_KEY: str | None = None
    AWS_ARN_ROLE: str | None = None

    # --- Optional settings used to tweak the code. ---

    # AWS SageMaker
    HF_MODEL_ID: str = "ocanthony4real/NigeriaTaxLlama-3.1-8B-RAG-v3"
    GPU_INSTANCE_TYPE: str = "ml.g5.xlarge"
    SM_NUM_GPUS: int = 1
    MAX_INPUT_LENGTH: int = 4096
    MAX_TOTAL_TOKENS: int = 8192
    MAX_BATCH_TOTAL_TOKENS: int = 8192
    COPIES: int = 1  # Number of replicas
    GPUS: int = 1  # Number of GPUs
    CPUS: int = 2  # Number of CPU cores

    SAGEMAKER_ENDPOINT_CONFIG_INFERENCE: str = "nigeria-tax-llama-v3"
    SAGEMAKER_ENDPOINT_INFERENCE: str = "nigeria-tax-llama-v3"
    TEMPERATURE_INFERENCE: float = 0.01  # Very low to reduce hallucination
    TOP_P_INFERENCE: float = 0.7  # Lower to focus on most likely tokens
    MAX_NEW_TOKENS_INFERENCE: int = 1024  # Increased for comprehensive answers

    # RAG
    TEXT_EMBEDDING_MODEL_ID: str = "BAAI/bge-large-en-v1.5"
    RERANKING_CROSS_ENCODER_MODEL_ID: str = "cross-encoder/ms-marco-MiniLM-L-4-v2"
    RAG_MODEL_DEVICE: str = "cpu"


    @property
    def OLLAMA_MAX_TOKEN_WINDOW(self) -> int:
        """
        Returns the maximum token window for the current Ollama model,
        with a 90% safety margin to avoid overflow.
        """
        # Map Ollama model names to their max context size
        OLLAMA_MAX_TOKEN_WINDOWS = {
            "gemma:2b": 2048,
        }

        # Look up the max window for the active model
        max_window = OLLAMA_MAX_TOKEN_WINDOWS.get(
            self.settings.OLLAMA_MODEL, 2048  # fallback
        )

        # Apply 90% safety margin
        return int(max_window * 0.9)



    @classmethod
    def load_settings(cls) -> "Settings":
        """
        Tries to load the settings from the ZenML secret store. If the secret does not exist or ZenML is not installed,
        it initializes the settings from the .env file and default values.

        Returns:
            Settings: The initialized settings object.
        """
        if HAS_ZENML:
            try:
                logger.info("Loading settings from the ZenML secret store.")
                settings_secrets = Client().get_secret("settings")
                return Settings(**settings_secrets.secret_values)
            except (RuntimeError, KeyError):
                logger.warning(
                    "Failed to load settings from the ZenML secret store. Defaulting to loading the settings from the '.env' file."
                )

        logger.info("Loading settings from environment variables.")
        return Settings()

    def export(self) -> None:
        """
        Exports the settings to the ZenML secret store.
        """
        if not HAS_ZENML:
            logger.warning("ZenML not installed. Cannot export settings to secret store.")
            return

        env_vars = settings.model_dump()
        for key, value in env_vars.items():
            env_vars[key] = str(value)

        client = Client()

        try:
            client.create_secret(name="settings", values=env_vars)
        except EntityExistsError:
            logger.warning(
                "Secret 'scope' already exists. Delete it manually by running 'zenml secret delete settings', before trying to recreate it."
            )


settings = Settings.load_settings()
