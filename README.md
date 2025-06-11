# VINEWS

An open-source library dedicated to searching and scraping Vietnamese news websites with the goal of providing tools and enhancing AI agents news searching capabilities.

**Note**: This library is still under active development. Expect bugs and incomplete features. Contributions are welcome and appreciated!

## Disclaimer & Terms of Use ‼️

This library is provided for **educational and research purposes only**. You are solely responsible for how you use it. Before scraping any website, you must ensure that your actions comply with all applicable laws and the website’s own policies — including their **Terms of Service** and `robots.txt` directives. Many websites explicitly prohibit automated access. The authors and contributors are not responsible for any misuse or legal issues arising from the use of this tool. Always scrape ethically, respectfully, and within legal boundaries.

## Responsible Scraping ‼️

Please be respectful of the websites you interact with. Always use appropriate rate limiting and avoid sending excessive requests. Scraping should never disrupt or degrade the performance of a website. Generating unreasonable traffic may not only lead to IP bans but could also violate legal or ethical standards. Respect the site's resources, policies, and the efforts of its creators.

## Supported Websites

- **VnExpress**
- *more coming soon...*

## Installation

```bash
pip install vinews==0.1.0b4
```

## Quick Start

```python
from vinews.modules.vnexpress.search import VinewsVnExpressSearch
import asyncio
import json

search_engine = VinewsVnExpressSearch()
query = "Bitcoin"
    
# Test synchronous search
results = search_engine.search(query=query, date_range="day", category="kinhdoanh", limit=5, advanced=True)
print(results)

homepage = search_engine.search_homepage()
print(homepage)    

def vinews_async():
    # Test asynchronous search
    async def async_test():
        async_results = await search_engine.async_search(query=query, date_range="day", category="kinhdoanh", limit=5, advanced=True)
        
        async_homepage = await search_engine.async_search_homepage()

        # Optional saving
        with open("tests/output/vnexpress_search.json", "w", encoding="utf-8") as f:
            json.dump(async_results.model_dump(), f, indent=2, ensure_ascii=False)
        
        with open("tests/output/vnexpress_homepage.json", "w", encoding="utf-8") as f:
            json.dump(async_homepage.model_dump(), f, indent=2, ensure_ascii=False)
    
    asyncio.run(async_test())

if __name__ == "__main__":
    vinews_async()
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the Apache 2.0 - see the `LICENSE` file for details.
