from dagster import ConfigurableResource
import os
from pydantic import Field

class BrowserbaseResource(ConfigurableResource):
    """Browserbase resource for Dagster pipelines, providing headless browser automation capabilities."""
    api_key: str = Field(description="Browserbase API Key", default="")
    project_id: str = Field(description="Browserbase Project ID", default="")

    def get_credentials(self) -> dict:
        """Retrieve credentials prioritizing configured values, falling back to environment variables injected via Infisical."""
        key = self.api_key or os.getenv("BROWSERBASE_API_KEY", "")
        proj = self.project_id or os.getenv("BROWSERBASE_PROJECT_ID", "")
        
        if not key or not proj:
            raise ValueError("BROWSERBASE_API_KEY and BROWSERBASE_PROJECT_ID must be configured or available in environment")
            
        return {"api_key": key, "project_id": proj}

# Singleton instance ready to be injected into assets
browserbase_resource = BrowserbaseResource()
