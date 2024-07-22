import dlt
from rest_api import RESTAPIConfig, rest_api_source

from dlt.sources.helpers.rest_client.paginators import BasePaginator, JSONResponsePaginator
from dlt.sources.helpers.requests import Response, Request

from dlt.destinations.adapters import lancedb_adapter

from datetime import datetime, timezone
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class PostBodyPaginator(BasePaginator):
    def __init__(self):
        super().__init__()
        self.cursor = None

    def update_state(self, response: Response) -> None:
        logging.info("Updating paginator state.")
        if not response.json():
            self._has_next_page = False
        else:
            self.cursor = response.json().get("next_cursor")
            if self.cursor is None:
                self._has_next_page = False
            logging.info(f"Paginator cursor updated to: {self.cursor}")
    
    def update_request(self, request: Request) -> None:
        logging.info(f"Paginator cursor updated to: {self.cursor}")
        if request.json is None:
            request.json = {}

            request.json["start_cursor"] = self.cursor
            logging.info(f"Request JSON updated: {request.json}")

@dlt.resource(name="employee_handbook")
def rest_api_notion_resource():
    logging.info("Setting up Notion API configuration.")
    notion_config: RESTAPIConfig = {
        "client": {
            "base_url": "https://api.notion.com/v1/",
            "auth": {
                "token": dlt.secrets["sources.rest_api.notion.api_key"]
            },
            "headers": {
                "Content-Type": "application/json",
                "Notion-Version": "2022-06-28"
            }
        },
        "resources": [
            {
                "name": "search",
                "endpoint": {
                    "path": "search",
                    "method": "POST",
                    "paginator": PostBodyPaginator(),
                    "json": {
                        "query": "homework",
                        "sort": {
                            "direction": "ascending",
                            "timestamp": "last_edited_time"
                        }
                    },
                    "data_selector": "results"
                }
            },
            {
                "name": "page_content",
                "endpoint": {
                    "path": "blocks/{page_id}/children",
                    "paginator": JSONResponsePaginator(),
                    "params": {
                        "page_id": {
                            "type": "resolve",
                            "resource": "search",
                            "field": "id"
                        }
                    },
                }
            }
        ]
    }

    yield from rest_api_source(notion_config, name="employee_handbook")

def extract_page_content(response):
    logging.info("Extracting page content.")
    block_id = response["id"]
    last_edited_time = response["last_edited_time"]
    block_type = response.get("type", "Not paragraph")
    if block_type != "paragraph":
        content = ""
    else:
        try:
            content = response["paragraph"]["rich_text"][0]["plain_text"]
        except IndexError:
            content = ""
    
    logging.info(f"Extracted content for block_id: {block_id}")
    return{
        "block_id": block_id,
        "block_type": block_type,
        "content": content,
        "last_edited_time": last_edited_time,
        "inserted_at_time": datetime.now(timezone.utc)
    }

@dlt.resource(
    name="employee_handbook",
    write_disposition="merge",
    primary_key="block_id",
    columns={"last_edited_time": {"dedup_sort": "desc"}}
)
def rest_api_notion_incremental(
    last_edited_time = dlt.sources.incremental(
        "last_edited_time", 
        initial_value="2024-06-26T08:16:00.000Z",
        primary_key=("block_id")
        )
):
    logging.info("Starting incremental data extraction.")
    for block in rest_api_notion_resource.add_map(extract_page_content):
        if not(len(block["content"])):
            logging.info(f"Skipping block with empty content. Block ID: {block['block_id']}")
            continue
        yield block

def load_notion() -> None:
    logging.info("Starting Notion data loading pipeline.")
    pipeline = dlt.pipeline(
        pipeline_name="company_policies",
        destination="lancedb",
        dataset_name="notion_pages_homework"
    )

    load_info = pipeline.run(
        lancedb_adapter(
            rest_api_notion_incremental,
            embed="content"
        ),
        table_name="homework",
        write_disposition="merge"
    )

    logging.info(f"Data loading completed. Load info: {load_info}")
    # print(load_info)

if __name__ == "__main__":
    load_notion()
