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
                    
                    # Display products in a clean grid
                    for i, product in enumerate(products):
                        st.markdown("""
                        <div class="product-card">
                        """, unsafe_allow_html=True)
                        
                        col1, col2, col3, col4 = st.columns([1, 3, 1, 1])
                        
                        with col1:
                            # Product image
                            image_url = product.get('image', 'https://via.placeholder.com/150x150/667eea/FFFFFF?text=Product')
                            try:
                                st.image(image_url, width=100)
                            except:
                                st.image('https://via.placeholder.com/150x150/667eea/FFFFFF?text=Product', width=100)
                        
                        with col2:
                            st.markdown(f"**{product.get('title', 'Product')[:60]}**")
                            description = product.get('description', 'No description available')
                            if len(description) > 100:
                                description = description[:100] + "..."
                            st.write(description)
                            
                            # Source info
                            source = product.get('source', 'Unknown Store')
                            st.caption(f"📍 {source}")
                        
                        with col3:
                            price = product.get('price', 'Price not available')
                            st.markdown(f'<div class="price-tag">{price}</div>', unsafe_allow_html=True)
                            
                            # Relevance score
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
                # Product image
                image_url = item.get('image', 'https://via.placeholder.com/150x150/667eea/FFFFFF?text=Product')
                try:
                    st.image(image_url, width=100)
                except:
                    st.image('https://via.placeholder.com/150x150/667eea/FFFFFF?text=Product', width=100)
            
            with col2:
                st.markdown(f"**{item['title'][:60]}**")
                description = item.get('description', 'No description available')
                if len(description) > 80:
                    description = description[:80] + "..."
                st.write(description)
                st.caption(f"📍 {item['source']}")
                
                # Added date
                if item.get('added_at'):
                    try:
                        added_date = datetime.fromisoformat(item['added_at']).strftime('%Y-%m-%d %H:%M')
                        st.caption(f"🕒 Added: {added_date}")
                    except:
                        pass
            
            with col3:
                st.markdown(f'<div class="price-tag">{item["price"]}</div>', unsafe_allow_html=True)
            
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
    """Add product to shopping list"""
    # Check if already in list
    for item in st.session_state.shopping_list:
        if item.get('url') == product.get('url') and item.get('title') == product.get('title'):
            return  # Already in list
    
    # Add to list
    list_item = {
        'title': product.get('title', 'Product'),
        'description': product.get('description', 'No description available'),
        'price': product.get('price', 'N/A'),
        'url': product.get('url', ''),
        'source': product.get('source', 'Unknown'),
        'image': product.get('image', 'https://via.placeholder.com/150x150/667eea/FFFFFF?text=Product'),
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