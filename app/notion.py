import httpx
from typing import List, Dict, Any
from .settings import settings


class NotionAPI:
    def __init__(self):
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {settings.notion_api_token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
    
    async def get_page(self, page_id: str) -> Dict[str, Any]:
        """Fetch a Notion page by ID."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/pages/{page_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
    
    async def get_block_children(self, block_id: str, page_size: int = 100) -> List[Dict[str, Any]]:
        """Fetch all children blocks for a given block ID with pagination."""
        all_blocks = []
        start_cursor = None
        
        async with httpx.AsyncClient() as client:
            while True:
                params = {"page_size": page_size}
                if start_cursor:
                    params["start_cursor"] = start_cursor
                
                response = await client.get(
                    f"{self.base_url}/blocks/{block_id}/children",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                all_blocks.extend(data["results"])
                
                if not data.get("has_more"):
                    break
                start_cursor = data.get("next_cursor")
        
        return all_blocks
    
    def extract_relation_ids(self, page_props: Dict[str, Any], relation_name: str) -> List[str]:
        """Extract page IDs from a relation property."""
        relation_prop = page_props.get("properties", {}).get(relation_name, {})
        if relation_prop.get("type") != "relation":
            return []
        
        return [item["id"] for item in relation_prop.get("relation", [])]
    
    async def update_page_url_property(self, page_id: str, prop_name: str, url: str) -> None:
        """Update a URL property on a Notion page."""
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/pages/{page_id}",
                headers=self.headers,
                json={
                    "properties": {
                        prop_name: {
                            "url": url
                        }
                    }
                }
            )
            response.raise_for_status()


# Global instance
notion_api = NotionAPI()
