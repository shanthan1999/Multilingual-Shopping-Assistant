import os
import requests
import json
import re
from typing import List, Dict, Optional
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

class RAGShoppingSearch:
    """
    RAG (Retrieval-Augmented Generation) shopping search service
    Uses Google Gemini API for AI responses and Serper for web search
    """
    
    def __init__(self):
        # Initialize APIs with graceful fallback
        self.gemini_api_key = os.getenv('GOOGLE_API_KEY')
        self.serper_api_key = os.getenv('SERPER_API_KEY')
        
        # Check if we have the required API keys
        self.has_gemini = bool(self.gemini_api_key)
        self.has_serper = bool(self.serper_api_key)
        
        # Configure Gemini if API key is available
        if self.has_gemini:
            try:
                genai.configure(api_key=self.gemini_api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
            except Exception as e:
                print(f"Warning: Failed to configure Gemini: {e}")
                self.has_gemini = False
        else:
            self.model = None
            print("Warning: GOOGLE_API_KEY not found. AI features will be limited.")
        
        if not self.has_serper:
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
            'pyaz': 'onion',
            'alu': 'potato',
            'gajjar': 'carrot',
            'brinjal': 'eggplant',
            'khira': 'cucumber',
            'kothmir': 'coriander',
            'dudh': 'milk',
            'chaval': 'rice',
            'dal': 'lentils'
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
            'kya', 'kaise', 'kahan', 'kab', 'kaun', 'hai', 'ho',
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
    
    def search_products_with_rag(self, query: str, limit: int = 10) -> Dict:
        """
        Search for products using RAG approach with Gemini and Serper
        """
        try:
            # Detect if query is in Hindi
            is_hindi = self.detect_hindi_query(query)
            
            if is_hindi:
                # Translate Hindi to English
                translated_query = self.translate_hindi_to_english(query)
                st.info(f"🔍 Translated query: '{query}' → '{translated_query}'")
                query = translated_query
            
            # Step 1: Get search results from Serper
            search_results = self._serper_search(query, limit)
            
            # Step 2: Generate AI response using Gemini
            ai_response = self._generate_ai_response(query, search_results)
            
            # Step 3: Format results
            formatted_results = self._format_results(search_results, query)
            
            return {
                'products': formatted_results,
                'ai_response': ai_response,
                'original_query': query,
                'is_hindi': is_hindi
            }
            
        except Exception as e:
            raise Exception(f"RAG search failed: {e}")
    
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
            "q": f"{query} buy online India price",
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
    
    def _generate_ai_response(self, query: str, search_results: List[Dict]) -> str:
        """
        Generate AI response using Gemini based on search results
        """
        try:
            
            # Prepare context from search results
            context = self._prepare_context(search_results)
            
            # Create prompt for Gemini
            prompt = f"""
            You are a helpful shopping assistant for Indian consumers. Based on the search query "{query}" and the following product information, provide a comprehensive and well-structured response.

            Product Information:
            {context}

            Please provide a response in this exact format:

            🛒 **Shopping Analysis for "{query}"**

            **📊 Quick Overview:**
            [Brief 2-3 sentence analysis of what you found]

            **🏆 Top Recommendations:**
            1. **Best Value:** [Store] - [Price] - [Why it's best value]
            2. **Fastest Delivery:** [Store] - [Delivery time] - [Price]
            3. **Premium Option:** [Store] - [Price] - [Why it's premium]
            4. **Budget Friendly:** [Store] - [Price] - [Why it's budget friendly]

            **💰 Price Analysis:**
            - **Price Range:** ₹[min] - ₹[max]
            - **Average Price:** ₹[average]
            - **Best Deal:** [Store] at ₹[price]

            **🚚 Delivery Options:**
            - **Instant:** [Stores with <30 min delivery]
            - **Same Day:** [Stores with same day delivery]
            - **Standard:** [Stores with 1-2 day delivery]

            **💡 Smart Shopping Tips:**
            • [Tip 1: Quantity/volume advice]
            • [Tip 2: Quality considerations]
            • [Tip 3: Delivery timing]
            • [Tip 4: Payment/offers]

            **🎯 Best Choice for You:**
            [Recommend the best overall option with reasoning]

            Keep it concise, use emojis for visual appeal, and focus on actionable advice. If the query is in Hindi, you can respond in Hindi as well.
            """
            
            # Generate response using Gemini
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            raise Exception(f"AI analysis failed: {e}")
    
    def _prepare_context(self, search_results: List[Dict]) -> str:
        """
        Prepare context from search results for Gemini
        """
        context_parts = []
        
        for i, result in enumerate(search_results[:8], 1):  # Increased to top 8 results
            title = result.get('title', 'Unknown Product')
            snippet = result.get('snippet', 'No description')
            link = result.get('link', '')
            
            # Extract price if available
            price = self._extract_price(snippet)
            
            # Extract delivery info
            delivery_info = self._extract_delivery_info(snippet, title)
            
            # Extract store/domain
            store = self._extract_domain(link)
            
            context_parts.append(f"Product {i}:")
            context_parts.append(f"Title: {title}")
            context_parts.append(f"Description: {snippet[:150]}...")
            if price != "Price not available":
                context_parts.append(f"Price: {price}")
            if delivery_info:
                context_parts.append(f"Delivery: {delivery_info}")
            context_parts.append(f"Store: {store}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
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
        content_lower = result.get('snippet', '').lower()
        
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