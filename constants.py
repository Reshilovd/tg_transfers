from typing import Dict, Any

from fake_useragent import UserAgent

user_agent = UserAgent()

store = {
    'leagues': {},
    'clubs': {},
    'clubs_leagues': {}
}

headers: dict[str, Any] = {'User-Agent': user_agent.chrome}
