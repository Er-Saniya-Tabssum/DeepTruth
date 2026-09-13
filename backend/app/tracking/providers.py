import os
from typing import List, Optional, Dict, Any

TRACKING_PROVIDER = os.getenv('TRACKING_PROVIDER', '').upper()
TRACKING_API_KEY = os.getenv('TRACKING_API_KEY', '')


class TrackingProvider:
    """Base interface for tracking providers."""
    name = 'BASE'

    def search(self, *, image_bytes: Optional[bytes] = None, image_url: Optional[str] = None, timeout: int = 30) -> List[Dict[str, Any]]:
        """Perform a search. Must return a list of result dicts.
        Each dict should only contain fields actually returned by the provider.
        Example fields: match_url, source_domain, page_title, thumbnail_url, match_score, first_seen, last_seen
        """
        raise NotImplementedError()


class MockTrackingProvider(TrackingProvider):
    name = 'MOCK'

    def search(self, *, image_bytes: Optional[bytes] = None, image_url: Optional[str] = None, timeout: int = 30):
        # Only return mock/demo results when explicitly configured (TRACKING_PROVIDER=MOCK).
        # Do NOT use mock results in production environments.
        return [
            {
                'match_url': 'https://example.com/sample-image-page',
                'source_domain': 'example.com',
                'page_title': 'Example Sample Page',
                'thumbnail_url': None,
                'match_score': 0.92,
                'first_seen': None,
                'last_seen': None,
            }
        ]


def get_provider() -> Optional[TrackingProvider]:
    provider = TRACKING_PROVIDER
    if not provider:
        return None
    if provider == 'MOCK':
        return MockTrackingProvider()
    # Placeholder for future providers: e.g. 'TINEYE', 'BING', etc.
    return None
