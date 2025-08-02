import os
import requests
import json
import re
from typing import List, Dict, Optional
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime

# Load environment variables
load_dotenv()

class ProductComparisonService:
    """
    Product comparison service that analyzes products across multiple providers
    """
    
    def __init__(self):
        # Initialize APIs with graceful fallback
        self.gemini_api_key = os.getenv('GOOGLE_API_KEY')
        self.serper_api_key = os.getenv('SERPER_API_KEY')
        
        # Check if we have the required API keys
        self.has_gemini = bool(self.gemini_api_key and self.gemini_api_key != 'your_google_api_key_here')
        self.has_serper = bool(self.serper_api_key and self.serper_api_key != 'your_serper_api_key_here')
        
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
            print("Warning: GOOGLE_API_KEY not found. AI analysis features will be limited.")
        
        if not self.has_serper:
            print("Warning: SERPER_API_KEY not found. Web search features will be limited.")
        
        # Define major Indian e-commerce providers
        self.providers = {
            'amazon': {
                'name': 'Amazon India',
                'domain': 'amazon.in',
                'search_url': 'https://www.amazon.in/s?k={query}',
                'color': '#FF9900'
            },
            'flipkart': {
                'name': 'Flipkart',
                'domain': 'flipkart.com',
                'search_url': 'https://www.flipkart.com/search?q={query}',
                'color': '#2874F0'
            },
            'bigbasket': {
                'name': 'BigBasket',
                'domain': 'bigbasket.com',
                'search_url': 'https://www.bigbasket.com/pd/{query}',
                'color': '#4CAF50'
            },
            'zepto': {
                'name': 'Zepto',
                'domain': 'zepto.in',
                'search_url': 'https://www.zepto.in/search?q={query}',
                'color': '#FF6B35'
            },
            'blinkit': {
                'name': 'Blinkit',
                'domain': 'blinkit.com',
                'search_url': 'https://blinkit.com/search?q={query}',
                'color': '#FF6B6B'
            },
            'grofers': {
                'name': 'Grofers',
                'domain': 'grofers.com',
                'search_url': 'https://grofers.com/search?q={query}',
                'color': '#4CAF50'
            }
        }
    
    def compare_product_across_providers(self, product_name: str) -> Dict:
        """
        Compare a product across multiple providers
        """
        try:
            # Search for the product across different providers
            comparison_results = {}
            
            for provider_key, provider_info in self.providers.items():
                try:
                    if self.has_serper:
                        # Use real search for each provider
                        provider_results = self._search_provider_specific(product_name, provider_key)
                    else:
                        # Use demo data for each provider
                        provider_results = self._get_demo_provider_results(product_name, provider_key)
                    
                    # Ensure we always have results in demo mode
                    if not provider_results and not self.has_serper:
                        provider_results = self._get_demo_provider_results(product_name, provider_key)
                    
                    comparison_results[provider_key] = {
                        'provider_info': provider_info,
                        'products': provider_results,
                        'best_deal': self._find_best_deal(provider_results),
                        'availability': len(provider_results) > 0
                    }
                    
                except Exception as e:
                    # In demo mode, still provide results
                    if not self.has_serper:
                        provider_results = self._get_demo_provider_results(product_name, provider_key)
                        comparison_results[provider_key] = {
                            'provider_info': provider_info,
                            'products': provider_results,
                            'best_deal': self._find_best_deal(provider_results),
                            'availability': len(provider_results) > 0
                        }
                    else:
                        comparison_results[provider_key] = {
                            'provider_info': provider_info,
                            'products': [],
                            'best_deal': None,
                            'availability': False,
                            'error': str(e)
                        }
            
            # Generate comparison analysis
            analysis = self._generate_comparison_analysis(product_name, comparison_results)
            
            return {
                'product_name': product_name,
                'providers': comparison_results,
                'analysis': analysis,
                'summary': self._generate_summary(product_name, comparison_results)
            }
            
        except Exception as e:
            return {
                'product_name': product_name,
                'error': f"Comparison failed: {e}",
                'providers': {},
                'analysis': "Unable to generate comparison analysis.",
                'summary': "Comparison could not be completed."
            }
    
    def _search_provider_specific(self, product_name: str, provider_key: str) -> List[Dict]:
        """Search for product on specific provider"""
        try:
            provider_info = self.providers[provider_key]
            search_query = f"{product_name} site:{provider_info['domain']}"
            
            payload = {
                "q": search_query,
                "num": 5,
                "gl": "in",
                "hl": "en"
            }
            
            headers = {
                "X-API-KEY": self.serper_api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.post("https://google.serper.dev/search", 
                                   headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_provider_results(data.get('organic', []), provider_key)
            else:
                return []
                
        except Exception as e:
            return []
    
    def _parse_provider_results(self, results: List[Dict], provider_key: str) -> List[Dict]:
        """Parse search results for specific provider"""
        parsed_results = []
        
        for result in results:
            try:
                title = result.get('title', '')
                url = result.get('link', '')
                snippet = result.get('snippet', '')
                
                # Extract price
                price = self._extract_price_from_text(snippet + ' ' + title)
                
                # Extract rating
                rating = self._extract_rating_from_text(snippet + ' ' + title)
                
                # Extract delivery info
                delivery_info = self._extract_delivery_info(snippet, provider_key)
                
                parsed_result = {
                    'title': title,
                    'url': url,
                    'price': price,
                    'rating': rating,
                    'delivery': delivery_info,
                    'snippet': snippet,
                    'provider': provider_key
                }
                
                parsed_results.append(parsed_result)
                
            except Exception as e:
                continue
        
        return parsed_results
    
    def _get_demo_provider_results(self, product_name: str, provider_key: str) -> List[Dict]:
        """Generate demo results for specific provider"""
        provider_info = self.providers[provider_key]
        
        # Generate realistic demo data based on provider
        demo_prices = {
            'amazon': ['₹299', '₹349', '₹399'],
            'flipkart': ['₹279', '₹329', '₹379'],
            'bigbasket': ['₹289', '₹339', '₹389'],
            'zepto': ['₹269', '₹319', '₹369'],
            'blinkit': ['₹259', '₹309', '₹359'],
            'grofers': ['₹279', '₹329', '₹379']
        }
        
        demo_delivery = {
            'amazon': ['1-2 days', 'Same day delivery', '2-3 days'],
            'flipkart': ['1-2 days', 'Next day delivery', '2-3 days'],
            'bigbasket': ['Same day', '2-3 hours', 'Next day'],
            'zepto': ['10 minutes', '15 minutes', '20 minutes'],
            'blinkit': ['10 minutes', '15 minutes', '20 minutes'],
            'grofers': ['Same day', '2-3 hours', 'Next day']
        }
        
        demo_ratings = [4.2, 4.5, 4.0, 4.3, 4.1]
        
        import random
        results = []
        
        # Always generate at least 2 results for demo
        num_results = random.randint(2, 3)
        
        for i in range(num_results):
            result = {
                'title': f"{product_name.title()} - {provider_info['name']} Option {i+1}",
                'url': f"https://{provider_info['domain']}/product{i+1}",
                'price': random.choice(demo_prices.get(provider_key, ['₹299'])),
                'rating': random.choice(demo_ratings),
                'delivery': random.choice(demo_delivery.get(provider_key, ['1-2 days'])),
                'snippet': f"High quality {product_name} available on {provider_info['name']}. Fresh and best price guaranteed.",
                'provider': provider_key
            }
            results.append(result)
        
        return results
    
    def _find_best_deal(self, products: List[Dict]) -> Optional[Dict]:
        """Find the best deal from a list of products"""
        if not products:
            return None
        
        # Sort by price (lowest first) and rating (highest first)
        def sort_key(product):
            price_str = product.get('price', '₹999')
            price_num = float(re.findall(r'₹(\d+)', price_str)[0]) if re.findall(r'₹(\d+)', price_str) else 999
            rating = product.get('rating', 0)
            # Handle None rating
            if rating is None:
                rating = 0
            return (price_num, -rating)  # Lower price, higher rating
        
        try:
            sorted_products = sorted(products, key=sort_key)
            return sorted_products[0] if sorted_products else None
        except Exception as e:
            # Return first product if sorting fails
            return products[0] if products else None
    
    def _generate_comparison_analysis(self, product_name: str, comparison_results: Dict) -> str:
        """Generate AI-powered comparison analysis"""
        if not self.has_gemini or not self.model:
            return self._generate_simple_comparison_analysis(product_name, comparison_results)
        
        try:
            # Prepare context for AI analysis
            context = self._prepare_comparison_context(product_name, comparison_results)
            
            prompt = f"""
            Analyze the following product comparison for "{product_name}" across multiple Indian e-commerce providers:

            {context}

            Please provide a comprehensive analysis including:
            1. 🏆 Best Value Provider: Which provider offers the best overall value
            2. 💰 Price Analysis: Price comparison across providers
            3. ⚡ Delivery Speed: Fastest delivery options
            4. 🌟 Quality Indicators: Ratings and reviews comparison
            5. 🎯 Recommendations: Top 3 recommendations with reasons
            6. 💡 Shopping Tips: When to buy, best deals, etc.

            Format with emojis and clear sections. Focus on Indian market context and practical advice.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return self._generate_simple_comparison_analysis(product_name, comparison_results)
    
    def _generate_simple_comparison_analysis(self, product_name: str, comparison_results: Dict) -> str:
        """Generate simple comparison analysis as fallback"""
        analysis = f"## 🛒 {product_name.title()} - Provider Comparison\n\n"
        
        available_providers = [k for k, v in comparison_results.items() if v.get('availability')]
        
        if not available_providers:
            analysis += "❌ No providers currently have this product available.\n"
            return analysis
        
        analysis += f"✅ Found {product_name} on {len(available_providers)} providers:\n\n"
        
        # Price comparison
        prices = []
        for provider_key in available_providers:
            best_deal = comparison_results[provider_key].get('best_deal')
            if best_deal:
                prices.append((provider_key, best_deal['price']))
        
        if prices:
            prices.sort(key=lambda x: float(re.findall(r'₹(\d+)', x[1])[0]) if re.findall(r'₹(\d+)', x[1]) else 999)
            analysis += "💰 **Price Comparison:**\n"
            for provider_key, price in prices:
                provider_name = comparison_results[provider_key]['provider_info']['name']
                analysis += f"• {provider_name}: {price}\n"
            analysis += f"\n🏆 **Best Price:** {prices[0][1]} on {comparison_results[prices[0][0]]['provider_info']['name']}\n\n"
        
        # Delivery comparison
        analysis += "⚡ **Delivery Options:**\n"
        for provider_key in available_providers:
            best_deal = comparison_results[provider_key].get('best_deal')
            if best_deal:
                provider_name = comparison_results[provider_key]['provider_info']['name']
                delivery = best_deal.get('delivery', 'Standard delivery')
                analysis += f"• {provider_name}: {delivery}\n"
        
        return analysis
    
    def _prepare_comparison_context(self, product_name: str, comparison_results: Dict) -> str:
        """Prepare context for AI analysis"""
        context = f"Product: {product_name}\n\n"
        
        for provider_key, data in comparison_results.items():
            provider_name = data['provider_info']['name']
            context += f"**{provider_name}:**\n"
            
            if data.get('availability'):
                best_deal = data.get('best_deal')
                if best_deal:
                    context += f"- Price: {best_deal.get('price', 'N/A')}\n"
                    context += f"- Rating: {best_deal.get('rating', 'N/A')}\n"
                    context += f"- Delivery: {best_deal.get('delivery', 'N/A')}\n"
                    context += f"- URL: {best_deal.get('url', 'N/A')}\n"
            else:
                context += "- Not available\n"
            
            context += "\n"
        
        return context
    
    def _generate_summary(self, product_name: str, comparison_results: Dict) -> Dict:
        """Generate summary statistics"""
        available_providers = [k for k, v in comparison_results.items() if v.get('availability')]
        
        if not available_providers:
            return {
                'total_providers': len(comparison_results),
                'available_providers': 0,
                'best_price': None,
                'best_provider': None,
                'fastest_delivery': None,
                'fastest_provider': None
            }
        
        # Find best price
        best_price = None
        best_provider = None
        for provider_key in available_providers:
            best_deal = comparison_results[provider_key].get('best_deal')
            if best_deal and best_deal.get('price'):
                price_str = best_deal['price']
                price_num = float(re.findall(r'₹(\d+)', price_str)[0]) if re.findall(r'₹(\d+)', price_str) else 999
                
                if best_price is None or price_num < best_price:
                    best_price = price_num
                    best_provider = provider_key
        
        # Find fastest delivery
        fastest_delivery = None
        fastest_provider = None
        for provider_key in available_providers:
            best_deal = comparison_results[provider_key].get('best_deal')
            if best_deal and best_deal.get('delivery'):
                delivery = best_deal['delivery']
                # Extract time in minutes
                time_match = re.search(r'(\d+)\s*(?:minutes?|mins?)', delivery.lower())
                if time_match:
                    time_minutes = int(time_match.group(1))
                    if fastest_delivery is None or time_minutes < fastest_delivery:
                        fastest_delivery = time_minutes
                        fastest_provider = provider_key
        
        return {
            'total_providers': len(comparison_results),
            'available_providers': len(available_providers),
            'best_price': f"₹{best_price}" if best_price else None,
            'best_provider': comparison_results[best_provider]['provider_info']['name'] if best_provider else None,
            'fastest_delivery': f"{fastest_delivery} minutes" if fastest_delivery else None,
            'fastest_provider': comparison_results[fastest_provider]['provider_info']['name'] if fastest_provider else None
        }
    
    def _extract_price_from_text(self, text: str) -> str:
        """Extract price from text"""
        price_patterns = [
            r'₹\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'Rs\.?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'INR\s*(\d+(?:,\d+)*(?:\.\d+)?)',
            r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:rupees?|rs)'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                price = match.group(1)
                return f"₹{price}"
        
        return "Price not available"
    
    def _extract_rating_from_text(self, text: str) -> Optional[float]:
        """Extract rating from text"""
        rating_match = re.search(r'(\d+\.?\d*)\s*(?:star|rating|out of 5)', text.lower())
        if rating_match:
            return float(rating_match.group(1))
        return None
    
    def _extract_delivery_info(self, text: str, provider_key: str) -> str:
        """Extract delivery information"""
        delivery_patterns = [
            r'(\d+)\s*(?:minutes?|mins?)',
            r'(\d+)\s*(?:hours?|hrs?)',
            r'(\d+)\s*(?:days?)',
            r'same\s*day',
            r'next\s*day'
        ]
        
        text_lower = text.lower()
        for pattern in delivery_patterns:
            match = re.search(pattern, text_lower)
            if match:
                if 'same day' in text_lower:
                    return "Same day delivery"
                elif 'next day' in text_lower:
                    return "Next day delivery"
                else:
                    time_value = match.group(1)
                    if 'minutes' in text_lower or 'mins' in text_lower:
                        return f"{time_value} minutes"
                    elif 'hours' in text_lower or 'hrs' in text_lower:
                        return f"{time_value} hours"
                    elif 'days' in text_lower:
                        return f"{time_value} days"
        
        # Default delivery times based on provider
        default_delivery = {
            'amazon': '1-2 days',
            'flipkart': '1-2 days',
            'bigbasket': 'Same day',
            'zepto': '10 minutes',
            'blinkit': '10 minutes',
            'grofers': 'Same day'
        }
        
        return default_delivery.get(provider_key, 'Standard delivery') 