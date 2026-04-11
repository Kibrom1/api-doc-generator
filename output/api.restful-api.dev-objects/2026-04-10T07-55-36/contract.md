# Restful API Dev — Objects API

## Overview

The **Objects API** (`https://api.restful-api.dev`) is a simple, publicly accessible RESTful API designed for testing and learning purposes. It stores and manages generic "objects" that represent consumer electronics (phones, tablets, laptops, wearables, etc.).

### Key Characteristics

| Property | Value |
|---|---|
| Base URL | `https://api.restful-api.dev` |
| Protocol | HTTPS |
| Data Format | JSON (`application/json;charset=UTF-8`) |
| Authentication | None required |
| Caching | Responses are not cached (`no-cache, no-store`) |
| CORS | Supported (`Vary: Origin, Access-Control-Request-Method`) |
| CDN / Proxy | Cloudflare |

### Data Model

Each **Object** has the following structure:

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` | No | Unique identifier (numeric string for seeded data; UUID-like string for created objects) |
| `name` | `string` | No | Human-readable name of the object |
| `data` | `object` \| `null` | Yes | Flexible key-value map of additional attributes. Keys and value types are arbitrary and vary per object. |

The `data` field is intentionally schema-less. Observed keys across all objects include (but are not limited to):

| Key | Value Type | Example |
|---|---|---|
| `color` / `Color` | string | `"Cloudy White"` |
| `capacity` / `Capacity` | string | `"128 GB"` |
| `capacity GB` | number | `512` |
| `price` / `Price` | number or string | `389.99`, `"419.99"` |
| `year` | integer | `2019` |
| `generation` / `Generation` | string | `"3rd"`, `"4th"` |
| `Screen size` | number | `7.9` |
| `CPU model` | string | `"Intel Core i9"` |
| `Hard disk size` | string | `"1 TB"` |
| `Strap Colour` | string | `"Elderberry"` |
| `Case Size` | string | `"41mm"` |
| `Description` | string | `"High-performance wireless noise cancelling headphones"` |

---

## Endpoint Summary

| Method | Path | Description | Auth |
|---|---|---|---|
| `GET` | `/objects` | List all objects (optionally filtered by ID) | None |
| `POST` | `/objects` | Create a new object | None |
| `GET` | `/objects/{id}` | Retrieve a single object by ID | None |
| `PUT` | `/objects/{id}` | Fully replace an existing object | None |
| `PATCH` | `/objects/{id}` | Partially update an existing object | None |
| `DELETE` | `/objects/{id}` | Delete an object | None |

---

## Endpoints

---

### `GET /objects` — List All Objects

Returns a JSON array of all objects in the system. Supports optional filtering by one or more IDs via query parameters.

#### Authentication
None required.

#### Query Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | `string` (repeatable) | No | Filter results to only include objects with the specified ID(s). Repeat the parameter for multiple values: `?id=3&id=5&id=10` |

#### Request Example

```http
GET /objects HTTP/1.1
Host: api.restful-api.dev
```

#### Request Example with Filter

```http
GET /objects?id=3&id=7&id=10 HTTP/1.1
Host: api.restful-api.dev
```

#### Response Fields

Returns a JSON **array** of Object resources. Each element:

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` | No | Unique object identifier |
| `name` | `string` | No | Human-readable object name |
| `data` | `object` \| `null` | Yes | Flexible attribute map (see Data Model above) |

#### Response Example — `200 OK`

```json
[
  {
    "id": "1",
    "name": "Google Pixel 6 Pro",
    "data": {
      "color": "Cloudy White",
      "capacity": "128 GB"
    }
  },
  {
    "id": "2",
    "name": "Apple iPhone 12 Mini, 256GB, Blue",
    "data": null
  },
  {
    "id": "7",
    "name": "Apple MacBook Pro 16",
    "data": {
      "year": 2019,
      "price": 1849.99,
      "CPU model": "Intel Core i9",
      "Hard disk size": "1 TB"
    }
  }
]
```

#### Error Codes

| HTTP Status | Description |
|---|---|
| `200 OK` | Success — array returned (may be empty if filter matches nothing) |
| `400 Bad Request` | Invalid query parameters |
| `500 Internal Server Error` | Unexpected server-side error |

---

### `POST /objects` — Create a New Object

Creates a new object and returns it with a server-assigned `id`.

#### Authentication
None required.

#### Request Headers

| Header | Value |
|---|---|
| `Content-Type` | `application/json` |

#### Request Body Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | `string` | **Yes** | Name of the object (min length: 1) |
| `data` | `object` \| `null` | No | Flexible key-value attributes map |

#### Request Example

```http
POST /objects HTTP/1.1
Host: api.restful-api.dev
Content-Type: application/json

{
  "name": "Apple iPhone 15 Pro",
  "data": {
    "color": "Natural Titanium",
    "capacity": "256 GB",
    "price": 999.99
  }
}
```

#### Response Fields

Returns the created object:

| Field | Type | Description |
|---|---|---|
| `id` | `string` | Server-assigned unique ID (UUID-like) |
| `name` | `string` | Object name as provided |
| `data` | `object` \| `null` | Data payload as provided |

#### Response Example — `200 OK`

```json
{
  "id": "ff8081819585b9ef019587262e8a000b",
  "name": "Apple iPhone 15 Pro",
  "data": {
    "color": "Natural Titanium",
    "capacity": "256 GB",
    "price": 999.99
  }
}
```

#### Error Codes

| HTTP Status | Description |
|---|---|
| `200 OK` | Object successfully created |
| `400 Bad Request` | Missing `name` field or malformed JSON |
| `500 Internal Server Error` | Unexpected server-side error |

---

### `GET /objects/{id}` — Retrieve a Single Object

Returns the object with the specified `id`.

#### Authentication
None required.

#### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | `string` | **Yes** | The unique identifier of the object |

#### Request Example

```http
GET /objects/7 HTTP/1.1
Host: api.restful-api.dev
```

#### Response Fields

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` | No | Unique object identifier |
| `name` | `string` | No | Human-readable object name |
| `data` | `object` \| `null` | Yes | Flexible attribute map |

#### Response Example — `200 OK`

```json
{
  "id": "7",
  "name": "Apple MacBook Pro 16",
  "data": {
    "year": 2019,
    "price": 1849.99,
    "CPU model": "Intel Core i9",
    "Hard disk size": "1 TB"
  }
}
```

#### Error Codes

| HTTP Status | Description |
|---|---|
| `200 OK` | Object found and returned |
| `404 Not Found` | No object exists with the given `id` |
| `500 Internal Server Error` | Unexpected server-side error |

#### `404` Error Response Example

```json
{
  "error": "Oject with id=999 was not found."
}
```

> **Note:** The API returns the misspelled word "Oject" (missing the letter 'b') in `404` error messages — this is a known quirk of the upstream API.

---

### `PUT /objects/{id}` — Replace an Object (Full Update)

Replaces all fields of an existing object with the provided body. Fields omitted from the request body may be cleared.

#### Authentication
None required.

#### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | `string` | **Yes** | The unique identifier of the object to replace |

#### Request Headers

| Header | Value |
|---|---|
| `Content-Type` | `application/json` |

#### Request Body Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | `string` | **Yes** | Replacement name (min length: 1) |
| `data` | `object` \| `null` | No | Replacement data payload |

#### Request Example

```http
PUT /objects/7 HTTP/1.1
Host: api.restful-api.dev
Content-Type: application/json

{
  "name": "Apple MacBook Pro 16 (Updated)",
  "data": {
    "year": 2023,
    "price": 2499.99,
    "CPU model": "Apple M3 Pro",
    "Hard disk size": "2 TB"
  }
}
```

#### Response Example — `200 OK`

```json
{
  "id": "7",
  "name": "Apple MacBook Pro 16 (Updated)",
  "data": {
    "year": 2023,
    "price": 2499.99,
    "CPU model": "Apple M3 Pro",
    "Hard disk size": "2 TB"
  }
}
```

#### Error Codes

| HTTP Status | Description |
|---|---|
| `200 OK` | Object successfully replaced |
| `400 Bad Request` | Missing required fields or malformed JSON |
| `404 Not Found` | No object exists with the given `id` |
| `500 Internal Server Error` | Unexpected server-side error |

---

### `PATCH /objects/{id}` — Partially Update an Object

Applies a partial update to an existing object. Only the fields included in the request body are modified; all other fields remain unchanged.

#### Authentication
None required.

#### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | `string` | **Yes** | The unique identifier of the object to update |

#### Request Headers

| Header | Value |
|---|---|
| `Content-Type` | `application/json` |

#### Request Body Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | `string` | No | New name for the object |
| `data` | `object` \| `null` | No | Partial or full replacement of the data payload |

#### Request Example

```http
PATCH /objects/7 HTTP/1.1
Host: api.restful-api.dev
Content-Type: application/json

{
  "name": "Apple MacBook Pro 16 (2023 Edition)"
}
```

#### Response Example — `200 OK`

```json
{
  "id": "7",
  "name": "Apple MacBook Pro 16 (2023 Edition)",
  "data": {
    "year": 2019,
    "price": 1849.99,
    "CPU model": "Intel Core i9",
    "Hard disk size": "1 TB"
  }
}
```

#### Error Codes

| HTTP Status | Description |
|---|---|
| `200 OK` | Object successfully patched |
| `400 Bad Request` | Malformed JSON body |
| `404 Not Found` | No object exists with the given `id` |
| `500 Internal Server Error` | Unexpected server-side error |

---

### `DELETE /objects/{id}` — Delete an Object

Permanently removes the object with the specified `id` from the system.

#### Authentication
None required.

#### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | `string` | **Yes** | The unique identifier of the object to delete |

#### Request Example

```http
DELETE /objects/7 HTTP/1.1
Host: api.restful-api.dev
```

#### Response Fields

| Field | Type | Description |
|---|---|---|
| `message` | `string` | Confirmation message stating which object was deleted |

#### Response Example — `200 OK`

```json
{
  "message": "Object with id = 7 has been deleted."
}
```

#### Error Codes

| HTTP Status | Description |
|---|---|
| `200 OK` | Object successfully deleted |
| `404 Not Found` | No object exists with the given `id` |
| `500 Internal Server Error` | Unexpected server-side error |

---

## Seeded Objects Reference

The following objects are pre-loaded in the API:

| ID | Name | Notable `data` Fields |
|---|---|---|
| `1` | Google Pixel 6 Pro | color: Cloudy White, capacity: 128 GB |
| `2` | Apple iPhone 12 Mini, 256GB, Blue | data: null |
| `3` | Apple iPhone 12 Pro Max | color: Cloudy White, capacity GB: 512 |
| `4` | Apple iPhone 11, 64GB | price: 389.99, color: Purple |
| `5` | Samsung Galaxy Z Fold2 | price: 689.99, color: Brown |
| `6` | Apple AirPods | generation: 3rd, price: 120 |
| `7` | Apple MacBook Pro 16 | year: 2019, price: 1849.99, CPU model: Intel Core i9, Hard disk size: 1 TB |
| `8` | Apple Watch Series 8 | Strap Colour: Elderberry, Case Size: 41mm |
| `9` | Beats Studio3 Wireless | Color: Red, Description: High-performance wireless noise cancelling headphones |
| `10` | Apple iPad Mini 5th Gen | Capacity: 64 GB, Screen size: 7.9 |
| `11` | Apple iPad Mini 5th Gen | Capacity: 254 GB, Screen size: 7.9 |
| `12` | Apple iPad Air | Generation: 4th, Price: 419.99, Capacity: 64 GB |
| `13` | Apple iPad Air | Generation: 4th, Price: 519.99, Capacity: 256 GB |

> **Note on `data` field inconsistency:** The `data` object uses inconsistent casing for keys across objects (e.g., `color` vs. `Color`, `Capacity` vs. `capacity`, `price` vs. `Price`). Consumers should handle key lookups case-insensitively when possible.

---

## Error Response Schema

All error responses share the following structure:

```json
{
  "error": "<human-readable error description>"
}
```

---

## Notes & Limitations

- **No authentication** — The API is open and does not require API keys, tokens, or any credentials.
- **No pagination** — `GET /objects` returns all objects in a single response with no pagination support observed.
- **Ephemeral user data** — Objects created via `POST` may be periodically reset by the server; do not rely on user-created objects persisting indefinitely.
- **Flexible `data` schema** — The `data` field is intentionally unstructured. Any valid JSON object (or `null`) is accepted and returned as-is.
- **Case sensitivity in `data` keys** — Key casing in the `data` field is not normalized and varies across objects.