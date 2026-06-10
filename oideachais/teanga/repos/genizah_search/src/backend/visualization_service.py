"""
Visualization Service - Proper dimensionality reduction usin standard Python libraries

This service provides PCA, t-SNE, and UMAP implementations using standard
scientific Python libraries (scikit-learn, umap-learn) instead of JavaScript...
"""

import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.neighbors import NearestNeighbors
import umap
import logging

logger = logging.getLogger(__name__)


class VisualizationService:
    """Service for performing dimensionality reduction on embeddings"""
    
    def __init__(self):
        # Store fitted models and data for query projection
        self._fitted_models = {}  # {method: fitted_model}
        self._original_embeddings = {}  # {method: embeddings_array}
        self._coordinates = {}  # {method: coordinates_array}
        self._knn_index = {}  # {method: knn_index} for t-SNE projection
    
    def perform_pca(
        self,
        embeddings: List[List[float]], 
        n_components: int = 2,
        random_state: Optional[int] = 42,
        store_model: bool = True
    ) -> tuple[List[List[float]], Optional[PCA]]:
        """
        Perform Principal Component Analysis (PCA) on embeddings.
        
        Args:
            embeddings: List of embedding vectors
            n_components: Number of dimensions to reduce to (default: 2)
            random_state: Random seed for reproducibility
            store_model: Whether to store the fitted model for query projection
            
        Returns:
            Tuple of (list of 2D coordinates, fitted PCA model)
        """
        if len(embeddings) < 2:
            return [[0.0, 0.0] for _ in embeddings], None
        
        # Convert to numpy array
        X = np.array(embeddings)
        
        # Ensure we don't request more components than we have samples
        n_components = min(n_components, X.shape[0] - 1, X.shape[1])
        
        logger.info(f"Performing PCA on {len(embeddings)} embeddings of dimension {X.shape[1]}, reducing to {n_components}D")
        
        # Perform PCA
        pca = PCA(n_components=n_components, random_state=random_state)
        coords = pca.fit_transform(X)
        
        # Store model and data for query projection
        if store_model:
            self._fitted_models['pca'] = pca
            self._original_embeddings['pca'] = X
            self._coordinates['pca'] = coords
        
        # Convert back to list format
        result = coords.tolist()
        
        logger.info(f"PCA explained variance ratio: {pca.explained_variance_ratio_.sum():.4f}")
        
        return result, pca
    
    def perform_tsne(
        self,
        embeddings: List[List[float]],
        perplexity: Optional[int] = None,
        n_iter: int = 1000,
        learning_rate: float = 200.0,
        random_state: Optional[int] = 42,
        early_exaggeration: float = 12.0,
        store_model: bool = True
    ) -> tuple[List[List[float]], Optional[TSNE]]:
        """
        Perform t-SNE (t-Distributed Stochastic Neighbor Embedding) on embeddings.
        
        Args:
            embeddings: List of embedding vectors
            perplexity: Perplexity parameter (default: min(30, n_samples-1))
            n_iter: Number of iterations (default: 1000) - mapped to max_iter for scikit-learn
            learning_rate: Learning rate (default: 200.0)
            random_state: Random seed for reproducibility
            early_exaggeration: Early exaggeration factor (default: 12.0)
            store_model: Whether to store the fitted model and k-NN index for query projection
            
        Returns:
            Tuple of (list of 2D coordinates, fitted TSNE model)
        """
        if len(embeddings) < 2:
            return [[0.0, 0.0] for _ in embeddings], None
        
        # Convert to numpy array
        X = np.array(embeddings)
        n_samples = X.shape[0]
        
        # Set default perplexity if not provided
        if perplexity is None:
            perplexity = min(30, max(5, (n_samples - 1) // 3))
        
        # Ensure perplexity is valid
        perplexity = min(perplexity, n_samples - 1)
        
        logger.info(f"Performing t-SNE on {n_samples} embeddings of dimension {X.shape[1]}, "
                   f"perplexity={perplexity}, iterations={n_iter}")
        
        # Perform t-SNE
        # Note: scikit-learn uses 'max_iter' instead of 'n_iter'
        tsne = TSNE(
            n_components=2,
            perplexity=perplexity,
            max_iter=n_iter,  # Use max_iter for scikit-learn compatibility
            learning_rate=learning_rate,
            random_state=random_state,
            early_exaggeration=early_exaggeration,
            verbose=1 if n_samples > 100 else 0
        )
        
        coords = tsne.fit_transform(X)
        
        # Store model and data for query projection using k-NN
        if store_model:
            self._fitted_models['tsne'] = tsne
            self._original_embeddings['tsne'] = X
            self._coordinates['tsne'] = coords
            
            # Build k-NN index for query projection
            # Use more neighbors than perplexity for better projection
            n_neighbors_knn = min(20, max(10, perplexity * 2), n_samples - 1)
            knn = NearestNeighbors(n_neighbors=n_neighbors_knn, metric='cosine')
            knn.fit(X)
            self._knn_index['tsne'] = knn
            logger.info(f"Built k-NN index for t-SNE with {n_neighbors_knn} neighbors")
        
        # Convert back to list format
        result = coords.tolist()
        
        logger.info(f"t-SNE completed successfully")
        
        return result, tsne
    
    def perform_umap(
        self,
        embeddings: List[List[float]],
        n_neighbors: int = 15,
        min_dist: float = 0.1,
        n_components: int = 2,
        metric: str = 'cosine',
        random_state: Optional[int] = 42,
        store_model: bool = True
    ) -> tuple[List[List[float]], Optional[umap.UMAP]]:
        """
        Perform UMAP (Uniform Manifold Approximation and Projection) on embeddings.
        
        Args:
            embeddings: List of embedding vectors
            n_neighbors: Number of neighbors (default: 15)
            min_dist: Minimum distance between points in embedding space (default: 0.1)
            n_components: Number of dimensions to reduce to (default: 2)
            metric: Distance metric to use (default: 'cosine')
            random_state: Random seed for reproducibility
            store_model: Whether to store the fitted reducer for query projection
            
        Returns:
            Tuple of (list of 2D coordinates, fitted UMAP reducer)
        """
        if len(embeddings) < 2:
            return [[0.0, 0.0] for _ in embeddings], None
        
        # Convert to numpy array
        X = np.array(embeddings)
        n_samples = X.shape[0]
        
        # Adjust n_neighbors if needed
        n_neighbors = min(n_neighbors, n_samples - 1)
        n_neighbors = max(n_neighbors, 2)  # At least 2 neighbors
        
        logger.info(f"Performing UMAP on {n_samples} embeddings of dimension {X.shape[1]}, "
                   f"n_neighbors={n_neighbors}, min_dist={min_dist}")
        
        # Perform UMAP
        reducer = umap.UMAP(
            n_neighbors=n_neighbors,
            min_dist=min_dist,
            n_components=n_components,
            metric=metric,
            random_state=random_state,
            verbose=True if n_samples > 100 else False
        )
        
        coords = reducer.fit_transform(X)
        
        # Store model and data for query projection
        if store_model:
            self._fitted_models['umap'] = reducer
            self._original_embeddings['umap'] = X
            self._coordinates['umap'] = coords
        
        # Convert back to list format
        result = coords.tolist()
        
        logger.info(f"UMAP completed successfully")
        
        return result, reducer
    
    def calculate_visualization(
        self,
        embeddings: List[List[float]],
        method: str = 'tsne',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Calculate visualization coordinates using the specified method.
        
        Args:
            embeddings: List of embedding vectors
            method: Method to use ('pca', 'tsne', or 'umap')
            **kwargs: Additional parameters for the specific method
            
        Returns:
            Dictionary with coordinates and metadata
        """
        if not embeddings or len(embeddings) == 0:
            raise ValueError("No embeddings provided")
        
        method = method.lower()
        
        if method == 'pca':
            coords, _ = self.perform_pca(
                embeddings,
                n_components=kwargs.get('n_components', 2),
                random_state=kwargs.get('random_state', 42),
                store_model=True
            )
        elif method == 'tsne':
            coords, _ = self.perform_tsne(
                embeddings,
                perplexity=kwargs.get('perplexity'),
                n_iter=kwargs.get('n_iter', 1000),
                learning_rate=kwargs.get('learning_rate', 200.0),
                random_state=kwargs.get('random_state', 42),
                early_exaggeration=kwargs.get('early_exaggeration', 12.0),
                store_model=True
            )
        elif method == 'umap':
            coords, _ = self.perform_umap(
                embeddings,
                n_neighbors=kwargs.get('n_neighbors', 15),
                min_dist=kwargs.get('min_dist', 0.1),
                n_components=kwargs.get('n_components', 2),
                metric=kwargs.get('metric', 'cosine'),
                random_state=kwargs.get('random_state', 42),
                store_model=True
            )
        else:
            raise ValueError(f"Unknown visualization method: {method}. Must be 'pca', 'tsne', or 'umap'")
        
        # Calculate statistics
        coords_array = np.array(coords)
        x_min, x_max = float(coords_array[:, 0].min()), float(coords_array[:, 0].max())
        y_min, y_max = float(coords_array[:, 1].min()), float(coords_array[:, 1].max())
        
        return {
            'coordinates': coords,
            'method': method,
            'num_points': len(coords),
            'statistics': {
                'x_range': [x_min, x_max],
                'y_range': [y_min, y_max]
            }
        }
    
    def project_query(
        self,
        query_embedding: List[float],
        method: str = 'umap',
        n_neighbors: int = 10
    ) -> Dict[str, Any]:
        """
        Project a query embedding onto an existing visualization space.
        
        Args:
            query_embedding: Embedding vector for the query
            method: Visualization method to project onto ('pca', 'tsne', or 'umap')
            n_neighbors: Number of neighbors to use for t-SNE projection (default: 10)
            
        Returns:
            Dictionary with projected coordinates and nearest neighbors info
        """
        method = method.lower()
        
        if method not in self._fitted_models:
            raise ValueError(
                f"No fitted model found for method '{method}'. "
                f"Please calculate a visualization first using '{method}' method."
            )
        
        query_embedding_array = np.array([query_embedding])
        
        if method == 'pca':
            # PCA supports direct transform
            pca = self._fitted_models['pca']
            coords = pca.transform(query_embedding_array)[0]
            x, y = float(coords[0]), float(coords[1])
            
        elif method == 'umap':
            # UMAP supports direct transform
            reducer = self._fitted_models['umap']
            coords = reducer.transform(query_embedding_array)[0]
            x, y = float(coords[0]), float(coords[1])
            
        elif method == 'tsne':
            # t-SNE doesn't support transform, use k-NN approximation
            if 'tsne' not in self._knn_index:
                raise ValueError("k-NN index not found for t-SNE. Please recalculate visualization.")
            
            knn = self._knn_index['tsne']
            original_embeddings = self._original_embeddings['tsne']
            coordinates = self._coordinates['tsne']
            
            # Find k nearest neighbors in high-dimensional space
            distances, indices = knn.kneighbors(query_embedding_array, n_neighbors=min(n_neighbors, len(original_embeddings)))
            
            # Get t-SNE coordinates of neighbors
            neighbor_coords = coordinates[indices[0]]
            
            # Weighted average by inverse distance
            weights = 1 / (distances[0] + 1e-6)  # Add epsilon to avoid division by zero
            weights = weights / weights.sum()
            
            coords = np.average(neighbor_coords, weights=weights, axis=0)
            x, y = float(coords[0]), float(coords[1])
            
        else:
            raise ValueError(f"Unknown visualization method: {method}")
        
        # Find nearest neighbors for context
        if method in self._original_embeddings:
            original_embeddings = self._original_embeddings[method]
            # Use cosine similarity to find nearest neighbors
            from sklearn.metrics.pairwise import cosine_similarity
            similarities = cosine_similarity(query_embedding_array, original_embeddings)[0]
            nearest_indices = np.argsort(similarities)[::-1][:20]  # Top 20
            
            nearest_neighbors = [
                {
                    'index': int(idx),
                    'similarity': float(similarities[idx])
                }
                for idx in nearest_indices
            ]
        else:
            nearest_neighbors = []
        
        return {
            'coordinates': {'x': x, 'y': y},
            'method': method,
            'nearest_neighbors': nearest_neighbors
        }



    def load_precomputed_visualization(self, path: str) -> Dict[str, Any]:
        """
        Load pre-computed visualization data from a JSON file.
        
        Args:
            path: Path to the JSON file containing pre-computed data
            
        Returns:
            Dictionary with visualization data
        """
        import json
        import os
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Pre-computed visualization file not found at {path}")
            
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                
            logger.info(f"Loaded pre-computed visualization with {data.get('count', 0)} documents")
            return data
        except Exception as e:
            logger.error(f"Failed to load pre-computed visualization: {e}")
            raise ValueError(f"Invalid pre-computed visualization file: {e}")


# Create singleton instance
visualization_service = VisualizationService()

