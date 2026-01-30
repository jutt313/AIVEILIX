#!/usr/bin/env python3
"""
Quick test script to verify the new AI-driven citation system helper functions
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.routers.chat import build_source_inventory, parse_ai_response_with_citations


def test_build_source_inventory():
    """Test source inventory builder"""
    print("Testing build_source_inventory()...")

    # Mock data
    all_files = {
        "file-123": {"name": "test.pdf"},
        "file-456": {"name": "report.docx"}
    }

    summaries_by_file = {
        "file-123": {"id": "sum-1", "content": "Test summary"}
    }

    chunks_by_file = {
        "file-123": [
            {"id": "chunk-1", "content": "First chunk"},
            {"id": "chunk-2", "content": "Second chunk"}
        ]
    }

    web_results = [
        {"title": "Example Result", "link": "https://example.com", "snippet": "Test snippet"}
    ]

    # Build inventory
    inventory = build_source_inventory(all_files, summaries_by_file, chunks_by_file, web_results)

    print("\nGenerated Sources:")
    for source_id, metadata in inventory["sources"].items():
        print(f"  - {source_id}: {metadata}")

    print("\nInventory Text:")
    print(inventory["inventory_text"])

    # Assertions
    assert "analysis_file-123" in inventory["sources"]
    assert "chunk_chunk-1" in inventory["sources"]
    assert "chunk_chunk-2" in inventory["sources"]
    assert "web_0" in inventory["sources"]

    print("\n✅ build_source_inventory() test passed!")


def test_parse_ai_response_valid_json():
    """Test parsing valid JSON response"""
    print("\nTesting parse_ai_response_with_citations() with valid JSON...")

    source_inventory = {
        "sources": {
            "analysis_file-123": {"file_name": "test.pdf", "type": "analysis", "summary_id": "sum-1"},
            "chunk_chunk-1": {"file_name": "test.pdf", "type": "chunk", "chunk_id": "chunk-1"},
            "web_0": {"type": "web_search", "title": "Example", "url": "https://example.com"}
        }
    }

    # Valid JSON response
    ai_response = '''{
  "message": "Based on test.pdf, the answer is 42.",
  "cited_sources": [
    {"id": "analysis_file-123"},
    {"id": "web_0"}
  ]
}'''

    message, sources = parse_ai_response_with_citations(ai_response, source_inventory)

    print(f"\nExtracted Message: {message}")
    print(f"Extracted Sources: {sources}")

    # Assertions
    assert message == "Based on test.pdf, the answer is 42."
    assert len(sources) == 2
    assert sources[0]["file_name"] == "test.pdf"
    assert sources[1]["type"] == "web_search"

    print("\n✅ Valid JSON parsing test passed!")


def test_parse_ai_response_invalid_source():
    """Test parsing with invalid source ID"""
    print("\nTesting parse_ai_response_with_citations() with invalid source ID...")

    source_inventory = {
        "sources": {
            "analysis_file-123": {"file_name": "test.pdf", "type": "analysis"}
        }
    }

    # JSON with invalid source ID
    ai_response = '''{
  "message": "Answer here",
  "cited_sources": [
    {"id": "analysis_file-123"},
    {"id": "invalid_source_xyz"}
  ]
}'''

    message, sources = parse_ai_response_with_citations(ai_response, source_inventory)

    print(f"\nExtracted Message: {message}")
    print(f"Extracted Sources: {sources}")

    # Should only include valid source
    assert len(sources) == 1
    assert sources[0]["file_name"] == "test.pdf"

    print("\n✅ Invalid source ID handling test passed!")


def test_parse_ai_response_fallback():
    """Test fallback when JSON parsing fails"""
    print("\nTesting parse_ai_response_with_citations() fallback...")

    source_inventory = {"sources": {}}

    # Invalid JSON (missing closing brace)
    ai_response = "This is a plain text response without JSON"

    message, sources = parse_ai_response_with_citations(ai_response, source_inventory)

    print(f"\nExtracted Message: {message}")
    print(f"Extracted Sources: {sources}")

    # Should return full response and empty sources
    assert message == ai_response
    assert len(sources) == 0

    print("\n✅ Fallback test passed!")


def test_parse_ai_response_empty_citations():
    """Test parsing with empty citations array"""
    print("\nTesting parse_ai_response_with_citations() with empty citations...")

    source_inventory = {
        "sources": {
            "analysis_file-123": {"file_name": "test.pdf", "type": "analysis"}
        }
    }

    # Valid JSON but no citations
    ai_response = '''{
  "message": "This is general knowledge, no sources needed.",
  "cited_sources": []
}'''

    message, sources = parse_ai_response_with_citations(ai_response, source_inventory)

    print(f"\nExtracted Message: {message}")
    print(f"Extracted Sources: {sources}")

    # Should have message but no sources
    assert message == "This is general knowledge, no sources needed."
    assert len(sources) == 0

    print("\n✅ Empty citations test passed!")


if __name__ == "__main__":
    print("=" * 60)
    print("AI-DRIVEN CITATION SYSTEM - UNIT TESTS")
    print("=" * 60)

    try:
        test_build_source_inventory()
        test_parse_ai_response_valid_json()
        test_parse_ai_response_invalid_source()
        test_parse_ai_response_fallback()
        test_parse_ai_response_empty_citations()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✅")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
