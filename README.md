# MultiAgent Shopping Assistant Chat

An advanced agentic RAG-powered shopping application built with Streamlit that helps users find, compare, and analyze products from various online stores using web data, link analysis, and intelligent multi-agent recommendations. **Now with Hindi language support!**

## Features

- 🤖 **Multi-Agent Shopping System**: Specialized AI agents for different shopping tasks
- 🔍 **Agentic RAG Product Search**: Web data-powered search using Google Gemini and Serper
- 🔗 **Link Analysis**: Extract and analyze product information from direct links
- 📊 **Product Comparison**: Side-by-side comparison of multiple products
- 🌐 **Hindi Language Support**: Search in Hindi or English with automatic translation
- 🤖 **AI Shopping Assistant**: Get intelligent insights and recommendations
- 💰 **Price Comparison**: Compare prices across different retailers
- 🛒 **Direct Purchase Links**: Click to buy products directly from stores
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 💡 **Smart Suggestions**: Get search suggestions as you type

### Multi-Agent System Components

- **🔄 Translation Agent**: Hindi to English translation specialist
- **🔍 Search Agent**: Product information extraction and analysis
- **💰 Price Analysis Agent**: Price comparison and value analysis
- **🚚 Delivery Analysis Agent**: Delivery options and timing analysis
- **🎯 Recommendation Agent**: Final recommendations and shopping tips
- **🔗 Link Analysis Agent**: Extract product data from URLs
- **📊 Comparison Agent**: Compare multiple products intelligently

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd regional-shopping-ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create a .env file with your API keys
   cp .env.example .env
   # Edit .env and add your Tavily API key
   ```

4. **Run the application**
   ```bash
   python run_streamlit.py
   ```
   
   Or directly with Streamlit:
   ```bash
   streamlit run streamlit_app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8501`

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
SERPER_API_KEY=your_serper_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

### Getting API Keys

#### Serper API Key
1. **Visit Serper**: Go to [https://serper.dev/](https://serper.dev/)
2. **Sign Up**: Create a free account
3. **Get API Key**: Copy your API key from the dashboard
4. **Update .env**: Replace `your_serper_api_key_here` with your actual API key

#### Google API Key (for Gemini)
1. **Visit Google AI Studio**: Go to [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
2. **Sign In**: Use your Google account
3. **Create API Key**: Click "Create API Key" and copy the key
4. **Update .env**: Replace `your_google_api_key_here` with your actual API key

## Usage

1. **Product Search**: Use the search bar to find products in Hindi or English
    - Try: "tamatar" (tomato), "doodh" (milk), "mobile", "laptop"
2. **Link Analysis**: Paste product links to get detailed analysis
    - Supports Amazon, Flipkart, and other major e-commerce sites
3. **Product Comparison**: Compare multiple products side by side
    - Enter 2-4 product links for intelligent comparison
4. **AI Insights**: Get intelligent recommendations and price analysis from the AI assistant
5. **Language Help**: Check the "Language Help" tab for Hindi-English translations

## Deployment

### Local Development
```bash
streamlit run streamlit_app.py
```

### Streamlit Cloud Deployment
1. Push your code to GitHub
2. Connect your repository to [Streamlit Cloud](https://streamlit.io/cloud)
3. Set your environment variables in the Streamlit Cloud dashboard
4. Deploy!

### Heroku Deployment
1. Create a `Procfile`:
   ```
   web: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
   ```
2. Deploy to Heroku using their standard Python deployment process

## Project Structure

```
multiagent-shopping-assistant/
├── streamlit_app.py          # Main Streamlit application
├── run_streamlit.py          # Streamlit runner script
├── requirements.txt          # Python dependencies
├── README.md                # This file
├── .env.example             # Environment variables template
└── src/
    ├── services/
    │   ├── multi_agent_shopping.py    # Multi-agent shopping system
    │   ├── rag_shopping_search.py     # RAG service with Gemini and Serper
    │   ├── hindi_shopping_search.py   # Hindi-English shopping search service
    │   └── serper_shopping_search.py  # Serper Google search service
    └── data/                # Data files (if any)
```

## Dependencies

- **Streamlit**: Web application framework
- **Requests**: HTTP library for API calls
- **Pandas**: Data manipulation
- **Google Generative AI**: Gemini AI integration
- **BeautifulSoup**: Web scraping utilities

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the application
5. Submit a pull request

## License

This project is licensed under the MIT License.
