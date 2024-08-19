import json as json_lib
from typing import List, Optional

from pydantic import BaseModel, Field, Json, validator


class ListProcessRunsInput(BaseModel):
    process_id: str = Field(..., example="123456", description="ID in string format.")
    limit: Optional[int] = Field(
        10,
        example=10,
        description="Optional limit of the results as an integer. Default is 10.",
    )
    state: Optional[str] = Field(
        None,
        description="Optional state filter. Can be 'new', 'in_progress', 'completed', 'unresolved', or 'stopping'.",
    )


class ListStepRunsInput(BaseModel):
    process_run_id: str = Field(
        ..., example="123456", description="ID of the process run in string format."
    )


class ListStepRunArtifactsInput(BaseModel):
    step_run_id: str = Field(..., example="123456", description="ID in string format.")


class GetStepRunArtifactInput(BaseModel):
    step_run_id: str = Field(
        ...,
        example="123456",
        description="ID of the step run in string format.",
    )
    artifact_id: str = Field(
        ..., example="123456", description="ID of the artifact in string format."
    )


class ListAssetInput(BaseModel):
    asset_id: str = Field(
        ...,
        example="123456",
        description="ID of the asset in string format.",
    )


class GetAssetInput(BaseModel):
    asset_id: str = Field(
        ...,
        example="123456",
        description="ID of the asset in string format.",
    )


class StartProcessRunInput(BaseModel):
    process_id: str = Field(
        ..., example="123456", description="ID of the process to start."
    )


class ListWorkItemsInput(BaseModel):
    process_id: str = Field(
        ...,
        example="123456",
        description="ID of the process.",
    )
    process_run_id: str = Field(
        ...,
        example="123456",
        description="ID of the process run.",
    )
    state: Optional[str] = Field(
        None,
        description="Optional state filter. Can be 'new', 'pending', 'in_progress', 'failed', or 'done'.",
        example="failed",
    )


class GetWorkItemsInput(BaseModel):
    work_item_ids: List[str] = Field(
        ...,
        example=["e9674445-ff5c-43d3-9992-75cf500975ec"],
        description="List of work item IDs to retrieve.",
    )


class WorkItemUpdate(BaseModel):
    work_item_id: str
    payload: Json

    @validator("payload", pre=True)
    def convert_dict_to_json(cls, v):
        if isinstance(v, dict):
            return json_lib.dumps(v)
        return v


class UpdateWorkItemPayloadInput(BaseModel):
    work_item_updates: List[WorkItemUpdate]


class RetryWorkItemsInput(BaseModel):
    work_item_ids: List[str] = Field(..., description="List of work item IDs to retry.")
