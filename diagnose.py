"""
Diagnose-script: tester hva et enkelt requests-kall faktisk far tilbake
fra de tre kamp-spesifikke resale-lenkene. Kjores en gang, resultatet
vises i Actions-loggen. Ikke ment for fast bruk.
"""
 
import requests
 
URLS = [
    "https://resale.fotball.no/selection/resale/item?performanceId=10229739913108&checkResaleAvailability=true",
    "https://resale.fotball.no/selection/resale/item?performanceId=10229739913107&checkResaleAvailability=true",
    "https://resale.fotball.no/selection/resale/item?performanceId=10229739913106&checkResaleAvailability=true",
]
 
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "no,en;q=0.8",
}
 
 
def main():
    session = requests.Session()
 
    for url in URLS:
        print("=" * 70)
        print(f"URL: {url}")
        try:
            resp = session.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
            print(f"Status code: {resp.status_code}")
            print(f"Final URL after redirects: {resp.url}")
            print(f"Content length: {len(resp.text)} characters")
            print("First 500 characters of response:")
            print(resp.text[:500])
            print("...")
            # Sjekk om noen kjente nokkeltekster finnes
            for phrase in [
                "no tickets", "ingen billetter", "resale", "Sold out",
                "utsolgt", "checkResaleAvailability", "waitingroom", "venterom",
            ]:
                if phrase.lower() in resp.text.lower():
                    print(f'  -> Fant mulig nokkeltekst: "{phrase}"')
        except Exception as e:
            print(f"FEIL ved henting: {e}")
        print()
 
 
if __name__ == "__main__":
    main()
 
