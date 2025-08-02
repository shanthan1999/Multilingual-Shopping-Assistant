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

# Note: Google ADK components removed due to compatibility issues
# Multi-agent functionality implemented through structured Gemini prompts

class MultiAgentShoppingSearch:
    """
    Multi-Agent Shopping System using Google ADK
    Implements specialized agents for different shopping tasks
    """
    
    def __init__(self):
        # Initialize APIs
        self.gemini_api_key = os.getenv('GOOGLE_API_KEY')
        if not self.gemini_api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        self.serper_api_key = os.getenv('SERPER_API_KEY')
        if not self.serper_api_key:
            raise ValueError("SERPER_API_KEY not found in environment variables")
        
        # Configure Gemini
        genai.configure(api_key=self.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Hindi-English mappings
        self.hindi_english_mappings = {
            'tamatar': 'tomato', 'pyaaz': 'onion', 'aloo': 'potato', 'gajar': 'carrot',
            'baingan': 'eggplant', 'kheera': 'cucumber', 'palak': 'spinach',
            'methi': 'fenugreek', 'kothimbir': 'coriander', 'pudina': 'mint',
            'dhaniya': 'coriander', 'dhania': 'coriander', 'doodh': 'milk',
            'paneer': 'cottage cheese', 'ghee': 'clarified butter', 'atta': 'wheat flour',
            'chawal': 'rice', 'daal': 'lentils', 'chai': 'tea', 'coffee': 'coffee',
            'mobile': 'mobile phone', 'laptop': 'laptop', 'computer': 'computer',
            'headphone': 'headphones', 'charger': 'mobile charger', 'kapda': 'clothes',
            'shirt': 'shirt', 'pant': 'pants', 'shoes': 'shoes', 'bag': 'bag',
            'pyaz': 'onion', 'alu': 'potato', 'gajjar': 'carrot', 'brinjal': 'eggplant',
            'khira': 'cucumber', 'kothmir': 'coriander', 'dudh': 'milk',
            'chaval': 'rice', 'dal': 'lentils'
        }
        
        # Initialize multi-agent system
        self._initialize_multi_agent_system()
    
    def _initialize_multi_agent_system(self):
        """Initialize the multi-agent shopping system"""
        # Simplified initialization - avoiding complex Google ADK setup for now
        # The multi-agent functionality is implemented through structured prompts
        self.agent_system = None  # Will use direct Gemini API calls instead
    
    def detect_hindi_query(self, query: str) -> bool:
        """Detect if query contains Hindi words"""
        query_lower = query.lower()
        
        # Check for Hindi indicators
        hindi_indicators = [
            'kya', 'kaise', 'kahan', 'kab', 'kaun', 'hai', 'ho',
            'main', 'aap', 'tum', 'hum', 'wo', 'ye', 'us', 'is', 'un',
            'in', 'ka', 'ki', 'ke', 'kaa', 'kii', 'kee', 'se', 'me',
            'par', 'pe', 'ko', 'ke', 'ka', 'ki', 'kya', 'kahan', 'kab'
        ]
        
        for indicator in hindi_indicators:
            if indicator in query_lower:
                return True
        
        # Check for transliterated Hindi words
        for hindi_word in self.hindi_english_mappings.keys():
            if hindi_word in query_lower:
                return True
        
        return False
    
    def translate_hindi_to_english(self, query: str) -> str:
        """Translate Hindi query to English"""
        query_lower = query.lower()
        translated_query = query
        
        # Replace Hindi words with English equivalents
        for hindi_word, english_word in self.hindi_english_mappings.items():
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
    
    def search_products_with_multi_agent(self, query: str, limit: int = 10) -> Dict:
        """Search products using multi-agent system"""
        try:
            # Detect if query is in Hindi
            is_hindi = self.detect_hindi_query(query)
            
            if is_hindi:
                translated_query = self.translate_hindi_to_english(query)
                st.info(f"🔍 Translated query: '{query}' → '{translated_query}'")
                query = translated_query
            
            # Get search results
            search_results = self._serper_search(query, limit)
            
            # Use multi-agent system
            ai_response = self._generate_multi_agent_response(query, search_results)
            
            # Format results
            formatted_results = self._format_results(search_results, query)
            
            return {
                'products': formatted_results,
                'ai_response': ai_response,
                'original_query': query,
                'is_hindi': is_hindi
            }
            
        except Exception as e:
            raise Exception(f"Multi-agent search failed: {e}")
    
    def _generate_multi_agent_response(self, query: str, search_results: List[Dict]) -> str:
        """Generate response using multi-agent system"""
        try:
            # Prepare context
            context = self._prepare_context(search_results)
            
            # For now, use direct Gemini API instead of complex multi-agent system
            # This avoids the InvocationContext validation issues
            prompt = f"""
            You are a multi-agent shopping assistant for Indian e-commerce. Analyze the following search results and provide comprehensive shopping recommendations.

            User Query: {query}
            
            Search Results:
            {context}
            
            Please provide:
            1. 🔍 Query Analysis: Understanding of what the user is looking for
            2. 💰 Price Analysis: Price ranges, best value options, budget considerations
            3. 🚚 Delivery Analysis: Delivery options, speed, and costs
            4. 🏆 Top Recommendations: Best 4 options (Best Value, Fastest Delivery, Premium, Budget)
            5. 💡 Smart Shopping Tips: Payment offers, timing, alternatives
            
            Format with emojis and clear sections. Focus on Indian market context.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            # Fallback to simple analysis
            return self._generate_simple_analysis(query, search_results)
    
    def _generate_simple_analysis(self, query: str, search_results: List[Dict]) -> str:
        """Generate simple analysis as fallback"""
        try:
            context = self._prepare_context(search_results)
            
            simple_prompt = f"""
            Analyze these search results for "{query}" and provide shopping recommendations:
            
            {context}
            
            Provide:
            - Best value products
            - Delivery options
            - Price comparison
            - Shopping tips
            
            Keep it concise and helpful for Indian shoppers.
            """
            
            response = self.model.generate_content(simple_prompt)
            return response.text
            
        except Exception as e:
            return f"🤖 Found {len(search_results)} products for '{query}'. Check the results below for detailed information."
    

    
    def _serper_search(self, query: str, limit: int) -> List[Dict]:
        """Perform search using Serper API"""
        url = "https://google.serper.dev/search"
        
        headers = {
            "X-API-KEY": self.serper_api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": f"{query} buy online India price",
            "num": limit,
            "gl": "in",
            "hl": "en"
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('organic', [])
        else:
            raise Exception(f"Serper API error: {response.status_code} - {response.text}")
    
    def _prepare_context(self, search_results: List[Dict]) -> str:
        """Prepare context from search results"""
        context_parts = []
        
        for i, result in enumerate(search_results[:8], 1):
            title = result.get('title', 'Unknown Product')
            snippet = result.get('snippet', 'No description')
            link = result.get('link', '')
            
            price = self._extract_price(snippet)
            delivery_info = self._extract_delivery_info(snippet, title)
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
    
    def _extract_delivery_info(self, snippet: str, title: str) -> str:
        """Extract delivery information from content"""
        delivery_patterns = [
            r'(\d+)\s*(?:min|minute)s?\s*delivery',
            r'instant\s*delivery',
            r'same\s*day\s*delivery',
            r'next\s*day\s*delivery',
            r'free\s*delivery',
            r'express\s*delivery'
        ]
        
        content = f"{title} {snippet}".lower()
        
        for pattern in delivery_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return ""
    
    def _extract_price(self, content: str) -> str:
        """Extract price information from content"""
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
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain name from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception:
            return "Unknown Store"
    
    def _format_results(self, results: List[Dict], original_query: str) -> List[Dict]:
        """Format search results for display"""
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
        
        formatted_results.sort(key=lambda x: x['score'], reverse=True)
        return formatted_results
    
    def _calculate_relevance_score(self, result: Dict, query: str) -> float:
        """Calculate relevance score for search results"""
        score = 0.0
        query_lower = query.lower()
        title_lower = result.get('title', '').lower()
        content_lower = result.get('snippet', '').lower()
        
        if query_lower in title_lower:
            score += 5.0
        
        if query_lower in content_lower:
            score += 2.0
        
        source = result.get('source', '').lower()
        shopping_sites = ['amazon', 'flipkart', 'myntra', 'snapdeal', 'paytmmall', 'bigbasket', 'zepto', 'blinkit']
        if any(site in source for site in shopping_sites):
            score += 3.0
        
        return min(score, 10.0)
    
    def get_search_suggestions(self, partial_query: str) -> List[str]:
        """Get search suggestions based on partial query"""
        suggestions = []
        partial_lower = partial_query.lower()
        
        for hindi_word, english_word in self.hindi_english_mappings.items():
            if hindi_word.startswith(partial_lower) or english_word.startswith(partial_lower):
                suggestions.append(f"{hindi_word} ({english_word})")
        
        # Get trending queries from search API
        trending_queries = self._get_trending_queries()
        
        for query in trending_queries:
            if partial_lower in query.lower():
                suggestions.append(query)
        
        return suggestions[:5]
    
    def get_popular_queries(self) -> List[str]:
        """Get popular search queries dynamically"""
        return self._get_trending_queries()[:8]
    
    def _get_trending_queries(self) -> List[str]:
        """Get trending search queries from various sources"""
        try:
            # Use Serper to get trending shopping queries
            trending_payload = {
                "q": "trending products India 2024 buy online",
                "num": 20,
                "gl": "in",
                "hl": "en"
            }
            
            headers = {
                "X-API-KEY": self.serper_api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.post("https://google.serper.dev/search", 
                                   headers=headers, json=trending_payload, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                queries = []
                
                # Extract product names from search results
                for result in data.get('organic', [])[:10]:
                    title = result.get('title', '').lower()
                    # Extract product keywords
                    for word in title.split():
                        if len(word) > 3 and word.isalpha():
                            queries.append(word)
                
                # Return unique queries
                return list(set(queries))[:20]
            
        except Exception as e:
            raise Exception(f"Failed to fetch trending queries: {e}")
    
 