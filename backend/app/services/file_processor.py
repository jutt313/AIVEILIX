import os
import hashlib
import logging
import base64
import io
from typing import List, Dict, Optional
import fitz  # PyMuPDF
from docx import Document
from openai import OpenAI
from PIL import Image
from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Initialize DeepSeek client (OpenAI-compatible) for chat
deepseek_client = None
if settings.deepseek_api_key:
    deepseek_client = OpenAI(
        api_key=settings.deepseek_api_key,
        base_url="https://api.deepseek.com/v1"
    )

# Initialize OpenAI client for embeddings and vision (highest quality)
openai_client = None
if settings.openai_api_key:
    openai_client = OpenAI(api_key=settings.openai_api_key)
    logger.info("OpenAI API configured for embeddings (text-embedding-3-large, 3072 dims) and vision")

# Embedding configuration
EMBEDDING_MODEL = "text-embedding-3-large"  # Best quality: 3072 dimensions
EMBEDDING_DIMENSIONS = 3072

# Image file extensions
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif'}


def is_image_file(file_path: str, mime_type: str) -> bool:
    """Check if file is an image"""
    file_ext = os.path.splitext(file_path)[1].lower()
    return (
        file_ext in IMAGE_EXTENSIONS or 
        mime_type.startswith('image/')
    )


def process_image_with_vision(file_path: str, filename: str = "") -> Dict:
    """
    Process image using GPT-4 Vision to extract text and describe content.
    
    Returns:
        Dict with extracted text and metadata
    """
    logger.info(f"🖼️  Processing image with GPT-4 Vision: {filename}")
    
    if not openai_client:
        logger.error("❌ OpenAI API not configured - image processing requires OpenAI API key")
        raise Exception("OpenAI API not configured - image processing requires OpenAI API key")
    
    try:
        # Read and encode image
        logger.debug(f"  📖 Reading image file: {file_path}")
        with open(file_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Determine image format from extension
        file_ext = os.path.splitext(file_path)[1].lower().replace('.', '')
        if file_ext == 'jpg':
            file_ext = 'jpeg'
        
        logger.info(f"  🤖 Calling GPT-4 Vision API for {filename}...")
        # Use GPT-4 Vision to analyze image
        response = openai_client.chat.completions.create(
            model="gpt-4o",  # or gpt-4-vision-preview
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""Analyze this image ({filename if filename else 'image'}) in detail. Extract ALL text you see (OCR) and describe the visual content.

Format your response as:

TEXT CONTENT:
[All text extracted from the image, if any]

VISUAL DESCRIPTION:
[Detailed description of what's in the image: objects, people, scenes, colors, layout, charts, diagrams, etc.]

KEY INFORMATION:
[Any important data, numbers, names, dates, or other notable information]"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{file_ext};base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )
        
        analysis = response.choices[0].message.content
        logger.info(f"  ✅ GPT-4 Vision analysis complete for {filename}")
        
        # Parse the response to extract text and description
        text_content = ""
        if "TEXT CONTENT:" in analysis:
            parts = analysis.split("VISUAL DESCRIPTION:")
            text_part = parts[0].replace("TEXT CONTENT:", "").strip()
            text_content = f"{text_part}\n\n{analysis}"
        else:
            text_content = analysis
        
        word_count = len(text_content.split())
        logger.debug(f"  📊 Extracted {word_count} words from image")
        
        return {
            "text": text_content,
            "metadata": {
                "type": "image",
                "word_count": word_count,
                "char_count": len(text_content),
                "vision_model": "gpt-4o"
            }
        }
    
    except Exception as e:
        logger.error(f"❌ Image processing failed for {filename}: {str(e)}", exc_info=True)
        raise Exception(f"Failed to process image: {str(e)}")


def extract_text_from_file(file_path: str, mime_type: str) -> Dict:
    """Extract text from various file types - handles text, PDFs, images, and more"""
    text = ""
    metadata = {}
    
    try:
        # Get file extension
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Handle IMAGE files with GPT-4 Vision
        if is_image_file(file_path, mime_type):
            logger.info(f"Processing image file with GPT-4 Vision: {file_path}")
            return process_image_with_vision(file_path, os.path.basename(file_path))
        
        # Handle PDF files with PyMuPDF (extracts text AND images)
        if mime_type == "application/pdf" or file_ext == ".pdf":
            logger.info(f"📄 Processing PDF with PyMuPDF: {file_path}")
            doc = fitz.open(file_path)
            text = ""
            images_processed = 0
            page_count = len(doc)
            
            for page_num in range(page_count):
                page = doc[page_num]
                
                # Extract text from page
                page_text = page.get_text()
                text += f"\n--- Page {page_num + 1} ---\n{page_text}"
                
                # Extract images from page
                image_list = page.get_images()
                if image_list:
                    logger.info(f"  🖼️  Found {len(image_list)} images on page {page_num + 1}")
                    
                    for img_index, img in enumerate(image_list):
                        try:
                            xref = img[0]
                            base_image = doc.extract_image(xref)
                            image_bytes = base_image["image"]
                            image_ext = base_image["ext"]
                            
                            # Save image temporarily
                            import tempfile
                            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{image_ext}') as temp_img:
                                temp_img.write(image_bytes)
                                temp_img_path = temp_img.name
                            
                            # Process image with Vision AI
                            logger.info(f"    🔍 Processing embedded image {img_index + 1} from page {page_num + 1}")
                            image_result = process_image_with_vision(temp_img_path, f"PDF_Page{page_num + 1}_Image{img_index + 1}")
                            
                            # Add image content to text
                            text += f"\n[IMAGE {img_index + 1} on Page {page_num + 1}]:\n{image_result['text']}\n"
                            images_processed += 1
                            
                            # Clean up temp file
                            os.unlink(temp_img_path)
                            
                        except Exception as e:
                            logger.warning(f"    ⚠️  Failed to process image {img_index + 1} on page {page_num + 1}: {str(e)}")
                            continue
            
            doc.close()
            metadata["page_count"] = page_count
            metadata["images_extracted"] = images_processed
            logger.info(f"  ✅ PDF processed: {page_count} pages, {images_processed} images extracted")
            
        # Handle Word documents
        elif mime_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"] or file_ext in [".doc", ".docx"]:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            metadata["page_count"] = len(doc.paragraphs) // 20  # Estimate
            
        # Handle CSV files
        elif mime_type == "text/csv" or file_ext == ".csv":
            import csv
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                text = "\n".join([", ".join(row) for row in rows])
                
        # Handle text-based code files and other text formats
        elif mime_type.startswith("text/") or file_ext in [
            ".txt", ".md", ".markdown", ".py", ".js", ".jsx", ".ts", ".tsx", 
            ".html", ".htm", ".css", ".json", ".xml", ".yaml", ".yml", ".sh", ".bash",
            ".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".java", ".go", ".rs", ".rb", ".php",
            ".swift", ".kt", ".scala", ".sql", ".r", ".m", ".pl", ".pm",
            ".lua", ".vim", ".conf", ".config", ".log", ".ini", ".toml",
            ".dockerfile", ".env", ".gitignore", ".readme", ".mdx", ".tex", ".rst",
            ".scss", ".sass", ".less", ".styl", ".vue", ".svelte",
            ".dart", ".elm", ".ex", ".exs", ".clj", ".cljs", ".hs", ".ml", ".fs",
            ".ps1", ".psm1", ".bat", ".cmd"
        ]:
            # Try multiple encodings for text files
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-16']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                        text = f.read()
                        break
                except (UnicodeDecodeError, UnicodeError):
                    continue
            
            if not text:
                raise Exception("File appears to be binary or uses unsupported encoding")
        
        # If no specific handler matched, try to read as text (generic fallback)
        else:
            # Try to read as text with multiple encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                        text = f.read()
                        
                        # Basic binary detection: check for null bytes or too many non-printable chars
                        if len(text) > 0:
                            null_bytes = text.count('\x00')
                            non_printable = sum(1 for c in text[:min(1000, len(text))] 
                                              if ord(c) < 32 and c not in '\n\r\t\f\v')
                            
                            # If more than 5% null bytes or 10% non-printable, likely binary
                            if null_bytes > len(text) * 0.05 or non_printable > len(text[:min(1000, len(text))]) * 0.1:
                                text = ""
                                continue
                        break
                except (UnicodeDecodeError, UnicodeError):
                    continue
            
            if not text:
                # Binary file - can't extract text
                raise Exception(f"File type '{mime_type}' ({file_ext}) appears to be binary and cannot be processed as text. Please upload a text-based file.")
                
        metadata["word_count"] = len(text.split()) if text else 0
        metadata["char_count"] = len(text) if text else 0
        
    except Exception as e:
        raise Exception(f"Failed to extract text: {str(e)}")
    
    return {"text": text, "metadata": metadata}


def chunk_text(text: str, chunk_size: int = 150, overlap: int = 50) -> List[Dict]:
    """
    Split text into overlapping chunks for maximum precision semantic search.
    
    Default: 150 words per chunk with 50-word overlap for high-quality retrieval.
    """
    if not text or len(text.strip()) == 0:
        return []
    
    words = text.split()
    chunks = []
    
    i = 0
    chunk_index = 0
    while i < len(words):
        chunk_words = words[i:i + chunk_size]
        chunk_content = " ".join(chunk_words)
        
        chunks.append({
            "content": chunk_content,
            "chunk_index": chunk_index,
            "start_offset": i,
            "end_offset": min(i + chunk_size, len(words)),
            "token_count": len(chunk_words)
        })
        
        i += chunk_size - overlap
        chunk_index += 1
        
    return chunks


def generate_embedding(text: str) -> Optional[List[float]]:
    """
    Generate embedding using OpenAI text-embedding-3-large model (BEST QUALITY).
    
    Args:
        text: Text to generate embedding for (max ~8000 tokens)
    
    Returns:
        List of 3072 floats (embedding vector) or None if failed
    """
    if not openai_client:
        logger.warning("OpenAI API not configured - embeddings disabled")
        return None
    
    if not text or len(text.strip()) == 0:
        return None
    
    try:
        # Truncate text if too long (OpenAI limit is ~8000 tokens)
        # Approximate: 4 chars per token = ~32000 chars max
        truncated_text = text[:30000] if len(text) > 30000 else text
        
        # Use text-embedding-3-large model (3072 dimensions - HIGHEST QUALITY)
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=truncated_text,
            dimensions=EMBEDDING_DIMENSIONS
        )
        
        embedding = response.data[0].embedding
        logger.debug(f"Generated embedding with {len(embedding)} dimensions (OpenAI {EMBEDDING_MODEL})")
        return embedding
    
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        return None


def generate_embeddings_batch(texts: List[str]) -> List[Optional[List[float]]]:
    """
    Generate embeddings for multiple texts in a single API call (much faster).
    
    Args:
        texts: List of texts to generate embeddings for
    
    Returns:
        List of embedding vectors (or None for failed items)
    """
    if not openai_client:
        logger.warning("⚠️  OpenAI API not configured - embeddings disabled")
        return [None] * len(texts)
    
    if not texts:
        return []
    
    try:
        # Filter out empty texts and track their indices
        valid_texts = []
        valid_indices = []
        for i, text in enumerate(texts):
            if text and len(text.strip()) > 0:
                # Truncate if needed
                truncated = text[:30000] if len(text) > 30000 else text
                valid_texts.append(truncated)
                valid_indices.append(i)
        
        if not valid_texts:
            return [None] * len(texts)
        
        logger.info(f"🔢 Generating {len(valid_texts)} embeddings in batch...")
        
        # Batch request to OpenAI (up to 2048 inputs per request)
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=valid_texts,
            dimensions=EMBEDDING_DIMENSIONS
        )
        
        # Map results back to original indices
        results = [None] * len(texts)
        for i, embedding_obj in enumerate(response.data):
            original_idx = valid_indices[i]
            results[original_idx] = embedding_obj.embedding
        
        logger.info(f"✅ Generated {len(valid_texts)} embeddings successfully")
        return results
    
    except Exception as e:
        logger.error(f"❌ Batch embedding generation failed: {e}", exc_info=True)
        return [None] * len(texts)


def generate_query_embedding(query: str) -> Optional[List[float]]:
    """
    Generate embedding for a search query using OpenAI text-embedding-3-large.
    
    Args:
        query: Search query text
    
    Returns:
        List of 3072 floats (embedding vector) or None if failed
    """
    if not openai_client:
        logger.warning("OpenAI API not configured - embeddings disabled")
        return None
    
    if not query or len(query.strip()) == 0:
        return None

    try:
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=query,
            dimensions=EMBEDDING_DIMENSIONS
        )
        
        embedding = response.data[0].embedding
        return embedding
    
    except Exception as e:
        logger.error(f"Query embedding generation failed: {e}")
        return None


def analyze_file_comprehensive(text: str, filename: str = "") -> Dict:
    """Generate comprehensive detailed analysis of file content - creates detailed analysis document"""
    try:
        if not deepseek_client:
            return {
                "summary": "Analysis unavailable - API not configured.",
                "model_used": None,
                "error": "API key not configured"
            }
        
        if not text or len(text.strip()) == 0:
            return {
                "summary": "No text content to analyze.",
                "model_used": None
            }
        
        # Use more content for detailed analysis (up to 8000 chars for better context)
        analysis_text = text[:8000] if len(text) > 8000 else text
        file_hint = f" ({filename})" if filename else ""
        
        prompt = f"""Analyze the following document in comprehensive detail. Extract all important information.

Document{file_hint}:
{analysis_text}

Provide a detailed analysis including:
1. Main purpose and topic (3-5 sentences covering what this document is about and why it exists)
2. Key concepts, topics, or themes discussed (list main topics)
3. Important facts, data, or information extracted (notable details worth remembering)
4. Document structure/type (code, documentation, data file, configuration, etc.)
5. Any notable patterns, functions, relationships, or important details

Format as a clear, structured analysis that fully explains what this document contains, its purpose, and key information. This analysis will be used by an AI to understand and answer questions about this file."""

        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500  # More tokens for detailed analysis
        )
        
        detailed_analysis = response.choices[0].message.content
        
        return {
            "summary": detailed_analysis,
            "model_used": "deepseek-chat"
        }
    except Exception as e:
        return {
            "summary": f"Comprehensive analysis generation failed: {str(e)}",
            "model_used": None,
            "error": str(e)
        }


def generate_summary(text: str, filename: str = "", model_name: str = "deepseek-chat") -> Dict:
    """Generate file summary - uses comprehensive analysis for detailed summaries"""
    # Use comprehensive analysis for better summaries
    result = analyze_file_comprehensive(text, filename)
    return {
        "summary": result.get("summary", "Summary generation failed."),
        "model_used": result.get("model_used", model_name),
        "error": result.get("error")
    }


def fetch_full_file_content(storage_path: str, supabase) -> str:
    """
    Fetch and extract complete content from original file in Supabase Storage.
    
    Args:
        storage_path: Path to file in Supabase Storage (e.g., 'user_id/bucket_id/filename')
        supabase: Supabase client instance
    
    Returns:
        str: Full extracted text content from the original file
    """
    logger.info(f"📥 Fetching full file from storage: {storage_path}")
    
    try:
        import tempfile
        
        # Download file from Supabase Storage
        logger.debug(f"  🔽 Downloading from storage...")
        file_data = supabase.storage.from_("files").download(storage_path)
        
        if not file_data:
            logger.error(f"❌ File not found in storage: {storage_path}")
            return ""
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(storage_path)[1]) as temp_file:
            temp_file.write(file_data)
            temp_path = temp_file.name
        
        logger.debug(f"  📄 Saved to temp: {temp_path}")
        
        # Detect MIME type from extension
        file_ext = os.path.splitext(storage_path)[1].lower()
        mime_type_map = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.csv': 'text/csv',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp'
        }
        mime_type = mime_type_map.get(file_ext, 'application/octet-stream')
        
        # Extract text using existing function
        logger.info(f"  🔍 Extracting text (MIME: {mime_type})...")
        text_data = extract_text_from_file(temp_path, mime_type)
        full_text = text_data["text"]
        
        # Clean up temp file
        os.unlink(temp_path)
        
        logger.info(f"  ✅ Full file content extracted: {len(full_text)} chars")
        return full_text
        
    except Exception as e:
        logger.error(f"❌ Error fetching full file: {str(e)}")
        return ""
