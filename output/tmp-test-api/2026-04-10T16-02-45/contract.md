# Items API

A simple API for retrieving item data by numeric ID, applying validation and standard response formatting.

## Overview

- **Base URL:** `/`
- **Authentication:** None
- **Content Type:** application/json

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/items/{item_id}` | Retrieve an item by its numeric ID |

## Items

### `GET /items/{item_id}`

Retrieves a single item by its integer ID, returning a formatted response payload.

#### Parameters

| Name | In | Type | Required | Description |
|------|----|------|----------|-------------|
| item_id | path | integer | Yes | The unique identifier of the item. Must be a positive integer less than 10000. |

#### Responses

| Status | Description |
|--------|-------------|
| 200 | Item retrieved successfully, returns success flag, payload, and metadata. |
| 400 | Invalid item ID supplied; returns error detail message. |

#### Error Codes

| Code | Meaning |
|------|---------|
| 400 | Item ID failed validation (not a positive integer, or not in the range 1–9999). |

#### Implementation Details

- `item_id` is validated to be strictly greater than `0` and strictly less than `10000` (i.e., valid range is 1–9999 inclusive); values outside this range cause a `ValueError` with the message `"Invalid item ID format"`.
- Any exception raised during processing is caught and re-raised as an HTTP `400` response, with the exception message forwarded as the `detail` field.
- Successful responses are wrapped by a formatting utility that always sets `success` to `true`, nests the raw data under `payload`, and appends a `metadata` object containing `{"version": "1.0"}`.
- The raw item payload contains the fields `id` (echoed integer) and `status` (hardcoded string value `"active"`).