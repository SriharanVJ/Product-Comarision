"""
Capture and inspect the raw QuickCommerce API response structure
"""

import asyncio
import json
import os
from dotenv import load_dotenv
import httpx

load_dotenv()

async def capture_response():
    """Capture raw API response for inspection"""

    api_key = os.getenv("QUICKCOMMERCE_API_KEY")
    base_url = os.getenv("QUICKCOMMERCE_BASE_URL", "https://api.quickcommerceapi.com")

    url = f"{base_url}/v1/groupsearch"
    params = {
        "q": "milk",
        "lat": 13.0827,
        "lon": 80.2707,
        "platforms": "BlinkIt,Zepto,Swiggy",
    }
    headers = {
        "X-API-Key": api_key,
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url, params=params, headers=headers)
        data = response.json()

        # Save raw response to file for inspection
        with open("api_response_sample.json", "w") as f:
            json.dump(data, f, indent=2)

        print("=" * 60)
        print("RAW API RESPONSE STRUCTURE")
        print("=" * 60)
        print(json.dumps(data, indent=2))

        # Print structure overview
        print("\n" + "=" * 60)
        print("RESPONSE STRUCTURE OVERVIEW")
        print("=" * 60)
        print(f"Status: {data.get('status')}")
        print(f"Request ID: {data.get('request_id')}")

        data_section = data.get("data", {})
        print(f"\nQuery: {data_section.get('query')}")
        print(f"Platforms: {data_section.get('platforms')}")
        print(f"Credit cost: {data_section.get('credit_cost')}")

        results = data_section.get("results", {})

        for platform, items in results.items():
            print(f"\n{'=' * 40}")
            print(f"Platform: {platform}")
            print(f"Items count: {len(items)}")

            if items:
                print(f"\nFirst item keys: {list(items[0].keys())}")
                print(f"\nFirst item sample:")
                print(json.dumps(items[0], indent=2))

                # Check for variations
                print(f"\nChecking for field variations across {len(items)} items...")
                all_keys = set()
                for item in items:
                    all_keys.update(item.keys())

                print(f"All unique keys in {platform}: {sorted(all_keys)}")

                # Check if different items have different nested structures
                if items and len(items) > 1:
                    print(f"\nComparing first 3 items...")
                    for i, item in enumerate(items[:3]):
                        print(f"\nItem {i+1}:")
                        for key in sorted(all_keys):
                            value = item.get(key)
                            if isinstance(value, dict):
                                print(f"  {key}: {{dict}}")
                            elif isinstance(value, list):
                                print(f"  {key}: [{len(value)} items]")
                            else:
                                print(f"  {key}: {value}")

if __name__ == "__main__":
    asyncio.run(capture_response())
