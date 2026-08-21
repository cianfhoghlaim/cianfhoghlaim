"""
Embedding Visualization.

t-SNE and UMAP projections for curriculum embedding exploration.
Based on genizah_search visualization patterns.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Literal, Optional

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class VisualizationPoint:
    """A single point in the visualization."""

    id: str
    x: float
    y: float
    label: str

    # Metadata for coloring/filtering
    subject: Optional[str] = None
    level: Optional[str] = None
    source_type: Optional[str] = None

    # Optional cluster assignment
    cluster: Optional[int] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "x": self.x,
            "y": self.y,
            "label": self.label,
            "subject": self.subject,
            "level": self.level,
            "source_type": self.source_type,
            "cluster": self.cluster,
        }


@dataclass
class VisualizationData:
    """Complete visualization dataset."""

    points: list[VisualizationPoint]
    method: str  # tsne, umap
    parameters: dict[str, Any] = field(default_factory=dict)

    # Cluster info if clustering was applied
    n_clusters: Optional[int] = None
    cluster_labels: list[str] = field(default_factory=list)

    # Statistics
    explained_variance: Optional[float] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "points": [p.to_dict() for p in self.points],
            "method": self.method,
            "parameters": self.parameters,
            "n_clusters": self.n_clusters,
            "cluster_labels": self.cluster_labels,
            "explained_variance": self.explained_variance,
        }

    def to_frontend_format(self) -> dict[str, Any]:
        """Format for frontend visualization libraries."""
        return {
            "data": [
                {
                    "id": p.id,
                    "x": p.x,
                    "y": p.y,
                    "label": p.label,
                    "color": p.subject or "unknown",
                    "cluster": p.cluster,
                }
                for p in self.points
            ],
            "metadata": {
                "method": self.method,
                "n_clusters": self.n_clusters,
                "parameters": self.parameters,
            },
        }


class EmbeddingVisualizer:
    """
    Generate 2D visualizations of curriculum embeddings.

    Supports:
    - t-SNE for local structure preservation
    - UMAP for global structure preservation
    - K-means clustering for grouping
    """

    def __init__(
        self,
        method: Literal["tsne", "umap"] = "tsne",
        n_components: int = 2,
        random_state: int = 42,
    ):
        """
        Initialize visualizer.

        Args:
            method: Dimensionality reduction method
            n_components: Output dimensions (2 for visualization)
            random_state: Random seed for reproducibility
        """
        self.method = method
        self.n_components = n_components
        self.random_state = random_state

    async def compute_projection(
        self,
        embeddings: np.ndarray,
        perplexity: int = 30,
        n_neighbors: int = 15,
        min_dist: float = 0.1,
        n_iter: int = 1000,
    ) -> np.ndarray:
        """
        Compute 2D projection of embeddings.

        Args:
            embeddings: Embedding matrix (n_samples x dim)
            perplexity: t-SNE perplexity parameter
            n_neighbors: UMAP n_neighbors parameter
            min_dist: UMAP min_dist parameter
            n_iter: Number of iterations

        Returns:
            2D coordinates (n_samples x 2)
        """
        if embeddings.shape[0] == 0:
            return np.array([])

        # Adjust perplexity for small datasets
        adjusted_perplexity = min(perplexity, embeddings.shape[0] - 1)
        adjusted_n_neighbors = min(n_neighbors, embeddings.shape[0] - 1)

        if self.method == "tsne":
            return await self._tsne_projection(embeddings, adjusted_perplexity, n_iter)
        else:
            return await self._umap_projection(embeddings, adjusted_n_neighbors, min_dist)

    async def _tsne_projection(
        self,
        embeddings: np.ndarray,
        perplexity: int,
        n_iter: int,
    ) -> np.ndarray:
        """Compute t-SNE projection."""
        try:
            from sklearn.manifold import TSNE

            tsne = TSNE(
                n_components=self.n_components,
                perplexity=perplexity,
                n_iter=n_iter,
                random_state=self.random_state,
                init="pca",
                learning_rate="auto",
            )
            return tsne.fit_transform(embeddings)

        except ImportError:
            logger.error("scikit-learn not installed for t-SNE")
            raise

    async def _umap_projection(
        self,
        embeddings: np.ndarray,
        n_neighbors: int,
        min_dist: float,
    ) -> np.ndarray:
        """Compute UMAP projection."""
        try:
            import umap

            reducer = umap.UMAP(
                n_components=self.n_components,
                n_neighbors=n_neighbors,
                min_dist=min_dist,
                random_state=self.random_state,
            )
            return reducer.fit_transform(embeddings)

        except ImportError:
            logger.warning("umap-learn not installed, falling back to t-SNE")
            return await self._tsne_projection(embeddings, n_neighbors, 1000)

    async def cluster_embeddings(
        self,
        embeddings: np.ndarray,
        n_clusters: Optional[int] = None,
        method: Literal["kmeans", "hdbscan"] = "kmeans",
    ) -> tuple[np.ndarray, int]:
        """
        Cluster embeddings.

        Args:
            embeddings: Embedding matrix
            n_clusters: Number of clusters (auto-detected if None)
            method: Clustering method

        Returns:
            Tuple of (cluster labels, n_clusters)
        """
        if method == "kmeans":
            return await self._kmeans_cluster(embeddings, n_clusters)
        else:
            return await self._hdbscan_cluster(embeddings)

    async def _kmeans_cluster(
        self,
        embeddings: np.ndarray,
        n_clusters: Optional[int],
    ) -> tuple[np.ndarray, int]:
        """K-means clustering."""
        from sklearn.cluster import KMeans

        # Auto-detect number of clusters using elbow method
        if n_clusters is None:
            n_clusters = min(8, max(2, embeddings.shape[0] // 10))

        kmeans = KMeans(
            n_clusters=n_clusters,
            random_state=self.random_state,
            n_init=10,
        )
        labels = kmeans.fit_predict(embeddings)

        return labels, n_clusters

    async def _hdbscan_cluster(
        self,
        embeddings: np.ndarray,
    ) -> tuple[np.ndarray, int]:
        """HDBSCAN clustering (auto-detects clusters)."""
        try:
            import hdbscan

            clusterer = hdbscan.HDBSCAN(
                min_cluster_size=5,
                min_samples=3,
            )
            labels = clusterer.fit_predict(embeddings)
            n_clusters = len(set(labels)) - (1 if -1 in labels else 0)

            return labels, n_clusters

        except ImportError:
            logger.warning("hdbscan not installed, falling back to kmeans")
            return await self._kmeans_cluster(embeddings, None)

    async def generate_visualization(
        self,
        embeddings: np.ndarray,
        documents: list[Any],
        cluster: bool = True,
        n_clusters: Optional[int] = None,
    ) -> VisualizationData:
        """
        Generate complete visualization data.

        Args:
            embeddings: Embedding matrix
            documents: List of documents with metadata
            cluster: Whether to apply clustering
            n_clusters: Number of clusters (auto if None)

        Returns:
            VisualizationData ready for frontend
        """
        if len(embeddings) == 0 or len(documents) == 0:
            return VisualizationData(points=[], method=self.method)

        # Compute projection
        coords = await self.compute_projection(embeddings)

        # Optional clustering
        cluster_labels = None
        actual_n_clusters = None
        if cluster:
            cluster_labels, actual_n_clusters = await self.cluster_embeddings(
                embeddings, n_clusters
            )

        # Build visualization points
        points = []
        for i, doc in enumerate(documents):
            point = VisualizationPoint(
                id=self._get_doc_id(doc),
                x=float(coords[i, 0]),
                y=float(coords[i, 1]),
                label=self._get_doc_label(doc),
                subject=self._get_doc_field(doc, "subject"),
                level=self._get_doc_field(doc, "level"),
                source_type=self._get_doc_field(doc, "source_type"),
                cluster=int(cluster_labels[i]) if cluster_labels is not None else None,
            )
            points.append(point)

        # Generate cluster labels
        cluster_label_names = []
        if actual_n_clusters:
            # Try to name clusters by most common subject
            for c in range(actual_n_clusters):
                cluster_docs = [
                    doc
                    for i, doc in enumerate(documents)
                    if cluster_labels is not None and cluster_labels[i] == c
                ]
                if cluster_docs:
                    subjects = [self._get_doc_field(d, "subject") for d in cluster_docs]
                    subjects = [s for s in subjects if s]
                    if subjects:
                        from collections import Counter

                        most_common = Counter(subjects).most_common(1)[0][0]
                        cluster_label_names.append(most_common)
                    else:
                        cluster_label_names.append(f"Cluster {c}")
                else:
                    cluster_label_names.append(f"Cluster {c}")

        return VisualizationData(
            points=points,
            method=self.method,
            parameters={
                "n_components": self.n_components,
                "random_state": self.random_state,
            },
            n_clusters=actual_n_clusters,
            cluster_labels=cluster_label_names,
        )

    def _get_doc_id(self, doc: Any) -> str:
        """Extract document ID."""
        if hasattr(doc, "doc_id"):
            return doc.doc_id
        if isinstance(doc, dict):
            return doc.get("doc_id", doc.get("id", str(id(doc))))
        return str(id(doc))

    def _get_doc_label(self, doc: Any) -> str:
        """Extract document label for display."""
        if hasattr(doc, "title"):
            return doc.title[:50]
        if isinstance(doc, dict):
            return doc.get("title", "")[:50]
        return ""

    def _get_doc_field(self, doc: Any, field: str) -> Optional[str]:
        """Extract a field from document."""
        if hasattr(doc, field):
            return getattr(doc, field)
        if hasattr(doc, "metadata"):
            return getattr(doc.metadata, field, None)
        if isinstance(doc, dict):
            return doc.get(field) or doc.get("metadata", {}).get(field)
        return None

    async def export_for_plotly(
        self,
        viz_data: VisualizationData,
    ) -> dict[str, Any]:
        """Export visualization data for Plotly."""
        subjects = list(set(p.subject for p in viz_data.points if p.subject))
        color_map = {subj: i for i, subj in enumerate(subjects)}

        return {
            "data": [
                {
                    "type": "scatter",
                    "mode": "markers",
                    "x": [p.x for p in viz_data.points],
                    "y": [p.y for p in viz_data.points],
                    "text": [p.label for p in viz_data.points],
                    "marker": {
                        "color": [color_map.get(p.subject, 0) for p in viz_data.points],
                        "colorscale": "Viridis",
                        "size": 8,
                    },
                    "hoverinfo": "text",
                }
            ],
            "layout": {
                "title": f"Curriculum Embeddings ({viz_data.method.upper()})",
                "xaxis": {"title": "Dimension 1"},
                "yaxis": {"title": "Dimension 2"},
            },
        }
