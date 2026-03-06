"""
API 集成模块 - 外部服务接入
"""
import requests
import json
from pathlib import Path

# 配置目录
CONFIG_DIR = Path("/root/.openclaw/workspace/memory-system/data")
CONFIG_FILE = CONFIG_DIR / "api_config.json"


def load_config() -> dict:
    """加载 API 配置"""
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}


def save_config(config: dict):
    """保存 API 配置"""
    CONFIG_DIR.mkdir(exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, ensure_ascii=False, indent=2))


# ========== GitHub API ==========

class GitHubAPI:
    """GitHub API 封装"""
    
    def __init__(self, token: str = ""):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
    
    def get_user(self):
        """获取用户信息"""
        resp = requests.get(f"{self.base_url}/user", headers=self.headers)
        return resp.json()
    
    def list_repos(self):
        """列出仓库"""
        resp = requests.get(f"{self.base_url}/user/repos", headers=self.headers)
        return resp.json()
    
    def get_repo(self, owner: str, repo: str):
        """获取仓库信息"""
        resp = requests.get(f"{self.base_url}/repos/{owner}/{repo}", headers=self.headers)
        return resp.json()
    
    def create_issue(self, owner: str, repo: str, title: str, body: str = ""):
        """创建 Issue"""
        resp = requests.post(
            f"{self.base_url}/repos/{owner}/{repo}/issues",
            headers=self.headers,
            json={"title": title, "body": body}
        )
        return resp.json()
    
    def list_issues(self, owner: str, repo: str):
        """列出 Issue"""
        resp = requests.get(
            f"{self.base_url}/repos/{owner}/{repo}/issues",
            headers=self.headers
        )
        return resp.json()


# ========== 天气 API ==========

class WeatherAPI:
    """天气 API (免费无需 key)"""
    
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1"
    
    def get_weather(self, lat: float = 39.9, lon: float = 116.4):
        """获取天气 (默认北京)"""
        url = f"{self.base_url}/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current_weather": "true",
            "hourly": "temperature_2m,relativehumidity_2m"
        }
        resp = requests.get(url, params=params)
        return resp.json()
    
    def get_current(self, city: str = "Beijing"):
        """简单获取当前天气"""
        city_coords = {
            "Beijing": (39.9, 116.4),
            "Shanghai": (31.2, 121.5),
            "Guangzhou": (23.1, 113.3),
            "Shenzhen": (22.5, 114.1)
        }
        coords = city_coords.get(city, (39.9, 116.4))
        return self.get_weather(coords[0], coords[1])


# ========== 翻译 API ==========

class TranslateAPI:
    """翻译 API (免费)"""
    
    def __init__(self):
        self.base_url = "https://api.mymemory.translated.net/get"
    
    def translate(self, text: str, lang_pair: str = "en|zh") -> str:
        """翻译文本"""
        params = {"q": text, "langpair": lang_pair}
        resp = requests.get(self.base_url, params=params)
        result = resp.json()
        if result.get("responseStatus") == 200:
            return result.get("responseData", {}).get("translatedText", "")
        return text


# ========== 搜索 API ==========

class SearchAPI:
    """搜索 API"""
    
    def __init__(self, token: str = ""):
        self.token = token
    
    def search_github(self, query: str) -> list:
        """GitHub 代码搜索"""
        url = "https://api.github.com/search/code"
        headers = {}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        
        resp = requests.get(url, params={"q": query}, headers=headers)
        data = resp.json()
        return data.get("items", [])[:5]


if __name__ == "__main__":
    # 测试
    print("=== API 集成测试 ===")
    
    # 天气测试
    print("\n🌤️ 天气测试:")
    weather = WeatherAPI()
    w = weather.get_current("Beijing")
    if "current_weather" in w:
        print(f"北京: {w['current_weather'].get('temperature')}°C")
    
    # 翻译测试
    print("\n🌐 翻译测试:")
    translate = TranslateAPI()
    result = translate.translate("Hello world", "en|zh")
    print(f"Hello world → {result}")
