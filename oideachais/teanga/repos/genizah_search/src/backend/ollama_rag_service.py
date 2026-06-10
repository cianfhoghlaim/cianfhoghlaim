"""
Ollama RAG Service for chat with bibliography search integration.
Supports both localhost and remote Ollama endpoints with optional Cloudflare Access authentication.
"""

import os
import logging
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import httpx
import json
import dotenv
dotenv.load_dotenv()

# Wandb Weave imports
import weave
from search_bibliography import bibliography_search_service, BibliographyHybridSearchRequest
from search_service import search_service

logger = logging.getLogger(__name__)

# Shelf mark search request model (duplicated here to avoid circular imports)
class ShelfMarkSearchRequest(BaseModel):
    shelf_mark: str = Field(..., min_length=1, max_length=100, description="Shelf mark to search for")
    exact_match: bool = Field(default=False, description="Whether to perform exact match or partial match")
    num_results: Optional[int] = Field(default=10, ge=1, le=50, description="Number of results to return")
    include_embeddings: Optional[bool] = Field(default=False, description="Include embedding vectors for visualization")
    index_name: Optional[str] = Field(default=None, description="Elasticsearch index to search (defaults to configured index)")

# Initialize weave with wandb API key
wandb_api_key = os.getenv("WANDB_API_KEY")
wandb_project = os.getenv("WANDB_PROJECT", "cairo-genizah-rag")

if wandb_api_key:
    os.environ["WANDB_API_KEY"] = wandb_api_key

weave.init(wandb_project)


class ChatMessage(BaseModel):
    """Individual chat message"""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Request for chat with RAG"""
    message: str = Field(..., min_length=1, max_length=2000, description="User's chat message")
    conversation_history: Optional[List[ChatMessage]] = Field(
        default=None, 
        description="Previous conversation messages for context.."
    )
    num_bibliography_results: int = Field(
        default=5, 
        ge=1, 
        le=20, 
        description="Number of bibliography results to retrieve for context"
    )
    model: str = Field(
        default="command-r:latest",
        description="Ollama model to use"
    )


class ChatResponse(BaseModel):
    """Response from chat"""
    message: str = Field(..., description="Assistant's response")
    bibliography_context: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Bibliography results used as context"
    )
    primary_sources: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Primary source documents retrieved from shelf marks mentioned in bibliography"
    )
    model_used: str = Field(..., description="Model that generated the response")


class OllamaRAGService:
    """Service for RAG-based chat using Ollama with bibliography search"""

    def __init__(self):
        self.ollama_base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.cf_authorization = os.getenv("CF_AUTHORIZATION")
        self.cf_client_id = os.getenv("CF-Access-Client-Id")
        self.cf_client_secret = os.getenv("CF-Access-Client-Secret")
        
        # Check if we're using a remote URL that might need CF auth
        is_remote = not any(host in self.ollama_base_url for host in ["localhost", "127.0.0.1"])
        has_cf_creds = all([self.cf_authorization, self.cf_client_id, self.cf_client_secret])
        
        if not is_remote:
            logger.info(f"Using local Ollama at {self.ollama_base_url}")
        elif is_remote and not has_cf_creds:
            logger.info(
                "Using remote Ollama endpoint without Cloudflare Access credentials. "
                "If authentication is required, set CF_AUTHORIZATION, CF-Access-Client-Id, "
                "and CF-Access-Client-Secret in .env"
            )

    def _needs_cf_auth(self) -> bool:
        """Check if Cloudflare authentication is needed"""
        # Only use CF auth for remote endpoints, not localhost
        is_remote = not any(host in self.ollama_base_url for host in ["localhost", "127.0.0.1"])
        has_cf_creds = all([self.cf_authorization, self.cf_client_id, self.cf_client_secret])
        return is_remote and has_cf_creds

    def _get_headers(self) -> Dict[str, str]:
        """Get Cloudflare Access headers for authentication (only if needed)"""
        if self._needs_cf_auth():
            return {
                "CF-Access-Client-Id": self.cf_client_id,
                "CF-Access-Client-Secret": self.cf_client_secret,
            }
        return {}

    def _get_cookies(self) -> Dict[str, str]:
        """Get Cloudflare Access cookies for authentication (only if needed)"""
        if self._needs_cf_auth() and self.cf_authorization:
            return {
                "CF_Authorization": self.cf_authorization
            }
        return {}

    @weave.op()
    async def _search_bibliography(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """Search bibliography for relevant context"""

        
        search_request = BibliographyHybridSearchRequest(
            query=query,
            semanticWeight=50,
            keywordWeight=50,
            num_results=num_results,
            page=1
        )
        
        search_response = await bibliography_search_service.search_hybrid(search_request)
        
        # Format results for context
        context_results = []
        for result in search_response.results:
            context_results.append({
                "doc_id": result.doc_id,
                "description": result.description,
                "full_text": result.full_text,
                "shelf_marks_mentioned": result.shelf_marks_mentioned,
                "author": result.author,
                "authors": result.authors,
                "title": result.title,
                "extracted_page_number": result.extracted_page_number,
                "subject_keywords": result.subject_keywords,
                "similarity_score": result.similarity_score
            })
        
        return context_results

    @weave.op()
    async def _fetch_primary_sources(self, shelf_marks: List[str], index_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch primary source documents for shelf marks mentioned in bibliography.
        Uses the shelf mark search endpoint to get the most relevant match for each shelf mark.
        """
        primary_sources = []
        
        for shelf_mark in shelf_marks:
            if not shelf_mark or not shelf_mark.strip():
                continue
                
            try:
                # Use shelf mark search to find the best matching document
                search_request = ShelfMarkSearchRequest(
                    shelf_mark=shelf_mark.strip(),
                    exact_match=False,  # Use liberal matching
                    num_results=1,  # Only get the best match
                    include_embeddings=False,  # Don't need embeddings for RAG context
                    index_name=index_name
                )
                
                search_response = await search_service.search_by_shelfmark(search_request, index_name)
                
                # Get the best match (first result)
                if search_response.results and len(search_response.results) > 0:
                    best_match = search_response.results[0]
                    similarity_score = best_match.similarity_score or 0
                    
                    # Verify it's a good match (similarity > 0.5 or shelf mark contained in doc)
                    doc_shelf_mark = (best_match.metadata.shelf_mark if best_match.metadata else None) or \
                                    (best_match.metadata.shelfmark if best_match.metadata else None) or \
                                    (best_match.metadata.classmark if best_match.metadata else None) or \
                                    best_match.doc_id or ''
                    
                    normalized_query = shelf_mark.strip().lower()
                    normalized_doc = doc_shelf_mark.strip().lower()
                    
                    has_match = (similarity_score > 0.5 or 
                                normalized_query in normalized_doc or
                                normalized_doc in normalized_query)
                    
                    if has_match:
                        # Format the document for primary sources
                        metadata = best_match.metadata
                        primary_sources.append({
                            "doc_id": best_match.doc_id,
                            "shelf_mark": shelf_mark,
                            "matched_shelf_mark": doc_shelf_mark,
                            "similarity_score": similarity_score,
                            "title": metadata.title if metadata else None,
                            "description": metadata.description if metadata else None,
                            "transcription_full_text": metadata.transcription_full_text if metadata else None,
                            "translation_full_text": metadata.translation_full_text if metadata else None,
                            "image_url": metadata.image_url if metadata else None,
                            "thumbnail_url": metadata.thumbnail_url if metadata else None,
                            "language": metadata.language if metadata else None,
                            "document_type": metadata.document_type if metadata else None,
                            "collection": metadata.collection if metadata else None,
                            "institution": metadata.institution if metadata else None
                        })
                        logger.info(f"Found primary source for shelf mark '{shelf_mark}': {best_match.doc_id} (score: {similarity_score})")
                    else:
                        logger.info(f"Shelf mark '{shelf_mark}' did not match well with document {best_match.doc_id} (score: {similarity_score})")
                else:
                    logger.info(f"No documents found for shelf mark '{shelf_mark}'")
                    
            except Exception as e:
                logger.error(f"Failed to fetch primary source for shelf mark '{shelf_mark}': {e}")
                continue
        
        return primary_sources

    @weave.op()
    def _build_rag_prompt(
        self, 
        user_message: str, 
        bibliography_context: List[Dict[str, Any]],
        conversation_history: Optional[List[ChatMessage]] = None
    ) -> List[Dict[str, Any]]:
        """Build RAG prompt with bibliography context"""
        
        # Build context section from bibliography results
        context_sections = []
        for i, bib in enumerate(bibliography_context, 1):
            # Get author(s) - prefer authors list, fall back to author string
            authors = bib.get("authors") or []
            if not authors and bib.get("author"):
                authors = [bib["author"]]
            author_str = ", ".join(authors) if authors else "Unknown author"
            
            # Get title
            title = bib.get("title") or "Untitled"
            
            # Get page number
            page_num = bib.get("extracted_page_number")
            page_str = f", p. {page_num}" if page_num else ""
            
            # Build citation header - this will be used as the reference label
            citation_header = f"{title} by {author_str}{page_str}"
            
            # Build reference content with citation header as the label
            context_parts = [f"Citation: {citation_header}"]
            
            if bib.get("full_text"):
                # Truncate full_text if too long
                full_text = bib['full_text']
                if len(full_text) > 500:
                    full_text = full_text[:500] + "..."
                context_parts.append(f"Text: {full_text}")
            
            if bib.get("description"):
                context_parts.append(f"Description: {bib['description']}")
            
            if bib.get("shelf_marks_mentioned"):
                shelfmarks = ", ".join(bib['shelf_marks_mentioned'][:5])  # Limit shelfmarks
                context_parts.append(f"Shelfmarks mentioned: {shelfmarks}")
            
            if bib.get("subject_keywords"):
                keywords = ", ".join(bib['subject_keywords'][:5])  # Limit keywords
                context_parts.append(f"Keywords: {keywords}")
            
            if context_parts:
                # Use the citation header as the reference label instead of "Reference {i}"
                context_sections.append(f"[{citation_header}]\n" + "\n".join(context_parts))
        
        context_block = "\n\n".join(context_sections) if context_sections else "No specific references found."
        
        # Build system prompt
        system_prompt = """You are Judaic Studies PhD AI Assistant specialized in the Cairo Genizah collection, a historical archive of more than 400,000 medieval Jewish manuscripts.

You have access to scholarly bibliography references about the Genizah collection. When answering questions, use the provided context from these references to give accurate, well-informed answers. 

IMPORTANT CITATION REQUIREMENTS:
- Always cite the full work using the title and author provided in the citation header
- Include page numbers when available for precise traceability
- When quoting directly, use the exact text from the source and cite it properly
- Format citations as: "[Title] by [Author], p. [page number]"
- If multiple authors, list them all
- Always make it clear which source you're referencing.

FORMATTING REQUIREMENTS:
- **Bold the source citation** using markdown (**text**) to make it stand out
- *Italicize direct quotes* using markdown (*text*) to distinguish them from your own words
- Always use this formatting pattern: **Source citation** followed by *direct quote*

Example citation format:
    - In **"A Mediterranean Society" by S.D. Goitein, p. 245**, it states: *"CUL Add 300 shows that there was substantial trade between..."*
    - As noted in **"A Table of New Moons from 1501 to 1577" by Bernard G. Goldstein, p. 15**: *"[quote text]"*
    - According to **"Title" by Author Name, p. 42**: *"The exact quoted text from the source should be in italics."*

     ALL ANSWERS MUST BE BASED ON THE RETURNED REFERENCES AND NOT GENERAL KNOWLEDGE. IF THE DOCUMENTS DO NOT ANSWER THE QUESTION, YOU MUST SAY SO AND EXPLAIN WHY." """
     
        # Build messages for Ollama
        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]
        
        # Add bibliography context as a system message
        if context_sections:
            messages.append({
                "role": "system",
                "content": f"""Bibliography Context for your response:

{context_block}

Use this context to answer the user's question about the Cairo Genizah collection. Always cite the full work (title, author, and page number when available) to ensure traceability and allow readers to look up the full work independently. Try to include direct quotes from the text as well where applicable."""
            })
        
        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history[-10:]:  # Keep last 10 messages for context
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages

    @weave.op()
    async def _call_ollama_api(self, messages: List[Dict[str, Any]], model: str) -> str:
        """Call Ollama API and return response"""
        ollama_url = f"{self.ollama_base_url}/api/chat"
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        logger.info(f"Calling Ollama API at {ollama_url} with model {model}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                ollama_url,
                headers=self._get_headers(),
                cookies=self._get_cookies(),
                json=payload
            )
            response.raise_for_status()
            result = response.json()
        
        assistant_message = result.get("message", {}).get("content", "")
        
        if not assistant_message:
            assistant_message = "I apologize, but I couldn't generate a response. Please try again."
        
        return assistant_message

    @weave.op()
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Perform RAG chat with Ollama"""
        # Step 1: Search bibliography for relevant context
        logger.info(f"Searching bibliography for query: {request.message[:100]}...")
        bibliography_context = await self._search_bibliography(
            request.message, 
            request.num_bibliography_results
        )
        
        # Step 2: Extract shelf marks from bibliography and fetch primary source documents
        all_shelf_marks = set()
        for bib in bibliography_context:
            if bib.get("shelf_marks_mentioned") and isinstance(bib["shelf_marks_mentioned"], list):
                for sm in bib["shelf_marks_mentioned"]:
                    if sm and sm.strip():
                        all_shelf_marks.add(sm.strip())
        
        primary_sources = []
        if all_shelf_marks:
            logger.info(f"Fetching primary sources for {len(all_shelf_marks)} shelf marks...")
            primary_sources = await self._fetch_primary_sources(list(all_shelf_marks))
            logger.info(f"Retrieved {len(primary_sources)} primary source documents")
        
        # Step 3: Build RAG prompt
        messages = self._build_rag_prompt(
            request.message,
            bibliography_context,
            request.conversation_history
        )
        
        # Step 4: Call Ollama API
        assistant_message = await self._call_ollama_api(messages, request.model)
        
        # Build response
        chat_response = ChatResponse(
            message=assistant_message,
            bibliography_context=bibliography_context if bibliography_context else None,
            primary_sources=primary_sources if primary_sources else None,
            model_used=request.model
        )
        
        return chat_response

    @weave.op()
    async def get_available_models(self) -> List[str]:
        """Get list of available Ollama models"""
        models_url = f"{self.ollama_base_url}/api/tags"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                models_url,
                headers=self._get_headers(),
                cookies=self._get_cookies()
            )
            response.raise_for_status()
            result = response.json()
        
        models = [model.get("name", "") for model in result.get("models", [])]
        return [m for m in models if m]  # Filter out empty names


# Global instance
ollama_rag_service = OllamaRAGService()

