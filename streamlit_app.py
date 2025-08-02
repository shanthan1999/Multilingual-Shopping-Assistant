import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import time
import os
import sys
import hashlib

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the services directly
try:
    from src.services.multi_agent_shopping import MultiAgentShoppingSearch
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Initialize services
@st.cache_resource
def init_services():
    """Initialize services"""
    try:
        multi_agent_service = MultiAgentShoppingSearch()
        return multi_agent_service
    except Exception as e:
        st.error(f"Failed to initialize Multi-Agent shopping service: {e}")
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
    multi_agent_service = init_services()
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Product Search", "🔗 Link Analysis", "📊 Compare Products", "🌐 Language Help"])
    
    with tab1:
        show_product_search(multi_agent_service)
    
    with tab2:
        show_link_analysis(multi_agent_service)
    
    with tab3:
        show_product_comparison(multi_agent_service)
    
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
                        
                        col1, col2, col3 = st.columns([3, 1, 1])
                        
                        with col1:
                            st.markdown(f"**{product.get('title', 'Product')[:80]}**")
                            description = product.get('description', 'No description available')
                            if len(description) > 120:
                                description = description[:120] + "..."
                            st.write(description)
                            
                            # Source info
                            source = product.get('source', 'Unknown Store')
                            st.caption(f"📍 {source}")
                        
                        with col2:
                            price = product.get('price', 'Price not available')
                            st.markdown(f'<div class="price-tag">{price}</div>', unsafe_allow_html=True)
                            
                            # Relevance score
                            score = product.get('score', 0)
                            st.caption(f"⭐ {score:.1f}/10")
                        
                        with col3:
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
                st.error(f"Search failed: {e}")
                st.stop()

def show_link_analysis(multi_agent_service):
    """Display link analysis interface"""
    st.header("🔗 Product Link Analysis")
    st.caption("Analyze product links and extract detailed information")
    
    # Link input
    col1, col2 = st.columns([4, 1])
    with col1:
        product_link = st.text_input(
            "Product Link",
            placeholder="Paste a product link from Amazon, Flipkart, etc.",
            label_visibility="collapsed"
        )
    with col2:
        if st.button("🔍 Analyze", use_container_width=True):
            if product_link:
                analyze_product_link(multi_agent_service, product_link)
            else:
                st.warning("Please enter a product link")

def show_product_comparison(multi_agent_service):
    """Display product comparison interface"""
    st.header("📊 Product Comparison")
    st.caption("Compare multiple products side by side")
    
    # Product links input
    st.subheader("Enter Product Links")
    col1, col2 = st.columns(2)
    
    with col1:
        link1 = st.text_input("Product 1 Link", placeholder="First product link")
    with col2:
        link2 = st.text_input("Product 2 Link", placeholder="Second product link")
    
    # Additional links
    col3, col4 = st.columns(2)
    with col3:
        link3 = st.text_input("Product 3 Link", placeholder="Third product link (optional)")
    with col4:
        link4 = st.text_input("Product 4 Link", placeholder="Fourth product link (optional)")
    
    if st.button("📊 Compare Products", use_container_width=True):
        links = [link for link in [link1, link2, link3, link4] if link.strip()]
        if len(links) >= 2:
            compare_products(multi_agent_service, links)
        else:
            st.warning("Please enter at least 2 product links")

def analyze_product_link(multi_agent_service, link):
    """Analyze a single product link"""
    with st.spinner("🔍 Analyzing product link..."):
        try:
            # Extract product info from link
            product_info = extract_product_from_link(link)
            
            if product_info:
                st.success("✅ Product link analyzed successfully!")
                
                # Display product information
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**Product:** {product_info.get('title', 'Unknown')}")
                    st.markdown(f"**Store:** {product_info.get('store', 'Unknown')}")
                    st.markdown(f"**Price:** {product_info.get('price', 'Not available')}")
                
                with col2:
                    if product_info.get('image'):
                        st.image(product_info['image'], width=150)
                
                # Get AI analysis
                analysis = get_product_analysis(multi_agent_service, product_info)
                st.markdown("### 🤖 AI Analysis")
                st.write(analysis)
                
            else:
                st.error("❌ Could not extract product information from the link")
                
        except Exception as e:
            st.error(f"Link analysis failed: {e}")
            st.stop()

def compare_products(multi_agent_service, links):
    """Compare multiple products"""
    with st.spinner("📊 Comparing products..."):
        try:
            products = []
            for i, link in enumerate(links):
                product_info = extract_product_from_link(link)
                if product_info:
                    products.append(product_info)
            
            if len(products) >= 2:
                st.success(f"✅ Successfully analyzed {len(products)} products!")
                
                # Display comparison table
                st.markdown("### 📊 Product Comparison")
                comparison_data = []
                for product in products:
                    comparison_data.append({
                        'Product': product.get('title', 'Unknown')[:50] + '...',
                        'Store': product.get('store', 'Unknown'),
                        'Price': product.get('price', 'N/A'),
                        'Rating': product.get('rating', 'N/A'),
                        'Availability': product.get('availability', 'Unknown')
                    })
                
                df = pd.DataFrame(comparison_data)
                st.dataframe(df, use_container_width=True)
                
                # Get AI comparison analysis
                comparison_analysis = get_comparison_analysis(multi_agent_service, products)
                st.markdown("### 🤖 AI Comparison Analysis")
                st.write(comparison_analysis)
                
            else:
                st.error("❌ Could not analyze enough products for comparison")
                
        except Exception as e:
            st.error(f"Product comparison failed: {e}")
            st.stop()

def extract_product_from_link(link):
    """Extract product information from a link"""
    try:
        from src.services.link_analysis_models import get_platform_from_url, validate_url
        
        if not validate_url(link):
            raise ValueError("Invalid URL format")
        
        platform = get_platform_from_url(link)
        
        # Use actual web scraping to extract product information
        import requests
        from bs4 import BeautifulSoup
        from urllib.parse import urlparse
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(link, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract basic information
        title = soup.find('title').get_text().strip() if soup.find('title') else 'Product'
        
        # Extract domain for store name
        parsed = urlparse(link)
        domain = parsed.netloc.replace('www.', '')
        
        return {
            'title': title,
            'store': domain,
            'price': 'Check website',
            'rating': 'Not available',
            'availability': 'Check website',
            'image': None
        }
        
    except Exception as e:
        raise Exception(f"Failed to extract product information: {e}")

def get_product_analysis(multi_agent_service, product_info):
    """Get AI analysis for a single product"""
    prompt = f"""
    Analyze this product information and provide insights:
    
    Product: {product_info.get('title', 'Unknown')}
    Store: {product_info.get('store', 'Unknown')}
    Price: {product_info.get('price', 'Not available')}
    Rating: {product_info.get('rating', 'Not available')}
    Availability: {product_info.get('availability', 'Unknown')}
    
    Please provide:
    1. Price analysis and value assessment
    2. Store reputation and reliability
    3. Product quality indicators
    4. Shopping recommendations
    5. Alternative suggestions
    
    Format with emojis and clear sections.
    """
    
    response = multi_agent_service.model.generate_content(prompt)
    return response.text

def get_comparison_analysis(multi_agent_service, products):
    """Get AI analysis for product comparison"""
    products_text = ""
    for i, product in enumerate(products, 1):
        products_text += f"""
        Product {i}:
        - Name: {product.get('title', 'Unknown')}
        - Store: {product.get('store', 'Unknown')}
        - Price: {product.get('price', 'Not available')}
        - Rating: {product.get('rating', 'Not available')}
        - Availability: {product.get('availability', 'Unknown')}
        """
    
    prompt = f"""
    Compare these products and provide analysis:
    
    {products_text}
    
    Please provide:
    1. Price comparison and best value
    2. Quality comparison based on ratings
    3. Store comparison and reliability
    4. Overall recommendation
    5. Pros and cons for each option
    
    Format with emojis and clear comparison table.
    """
    
    response = multi_agent_service.model.generate_content(prompt)
    return response.text

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
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"**{item['title'][:60]}**")
                    st.caption(f"📍 {item['source']}")
                
                with col2:
                    st.markdown(f'<div class="price-tag">{item["price"]}</div>', unsafe_allow_html=True)
                
                with col3:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if item.get('url'):
                            st.link_button("🛒", item['url'], help="Buy Now")
                    with col_b:
                        if st.button("🗑️", key=f"remove_{i}", help="Remove"):
                            st.session_state.shopping_list.pop(i)
                            st.rerun()
                
                st.divider()
    else:
        st.info("Your shopping list is empty. Search for products to add items!")
        
        # Quick search suggestions from service
        st.subheader("💡 Quick Search Ideas")
        multi_agent_service = init_services()
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
        if item.get('url') == product.get('url'):
            return  # Already in list
    
    # Add to list
    list_item = {
        'title': product.get('title', 'Product'),
        'price': product.get('price', 'N/A'),
        'url': product.get('url', ''),
        'source': product.get('source', 'Unknown'),
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
        export_text += f"   💰 Price: {item['price']}\n"
        export_text += f"   🏪 Store: {item['source']}\n"
        if item.get('url'):
            export_text += f"   🔗 Link: {item['url']}\n"
        export_text += "\n"
    
    export_text += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    # Download button
    st.download_button(
        label="📥 Download Shopping List",
        data=export_text,
        file_name=f"shopping_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )

def show_language_help():
    """Display language help and examples"""
    st.header("🌐 Language Support")
    st.write("This app supports both Hindi and English queries for shopping searches.")
    
    # Get language mappings from the service
    multi_agent_service = init_services()
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