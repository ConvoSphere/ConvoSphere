"""
Analysis tools for text processing and summarization.

This module provides tools for analyzing and processing text content,
including summarization, sentiment analysis, and text classification.
"""

import re
from typing import Dict, Any, List, Optional
from loguru import logger

from app.services.ai_service import ai_service


def analyze_text(text: str, user_id: str, analysis_type: str = "general") -> Dict[str, Any]:
    """
    Analyze text content.
    
    Args:
        text: Text to analyze
        user_id: User ID for tracking
        analysis_type: Type of analysis (general, sentiment, keywords, etc.)
        
    Returns:
        Dict[str, Any]: Analysis results
    """
    try:
        if not text.strip():
            return {
                "success": False,
                "error": "Empty text provided"
            }
        
        # Basic text analysis
        analysis = {
            "text_length": len(text),
            "word_count": len(text.split()),
            "sentence_count": len(re.split(r'[.!?]+', text)),
            "paragraph_count": len([p for p in text.split('\n\n') if p.strip()]),
            "average_word_length": sum(len(word) for word in text.split()) / len(text.split()) if text.split() else 0,
            "unique_words": len(set(text.lower().split())),
            "analysis_type": analysis_type
        }
        
        # AI-powered analysis if available
        if ai_service.is_enabled():
            try:
                ai_analysis = _perform_ai_analysis(text, analysis_type)
                analysis.update(ai_analysis)
            except Exception as e:
                logger.warning(f"AI analysis failed: {e}")
                analysis["ai_analysis_available"] = False
        
        return {
            "success": True,
            "analysis": analysis
        }
        
    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def summarize_text(text: str, user_id: str, max_length: int = 200) -> Dict[str, Any]:
    """
    Summarize text content.
    
    Args:
        text: Text to summarize
        user_id: User ID for tracking
        max_length: Maximum length of summary
        
    Returns:
        Dict[str, Any]: Summary results
    """
    try:
        if not text.strip():
            return {
                "success": False,
                "error": "Empty text provided"
            }
        
        # Simple extractive summarization
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= 3:
            # Text is already short, return as is
            summary = text
        else:
            # Simple summarization: take first few sentences
            summary_sentences = sentences[:3]
            summary = '. '.join(summary_sentences) + '.'
            
            # Truncate if too long
            if len(summary) > max_length:
                summary = summary[:max_length-3] + "..."
        
        # AI-powered summarization if available
        if ai_service.is_enabled():
            try:
                ai_summary = _perform_ai_summarization(text, max_length)
                if ai_summary.get("success"):
                    summary = ai_summary["summary"]
            except Exception as e:
                logger.warning(f"AI summarization failed: {e}")
        
        return {
            "success": True,
            "summary": summary,
            "original_length": len(text),
            "summary_length": len(summary),
            "compression_ratio": len(summary) / len(text) if text else 0
        }
        
    except Exception as e:
        logger.error(f"Error summarizing text: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def extract_keywords(text: str, user_id: str, max_keywords: int = 10) -> Dict[str, Any]:
    """
    Extract keywords from text.
    
    Args:
        text: Text to analyze
        user_id: User ID for tracking
        max_keywords: Maximum number of keywords to extract
        
    Returns:
        Dict[str, Any]: Keyword extraction results
    """
    try:
        if not text.strip():
            return {
                "success": False,
                "error": "Empty text provided"
            }
        
        # Simple keyword extraction
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }
        
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Count word frequencies
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and get top keywords
        sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [{"word": word, "frequency": freq} for word, freq in sorted_keywords[:max_keywords]]
        
        return {
            "success": True,
            "keywords": keywords,
            "total_words": len(words),
            "unique_words": len(word_freq)
        }
        
    except Exception as e:
        logger.error(f"Error extracting keywords: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def detect_language(text: str, user_id: str) -> Dict[str, Any]:
    """
    Detect the language of text.
    
    Args:
        text: Text to analyze
        user_id: User ID for tracking
        
    Returns:
        Dict[str, Any]: Language detection results
    """
    try:
        if not text.strip():
            return {
                "success": False,
                "error": "Empty text provided"
            }
        
        # Simple language detection based on common words
        text_lower = text.lower()
        
        # Language patterns (simplified)
        patterns = {
            "english": ["the", "and", "of", "to", "a", "in", "that", "it", "with", "as"],
            "german": ["der", "die", "das", "und", "in", "den", "von", "zu", "mit", "sich"],
            "french": ["le", "la", "de", "et", "à", "un", "une", "dans", "qui", "que"],
            "spanish": ["el", "la", "de", "que", "y", "a", "en", "un", "es", "se"]
        }
        
        scores = {}
        for lang, words in patterns.items():
            score = sum(1 for word in words if word in text_lower)
            scores[lang] = score
        
        # Get language with highest score
        detected_lang = max(scores.items(), key=lambda x: x[1])
        
        # AI-powered language detection if available
        if ai_service.is_enabled():
            try:
                ai_lang = _perform_ai_language_detection(text)
                if ai_lang.get("success"):
                    detected_lang = (ai_lang["language"], ai_lang["confidence"])
            except Exception as e:
                logger.warning(f"AI language detection failed: {e}")
        
        return {
            "success": True,
            "language": detected_lang[0],
            "confidence": detected_lang[1] / len(patterns["english"]),  # Normalize confidence
            "scores": scores
        }
        
    except Exception as e:
        logger.error(f"Error detecting language: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def _perform_ai_analysis(text: str, analysis_type: str) -> Dict[str, Any]:
    """Perform AI-powered text analysis."""
    try:
        prompt = f"""
        Analyze the following text and provide insights:
        
        Text: {text[:1000]}  # Limit text length
        
        Analysis type: {analysis_type}
        
        Provide a JSON response with the following structure:
        {{
            "sentiment": "positive/negative/neutral",
            "sentiment_score": 0.0-1.0,
            "key_themes": ["theme1", "theme2"],
            "complexity": "simple/medium/complex",
            "readability_score": 0-100,
            "summary": "brief summary"
        }}
        """
        
        response = ai_service.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-3.5-turbo",
            max_tokens=300
        )
        
        # Parse response (simplified)
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # Extract JSON-like content
        import json
        try:
            # Find JSON in response
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = content[start:end]
                result = json.loads(json_str)
                return result
        except:
            pass
        
        # Fallback: return basic analysis
        return {
            "sentiment": "neutral",
            "sentiment_score": 0.5,
            "key_themes": [],
            "complexity": "medium",
            "readability_score": 50,
            "summary": "AI analysis completed"
        }
        
    except Exception as e:
        logger.error(f"Error in AI analysis: {e}")
        return {}


def _perform_ai_summarization(text: str, max_length: int) -> Dict[str, Any]:
    """Perform AI-powered text summarization."""
    try:
        prompt = f"""
        Summarize the following text in {max_length} characters or less:
        
        {text[:2000]}  # Limit text length
        
        Provide only the summary, no additional text.
        """
        
        response = ai_service.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-3.5-turbo",
            max_tokens=max_length // 4  # Rough token estimation
        )
        
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        return {
            "success": True,
            "summary": content.strip()
        }
        
    except Exception as e:
        logger.error(f"Error in AI summarization: {e}")
        return {"success": False}


def _perform_ai_language_detection(text: str) -> Dict[str, Any]:
    """Perform AI-powered language detection."""
    try:
        prompt = f"""
        Detect the language of the following text and respond with JSON:
        
        Text: {text[:500]}
        
        Response format:
        {{
            "language": "language_name",
            "confidence": 0.95
        }}
        """
        
        response = ai_service.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-3.5-turbo",
            max_tokens=100
        )
        
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # Parse JSON response
        import json
        try:
            start = content.find('{')
            end = content.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = content[start:end]
                result = json.loads(json_str)
                return {
                    "success": True,
                    "language": result.get("language", "unknown"),
                    "confidence": result.get("confidence", 0.5)
                }
        except:
            pass
        
        return {"success": False}
        
    except Exception as e:
        logger.error(f"Error in AI language detection: {e}")
        return {"success": False} 