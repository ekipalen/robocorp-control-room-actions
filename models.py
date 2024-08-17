from typing import Optional

from pydantic import BaseModel, Field


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
