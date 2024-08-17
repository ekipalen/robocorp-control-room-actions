import os
from typing import Any, Dict

import requests
from dotenv import load_dotenv
from sema4ai.actions import ActionError, Response, action

from models import (
    GetAssetInput,
    GetStepRunArtifactInput,
    ListProcessRunsInput,
    ListStepRunArtifactsInput,
    ListStepRunsInput,
    StartProcessRunInput,
)

load_dotenv()
organization_id = os.getenv("ORGANIZATION_ID")
workspace_id = os.getenv("WORKSPACE_ID")
api_key = os.getenv("API_KEY")

BASE_URL = "https://cloud.robocorp.com/api/v1/workspaces"
HEADERS = {"Content-Type": "application/json", "Authorization": api_key}


def make_get_request(url: str) -> Response[Dict[str, Any]]:
    """
    Make a GET request and return the response as a dictionary.

    Args:
        url (str): The URL to send the GET request to.

    Returns:
        Response[Dict[str, Any]]: The response wrapped in a Response object.

    Raises:
        ActionError: If the request fails.
    """
    response = requests.get(url, headers=HEADERS)

    if response.status_code in [200, 201]:
        return Response(result=response.json())
    else:
        raise ActionError(f"Failed to retrieve data: {response.text}")


@action(is_consequential=False)
def list_processes() -> Response[dict]:
    """
    List the Control Room (aka. CR) processes including names and ID's.

    Returns:
        Result of the operation
    """
    url = f"{BASE_URL}/{workspace_id}/processes"
    return make_get_request(url)


@action(is_consequential=False)
def list_process_runs(input_data: ListProcessRunsInput) -> Response[dict]:
    """
    List process runs. Get process ID's from "list_processes" if needed. Optional limit and state.

    Returns:
        Response[dict]: The result of the operation like IDs.
    """

    url = f"{BASE_URL}/{workspace_id}/process-runs?process_id={input_data.process_id}"

    if input_data.limit is not None:
        url += f"&limit={input_data.limit}"

    if input_data.state in {
        "new",
        "in_progress",
        "completed",
        "unresolved",
        "stopping",
    }:
        url += f"&state={input_data.state}"

    return make_get_request(url)


@action(is_consequential=False)
def list_step_runs(input_data: ListStepRunsInput) -> Response[dict]:
    """
    List step runs from a process run. Get process run ID from 'list_process_runs' if needed.

    Returns:
        Result of the operation like ID's
    """

    url = f"{BASE_URL}/{workspace_id}/step-runs?process_run_id={input_data.process_run_id}&limit=1"
    return make_get_request(url)


@action(is_consequential=False)
def list_step_run_artifacts(input_data: ListStepRunArtifactsInput) -> Response[dict]:
    """
    List step run artifacts (files) for a process step run. Get step run ID from 'list_step_runs' if needed

    Returns:
        Result of the operation
    """

    url = f"{BASE_URL}/{workspace_id}/step-runs/{input_data.step_run_id}/artifacts"
    return make_get_request(url)


@action(is_consequential=False)
def get_step_run_artifact(input_data: GetStepRunArtifactInput) -> Response[dict]:
    """
    Get step run artifact (file) details and URL for a process step run. Get IDs from other functions if needed.

    Returns:
        Result of the operation
    """

    url = f"{BASE_URL}/{workspace_id}/step-runs/{input_data.step_run_id}/artifacts/{input_data.artifact_id}"
    return make_get_request(url)


@action(is_consequential=False)
def list_workers() -> Response[dict]:
    """
    List the Control Room Workers.

    Returns:
        Result of the operation
    """

    url = f"{BASE_URL}/{workspace_id}/workers"
    return make_get_request(url)


@action(is_consequential=False)
def list_assets() -> Response[dict]:
    """
    List the Control Room Assets.

    Returns:
        Result of the operation like ID's
    """

    url = f"{BASE_URL}/{workspace_id}/assets"
    return make_get_request(url)


@action(is_consequential=False)
def get_asset(input_data: GetAssetInput) -> Response[dict]:
    """
    Get asset details for a specific Control Room Asset. Get ID from list_assets if needed.

    Returns:
        Response[dict]: The result of the operation containing the asset details.
    """

    url = f"{BASE_URL}/{workspace_id}/assets/{input_data.asset_id}"
    return make_get_request(url)


@action(is_consequential=True)
def start_process_run(input_data: StartProcessRunInput) -> Response[dict]:
    """
    Start a process run based on the process ID which you can get from list_processes.

    Returns:
        Result of the operation like the ID that you can check the status with list_process_runs
    """

    url = f"{BASE_URL}/{workspace_id}/processes/{input_data.process_id}/process-runs"
    response = requests.post(url, headers=HEADERS)

    if response.status_code in [200, 201]:
        return Response(result=response.json())
    else:
        raise ActionError(f"Failed to start process run: {response.text}")
