"""
Data models and core infrastructure for multi-agent link analysis system.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class Platform(Enum):
    """Supported e-commerce platforms"""
    AMAZON_IN = "amazon.in"
    FLIPKART = "flipkart.com"
    MYNTRA = "myntra.com"
    SNAPDEAL = "snapdeal.com"
    BIGBASKET = "bigbasket.com"
    GENERIC = "generic"
    UNKNOWN = "unknown"


class ExtractionStatus(Enum):
    """Status of data extraction"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    FALLBACK = "fallback"


@dataclass
class ProductData:
    """Core product data model"""
    title: str
    url: str
    platform: Platform
    price: Optional[float] = None
    currency: str = "INR"
    original_price: Optional[float] = None
    discount_percentage: Optional[float] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    availability: str = "Unknown"
    image_urls: List[str] = field(default_factory=list)
    specifications: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    brand: Optional[str] = None
    category: Optional[str] = None
    seller: Optional[str] = None
    delivery_info: Optional[str] = None
    offers: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    extracted_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'title': self.title,
            'url': self.url,
            'platform': self.platform.value,
            'price': self.price,
            'currency': self.currency,
            'original_price': self.original_price,
            'discount_percentage': self.discount_percentage,
            'rating': self.rating,
            'review_count': self.review_count,
            'availability': self.availability,
            'image_urls': self.image_urls,
            'specifications': self.specifications,
            'description': self.description,
            'brand': self.brand,
            'category': self.category,
            'seller': self.seller,
            'delivery_info': self.delivery_info,
            'offers': self.offers,
            'features': self.features,
            'extracted_at': self.extracted_at.isoformat()
        }


@dataclass
class AnalysisResult:
    """Complete analysis result from multi-agent system"""
    product_data: ProductData
    price_analysis: Dict[str, Any] = field(default_factory=dict)
    review_analysis: Dict[str, Any] = field(default_factory=dict)
    spec_analysis: Dict[str, Any] = field(default_factory=dict)
    recommendations: str = ""
    value_score: float = 0.0
    confidence_score: float = 0.0
    extraction_status: ExtractionStatus = ExtractionStatus.FAILED
    errors: List[str] = field(default_factory=list)
    alternatives: List[Dict] = field(default_factory=list)
    processing_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'product_data': self.product_data.to_dict(),
            'price_analysis': self.price_analysis,
            'review_analysis': self.review_analysis,
            'spec_analysis': self.spec_analysis,
            'recommendations': self.recommendations,
            'value_score': self.value_score,
            'confidence_score': self.confidence_score,
            'extraction_status': self.extraction_status.value,
            'errors': self.errors,
            'alternatives': self.alternatives,
            'processing_time': self.processing_time
        }


class LinkAnalysisError(Exception):
    """Base exception for link analysis errors"""
    pass


class NetworkError(LinkAnalysisError):
    """Network-related errors"""
    pass


class AccessError(LinkAnalysisError):
    """Access-related errors (403, rate limiting, etc.)"""
    pass


class ParsingError(LinkAnalysisError):
    """HTML parsing and data extraction errors"""
    pass


class ValidationError(LinkAnalysisError):
    """URL and data validation errors"""
    pass


# Platform-specific configurations
PLATFORM_CONFIGS = {
    Platform.AMAZON_IN: {
        "selectors": {
            "title": [
                "#productTitle",
                ".product-title",
                "h1.a-size-large"
            ],
            "price": [
                ".a-price-whole",
                ".a-offscreen",
                "#priceblock_dealprice",
                "#priceblock_ourprice"
            ],
            "original_price": [
                ".a-price.a-text-price .a-offscreen",
                "#priceblock_listprice"
            ],
            "rating": [
                ".a-icon-alt",
                "[data-hook='average-star-rating'] .a-icon-alt",
                ".reviewCountTextLinkedHistogram .a-icon-alt"
            ],
            "review_count": [
                "#acrCustomerReviewText",
                "[data-hook='total-review-count']"
            ],
            "availability": [
                "#availability span",
                "#availability .a-color-success",
                "#availability .a-color-state"
            ],
            "image": [
                "#landingImage",
                "#imgBlkFront",
                ".a-dynamic-image"
            ],
            "specifications": [
                "#feature-bullets ul",
                "#productDetails_techSpec_section_1",
                ".a-unordered-list.a-vertical.a-spacing-mini"
            ],
            "description": [
                "#feature-bullets",
                "#productDescription",
                ".a-section.a-spacing-medium"
            ],
            "brand": [
                "#bylineInfo",
                ".a-link-normal#bylineInfo"
            ],
            "seller": [
                "#sellerProfileTriggerId",
                "#merchant-info"
            ]
        },
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        },
        "rate_limit": 2.0,
        "timeout": 10
    },
    
    Platform.FLIPKART: {
        "selectors": {
            "title": [
                ".B_NuCI",
                "h1.yhB1nd",
                ".x-product-title-label"
            ],
            "price": [
                "._30jeq3",
                "._1_WHN1",
                ".CEmiEU .srp-x-price"
            ],
            "original_price": [
                "._3I9_wc",
                "._14Jd01"
            ],
            "rating": [
                "._3LWZlK",
                ".hGSR34"
            ],
            "review_count": [
                "._2_R_DZ",
                ".row._2afbiS"
            ],
            "availability": [
                "._16FRp0",
                ".CEmiEU ._2aK_gu"
            ],
            "image": [
                "._396cs4",
                ".CXW8mj img",
                "._2r_T1I img"
            ],
            "specifications": [
                "._1mXcCf",
                ".row:has(._1hKmbr)"
            ],
            "description": [
                "._1mXcCf",
                ".IMZzTf"
            ],
            "brand": [
                ".G6XhBx",
                "._2B099V"
            ],
            "seller": [
                "._1fMR0A",
                ".sdN4QG"
            ]
        },
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        },
        "rate_limit": 1.5,
        "timeout": 10
    },
    
    Platform.GENERIC: {
        "selectors": {
            "title": [
                "h1",
                ".product-title",
                "[itemprop='name']",
                ".title"
            ],
            "price": [
                "[itemprop='price']",
                ".price",
                ".product-price",
                ".cost"
            ],
            "rating": [
                "[itemprop='ratingValue']",
                ".rating",
                ".stars"
            ],
            "image": [
                "[itemprop='image']",
                ".product-image img",
                ".main-image img"
            ],
            "description": [
                "[itemprop='description']",
                ".product-description",
                ".description"
            ]
        },
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        },
        "rate_limit": 1.0,
        "timeout": 8
    }
}


def get_platform_from_url(url: str) -> Platform:
    """Determine platform from URL"""
    url_lower = url.lower()
    
    if 'amazon.in' in url_lower:
        return Platform.AMAZON_IN
    elif 'flipkart.com' in url_lower:
        return Platform.FLIPKART
    elif 'myntra.com' in url_lower:
        return Platform.MYNTRA
    elif 'snapdeal.com' in url_lower:
        return Platform.SNAPDEAL
    elif 'bigbasket.com' in url_lower:
        return Platform.BIGBASKET
    else:
        return Platform.GENERIC


def validate_url(url: str) -> bool:
    """Basic URL validation"""
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None


def clean_text(text: str) -> str:
    """Clean extracted text"""
    if not text:
        return ""
    
    import re
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\-.,()₹$%/]', '', text)
    return text


def extract_price_from_text(text: str) -> Optional[float]:
    """Extract price from text string"""
    if not text:
        return None
    
    import re
    # Remove currency symbols and commas
    price_text = re.sub(r'[₹$,]', '', text)
    
    # Find price patterns
    price_patterns = [
        r'(\d+(?:\.\d{2})?)',  # Simple decimal
        r'(\d+(?:,\d+)*(?:\.\d{2})?)'  # With commas
    ]
    
    for pattern in price_patterns:
        match = re.search(pattern, price_text)
        if match:
            try:
                price_str = match.group(1).replace(',', '')
                return float(price_str)
            except ValueError:
                continue
    
    return None


def extract_rating_from_text(text: str) -> Optional[float]:
    """Extract rating from text string"""
    if not text:
        return None
    
    import re
    # Look for rating patterns like "4.5 out of 5" or "4.5/5"
    rating_patterns = [
        r'(\d+\.?\d*)\s*out\s*of\s*5',
        r'(\d+\.?\d*)\s*/\s*5',
        r'(\d+\.?\d*)\s*stars?',
        r'(\d+\.?\d*)'
    ]
    
    for pattern in rating_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                rating = float(match.group(1))
                if 0 <= rating <= 5:
                    return rating
            except ValueError:
                continue
    
    return None