import requests

def fetch_top_10000_models():
    """
    Fetches the top 10000 trending models from Hugging Face by paginating.
    Returns a list of dicts formatted similarly to our MatchScoreResult.
    """
    base_url = "https://huggingface.co/api/models"
    
    params = {
        "limit": 1000,
        "sort": "trendingScore",
        "direction": -1,
        "full": "False" # We just need basic metadata
    }
    
    all_results = []
    next_url = base_url
    
    try:
        # Loop up to 10 times to get 10,000 models
        for _ in range(10):
            if next_url == base_url:
                response = requests.get(next_url, params=params, timeout=15)
            else:
                response = requests.get(next_url, timeout=15)
                
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data:
                # Map HF metadata to our MatchScoreResult structure
                
                # Extract provider/author if available
                model_id = item.get("id", "")
                provider = model_id.split("/")[0] if "/" in model_id else "Community"
                name = model_id.split("/")[-1] if "/" in model_id else model_id
                
                # Find license from tags
                hf_tags_from_api = item.get("tags", [])
                license_val = "Open (Check HF Card)"
                for tag in hf_tags_from_api:
                    if tag.startswith("license:"):
                        license_val = tag.replace("license:", "").upper()
                        
                # Create a mock MatchScoreResult for UI compatibility
                mock_result = {
                    "is_hf_dynamic": True, # Flag to show HF badge
                    "model": {
                        "id": model_id,
                        "name": name,
                        "provider": provider,
                        "isModelOpenSource": True,
                        "licenseType": license_val,
                        "downloads": item.get("downloads", 0),
                        "likes": item.get("likes", 0),
                        "tags": hf_tags_from_api,
                        "createdAt": item.get("createdAt", "")
                    },
                    "overallScore": 85, # Default "good" score for trending models
                    "hardConstraintFailed": False,
                    "justification": {
                        "summary": "Dynamically fetched from Hugging Face Hub.",
                        "keyPros": [
                            f"{item.get('downloads', 0):,} recent downloads",
                            f"{item.get('likes', 0):,} community likes"
                        ],
                        "tradeOffs": ["Missing strict enterprise compliance guarantees", "Self-hosting required for data privacy"],
                        "governanceRationale": "Community-hosted weights. Review license for commercial use.",
                        "sovereigntyRationale": "Downloadable weights allow for 100% on-prem deployment."
                    }
                }
                results.append(mock_result)
                
            all_results.extend(results)
            
            # Check for next page
            link_header = response.headers.get("Link")
            if not link_header or 'rel="next"' not in link_header:
                break
                
            # Parse the next URL from the link header (e.g. '<https://...>; rel="next"')
            links = link_header.split(", ")
            next_link = [link for link in links if 'rel="next"' in link]
            if not next_link:
                break
                
            next_url = next_link[0].split(";")[0].strip("<>")
            
    except Exception as e:
        print(f"Error fetching from HF: {e}")
        
    return all_results
