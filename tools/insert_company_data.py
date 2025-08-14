#!/usr/bin/env python3
"""
API Client for testing process_file endpoint
Processes all company_ex*.json files in example_datas directory
"""

import glob
from pathlib import Path
from typing import List

import httpx
from pydantic import BaseModel, Field


# API Request/Response Models
class SourceType:
    FORESTOFHYUCKSIN = "forestofhyucksin"


class FileProcessRequest(BaseModel):
    source: str
    file_path: str = Field(description="처리할 파일의 경로")


class FileProcessResponse(BaseModel):
    message: str = Field(..., description="처리 결과 메시지")
    file_path: str = Field(..., description="처리된 파일 경로")
    status: str = Field(..., description="처리 상태")


class ApiClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()

    async def process_file(self, file_path: str) -> FileProcessResponse:
        """Call the process_file API endpoint"""
        url = f"{self.base_url}/api/v1/enrichments/data-sources"

        request_data = FileProcessRequest(
            source=SourceType.FORESTOFHYUCKSIN, file_path=file_path
        )

        print(f"📤 Calling API for file: {file_path}")

        response = await self.client.post(
            url,
            json=request_data.model_dump(),
            headers={"Content-Type": "application/json"},
        )

        if response.status_code < 300:
            result = FileProcessResponse(**response.json())
            print(f"✅ Success: {result.message}")
            return result
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            raise httpx.HTTPStatusError(
                message=f"API call failed: {response.status_code}",
                request=response.request,
                response=response,
            )

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


def get_company_files() -> List[str]:
    """Get all company_ex*.json files from example_datas directory"""
    project_root = Path(__file__).parent.parent
    example_data_dir = project_root / "example_datas"

    # Find all company_ex*.json files
    pattern = str(example_data_dir / "company_ex*.json")
    files = glob.glob(pattern)

    # Sort files for consistent ordering
    files.sort()

    print(f"📁 Found {len(files)} company data files:")
    for file_path in files:
        print(f"  - {Path(file_path).name}")

    return files


async def save_companies():
    """Main function to process all company files"""
    print("🚀 Starting API client test...")

    # Get all company files
    files = get_company_files()

    if not files:
        print("❌ No company files found in example_datas/")
        return

    # Initialize API client
    client = ApiClient()

    try:
        results = []

        for file_path in files:
            try:
                # Convert to absolute path
                p = f"./example_datas/{file_path.split('/')[-1]}"

                # Call API
                result = await client.process_file(p)
                results.append((Path(file_path).name, result))

                print(f"✅ Processed: {Path(file_path).name}")
                print(f"   Status: {result.status}")
                print(f"   Message: {result.message}")
                print()

            except Exception as e:
                print(f"❌ Failed to process {Path(file_path).name}: {e}")
                print()

        # Summary
        print("📊 Summary:")
        print(f"Total files: {len(files)}")
        print(f"Successfully processed: {len(results)}")
        print(f"Failed: {len(files) - len(results)}")

        if results:
            print("\n✅ Successfully processed files:")
            for filename, result in results:
                print(f"  - {filename}: {result.status}")

    except Exception as e:
        print(f"❌ Client error: {e}")

    finally:
        await client.close()
        print("🏁 Client test completed")
