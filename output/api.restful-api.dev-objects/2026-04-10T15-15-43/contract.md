# Restful API Dev Objects API

A simple RESTful API for managing a collection of objects representing various consumer electronics and devices.

## Overview

- **Base URL:** `https://api.restful-api.dev`
- **Authentication:** None
- **Content Type:** `application/json`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /objects | List all objects |
| POST | /objects | Create a new object |
| GET | /objects/{id} | Get a single object by ID |
| PUT | /objects/{id} | Replace an object by ID |
| PATCH | /objects/{id} | Partially update an object by ID |
| DELETE | /objects/{id} | Delete an object by ID |

## Objects

### `GET /objects`

Returns a list of all objects stored in the collection.

#### Responses

| Status | Description |
|--------|-------------|
| 200 | A JSON array of all object items |

### `POST /objects`

Creates a new object and adds it to the collection.

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | The name of the object |
| data | object \| null | No | A flexible key-value map of additional attributes; may be null |

#### Responses

| Status | Description |
|--------|-------------|
| 200 | The newly created object |
| 400 | Bad request — invalid input |

### `GET /objects/{id}`

Retrieves a single object by its unique identifier.

#### Parameters

| Name | In | Type | Required | Description |
|------|----|------|----------|-------------|
| id | path | string | Yes | The unique identifier of the object |

#### Responses

| Status | Description |
|--------|-------------|
| 200 | The requested object |
| 404 | Object not found |

### `PUT /objects/{id}`

Fully replaces an existing object identified by its ID.

#### Parameters

| Name | In | Type | Required | Description |
|------|----|------|----------|-------------|
| id | path | string | Yes | The unique identifier of the object to replace |

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | The name of the object |
| data | object \| null | No | A flexible key-value map of additional attributes; may be null |

#### Responses

| Status | Description |
|--------|-------------|
| 200 | The updated object |
| 400 | Bad request — invalid input |
| 404 | Object not found |

### `PATCH /objects/{id}`

Partially updates an existing object identified by its ID.

#### Parameters

| Name | In | Type | Required | Description |
|------|----|------|----------|-------------|
| id | path | string | Yes | The unique identifier of the object to update |

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | No | The name of the object |
| data | object \| null | No | A flexible key-value map of additional attributes; may be null |

#### Responses

| Status | Description |
|--------|-------------|
| 200 | The patched object |
| 400 | Bad request — invalid input |
| 404 | Object not found |

### `DELETE /objects/{id}`

Deletes an existing object identified by its ID.

#### Parameters

| Name | In | Type | Required | Description |
|------|----|------|----------|-------------|
| id | path | string | Yes | The unique identifier of the object to delete |

#### Responses

| Status | Description |
|--------|-------------|
| 200 | Confirmation message of deletion |
| 404 | Object not found |