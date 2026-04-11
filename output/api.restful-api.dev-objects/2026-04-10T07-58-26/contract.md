# Restful API Dev — Objects API

## Overview

The **Objects API** (`https://api.restful-api.dev`) is a lightweight, publicly accessible RESTful service designed for learning and testing HTTP client integrations. It stores a collection of generic consumer-electronics "objects" (phones, tablets, laptops, headphones, etc.) and exposes full **CRUD** (Create, Read, Update, Delete) operations on them.

### Key characteristics

| Property | Value |
|---|---|
| Base URL | `https://api.restful-api.dev` |
| Protocol | HTTPS |
| Data format | JSON (`application/json;charset=UTF-8`) |
| Authentication | **None** – fully public |
| Caching | Disabled (`no-cache, no-store, must-revalidate`) |
| CDN / Edge | Cloudflare |

### The `data` field

Every object carries an optional `data` field that is a **free-form JSON object** (or `null`). Because the API is schema-less for this field, the keys and value types vary per object. Examples observed in production:

| Object | Notable `data` keys |
|---|---|
| Google Pixel 6 Pro | `color`, `capacity` |
| Apple MacBook Pro 16 | `year`, `price`, `CPU model`, `Hard disk size` |
| Apple Watch Series 8 | `Strap Colour`, `Case Size` |
| Apple iPad Air | `Generation`, `Price`, `Capacity` |
| Beats Studio3 Wireless | `Color`, `Description` |

---

## Endpoint Summary

| Method | Path | Description |
|---|---|---|
| `GET` | `/objects` | List all objects (optionally filtered by ID) |
| `POST` | `/objects` | Create a new object |
| `GET` | `/objects/{id}` | Retrieve a single object by ID |
| `PUT` | `/objects/{id}` | Fully replace an object |
| `PATCH` | `/objects/{id}` | Partially update an object |
| `DELETE` | `/objects/{id}` | Delete an object |

---

## Endpoints

---

### `GET /objects` — List All Objects

Returns the complete collection of stored objects as a JSON array. Supports optional ID-based filtering via query parameters.

#### Authentication
None required.

#### Query Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | `string` (repeatable) | No | Filter by one or more object IDs. Repeat the parameter for multiple values, e.g. `?id=3&id=5&id=10`. |

#### Request Example

```http
GET https://api.restful-api.dev/objects
```

Filtered request:

```http
GET https://api.restful-api.dev/objects?id=1&id=7
```

#### Response — `200 OK`

Returns a JSON array of object resources.

**Response Body Schema**

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` | No | Server-assigned unique identifier. |
| `name` | `string` | No | Human-readable name of the object. |
| `data` | `object \| null` | Yes | Arbitrary key/value attributes; structure varies per object. |

**Example Response Body**

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

| Status Code | Meaning |
|---|---|
| `400 Bad Request` | One or more query parameters are invalid. |
| `500 Internal Server Error` | Unexpected server-side failure. |

---

### `POST /objects` — Create a New Object

Creates a new object with the supplied `name` and optional `data` payload. The server assigns a unique `id` and returns the persisted resource.

#### Authentication
None required.

#### Request Headers

| Header | Value |
|---|---|
| `Content-Type` | `application/json` |

#### Request Body Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | `string` (min length 1) | **Yes** | Human-readable name of the object. |
| `data` | `object \| null` | No | Arbitrary key/value attributes. Any valid JSON object is accepted. |

**Example Request Body**

```json
{
  "name": "Apple iPhone 15 Pro",
  "data": {
    "color": "Natural Titanium",
    "capacity": "256 GB",
    "price": 999.99
  }
}
```

#### Response — `200 OK`

Returns the newly created object, including the server-assigned `id`.

```json
{
  "id": "ff808181-abc1-def2-3456-7890abcdef01",
  "name": "Apple iPhone 15 Pro",
  "data": {
    "color": "Natural Titanium",
    "capacity": "256 GB",
    "price": 999.99
  }
}
```

#### Error Codes

| Status Code | Meaning |
|---|---|
| `400 Bad Request` | Request body is missing, not valid JSON, or `name` is absent. |
| `500 Internal Server Error` | Unexpected server-side failure. |

---

### `GET /objects/{id}` — Retrieve a Single Object

Fetches one object by its unique `id`.

#### Authentication
None required.

#### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | `string` | **Yes** | The unique identifier of the object to retrieve. |

#### Request Example

```http
GET https://api.restful-api.dev/objects/7
```

#### Response — `200 OK`

Returns a single object resource.

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

| Status Code | Meaning |
|---|---|
| `404 Not Found` | No object exists with the given `id`. |
| `500 Internal Server Error` | Unexpected server-side failure. |

**Example 404 Body**

```json
{
  "error": "Oject with id=99 was not found. Checkout list of all objects on method Get Objects"
}
```

> **Note:** The typo `"Oject"` (missing the "b") is part of the live API's error message.

---

### `PUT /objects/{id}` — Fully Replace an Object

Replaces an existing object with the supplied payload. This is a **full update** — any fields not present in the request body are cleared/reset.

#### Authentication
None required.

#### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | `string` | **Yes** | The unique identifier of the object to replace. |

#### Request Headers

| Header | Value |
|---|---|
| `Content-Type` | `application/json` |

#### Request Body Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | `string` (min length 1) | **Yes** | New name for the object. |
| `data` | `object \| null` | No | New data payload. Replaces the existing `data` entirely. |

**Example Request Body**

```json
{
  "name": "Apple iPhone 15 Pro Max",
  "data": {
    "color": "Black Titanium",
    "capacity": "512 GB",
    "price": 1199.99
  }
}
```

#### Response — `200 OK`

Returns the fully replaced object resource.

```json
{
  "id": "7",
  "name": "Apple iPhone 15 Pro Max",
  "data": {
    "color": "Black Titanium",
    "capacity": "512 GB",
    "price": 1199.99
  }
}
```

#### Error Codes

| Status Code | Meaning |
|---|---|
| `400 Bad Request` | Request body is missing, not valid JSON, or `name` is absent. |
| `404 Not Found` | No object exists with the given `id`. |
| `500 Internal Server Error` | Unexpected server-side failure. |

---

### `PATCH /objects/{id}` — Partially Update an Object

Applies a partial update to an existing object. Only the fields supplied in the request body are modified; all other fields remain unchanged.

#### Authentication
None required.

#### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | `string` | **Yes** | The unique identifier of the object to patch. |

#### Request Headers

| Header | Value |
|---|---|
| `Content-Type` | `application/json` |

#### Request Body Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | `string` (min length 1) | No | Updated name. |
| `data` | `object \| null` | No | Updated data payload. Replaces the `data` field if supplied. |

**Example Request Body** (update name only)

```json
{
  "name": "Apple MacBook Pro 16 (2019 Model)"
}
```

#### Response — `200 OK`

Returns the patched object resource with all merged fields.

```json
{
  "id": "7",
  "name": "Apple MacBook Pro 16 (2019 Model)",
  "data": {
    "year": 2019,
    "price": 1849.99,
    "CPU model": "Intel Core i9",
    "Hard disk size": "1 TB"
  }
}
```

#### Error Codes

| Status Code | Meaning |
|---|---|
| `400 Bad Request` | Request body is missing or not valid JSON. |
| `404 Not Found` | No object exists with the given `id`. |
| `500 Internal Server Error` | Unexpected server-side failure. |

---

### `DELETE /objects/{id}` — Delete an Object

Permanently deletes the object identified by `id`.

#### Authentication
None required.

#### Path Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `id` | `string` | **Yes** | The unique identifier of the object to delete. |

#### Request Example

```http
DELETE https://api.restful-api.dev/objects/7
```

#### Response — `200 OK`

Returns a plain confirmation message.

```json
{
  "message": "Object with id = 7 has been deleted."
}
```

#### Error Codes

| Status Code | Meaning |
|---|---|
| `404 Not Found` | No object exists with the given `id`. |
| `500 Internal Server Error` | Unexpected server-side failure. |

---

## Schemas

### `ObjectResource`

| Field | Type | Nullable | Description |
|---|---|---|---|
| `id` | `string` | No | Server-assigned unique identifier. |
| `name` | `string` | No | Human-readable object name. Min length: 1. |
| `data` | `object` | Yes | Free-form key/value attributes; may be `null`. |

### `ObjectInput` (POST / PUT body)

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | `string` | **Yes** | Human-readable object name. Min length: 1. |
| `data` | `object \| null` | No | Arbitrary key/value attributes. |

### `ObjectPatch` (PATCH body)

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | `string` | No | Updated name. Min length: 1. |
| `data` | `object \| null` | No | Updated data payload. |

### `DeleteResponse`

| Field | Type | Description |
|---|---|---|
| `message` | `string` | Confirmation message, e.g. `"Object with id = 7 has been deleted."` |

### `ErrorResponse`

| Field | Type | Description |
|---|---|---|
| `error` | `string` | Human-readable description of the error. |

---

## Live Data Snapshot

The following 13 objects were observed in the API at the time of documentation (April 2026):

| ID | Name | Notable Data Fields |
|---|---|---|
| 1 | Google Pixel 6 Pro | color: Cloudy White, capacity: 128 GB |
| 2 | Apple iPhone 12 Mini, 256GB, Blue | *(null)* |
| 3 | Apple iPhone 12 Pro Max | color: Cloudy White, capacity GB: 512 |
| 4 | Apple iPhone 11, 64GB | price: 389.99, color: Purple |
| 5 | Samsung Galaxy Z Fold2 | price: 689.99, color: Brown |
| 6 | Apple AirPods | generation: 3rd, price: 120 |
| 7 | Apple MacBook Pro 16 | year: 2019, price: 1849.99, CPU model: Intel Core i9, Hard disk size: 1 TB |
| 8 | Apple Watch Series 8 | Strap Colour: Elderberry, Case Size: 41mm |
| 9 | Beats Studio3 Wireless | Color: Red, Description: High-performance wireless noise cancelling headphones |
| 10 | Apple iPad Mini 5th Gen | Capacity: 64 GB, Screen size: 7.9 |
| 11 | Apple iPad Mini 5th Gen | Capacity: 254 GB, Screen size: 7.9 |
| 12 | Apple iPad Air | Generation: 4th, Price: 419.99, Capacity: 64 GB |
| 13 | Apple iPad Air | Generation: 4th, Price: 519.99, Capacity: 256 GB |

---

## Notes & Caveats

1. **No authentication** — This API is open and public; do not store sensitive information in it.
2. **`data` is schema-less** — Key names, casing, and value types are inconsistent across objects (e.g., `"color"` vs `"Color"`, `"capacity"` as a string vs `"capacity GB"` as a number). Consumers should handle this defensively.
3. **`data` can be `null`** — Always check for `null` before accessing nested properties (see object `id: 2`).
4. **IDs are strings** — Even when they look numeric (`"1"`, `"7"`), IDs are returned as strings. Objects created via POST may receive UUID-style string IDs.
5. **Persistence** — Objects created, updated, or deleted via the API persist for a limited time on the server and may be reset periodically.
6. **CORS** — The `Vary: Origin, Access-Control-Request-Method, Access-Control-Request-Headers` header indicates CORS support, making this API usable directly from browser-based applications.