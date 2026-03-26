"""
Dagster resources for curriculum processing.

Provides configurable resources for:
- LanceDB vector database
- CocoIndex flow execution
- DLT pipeline execution
"""

from pathlib import Path
from typing import Optional

from dagster import ConfigurableResource, InitResourceContext
import lancedb


class LanceDBResource(ConfigurableResource):
    """
    Dagster resource for LanceDB vector database.

    Provides connection to LanceDB for storing and querying
    curriculum embeddings and generated asset metadata.
    """

    uri: str = "data/lancedb"

    _db: Optional[lancedb.DBConnection] = None

    def setup_for_execution(self, context: InitResourceContext) -> None:
        """Initialize LanceDB connection."""
        Path(self.uri).mkdir(parents=True, exist_ok=True)
        self._db = lancedb.connect(self.uri)

    @property
    def db(self) -> lancedb.DBConnection:
        """Get the LanceDB connection."""
        if self._db is None:
            self._db = lancedb.connect(self.uri)
        return self._db

    def get_table(self, table_name: str):
        """Get a table from the database."""
        return self.db.open_table(table_name)

    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists."""
        return table_name in self.db.table_names()


class CocoIndexResource(ConfigurableResource):
    """
    Dagster resource for running CocoIndex flows.

    Wraps CocoIndex flow execution for curriculum indexing
    and concept extraction.
    """

    postgres_url: str = ""

    def setup_for_execution(self, context: InitResourceContext) -> None:
        """Initialize CocoIndex."""
        import cocoindex
        cocoindex.init()

    def run_flow(self, flow_name: str) -> dict:
        """
        Execute a CocoIndex flow by name.

        Args:
            flow_name: Name of the flow to execute

        Returns:
            Flow execution results
        """
        import cocoindex

        flow = cocoindex.get_flow(flow_name)
        result = flow.run()

        return {
            "flow_name": flow_name,
            "status": "completed",
            "result": str(result),
        }

    def run_curriculum_indexing(self) -> dict:
        """Run the curriculum document indexing flow."""
        return self.run_flow("CurriculumDocumentIndexing")

    def run_concept_extraction(self) -> dict:
        """Run the concept extraction flow."""
        return self.run_flow("ConceptExtraction")


class DLTResource(ConfigurableResource):
    """
    Dagster resource for running DLT pipelines.

    Manages DLT pipeline execution for curriculum metadata loading.
    """

    destination: str = "duckdb"
    dataset_name: str = "curriculum"

    def run_curriculum_pipeline(
        self,
        subjects: Optional[list[str]] = None,
    ) -> dict:
        """
        Run the curriculum metadata DLT pipeline.

        Args:
            subjects: Optional list of subjects to load

        Returns:
            Pipeline execution results
        """
        from ..pipelines.curriculum_dlt import run_curriculum_pipeline

        return run_curriculum_pipeline(
            destination=self.destination,
            dataset_name=self.dataset_name,
            subjects=subjects,
        )


class ColPaliResource(ConfigurableResource):
    """
    Dagster resource for ColPali embeddings.

    Provides ColPali model for visual document embeddings.
    """

    model_name: str = "vidore/colpali-v1.2"

    _embedder = None

    def setup_for_execution(self, context: InitResourceContext) -> None:
        """Initialize ColPali embedder."""
        from ..models.colpali import ColPaliEmbedder
        self._embedder = ColPaliEmbedder(model_name=self.model_name)

    @property
    def embedder(self):
        """Get the ColPali embedder."""
        if self._embedder is None:
            from ..models.colpali import ColPaliEmbedder
            self._embedder = ColPaliEmbedder(model_name=self.model_name)
        return self._embedder

    def embed_image(self, image_bytes: bytes) -> list[list[float]]:
        """Embed an image."""
        return self.embedder.embed_image(image_bytes)

    def embed_query(self, query: str) -> list[list[float]]:
        """Embed a query."""
        return self.embedder.embed_query(query)


class Qwen3VLResource(ConfigurableResource):
    """
    Dagster resource for Qwen3-VL model.

    Provides vision-language understanding for concept extraction
    and image validation.
    """

    model_path: str = "mlx-community/Qwen2.5-VL-32B-Instruct-8bit"
    max_tokens: int = 2048

    _client = None

    def setup_for_execution(self, context: InitResourceContext) -> None:
        """Initialize Qwen3-VL client."""
        from ..models.qwen_vlm import Qwen3VLClient
        self._client = Qwen3VLClient(
            model_path=self.model_path,
            max_tokens=self.max_tokens,
        )

    @property
    def client(self):
        """Get the Qwen3-VL client."""
        if self._client is None:
            from ..models.qwen_vlm import Qwen3VLClient
            self._client = Qwen3VLClient(
                model_path=self.model_path,
                max_tokens=self.max_tokens,
            )
        return self._client
