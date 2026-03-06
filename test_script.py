import time
from system_actions import get_installed_apps, fetch_info

def test():
    print("Testing App Discovery...")
    apps = get_installed_apps()
    print(f"Discovered {len(apps)} apps.")
    if "chrome" in apps:
        print("Chrome found:", apps["chrome"])
    else:
        print("Chrome not found :(")
        
    print("\nTesting Web Search...")
    query = "Who is the CEO of Tesla?"
    print(f"Query: {query}")
    answer = fetch_info(query)
    print(f"Answer: {answer}")

    print("\nTesting Web Search Fallback (DuckDuckGo HTML)...")
    query2 = "latest spatial computing headset apple name"
    print(f"Query: {query2}")
    answer2 = fetch_info(query2)
    print(f"Answer: {answer2}")

if __name__ == "__main__":
    test()
