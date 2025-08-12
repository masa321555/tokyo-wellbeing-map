import httpx
from typing import Dict, List, Optional, Any
import json
from urllib.parse import urljoin
import asyncio
from datetime import datetime, timedelta

from app.core.config import settings


class TokyoOpenDataClient:
    """東京都オープンデータカタログAPIクライアント"""
    
    def __init__(self):
        self.base_url = settings.TOKYO_OPENDATA_API_URL
        self.api_key = settings.TOKYO_OPENDATA_API_KEY
        self.timeout = 30.0
        self._client = None
        self._cache = {}
        self._cache_expiry = {}
        
    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            headers = {"User-Agent": "TokyoWellbeingMap/1.0"}
            if self.api_key:
                headers["Authorization"] = self.api_key
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                headers=headers
            )
        return self._client
    
    async def close(self):
        if self._client:
            await self._client.aclose()
            
    def _get_cache_key(self, endpoint: str, params: Optional[Dict] = None) -> str:
        """キャッシュキーを生成"""
        param_str = json.dumps(params or {}, sort_keys=True)
        return f"{endpoint}:{param_str}"
    
    def _is_cache_valid(self, key: str) -> bool:
        """キャッシュが有効かチェック"""
        return key in self._cache and self._cache_expiry.get(key, datetime.min) > datetime.now()
    
    async def _request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """APIリクエストの実行"""
        cache_key = self._get_cache_key(endpoint, params)
        
        # キャッシュチェック
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        url = urljoin(self.base_url, endpoint)
        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # キャッシュに保存（1時間）
            self._cache[cache_key] = data
            self._cache_expiry[cache_key] = datetime.now() + timedelta(hours=1)
            
            return data
        except httpx.HTTPStatusError as e:
            raise Exception(f"API request failed: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"API request error: {str(e)}")
    
    async def package_list(self) -> List[str]:
        """データセット一覧を取得"""
        data = await self._request("action/package_list")
        return data.get("result", [])
    
    async def package_search(self, query: str = "", rows: int = 100, 
                           start: int = 0, fq: Optional[str] = None) -> Dict:
        """データセットを検索"""
        params = {
            "q": query,
            "rows": rows,
            "start": start
        }
        if fq:
            params["fq"] = fq
            
        data = await self._request("action/package_search", params)
        return data.get("result", {})
    
    async def package_show(self, id: str) -> Dict:
        """データセットの詳細を取得"""
        params = {"id": id}
        data = await self._request("action/package_show", params)
        return data.get("result", {})
    
    async def resource_show(self, id: str) -> Dict:
        """リソースの詳細を取得"""
        params = {"id": id}
        data = await self._request("action/resource_show", params)
        return data.get("result", {})
    
    async def group_list(self) -> List[str]:
        """グループ一覧を取得"""
        data = await self._request("action/group_list")
        return data.get("result", [])
    
    async def organization_list(self) -> List[str]:
        """組織一覧を取得"""
        data = await self._request("action/organization_list")
        return data.get("result", [])
    
    async def tag_list(self) -> List[str]:
        """タグ一覧を取得"""
        data = await self._request("action/tag_list")
        return data.get("result", [])
    
    async def get_dataset_by_category(self, category: str) -> List[Dict]:
        """カテゴリ別にデータセットを取得"""
        # カテゴリマッピング
        category_map = {
            "housing": ["住宅", "不動産", "家賃"],
            "parks": ["公園", "緑地", "広場"],
            "education": ["学校", "教育", "保育"],
            "safety": ["治安", "犯罪", "防犯"],
            "medical": ["医療", "病院", "診療所"],
            "culture": ["文化", "図書館", "美術館"],
            "childcare": ["子育て", "保育園", "待機児童"]
        }
        
        search_terms = category_map.get(category, [category])
        all_results = []
        
        for term in search_terms:
            result = await self.package_search(query=term, rows=50)
            all_results.extend(result.get("results", []))
        
        # 重複を除去
        unique_results = {r["id"]: r for r in all_results}
        return list(unique_results.values())
    
    async def download_resource(self, resource_url: str) -> bytes:
        """リソースファイルをダウンロード"""
        async with httpx.AsyncClient() as client:
            response = await client.get(resource_url)
            response.raise_for_status()
            return response.content


# シングルトンインスタンス
tokyo_opendata_client = TokyoOpenDataClient()