import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import time
import os
import sys
import hashlib
import re # Added for price extraction
import urllib.parse

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the services directly
try:
    from src.services.multi_agent_shopping import MultiAgentShoppingSearch
    from src.services.product_comparison import ProductComparisonService
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Initialize services
@st.cache_resource
def init_services():
    """Initialize services"""
    try:
        multi_agent_service = MultiAgentShoppingSearch()
        comparison_service = ProductComparisonService()
        return multi_agent_service, comparison_service
    except Exception as e:
        st.error(f"⚠️ Service initialization issue: {e}")
        st.info("💡 To enable full functionality, please configure your API keys in the .env file:")
        st.code("""
# Add your API keys to .env file:
GOOGLE_API_KEY=your_google_api_key_here
SERPER_API_KEY=your_serper_api_key_here
        """)
        st.info("🔗 Get API keys from:")
        st.markdown("- [Google AI Studio](https://makersuite.google.com/app/apikey) for Gemini AI")
        st.markdown("- [Serper.dev](https://serper.dev/) for web search")
        st.stop()

# Page configuration
st.set_page_config(
    page_title="MultiAgent Shopping Assistant Chat",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS for cleaner UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .product-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #e8eaf6;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        transition: transform 0.2s ease;
    }
    
    .product-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }
    
    .price-tag {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 25px;
        font-weight: bold;
        font-size: 0.9rem;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    .buy-button {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        text-decoration: none;
        font-weight: bold;
        box-shadow: 0 2px 8px rgba(255, 107, 107, 0.3);
    }
    
    .list-item {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .sample-query {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.2rem;
        display: inline-block;
        cursor: pointer;
        transition: transform 0.2s ease;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    .sample-query:hover {
        transform: scale(1.05);
    }
    
    .ai-response {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(102, 126, 234, 0.2);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: transform 0.2s ease;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e8eaf6;
        padding: 0.75rem;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'shopping_list' not in st.session_state:
    st.session_state.shopping_list = []

# Enhanced product detail extraction functions
def extract_product_details_with_regex(product_data):
    """Enhanced product detail extraction using regex patterns"""
    title = product_data.get('title', 'Product')
    description = product_data.get('description', 'No description available')
    combined_text = f"{title} {description}".lower()
    
    # Enhanced price extraction with multiple patterns
    price_patterns = [
        r'₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)',  # ₹1,234.56
        r'rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',  # Rs. 1234
        r'inr\s*(\d+(?:,\d+)*(?:\.\d{2})?)',  # INR 1234
        r'price[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',  # Price: ₹1234
        r'cost[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',  # Cost: 1234
        r'(\d+(?:,\d+)*(?:\.\d{2})?)\s*(?:rupees?|rs\.?)',  # 1234 rupees
        r'mrp[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',  # MRP: ₹1234
        r'offer[:\s]*₹?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',  # Offer: ₹1234
    ]
    
    extracted_price = "Price not available"
    for pattern in price_patterns:
        match = re.search(pattern, combined_text, re.IGNORECASE)
        if match:
            price_value = match.group(1)
            extracted_price = f"₹{price_value}"
            break
    
    # Extract discount information
    discount_patterns = [
        r'(\d+)%\s*off',
        r'save\s*₹?\s*(\d+)',
        r'discount[:\s]*(\d+)%',
        r'(\d+)%\s*discount',
        r'flat\s*(\d+)%\s*off'
    ]
    
    discount_info = ""
    for pattern in discount_patterns:
        match = re.search(pattern, combined_text, re.IGNORECASE)
        if match:
            discount_info = f"🏷️ {match.group(0)}"
            break
    
    # Extract rating information
    rating_patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:star|stars|\*)',
        r'rating[:\s]*(\d+(?:\.\d+)?)',
        r'rated\s*(\d+(?:\.\d+)?)',
        r'(\d+(?:\.\d+)?)/5',
        r'(\d+(?:\.\d+)?)\s*out\s*of\s*5'
    ]
    
    rating = ""
    for pattern in rating_patterns:
        match = re.search(pattern, combined_text, re.IGNORECASE)
        if match:
            rating_value = match.group(1)
            rating = f"⭐ {rating_value}/5"
            break
    
    # Extract delivery information
    delivery_patterns = [
        r'(\d+)\s*(?:min|minute)s?\s*delivery',
        r'instant\s*delivery',
        r'same\s*day\s*delivery',
        r'next\s*day\s*delivery',
        r'free\s*delivery',
        r'express\s*delivery',
        r'(\d+)\s*(?:day|days)\s*delivery',
        r'delivery\s*in\s*(\d+)\s*(?:day|days|hour|hours)',
        r'ships\s*in\s*(\d+)\s*(?:day|days)'
    ]
    
    delivery_info = ""
    for pattern in delivery_patterns:
        match = re.search(pattern, combined_text, re.IGNORECASE)
        if match:
            delivery_info = f"🚚 {match.group(0).title()}"
            break
    
    # Extract brand information
    brand_patterns = [
        r'brand[:\s]*([a-zA-Z]+)',
        r'by\s+([a-zA-Z]+)',
        r'from\s+([a-zA-Z]+)',
        r'^([A-Z][a-zA-Z]+)\s+',  # Brand at start of title
    ]
    
    brand = ""
    for pattern in brand_patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            brand_name = match.group(1)
            if len(brand_name) > 2 and brand_name.lower() not in ['the', 'and', 'for', 'with']:
                brand = f"🏷️ {brand_name}"
                break
    
    # Extract size/quantity information
    size_patterns = [
        r'(\d+(?:\.\d+)?)\s*(?:kg|gm|gram|grams|ml|liter|litre|l)',
        r'(\d+)\s*(?:piece|pieces|pcs|pack)',
        r'size[:\s]*([a-zA-Z0-9]+)',
        r'(\d+)\s*(?:inch|inches|cm|mm)',
        r'(\d+(?:\.\d+)?)\s*(?:gb|tb|mb)'
    ]
    
    size_info = ""
    for pattern in size_patterns:
        match = re.search(pattern, combined_text, re.IGNORECASE)
        if match:
            size_info = f"📏 {match.group(0)}"
            break
    
    return {
        'price': extracted_price,
        'discount': discount_info,
        'rating': rating,
        'delivery': delivery_info,
        'brand': brand,
        'size': size_info
    }

def get_generic_product_image(query, product_title=""):
    """Generate generic product images based on search query and product title"""
    query_lower = query.lower()
    title_lower = product_title.lower()
    combined = f"{query_lower} {title_lower}"
    
    # Product category mappings to appropriate images
    category_images = {
        # Electronics
        'mobile': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=150&h=150&fit=crop',
        'phone': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=150&h=150&fit=crop',
        'laptop': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=150&h=150&fit=crop',
        'computer': 'https://images.unsplash.com/photo-1547082299-de196ea013d6?w=150&h=150&fit=crop',
        'headphone': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=150&h=150&fit=crop',
        'earphone': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=150&h=150&fit=crop',
        'charger': 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=150&h=150&fit=crop',
        'tablet': 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=150&h=150&fit=crop',
        'watch': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=150&h=150&fit=crop',
        'camera': 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=150&h=150&fit=crop',
        
        # Vegetables
        'tomato': 'https://images.unsplash.com/photo-1546470427-e26264be0b0d?w=150&h=150&fit=crop',
        'tamatar': 'https://images.unsplash.com/photo-1546470427-e26264be0b0d?w=150&h=150&fit=crop',
        'onion': 'https://images.unsplash.com/photo-1508747703725-719777637510?w=150&h=150&fit=crop',
        'pyaaz': 'https://images.unsplash.com/photo-1508747703725-719777637510?w=150&h=150&fit=crop',
        'potato': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=150&h=150&fit=crop',
        'aloo': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=150&h=150&fit=crop',
        'carrot': 'https://images.unsplash.com/photo-1445282768818-728615cc910a?w=150&h=150&fit=crop',
        'gajar': 'https://images.unsplash.com/photo-1445282768818-728615cc910a?w=150&h=150&fit=crop',
        'cucumber': 'https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?w=150&h=150&fit=crop',
        'kheera': 'https://images.unsplash.com/photo-1449300079323-02e209d9d3a6?w=150&h=150&fit=crop',
        'spinach': 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=150&h=150&fit=crop',
        'palak': 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=150&h=150&fit=crop',
        
        # Fruits
        'apple': 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=150&h=150&fit=crop',
        'banana': 'https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=150&h=150&fit=crop',
        'orange': 'https://images.unsplash.com/photo-1547514701-42782101795e?w=150&h=150&fit=crop',
        'mango': 'https://images.unsplash.com/photo-1553279768-865429fa0078?w=150&h=150&fit=crop',
        'grapes': 'https://images.unsplash.com/photo-1537640538966-79f369143f8f?w=150&h=150&fit=crop',
        
        # Dairy & Groceries
        'milk': 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=150&h=150&fit=crop',
        'doodh': 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=150&h=150&fit=crop',
        'bread': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=150&h=150&fit=crop',
        'rice': 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=150&h=150&fit=crop',
        'chawal': 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=150&h=150&fit=crop',
        'oil': 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=150&h=150&fit=crop',
        'sugar': 'https://images.unsplash.com/photo-1587735243615-c03f25aaff15?w=150&h=150&fit=crop',
        'tea': 'https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=150&h=150&fit=crop',
        'chai': 'https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=150&h=150&fit=crop',
        'coffee': 'https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=150&h=150&fit=crop',
        
        # Clothing
        'shirt': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=150&h=150&fit=crop',
        'pant': 'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=150&h=150&fit=crop',
        'jeans': 'https://images.unsplash.com/photo-1542272604-787c3835535d?w=150&h=150&fit=crop',
        'shoes': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=150&h=150&fit=crop',
        'bag': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=150&h=150&fit=crop',
        'dress': 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=150&h=150&fit=crop',
        
        # Home & Kitchen
        'plate': 'https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=150&h=150&fit=crop',
        'cup': 'https://images.unsplash.com/photo-1544787219-7f47ccb76574?w=150&h=150&fit=crop',
        'bottle': 'https://images.unsplash.com/photo-1523362628745-0c100150b504?w=150&h=150&fit=crop',
        'chair': 'https://images.unsplash.com/photo-1506439773649-6e0eb8cfb237?w=150&h=150&fit=crop',
        'table': 'https://images.unsplash.com/photo-1449247709967-d4461a6a6103?w=150&h=150&fit=crop',
        
        # Books & Stationery
        'book': 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=150&h=150&fit=crop',
        'pen': 'https://images.unsplash.com/photo-1455390582262-044cdead277a?w=150&h=150&fit=crop',
        'notebook': 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=150&h=150&fit=crop',
    }
    
    # Find matching category
    for category, image_url in category_images.items():
        if category in combined:
            return image_url
    
    # Fallback to a generic product image
    return 'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=150&h=150&fit=crop'

def enhance_product_data(product, search_query):
    """Enhance product data with extracted details and generic images"""
    # Extract enhanced details
    details = extract_product_details_with_regex(product)
    
    # Get generic product image
    generic_image = get_generic_product_image(search_query, product.get('title', ''))
    
    # Enhanced product data
    enhanced_product = {
        'title': product.get('title', 'Product'),
        'description': product.get('description', 'No description available'),
        'url': product.get('url', ''),
        'source': product.get('source', 'Unknown Store'),
        'price': details['price'],
        'image': generic_image,  # Use generic image instead of original
        'score': product.get('score', 0),
        'discount': details['discount'],
        'rating': details['rating'],
        'delivery': details['delivery'],
        'brand': details['brand'],
        'size': details['size']
    }
    
    return enhanced_product

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 MultiAgent Shopping Assistant Chat</h1>
        <p>Agentic RAG-powered shopping with web data comparison, product analysis, and intelligent recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize services
    try:
        multi_agent_service, comparison_service = init_services()
        
        # Show API key status
        if not multi_agent_service.has_gemini or not multi_agent_service.has_serper:
            st.warning("⚠️ Demo Mode: Some features are limited. Configure API keys for full functionality.")
            if not multi_agent_service.has_gemini:
                st.info("🔑 Add GOOGLE_API_KEY for AI-powered analysis")
            if not multi_agent_service.has_serper:
                st.info("🔑 Add SERPER_API_KEY for real web search results")
        
    except Exception as e:
        st.error(f"❌ Failed to initialize services: {e}")
        st.info("💡 Please check your API keys in the .env file")
        return
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Product Search", "🛒 Shopping List", "📊 Provider Comparison", "🌐 Language Help"])
    
    with tab1:
        show_product_search(multi_agent_service)
    
    with tab2:
        show_shopping_list()
    
    with tab3:
        show_provider_comparison(comparison_service)
    
    with tab4:
        show_language_help()

def show_product_search(multi_agent_service):
    """Display the product search interface"""
    st.header("🔍 Search Products Online")
    st.caption("🌐 Supports Hindi and English queries with AI-powered insights")
    
    # Sample queries section
    st.subheader("💡 Try these sample queries:")
    
    # Get dynamic sample queries from the service
    sample_queries = multi_agent_service.get_popular_queries()
    
    cols = st.columns(4)
    for i, query in enumerate(sample_queries):
        with cols[i % 4]:
            if st.button(query, key=f"sample_{i}", use_container_width=True):
                st.session_state.search_query = query
                st.rerun()
    
    st.divider()
    
    # Search input
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        # Get the search query from session state or use empty string
        current_query = st.session_state.get('search_query', '')
        search_query = st.text_input(
            "Search Products",
            value=current_query,
            placeholder="Search in Hindi or English (e.g., tamatar, tomato, mobile, laptop)",
            label_visibility="collapsed"
        )
        # Update session state when user types
        if search_query != current_query:
            st.session_state.search_query = search_query
    with col2:
        limit = st.selectbox("Results", [5, 10, 15, 20], index=1)
    with col3:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.search_query = ""
            st.rerun()
    
    # Show search suggestions
    if search_query and len(search_query) > 2:
        suggestions = multi_agent_service.get_search_suggestions(search_query)
        if suggestions:
            st.caption("💡 Suggestions:")
            cols = st.columns(len(suggestions))
            for i, suggestion in enumerate(suggestions):
                with cols[i]:
                    if st.button(suggestion, key=f"search_suggest_{i}", use_container_width=True):
                        st.session_state.search_query = suggestion
                        st.rerun()
    
    if search_query:
        with st.spinner("🔍 Searching with AI-powered insights..."):
            try:
                # Use Multi-Agent service for enhanced search
                multi_agent_results = multi_agent_service.search_products_with_multi_agent(search_query, limit)
                
                # Display AI response
                if multi_agent_results.get('ai_response'):
                    st.markdown("""
                    <div class="ai-response">
                        <h4>🤖 Multi-Agent Shopping Assistant</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write(multi_agent_results['ai_response'])
                    st.divider()
                
                products = multi_agent_results.get('products', [])
                
                if products:
                    st.success(f"Found {len(products)} products")
                    
                    # Enhance products with regex extraction and generic images
                    enhanced_products = [enhance_product_data(product, search_query) for product in products]
                    
                    # Display products in a clean grid
                    for i, product in enumerate(enhanced_products):
                        st.markdown("""
                        <div class="product-card">
                        """, unsafe_allow_html=True)
                        
                        col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
                        
                        with col1:
                            # Product image (now using generic images)
                            image_url = product.get('image')
                            try:
                                st.image(image_url, width=100)
                            except:
                                st.image('https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=150&h=150&fit=crop', width=100)
                        
                        with col2:
                            st.markdown(f"**{product.get('title', 'Product')[:60]}**")
                            
                            # Enhanced product details
                            if product.get('brand'):
                                st.caption(product['brand'])
                            if product.get('size'):
                                st.caption(product['size'])
                            
                            description = product.get('description', 'No description available')
                            if len(description) > 80:
                                description = description[:80] + "..."
                            st.write(description)
                            
                            # Source info with delivery
                            source = product.get('source', 'Unknown Store')
                            delivery = product.get('delivery', '')
                            if delivery:
                                st.caption(f"📍 {source} • {delivery}")
                            else:
                                st.caption(f"📍 {source}")
                        
                        with col3:
                            price = product.get('price', 'Price not available')
                            st.markdown(f'<div class="price-tag">{price}</div>', unsafe_allow_html=True)
                            
                            # Show discount if available
                            if product.get('discount'):
                                st.caption(product['discount'])
                            
                            # Show rating if available
                            if product.get('rating'):
                                st.caption(product['rating'])
                            else:
                                # Relevance score as fallback
                                score = product.get('score', 0)
                                st.caption(f"⭐ {score:.1f}/10")
                        
                        with col4:
                            # Buy button
                            if product.get('url'):
                                st.link_button("🛒 Buy Now", product['url'], use_container_width=True)
                            
                            # Add to list button
                            if st.button("➕ Add to List", key=f"add_{i}", use_container_width=True):
                                add_to_shopping_list(product)
                                st.success("Added to list!")
                                time.sleep(0.5)
                                st.rerun()
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.warning("No products found. Try different keywords.")
                    
            except Exception as e:
                st.error(f"❌ Search failed: {e}")
                st.info("💡 This might be due to:")
                st.markdown("- Missing or invalid API keys")
                st.markdown("- Network connectivity issues")
                st.markdown("- Rate limiting from search providers")
                st.info("🔄 Try again or check your API configuration")
                return



def show_shopping_list():
    """Display the shopping list interface"""
    st.header("📝 Your Shopping List")
    
    if st.session_state.shopping_list:
        # List controls
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"**{len(st.session_state.shopping_list)} items** in your list")
        with col2:
            if st.button("📤 Export List"):
                export_shopping_list()
        with col3:
            if st.button("🗑️ Clear All"):
                st.session_state.shopping_list = []
                st.success("List cleared!")
                st.rerun()
        
        st.divider()
        
        # Display list items
        for i, item in enumerate(st.session_state.shopping_list):
            st.markdown("""
            <div class="product-card">
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
            
            with col1:
                # Product image (enhanced with generic images)
                image_url = item.get('image')
                if not image_url or 'placeholder' in image_url:
                    # Generate generic image based on product title
                    image_url = get_generic_product_image("", item.get('title', ''))
                try:
                    st.image(image_url, width=100)
                except:
                    st.image('https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=150&h=150&fit=crop', width=100)
            
            with col2:
                st.markdown(f"**{item['title'][:60]}**")
                
                # Enhanced product details
                if item.get('brand'):
                    st.caption(item['brand'])
                if item.get('size'):
                    st.caption(item['size'])
                
                description = item.get('description', 'No description available')
                if len(description) > 80:
                    description = description[:80] + "..."
                st.write(description)
                
                # Source info with delivery
                source_info = f"📍 {item['source']}"
                if item.get('delivery'):
                    source_info += f" • {item['delivery']}"
                st.caption(source_info)
                
                # Added date
                if item.get('added_at'):
                    try:
                        added_date = datetime.fromisoformat(item['added_at']).strftime('%Y-%m-%d %H:%M')
                        st.caption(f"🕒 Added: {added_date}")
                    except:
                        pass
            
            with col3:
                st.markdown(f'<div class="price-tag">{item["price"]}</div>', unsafe_allow_html=True)
                
                # Show discount if available
                if item.get('discount'):
                    st.caption(item['discount'])
                
                # Show rating if available
                if item.get('rating'):
                    st.caption(item['rating'])
            
            with col4:
                # Buy button
                if item.get('url') and item['url'].strip():
                    st.link_button("🛒 Buy Now", item['url'], use_container_width=True)
                else:
                    st.write("🔗 No link")
                
                # Remove button
                if st.button("🗑️ Remove", key=f"remove_{i}", use_container_width=True):
                    st.session_state.shopping_list.pop(i)
                    st.success("Item removed!")
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Your shopping list is empty. Search for products to add items!")
        
        # Quick search suggestions from service
        st.subheader("💡 Quick Search Ideas")
        multi_agent_service, _ = init_services()
        if multi_agent_service:
            suggestions = multi_agent_service.get_popular_queries()[:6]
            
            cols = st.columns(3)
            for i, suggestion in enumerate(suggestions):
                with cols[i % 3]:
                    if st.button(suggestion, key=f"quick_suggest_{i}"):
                        # Switch to search tab with suggestion
                        st.session_state.search_query = suggestion
                        st.switch_page("streamlit_app.py")

def add_to_shopping_list(product):
    """Add product to shopping list with enhanced details"""
    # Check if already in list
    for item in st.session_state.shopping_list:
        if item.get('url') == product.get('url') and item.get('title') == product.get('title'):
            return  # Already in list
    
    # Add to list with enhanced details
    list_item = {
        'title': product.get('title', 'Product'),
        'description': product.get('description', 'No description available'),
        'price': product.get('price', 'N/A'),
        'url': product.get('url', ''),
        'source': product.get('source', 'Unknown'),
        'image': product.get('image', get_generic_product_image("", product.get('title', ''))),
        'discount': product.get('discount', ''),
        'rating': product.get('rating', ''),
        'delivery': product.get('delivery', ''),
        'brand': product.get('brand', ''),
        'size': product.get('size', ''),
        'added_at': datetime.now().isoformat()
    }
    
    st.session_state.shopping_list.append(list_item)

def export_shopping_list():
    """Export shopping list as text"""
    if not st.session_state.shopping_list:
        st.warning("No items to export")
        return
    
    # Create export text
    export_text = "🛒 My Shopping List\n"
    export_text += "=" * 30 + "\n\n"
    
    for i, item in enumerate(st.session_state.shopping_list, 1):
        export_text += f"{i}. {item['title']}\n"
        if item.get('description'):
            export_text += f"   📝 Description: {item['description'][:100]}...\n"
        export_text += f"   💰 Price: {item['price']}\n"
        export_text += f"   🏪 Store: {item['source']}\n"
        if item.get('url') and item['url'].strip():
            export_text += f"   🔗 Link: {item['url']}\n"
        if item.get('added_at'):
            try:
                added_date = datetime.fromisoformat(item['added_at']).strftime('%Y-%m-%d %H:%M')
                export_text += f"   🕒 Added: {added_date}\n"
            except:
                pass
        export_text += "\n"
    
    export_text += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    # Download button
    st.download_button(
        label="📥 Download Shopping List",
        data=export_text,
        file_name=f"shopping_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )

def show_provider_comparison(comparison_service):
    """Display the provider comparison interface"""
    st.header("📊 Compare Product Across Providers")
    st.caption("Compare prices, availability, and delivery options across major Indian e-commerce platforms")
    
    # Sample products for comparison
    sample_products = [
        "tomato", "onion", "potato", "milk", "bread", "rice", "apple", "banana",
        "tomatoes", "onions", "potatoes", "fresh milk", "white bread", "basmati rice"
    ]
    
    # Product input
    col1, col2 = st.columns([3, 1])
    with col1:
        product_name = st.text_input(
            "Enter product name to compare",
            placeholder="e.g., tomato, milk, bread, rice",
            label_visibility="collapsed"
        )
    with col2:
        if st.button("🔍 Compare", use_container_width=True):
            if product_name:
                st.session_state.comparison_product = product_name
                st.rerun()
    
    # Show sample products
    st.subheader("💡 Try these products:")
    cols = st.columns(4)
    for i, product in enumerate(sample_products):
        with cols[i % 4]:
            if st.button(product.title(), key=f"compare_{i}", use_container_width=True):
                st.session_state.comparison_product = product
                st.rerun()
    
    # Perform comparison if product is selected
    if st.session_state.get('comparison_product'):
        product_name = st.session_state.comparison_product
        
        with st.spinner(f"🔍 Comparing {product_name} across providers..."):
            try:
                comparison_results = comparison_service.compare_product_across_providers(product_name)
                
                if 'error' in comparison_results:
                    st.error(f"❌ Comparison failed: {comparison_results['error']}")
                    return
                
                # Display summary
                summary = comparison_results['summary']
                st.success(f"✅ Found {product_name} on {summary['available_providers']} out of {summary['total_providers']} providers")
                
                # Summary cards
                col1, col2, col3 = st.columns(3)
                with col1:
                    if summary['best_price']:
                        st.metric("🏆 Best Price", summary['best_price'], summary['best_provider'])
                    else:
                        st.metric("🏆 Best Price", "Not available")
                
                with col2:
                    if summary['fastest_delivery']:
                        st.metric("⚡ Fastest Delivery", summary['fastest_delivery'], summary['fastest_provider'])
                    else:
                        st.metric("⚡ Fastest Delivery", "Not available")
                
                with col3:
                    st.metric("📦 Available On", f"{summary['available_providers']} providers")
                
                st.divider()
                
                # Display analysis
                if comparison_results.get('analysis'):
                    st.markdown("### 🤖 AI Analysis")
                    st.write(comparison_results['analysis'])
                    st.divider()
                
                # Display provider results
                st.markdown("### 🏪 Provider Comparison")
                
                providers = comparison_results['providers']
                for provider_key, provider_data in providers.items():
                    provider_info = provider_data['provider_info']
                    
                    with st.expander(f"🏪 {provider_info['name']}", expanded=True):
                        if provider_data.get('availability'):
                            best_deal = provider_data.get('best_deal')
                            if best_deal:
                                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                                
                                with col1:
                                    st.markdown(f"**{best_deal['title']}**")
                                    st.caption(best_deal.get('snippet', 'No description'))
                                
                                with col2:
                                    st.markdown(f"**{best_deal['price']}**")
                                
                                with col3:
                                    if best_deal.get('rating'):
                                        st.markdown(f"⭐ {best_deal['rating']}")
                                    else:
                                        st.markdown("⭐ N/A")
                                
                                with col4:
                                    st.markdown(f"🚚 {best_deal.get('delivery', 'Standard')}")
                                
                                # Buy button
                                if best_deal.get('url'):
                                    st.link_button("🛒 Buy Now", best_deal['url'], use_container_width=True)
                            
                            # Show all products from this provider
                            if len(provider_data['products']) > 1:
                                st.markdown("**Other options:**")
                                for i, product in enumerate(provider_data['products'][1:3]):  # Show up to 2 more options
                                    col1, col2, col3 = st.columns([2, 1, 1])
                                    with col1:
                                        st.write(f"• {product['title'][:50]}...")
                                    with col2:
                                        st.write(product['price'])
                                    with col3:
                                        if product.get('rating'):
                                            st.write(f"⭐ {product['rating']}")
                        else:
                            st.warning("❌ Product not available on this provider")
                            if provider_data.get('error'):
                                st.caption(f"Error: {provider_data['error']}")
                
                # Add to shopping list button
                if st.button("➕ Add Best Deal to Shopping List", use_container_width=True):
                    best_provider = None
                    best_price = float('inf')
                    
                    for provider_key, provider_data in providers.items():
                        if provider_data.get('availability'):
                            best_deal = provider_data.get('best_deal')
                            if best_deal and best_deal.get('price'):
                                price_str = best_deal['price']
                                price_num = float(re.findall(r'₹(\d+)', price_str)[0]) if re.findall(r'₹(\d+)', price_str) else 999
                                if price_num < best_price:
                                    best_price = price_num
                                    best_provider = provider_data
                    
                    if best_provider:
                        best_deal = best_provider['best_deal']
                        add_to_shopping_list({
                            'title': best_deal['title'],
                            'description': best_deal.get('snippet', 'Best deal from comparison'),
                            'price': best_deal['price'],
                            'url': best_deal.get('url', ''),
                            'source': best_provider['provider_info']['name'],
                            'image': 'https://via.placeholder.com/150x150/667eea/FFFFFF?text=Best'
                        })
                        st.success("✅ Added best deal to shopping list!")
                        time.sleep(0.5)
                        st.rerun()
                
            except Exception as e:
                st.error(f"❌ Comparison failed: {e}")
                st.info("💡 This might be due to:")
                st.markdown("- Network connectivity issues")
                st.markdown("- Rate limiting from search providers")
                st.markdown("- Product not available on any provider")
                st.info("🔄 Try again with a different product")

def show_language_help():
    """Display language help and examples"""
    st.header("🌐 Language Support")
    st.write("This app supports both Hindi and English queries for shopping searches.")
    
    # Get language mappings from the service
    multi_agent_service, _ = init_services()
    if multi_agent_service:
        mappings = multi_agent_service.hindi_english_mappings
        
        # Categorize mappings
        categories = {
            'Vegetables & Fruits': ['tamatar', 'pyaaz', 'aloo', 'gajar', 'baingan', 'kheera', 'palak'],
            'Dairy & Groceries': ['doodh', 'paneer', 'ghee', 'atta', 'chawal', 'daal', 'chai'],
            'Electronics': ['mobile', 'laptop', 'computer', 'headphone', 'charger'],
            'Clothing': ['kapda', 'shirt', 'pant', 'shoes', 'bag']
        }
        
        st.subheader("🇮🇳 Hindi to English Translations")
        
        col1, col2 = st.columns(2)
        
        for i, (category, words) in enumerate(categories.items()):
            with col1 if i % 2 == 0 else col2:
                st.markdown(f"**{category}:**")
                for word in words:
                    if word in mappings:
                        st.write(f"• {word} → {mappings[word]}")
    
    st.subheader("💡 Tips")
    st.write("• You can mix Hindi and English in your searches")
    st.write("• Brand names are preserved (e.g., Amul, Samsung)")
    st.write("• Common misspellings are automatically corrected")
    st.write("• The app will show translation when Hindi is detected")

if __name__ == "__main__":
    main()