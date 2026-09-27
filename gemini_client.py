"""
Gemini API integration for medical report analysis.
Uses google-genai SDK (REST-based, no gRPC dependency).
"""

from google import genai
from google.genai import types
from PIL import Image
import io

from prompts import SYSTEM_INSTRUCTION, ANALYSIS_PROMPT, IMAGE_ANALYSIS_PROMPT

_client: genai.Client | None = None


def configure_gemini(api_key: str) -> None:
    """Configure the Gemini client with the provided API key."""
    global _client
    _client = genai.Client(api_key=api_key)


def _get_client() -> genai.Client:
    if _client is None:
        raise RuntimeError("Gemini client not configured. Call configure_gemini() first.")
    return _client


def analyze_report_from_text(text: str) -> str:
    """
    Send extracted text to Gemini and return the patient-friendly summary.
    """
    client = _get_client()
    prompt = ANALYSIS_PROMPT.format(report_text=text)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.3,
            max_output_tokens=4096,
        ),
    )
    return response.text


def analyze_report_from_images(images: list[Image.Image]) -> str:
    """
    Send page images to Gemini Vision and return the patient-friendly summary.
    Used as fallback when text extraction yields little/no content (scanned PDFs).
    """
    client = _get_client()

    # Build content parts: images first, then the prompt text
    parts = []
    for img in images[:5]:  # cap at 5 pages to stay within token limits
        # Convert PIL Image to bytes
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        image_bytes = buf.getvalue()
        parts.append(
            types.Part.from_bytes(data=image_bytes, mime_type="image/png")
        )
    parts.append(types.Part.from_text(text=IMAGE_ANALYSIS_PROMPT))

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=types.Content(role="user", parts=parts),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.3,
            max_output_tokens=4096,
        ),
    )
    return response.text


def analyze_report(text: str, images: list[Image.Image], file_type: str) -> str:
    """
    Smart dispatcher: uses text if substantial, falls back to vision for images/scans.

    Args:
        text:      Extracted text from the document (may be empty for scanned docs).
        images:    List of PIL images (PDF pages or uploaded images).
        file_type: Label like "PDF", "DOCX", "TXT", "Image".

    Returns:
        Formatted markdown string from Gemini.
    """
    # If text is rich enough, prefer text-based analysis (faster, cheaper)
    if text and len(text.strip()) > 100:
        return analyze_report_from_text(text)

    # For image files or scanned PDFs with no extractable text
    if images:
        return analyze_report_from_images(images)

    # Edge case: no text and no images
    raise ValueError("No readable content found in the uploaded file.")
