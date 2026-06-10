# visualization.py
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from sklearn.manifold import TSNE
from pathlib import Path
import logging
import base64
import io
from PIL import Image
from typing import Optional, List
import numpy as np
import html
import os

logger = logging.getLogger(__name__)


class DocumentVisualization:
    """Class for creating document embedding visualizations"""

    def __init__(self, output_dir: str = ".", thumbnail_size: tuple = (150, 150)):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.thumbnail_size = thumbnail_size

    def reduce_dimensions(self, embeddings: np.ndarray, n_components: int = 2, perplexity: int = 30) -> np.ndarray:
        """Reduce dimensions of embeddings for visualization"""
        num_samples = embeddings.shape[0]
        # Adjust perplexity if the number of samples is less than the default perplexity
        if num_samples <= perplexity:
            perplexity = max(1, num_samples // 3)

        logger.info(f"Reducing dimensions from {embeddings.shape[1]} to {n_components} with perplexity {perplexity}...")
        return TSNE(n_components=n_components, perplexity=perplexity, random_state=42).fit_transform(embeddings)

    def image_to_base64(self, image, max_size: tuple = None) -> Optional[str]:
        """Convert PIL Image to base64 string for embedding in HTML"""
        if image is None:
            return None

        try:
            # Handle different image input types
            if isinstance(image, str):
                if "Invalid" in image or not Path(image).exists():
                    return None
                image = Image.open(image)

            # Resize image if needed
            if max_size is None:
                max_size = self.thumbnail_size

            # Convert to RGB if necessary (for JPEG compatibility)
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')

            # Resize maintaining aspect ratio
            image.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Convert to base64
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=85)
            img_str = base64.b64encode(buffer.getvalue()).decode()

            return f"data:image/jpeg;base64,{img_str}"

        except Exception as e:
            logger.warning(f"Failed to convert image to base64: {e}")
            return None

    def get_full_transcription(self, doc) -> str:
        """Get the full transcription text from a document with robust Unicode handling"""
        transcription_text = ""
        try:
            if hasattr(doc, 'transcriptions') and doc.transcriptions:
                for transcription in doc.transcriptions:
                    try:
                        if hasattr(transcription, 'lines') and transcription.lines:
                            for line_text in transcription.lines.values():
                                if line_text:
                                    # Ensure string conversion and normalize Unicode
                                    clean_text = self._clean_text_for_html(str(line_text))
                                    transcription_text += clean_text + "\n"
                        elif isinstance(transcription, dict) and 'lines' in transcription:
                            for line_text in transcription['lines'].values():
                                if line_text:
                                    clean_text = self._clean_text_for_html(str(line_text))
                                    transcription_text += clean_text + "\n"
                    except (AttributeError, TypeError, UnicodeError) as e:
                        logger.warning(f"Error processing transcription: {e}")
                        continue
        except Exception as e:
            logger.warning(f"Error extracting transcription: {e}")
            return "Error reading transcription"

        return transcription_text.strip()

    def create_hover_template_with_images(self, df: pd.DataFrame) -> str:
        """Create custom hover template that includes image thumbnails"""
        hover_template = (
                "<b>%{customdata[0]}</b><br>" +
                "Language: %{customdata[1]}<br>" +
                "Has Image: %{customdata[2]}<br>" +
                "Has Transcription: %{customdata[3]}<br>" +
                "Transcription Length: %{customdata[4]}<br>" +
                "Description: %{customdata[5]}<br>" +
                "<extra></extra>"
        )
        return hover_template

    def create_figure_with_image_subplots(self, df: pd.DataFrame, title: str, **kwargs) -> go.Figure:
        """Create figure with image subplots for thumbnail preview"""
        from plotly.subplots import make_subplots

        # Create main scatter plot
        main_fig = self._create_base_figure(df, title, **kwargs)

        # For now, return the main figure and add click event handling
        # We'll implement a different approach using click events to show images
        return main_fig

    def add_image_click_functionality(self, fig: go.Figure, df: pd.DataFrame) -> go.Figure:
        """Add JavaScript for image display on click"""

        # Add custom JavaScript for click handling
        custom_js = """
        <script>
        var plotDiv = document.getElementById('plotly-div');

        plotDiv.on('plotly_click', function(data){
            var pointIndex = data.points[0].pointIndex;
            var traceIndex = data.points[0].curveNumber;

            // Get the image data from customdata
            var imageData = data.points[0].customdata[6];

            if (imageData && imageData !== "No image available") {
                // Create or update image popup
                var popup = document.getElementById('image-popup');
                if (!popup) {
                    popup = document.createElement('div');
                    popup.id = 'image-popup';
                    popup.style.cssText = `
                        position: fixed;
                        top: 50%;
                        left: 50%;
                        transform: translate(-50%, -50%);
                        background: white;
                        border: 2px solid #333;
                        border-radius: 8px;
                        padding: 10px;
                        z-index: 9999;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
                        max-width: 90%;
                        max-height: 90%;
                    `;
                    document.body.appendChild(popup);

                    // Add close button
                    var closeBtn = document.createElement('button');
                    closeBtn.innerHTML = '×';
                    closeBtn.style.cssText = `
                        position: absolute;
                        top: 5px;
                        right: 10px;
                        border: none;
                        background: none;
                        font-size: 20px;
                        cursor: pointer;
                    `;
                    closeBtn.onclick = function() { popup.style.display = 'none'; };
                    popup.appendChild(closeBtn);
                }

                popup.innerHTML = '<button onclick="this.parentElement.style.display=\'none\'" style="position:absolute;top:5px;right:10px;border:none;background:none;font-size:20px;cursor:pointer;">×</button><img src="' + imageData + '" style="max-width:100%;max-height:80vh;">';
                popup.style.display = 'block';
            }
        });
        </script>
        """

        return fig, custom_js


    def _clean_text_for_html(self, text: str) -> str:
        """Clean and normalize text for safe HTML display, especially for RTL languages"""
        if not text:
            return ""

        try:
            # Convert to string if not already
            text = str(text)

            # Normalize Unicode (NFD to combine diacritics properly)
            import unicodedata
            text = unicodedata.normalize('NFC', text)

            # Remove problematic control characters but preserve RTL marks
            import re
            # Keep essential RTL/LTR marks but remove other control chars
            rtl_marks = '\u200F\u200E\u202A\u202B\u202C\u202D\u202E'
            control_chars = ''.join(chr(i) for i in range(32) if chr(i) not in '\t\n\r')
            control_chars = ''.join(c for c in control_chars if c not in rtl_marks)

            # Remove problematic control characters
            for char in control_chars:
                text = text.replace(char, '')

            # Replace various quote types that can break HTML
            text = text.replace('"', '&quot;').replace("'", '&#39;')
            text = text.replace('\u201C', '&ldquo;').replace('\u201D', '&rdquo;')
            text = text.replace('\u2018', '&lsquo;').replace('\u2019', '&rsquo;')

            # Normalize whitespace but preserve intentional formatting
            text = re.sub(r'\r\n|\r|\n', '\n', text)  # Normalize line endings
            text = re.sub(r'[ \t]+', ' ', text)  # Collapse multiple spaces/tabs

            return text.strip()

        except Exception as e:
            logger.warning(f"Error cleaning text: {e}")
            # Fallback: basic cleaning
            return str(text).replace('"', '&quot;').replace("'", '&#39;')[:1000]

    def get_transcription_length(self, doc) -> int:
        """Get the total length of transcriptions in a document with error handling"""
        length = 0
        try:
            if hasattr(doc, 'transcriptions') and doc.transcriptions:
                for transcription in doc.transcriptions:
                    try:
                        if hasattr(transcription, 'lines') and transcription.lines:
                            for line_text in transcription.lines.values():
                                if line_text:
                                    length += len(str(line_text))
                        elif isinstance(transcription, dict) and 'lines' in transcription:
                            for line_text in transcription['lines'].values():
                                if line_text:
                                    length += len(str(line_text))
                    except (AttributeError, TypeError) as e:
                        logger.warning(f"Error calculating transcription length: {e}")
                        continue
        except Exception as e:
            logger.warning(f"Error getting transcription length: {e}")
        return length

    def create_visualization_dataframe(self, docs: List, embeddings_2d: np.ndarray) -> pd.DataFrame:
        """Create a DataFrame for visualization from document objects with robust text handling"""
        # Convert images to base64 for hover display
        image_data = []
        full_descriptions = []
        full_transcriptions = []
        original_image_urls = []  # New: Store original image URLs

        for i, doc in enumerate(docs):
            if i % 10 == 0:  # Progress logging
                logger.info(f"Processing document {i + 1}/{len(docs)}")

            try:
                # Process image
                image = getattr(doc, 'image', None)
                base64_image = self.image_to_base64(image)
                image_data.append(base64_image)

                # Get original image URLs for full-size viewing
                # Use the actual URL that was used for caching/downloading
                actual_url = getattr(doc, 'actual_image_url', '')
                if not actual_url:
                    # Fallback to parsing from image_urls if actual_image_url not available
                    image_urls = getattr(doc, 'image_urls', [])
                    if image_urls:
                        # Determine if cambridge doc and get appropriate URL
                        is_cambridge = "/" in getattr(doc, 'doc_id', '')
                        if is_cambridge:
                            actual_url = image_urls[0] if image_urls[0] else ""
                        else:
                            # Import get_largest_image_url if needed for fallback
                            try:
                                from your_module_name import get_largest_image_url  # Replace with actual module name
                                actual_url = get_largest_image_url(image_urls[0]) if image_urls[0] else ""
                            except ImportError:
                                logging.warning("Could not import get_largest_image_url, using first URL as fallback")
                                actual_url = image_urls[0] if image_urls[0] else ""
                original_image_urls.append(actual_url)

                # Get full description with safe handling
                try:
                    raw_desc = getattr(doc, 'description', '')
                    full_desc = self._clean_text_for_html(raw_desc) if raw_desc else ''
                except Exception as e:
                    logger.warning(f"Error processing description for doc {i}: {e}")
                    full_desc = "Error reading description"
                full_descriptions.append(full_desc)

                # Get full transcription with safe handling
                try:
                    full_trans = self.get_full_transcription(doc)
                except Exception as e:
                    logger.warning(f"Error processing transcription for doc {i}: {e}")
                    full_trans = "Error reading transcription"
                full_transcriptions.append(full_trans)

            except Exception as e:
                logger.error(f"Critical error processing document {i}: {e}")
                # Provide fallback data
                image_data.append(None)
                original_image_urls.append("")
                full_descriptions.append("Error processing document")
                full_transcriptions.append("Error processing document")

        # Create DataFrame with safe text handling
        try:
            df = pd.DataFrame({
                'x': embeddings_2d[:, 0],
                'y': embeddings_2d[:, 1],
                'id': [self._safe_get_attr(doc, 'doc_id', f"doc_{i}") for i, doc in enumerate(docs)],
                'language': [self._safe_get_attr(doc, 'language', 'Unknown') for doc in docs],
                'has_image': [self._safe_has_image(doc) for doc in docs],
                'has_transcription': [self.get_transcription_length(doc) > 0 for doc in docs],
                'description': [
                    (desc[:100] + '...' if len(desc) > 100 else desc)
                    for desc in full_descriptions
                ],
                'full_description': full_descriptions,
                'full_transcription': full_transcriptions,
                'image_base64': image_data,
                'original_image_url': original_image_urls  # New column
            })
        except Exception as e:
            logger.error(f"Error creating DataFrame: {e}")
            raise

        # Extract date information safely
        for doc, row_idx in zip(docs, df.index):
            try:
                if hasattr(doc, 'date') and doc.date:
                    for key, value in doc.date.items():
                        safe_value = self._clean_text_for_html(str(value)) if value else ''
                        df.loc[row_idx, f'date_{key}'] = safe_value
            except Exception as e:
                logger.warning(f"Error processing date for doc {row_idx}: {e}")

        # Add transcription length
        df['transcription_length'] = [self.get_transcription_length(doc) for doc in docs]

        # Create custom hover data including all data for click events
        df['image_data_for_click'] = df['image_base64'].copy()

        return df

    def _create_base_figure(self, df: pd.DataFrame, title: str, **kwargs) -> go.Figure:
        """Create a base plotly figure with common settings and image hover support"""

        # Prepare custom data for hover template (including full content for popups)
        customdata = np.column_stack([
            df['id'],
            df['language'],
            df['has_image'],
            df['has_transcription'],
            df['transcription_length'],
            df['description'],
            df['image_data_for_click'],
            df['full_description'],
            df['full_transcription'],
            df['original_image_url']  # New: Add original image URL to customdata
        ])

        # Create figure using graph_objects for more control over hover
        fig = go.Figure()

        # Handle different coloring options
        color_col = kwargs.get('color', 'language')
        symbol_col = kwargs.get('symbol', 'has_transcription')

        # Get unique values for grouping
        unique_colors = df[color_col].unique()
        unique_symbols = df[symbol_col].unique() if symbol_col else [None]

        # Define symbol mapping
        symbol_map = {True: 'circle', False: 'circle-open'} if symbol_col == 'has_transcription' else {}

        # Add traces for each color/symbol combination
        for color_val in unique_colors:
            for symbol_val in unique_symbols:
                if symbol_col:
                    mask = (df[color_col] == color_val) & (df[symbol_col] == symbol_val)
                    symbol_name = symbol_map.get(symbol_val, 'circle')
                    trace_name = f"{color_val} ({'Has Transcription' if symbol_val else 'No Transcription'})"
                else:
                    mask = df[color_col] == color_val
                    symbol_name = 'circle'
                    trace_name = str(color_val)

                if mask.sum() == 0:
                    continue

                # Determine marker size
                sizes = df.loc[mask, 'has_image'].apply(lambda x: 12 if x else 8)

                fig.add_trace(go.Scatter(
                    x=df.loc[mask, 'x'],
                    y=df.loc[mask, 'y'],
                    mode='markers+text',
                    marker=dict(
                        symbol=symbol_name,
                        size=sizes,
                        line=dict(width=1)
                    ),
                    text=df.loc[mask, 'id'],
                    textposition='top center',
                    name=trace_name,
                    customdata=customdata[mask],
                    hovertemplate=self.create_hover_template_with_images(df),
                    showlegend=True
                ))

        # Update layout with responsive width and better spacing
        fig.update_layout(
            title=title,
            height=900,  # Increased height
            autosize=True,  # Enable responsive sizing
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                align="left"
            ),
            xaxis_title="Dimension 1",
            yaxis_title="Dimension 2",
            margin=dict(l=50, r=50, t=80, b=50),  # Reduced margins for more plot area
            xaxis=dict(
                scaleanchor="y",  # Keep aspect ratio
                scaleratio=1,
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            )
        )

        return fig

    def _safe_get_attr(self, obj, attr_name: str, default_value: str) -> str:
        """Safely get attribute value with text cleaning"""
        try:
            value = getattr(obj, attr_name, default_value)
            return self._clean_text_for_html(str(value)) if value else default_value
        except Exception:
            return default_value

    def _safe_has_image(self, doc) -> bool:
        """Safely check if document has a valid image"""
        try:
            image = getattr(doc, 'image', None)
            if image is None:
                return False
            if isinstance(image, str) and "Invalid" in image:
                return False
            return True
        except Exception:
            return False

    def _create_base_figure(self, df: pd.DataFrame, title: str, **kwargs) -> go.Figure:
        """Create a base plotly figure with common settings and image hover support"""

        # Prepare custom data for hover template (including full content for popups)
        customdata = np.column_stack([
            df['id'],
            df['language'],
            df['has_image'],
            df['has_transcription'],
            df['transcription_length'],
            df['description'],
            df['image_data_for_click'],
            df['full_description'],
            df['full_transcription'],
            df['original_image_url']
        ])

        # Create figure using graph_objects for more control over hover
        fig = go.Figure()

        # Handle different coloring options
        color_col = kwargs.get('color', 'language')
        symbol_col = kwargs.get('symbol', 'has_transcription')

        # Get unique values for grouping
        unique_colors = df[color_col].unique()
        unique_symbols = df[symbol_col].unique() if symbol_col else [None]

        # Define symbol mapping
        symbol_map = {True: 'circle', False: 'circle-open'} if symbol_col == 'has_transcription' else {}

        # Add traces for each color/symbol combination
        for color_val in unique_colors:
            for symbol_val in unique_symbols:
                if symbol_col:
                    mask = (df[color_col] == color_val) & (df[symbol_col] == symbol_val)
                    symbol_name = symbol_map.get(symbol_val, 'circle')
                    trace_name = f"{color_val} ({'Has Transcription' if symbol_val else 'No Transcription'})"
                else:
                    mask = df[color_col] == color_val
                    symbol_name = 'circle'
                    trace_name = str(color_val)

                if mask.sum() == 0:
                    continue

                # Determine marker size
                sizes = df.loc[mask, 'has_image'].apply(lambda x: 12 if x else 8)

                fig.add_trace(go.Scatter(
                    x=df.loc[mask, 'x'],
                    y=df.loc[mask, 'y'],
                    mode='markers+text',
                    marker=dict(
                        symbol=symbol_name,
                        size=sizes,
                        line=dict(width=1)
                    ),
                    text=df.loc[mask, 'id'],
                    textposition='top center',
                    name=trace_name,
                    customdata=customdata[mask],
                    hovertemplate=self.create_hover_template_with_images(df),
                    showlegend=True
                ))

        # Update layout with responsive width and better spacing
        fig.update_layout(
            title=title,
            height=900,  # Increased height
            autosize=True,  # Enable responsive sizing
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                align="left"
            ),
            xaxis_title="Dimension 1",
            yaxis_title="Dimension 2",
            margin=dict(l=50, r=50, t=80, b=50),  # Reduced margins for more plot area
            xaxis=dict(
                scaleanchor="y",  # Keep aspect ratio
                scaleratio=1,
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='lightgray'
            )
        )

        return fig

    def create_enhanced_popup_js(self) -> str:
        """Create enhanced JavaScript for popups with full content and robust multilingual support"""
        with open(os.path.join(os.path.dirname(__file__), 'popup_enhanced.js'), 'r', encoding='utf-8') as f:
            js_code = f.read()
        return "<script>" + js_code + "</script>"

    def create_main_visualization(self, df: pd.DataFrame,
                                  output_filename: str = "document_embeddings.html") -> go.Figure:
        """Create the main visualization of document embeddings"""
        logger.info("Creating main visualization with enhanced click-to-view popups...")

        fig = self._create_base_figure(
            df,
            title='Document Embeddings (Click points to view full content)',
            color='language',
            symbol='has_transcription'
        )

        # Save as HTML with enhanced JavaScript
        output_path = self.output_dir / output_filename

        # Get the HTML and add custom JavaScript with responsive configuration
        html_string = fig.to_html(include_plotlyjs=True, config={
            'displayModeBar': True,
            'displaylogo': False,
            'modeBarButtonsToRemove': ['pan2d', 'lasso2d'],
            'responsive': True
        })

        # Add enhanced JavaScript for popups
        custom_js = self.create_enhanced_popup_js()

        # Insert the custom JavaScript before the closing body tag
        html_string = html_string.replace('</body>', custom_js + '</body>')

        # Write the modified HTML
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_string)

        logger.info(f"Main visualization saved as {output_path}")

        return fig

    def create_language_visualization(self, df: pd.DataFrame,
                                      output_filename: str = "language_embeddings.html") -> go.Figure:
        """Create a visualization highlighting document languages"""
        logger.info("Creating language-based visualization with enhanced click-to-view popups...")

        fig = self._create_base_figure(
            df,
            title='Document Embeddings by Language (Click points to view full content)',
            color='language',
            symbol='has_transcription'
        )

        # Save with enhanced JavaScript
        output_path = self.output_dir / output_filename
        html_string = fig.to_html(include_plotlyjs=True)

        # Add enhanced JavaScript
        custom_js = self.create_enhanced_popup_js()
        html_string = html_string.replace('</body>', custom_js + '</body>')

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_string)

        logger.info(f"Language visualization saved as {output_path}")

        return fig

    def create_completeness_visualization(self, df: pd.DataFrame,
                                          output_filename: str = "completeness_embeddings.html") -> go.Figure:
        """Create a visualization based on document completeness"""
        logger.info("Creating completeness-based visualization with enhanced click-to-view popups...")

        # Create a completeness category
        df_copy = df.copy()
        df_copy['completeness'] = df_copy.apply(
            lambda row: 'Complete' if row['has_image'] and row['has_transcription']
            else 'Image Only' if row['has_image'] and not row['has_transcription']
            else 'Transcription Only' if not row['has_image'] and row['has_transcription']
            else 'Incomplete',
            axis=1
        )

        # Use the base figure creation but with completeness coloring
        fig = self._create_base_figure(
            df_copy,
            title='Document Embeddings by Completeness (Click points to view full content)',
            color='completeness',
            symbol='language'
        )

        # Manually set colors for completeness categories
        color_map = {
            'Complete': 'green',
            'Image Only': 'blue',
            'Transcription Only': 'orange',
            'Incomplete': 'red'
        }

        # Update trace colors
        for trace in fig.data:
            for comp_type, color in color_map.items():
                if comp_type in trace.name:
                    trace.marker.color = color
                    break

        # Save with enhanced JavaScript
        output_path = self.output_dir / output_filename
        html_string = fig.to_html(include_plotlyjs=True)

        # Add enhanced JavaScript
        custom_js = self.create_enhanced_popup_js()
        html_string = html_string.replace('</body>', custom_js + '</body>')

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_string)

        logger.info(f"Completeness visualization saved as {output_path}")

        return fig

    def create_all_visualizations(self, docs: List, embeddings: np.ndarray, prefix: str = ""):
        """Create all visualization types
        :param docs: list of documents
        :type docs: List
        :param embeddings: embedding matrix
        """
        # Reduce dimensions
        embeddings_2d = self.reduce_dimensions(embeddings)

        # Create DataFrame
        df = self.create_visualization_dataframe(docs, embeddings_2d)

        # Create all visualizations
        self.create_main_visualization(df, f"{prefix}main_embeddings.html")
        self.create_language_visualization(df, f"{prefix}language_embeddings.html")
        self.create_completeness_visualization(df, f"{prefix}completeness_embeddings.html") # Thanks claude