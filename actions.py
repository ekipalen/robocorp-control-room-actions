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
    ListWorkItemsInput,
    GetWorkItemsInput,
    UpdateWorkItemPayloadInput,
    RetryWorkItemsInput,
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


@action(is_consequential=False)
def list_work_items(input_data: ListWorkItemsInput) -> Response[dict]:
    """
    List work items for a given process and process run. Optionally filter by state.

    Args:
        input_data (ListWorkItemsInput): The input data containing process_id, process_run_id, and optional state.

    Returns:
        Response[dict]: The result of the operation containing the list of work items.
    """

    url = f"{BASE_URL}/{workspace_id}/work-items?process_id={input_data.process_id}&process_run_id={input_data.process_run_id}"

    if input_data.state in {"new", "pending", "in_progress", "failed", "done"}:
        url += f"&state={input_data.state}"

    response = make_get_request(url)

    result_data = response.result.get("data", [])
    has_more = response.result.get("has_more", False)
    next_url = response.result.get("next")

    while has_more and next_url:
        additional_response = make_get_request(next_url)
        additional_data = additional_response.result.get("data", [])
        result_data.extend(additional_data)
        has_more = additional_response.result.get("has_more", False)
        next_url = additional_response.result.get("next")

    return Response(result={"data": result_data})


@action(is_consequential=False)
def get_all_work_items(input_data: GetWorkItemsInput) -> Response[dict]:
    """
    Get details for all work items provided in the list of work item IDs, focusing only on ID, exception, and payload.

    Args:
        input_data (GetWorkItemsInput): The input data containing a list of work item IDs.

    Returns:
        Response[dict]: The result of the operation containing selected details of all work items.
    """

    selected_work_item_details = []

    for work_item_id in input_data.work_item_ids:
        url = f"{BASE_URL}/{workspace_id}/work-items/{work_item_id}"
        response = make_get_request(url)

        work_item = {
            "id": response.result.get("id"),
            "exception": response.result.get("exception"),
            "payload": response.result.get("payload"),
        }
        selected_work_item_details.append(work_item)

    return Response(result={"data": selected_work_item_details})


@action(is_consequential=True)
def update_work_item_payloads(input_data: UpdateWorkItemPayloadInput) -> Response[dict]:
    """
    Update the payloads for multiple work items.

    Args:
        input_data (UpdateWorkItemPayloadInput): The input data containing work item IDs and their new payloads.

    Returns:
        Response[dict]: The result of the operation containing the update status for each work item.
    """

    update_results = []

    for update in input_data.work_item_updates:
        work_item_id = update.work_item_id
        payload = update.payload

        if work_item_id and payload:
            url = f"{BASE_URL}/{workspace_id}/work-items/{work_item_id}/payload"
            response = requests.post(url, headers=HEADERS, json={"payload": payload})

            if response.status_code in [200, 201]:
                update_results.append(
                    {
                        "work_item_id": work_item_id,
                        "status": "success",
                        "response": response.json(),
                    }
                )
            else:
                update_results.append(
                    {
                        "work_item_id": work_item_id,
                        "status": "failure",
                        "error": response.text,
                    }
                )

    return Response(result={"updates": update_results})


@action(is_consequential=True)
def retry_work_items(input_data: RetryWorkItemsInput) -> Response[dict]:
    """
    Retry the specified work items using a batch operation.

    Args:
        input_data (RetryWorkItemsInput): The input data containing work item IDs to be retried.

    Returns:
        Response[dict]: The result of the operation containing the retry status for the work items.
    """

    url = f"{BASE_URL}/{workspace_id}/work-items/batch"

    payload = {"batch_operation": "retry", "work_item_ids": input_data.work_item_ids}

    response = requests.post(url, headers=HEADERS, json=payload)

    # Handle the response
    if response.status_code in [200, 201]:
        return Response(result=response.json())
    else:
        raise ActionError(f"Failed to retry work items: {response.text}")
