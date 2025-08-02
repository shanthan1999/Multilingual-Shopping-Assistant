import os
import requests
import json
import re
from typing import List, Dict, Optional
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class HindiShoppingSearch:
    """
    Enhanced shopping search service with Hindi to English translation
    Inspired by Zepto's multilingual query correction approach
    """
    
    def __init__(self):
        self.serper_api_key = os.getenv('SERPER_API_KEY')
        
        # Check if we have a valid API key
        self.has_api_key = bool(self.serper_api_key and self.serper_api_key != 'your_serper_api_key_here')
        
        if not self.has_api_key:
            print("Warning: SERPER_API_KEY not found. Web search features will be limited.")
        
        # Common Hindi to English mappings for shopping terms
        self.hindi_english_mappings = {
            # Vegetables and fruits
            'tamatar': 'tomato',
            'pyaaz': 'onion',
            'aloo': 'potato',
            'gajar': 'carrot',
            'baingan': 'eggplant',
            'kheera': 'cucumber',
            'palak': 'spinach',
            'methi': 'fenugreek',
                         'kothimbir': 'coriander',
             'pudina': 'mint',
             'dhaniya': 'coriander',
             'dhania': 'coriander',
            
            # Dairy and groceries
            'doodh': 'milk',
            'paneer': 'cottage cheese',
            'ghee': 'clarified butter',
            'atta': 'wheat flour',
            'chawal': 'rice',
            'daal': 'lentils',
            'chai': 'tea',
            'coffee': 'coffee',
            
            # Electronics
            'mobile': 'mobile phone',
            'laptop': 'laptop',
            'computer': 'computer',
            'headphone': 'headphones',
            'charger': 'mobile charger',
            
            # Clothing
            'kapda': 'clothes',
            'shirt': 'shirt',
            'pant': 'pants',
            'shoes': 'shoes',
            'bag': 'bag',
            
            # Common misspellings and phonetic variations
            'tamatar': 'tomato',
            'tamatar': 'tomato',
            'pyaaz': 'onion',
            'pyaz': 'onion',
            'aloo': 'potato',
            'alu': 'potato',
            'gajar': 'carrot',
            'gajjar': 'carrot',
            'baingan': 'eggplant',
            'brinjal': 'eggplant',
            'kheera': 'cucumber',
            'khira': 'cucumber',
            'palak': 'spinach',
            'methi': 'fenugreek',
                         'kothimbir': 'coriander',
             'kothmir': 'coriander',
             'pudina': 'mint',
             'dhaniya': 'coriander',
             'dhania': 'coriander',
            'doodh': 'milk',
            'dudh': 'milk',
            'paneer': 'cottage cheese',
            'ghee': 'clarified butter',
            'atta': 'wheat flour',
            'chawal': 'rice',
            'chaval': 'rice',
            'daal': 'lentils',
            'dal': 'lentils',
            'chai': 'tea',
            'coffee': 'coffee',
            'mobile': 'mobile phone',
            'laptop': 'laptop',
            'computer': 'computer',
            'headphone': 'headphones',
            'charger': 'mobile charger',
            'kapda': 'clothes',
            'shirt': 'shirt',
            'pant': 'pants',
            'shoes': 'shoes',
            'bag': 'bag'
        }
        
        # Brand names to preserve (don't translate)
        self.brand_names = {
            'amul', 'nirma', 'surf', 'rin', 'wheel', 'ariel', 'tide',
            'colgate', 'closeup', 'pepsodent', 'samsung', 'apple', 'nokia',
            'micromax', 'lava', 'karbonn', 'intex', 'panasonic', 'lg',
            'sony', 'philips', 'whirlpool', 'godrej', 'bajaj', 'usha',
            'prestige', 'butterfly', 'havells', 'anchor', 'finolex'
        }
    
    def detect_hindi_query(self, query: str) -> bool:
        """
        Detect if query contains Hindi words or transliterated Hindi
        """
        # Check for common Hindi words in English script
        hindi_indicators = [
            'kya', 'kaise', 'kahan', 'kab', 'kaun', 'kya', 'hai', 'ho',
            'main', 'aap', 'tum', 'hum', 'wo', 'ye', 'us', 'is', 'un',
            'in', 'ka', 'ki', 'ke', 'kaa', 'kii', 'kee', 'se', 'me',
            'par', 'pe', 'ko', 'ke', 'ka', 'ki', 'kya', 'kahan', 'kab'
        ]
        
        query_lower = query.lower()
        for indicator in hindi_indicators:
            if indicator in query_lower:
                return True
        
        # Check for transliterated Hindi words
        for hindi_word in self.hindi_english_mappings.keys():
            if hindi_word in query_lower:
                return True
        
        return False
    
    def translate_hindi_to_english(self, query: str) -> str:
        """
        Translate Hindi query to English for better search results
        """
        query_lower = query.lower()
        translated_query = query
        
        # Replace Hindi words with English equivalents
        for hindi_word, english_word in self.hindi_english_mappings.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(hindi_word) + r'\b'
            translated_query = re.sub(pattern, english_word, translated_query, flags=re.IGNORECASE)
        
        # Handle common Hindi phrases
        hindi_phrases = {
            'kya chahiye': 'what do you want',
            'kya hai': 'what is',
            'kahan hai': 'where is',
            'kitne ka': 'how much',
            'kaise hai': 'how is',
            'acha hai': 'good',
            'bura hai': 'bad',
            'mehenga': 'expensive',
            'sasta': 'cheap',
            'accha': 'good',
            'bura': 'bad'
        }
        
        for hindi_phrase, english_phrase in hindi_phrases.items():
            if hindi_phrase in query_lower:
                translated_query = translated_query.replace(hindi_phrase, english_phrase)
        
        return translated_query.strip()
    
    def enhance_search_query(self, query: str) -> str:
        """
        Enhance search query with shopping context
        """
        # Add shopping context if not present
        shopping_keywords = ['buy', 'purchase', 'shop', 'order', 'online', 'store', 'price']
        query_lower = query.lower()
        
        has_shopping_context = any(keyword in query_lower for keyword in shopping_keywords)
        
        if not has_shopping_context:
            # Add shopping context
            enhanced_query = f"{query} buy online price"
        else:
            enhanced_query = query
        
        return enhanced_query
    
    def search_products(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for products with Hindi to English translation
        """
        try:
            # Detect if query is in Hindi
            is_hindi = self.detect_hindi_query(query)
            
            if is_hindi:
                # Translate Hindi to English
                translated_query = self.translate_hindi_to_english(query)
                st.info(f"🔍 Translated query: '{query}' → '{translated_query}'")
                query = translated_query
            
            # Enhance query with shopping context
            enhanced_query = self.enhance_search_query(query)
            
            # Check if we have API access
            if not self.has_api_key:
                # Return demo data when API key is not available
                return self._get_demo_products(query, limit)
            
            # Search using Serper
            search_results = self._serper_search(enhanced_query, limit)
            
            # Process and format results
            formatted_results = self._format_results(search_results, original_query=query)
            
            return formatted_results
            
        except Exception as e:
            # Return demo data as fallback
            return self._get_demo_products(query, limit)
    
    def _get_demo_products(self, query: str, limit: int) -> List[Dict]:
        """Generate demo products for demonstration purposes"""
        demo_products = [
            {
                'title': f"Demo {query.title()} Product 1",
                'description': f"This is a demo product for {query}. It's a great product for demonstration purposes.",
                'url': 'https://example.com/product1',
                'source': 'Demo Store',
                'price': '₹299',
                'score': 8.5
            },
            {
                'title': f"Demo {query.title()} Product 2",
                'description': f"Another demo product for {query}. Perfect for testing the application.",
                'url': 'https://example.com/product2',
                'source': 'Demo Mart',
                'price': '₹199',
                'score': 7.8
            },
            {
                'title': f"Demo {query.title()} Product 3",
                'description': f"Third demo product for {query}. Shows how the app works.",
                'url': 'https://example.com/product3',
                'source': 'Demo Shop',
                'price': '₹399',
                'score': 8.2
            }
        ]
        return demo_products[:limit]
    
    def _serper_search(self, query: str, limit: int) -> List[Dict]:
        """
        Perform search using Serper API (Google Search)
        """
        url = "https://google.serper.dev/search"
        
        headers = {
            "X-API-KEY": self.serper_api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": query,
            "num": limit,
            "gl": "in",  # India
            "hl": "en"   # English
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('organic', [])
        else:
            raise Exception(f"Serper API error: {response.status_code} - {response.text}")
    
    def _format_results(self, results: List[Dict], original_query: str) -> List[Dict]:
        """
        Format search results for display
        """
        formatted_results = []
        
        for result in results:
            formatted_result = {
                'title': result.get('title', 'Product'),
                'description': result.get('snippet', 'No description available'),
                'url': result.get('link', ''),
                'source': self._extract_domain(result.get('link', '')),
                'price': self._extract_price(result.get('snippet', '')),
                'score': self._calculate_relevance_score(result, original_query)
            }
            formatted_results.append(formatted_result)
        
        # Sort by relevance score
        formatted_results.sort(key=lambda x: x['score'], reverse=True)
        
        return formatted_results
    
    def _extract_price(self, content: str) -> str:
        """
        Extract price information from content
        """
        # Look for price patterns
        price_patterns = [
            r'₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'Rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'INR\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'\$(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:rupees?|rs)'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                price = match.group(1)
                return f"₹{price}"
        
        return "Price not available"
    
    def _calculate_relevance_score(self, result: Dict, query: str) -> float:
        """
        Calculate relevance score for search results
        """
        score = 0.0
        query_lower = query.lower()
        title_lower = result.get('title', '').lower()
        content_lower = result.get('content', '').lower()
        
        # Title relevance
        if query_lower in title_lower:
            score += 5.0
        
        # Content relevance
        if query_lower in content_lower:
            score += 2.0
        
        # Source relevance (prefer shopping sites)
        source = result.get('source', '').lower()
        shopping_sites = ['amazon', 'flipkart', 'myntra', 'snapdeal', 'paytmmall', 'bigbasket', 'zepto', 'blinkit']
        if any(site in source for site in shopping_sites):
            score += 3.0
        
        return min(score, 10.0)  # Cap at 10
    
    def _extract_domain(self, url: str) -> str:
        """
        Extract domain name from URL
        """
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception:
            return "Unknown Store"
    
    def get_search_suggestions(self, partial_query: str) -> List[str]:
        """
        Get search suggestions based on partial Hindi/English query
        """
        suggestions = []
        partial_lower = partial_query.lower()
        
        # Add Hindi suggestions
        for hindi_word, english_word in self.hindi_english_mappings.items():
            if hindi_word.startswith(partial_lower) or english_word.startswith(partial_lower):
                suggestions.append(f"{hindi_word} ({english_word})")
        
        # Add common shopping queries
        common_queries = [
            "tomato price", "onion online", "milk delivery", "bread fresh",
            "mobile phone", "laptop buy", "shirt men", "shoes women"
        ]
        
        for query in common_queries:
            if partial_lower in query.lower():
                suggestions.append(query)
        
        return suggestions[:5]  # Limit to 5 suggestions 