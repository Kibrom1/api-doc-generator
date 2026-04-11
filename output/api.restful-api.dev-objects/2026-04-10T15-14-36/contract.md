# Restful API Dev — Objects API Documentation

## Overview

The **Restful API Dev Objects API** is a simple, publicly accessible RESTful API for managing a collection of objects — primarily consumer electronics such as smartphones, tablets, laptops, and accessories. It supports full CRUD (Create, Read, Update, Delete) operations.

- **Base URL:** `https://api.restful-api.dev`
- **Content Type:** `application/json;charset=UTF-8`
- **Authentication:** None required (public API)
- **Caching:** Responses are explicitly non-cached (`no-cache, no-store`)
- **Security Headers:** `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `X-XSS-Protection: 1; mode=block`

Each **Object** has:
| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Server-assigned unique identifier |
| `name` | `string` | Human-readable device name |
| `data` | `object` \| `null` | Free-form key/value map of device attributes (varies per object) |
| `createdAt` | `string (date-time)` | Timestamp of creation (POST response only) |
| `updatedAt` | `string (date-time)` | Timestamp of last update (PUT/PATCH response only) |

---

## Endpoints Summary

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/objects` | List all objects (optionally filter by ID) |
| `POST` | `/objects` | Create a new object |
| `GET` | `/objects/{id}` | Retrieve a single object by ID |
| `PUT` | `/objects/{id}` | Fully replace an existing object |
| `PATCH` | `/objects/{id}` | Partially update an existing object |
| `DELETE` | `/objects/{id}` | Delete an object |

---

## Endpoints

---

### `GET /objects` — List All Objects

Returns an array of all objects in the system. An optional query parameter allows filtering by one or more specific IDs.

**Authentication:** Not required

#### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `string[]` | No | Filter by one or more object IDs. Repeat the parameter for multiple values: `?id=3&id=5&id=10` |

#### Request Example

```http
GET https://api.restful-api.dev/objects
```

```http
GET https://api.restful-api.dev/objects?id=3&id=5&id=10
```

#### Response — `200 OK`

Returns a JSON array of Object items.

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

#### Response Fields

| Field | Type | Nullable | Description |
|-------|------|----------|-------------|
| `id` | `string` | No | Unique object identifier |
| `name` | `string` | No | Human-readable name |
| `data` | `object` | Yes | Free-form key/value device attributes; `null` if no data provided |

#### Known `data` Keys (observed in the wild)

| Key | Example Value | Type |
|-----|--------------|------|
| `color` / `Color` | `"Cloudy White"` | string |
| `capacity` / `Capacity` | `"128 GB"` | string |
| `capacity GB` | `512` | number |
| `price` / `Price` | `389.99` or `"419.99"` | number or string |
| `year` | `2019` | number |
| `generation` / `Generation` | `"3rd"`, `"4th"` | string |
| `CPU model` | `"Intel Core i9"` | string |
| `Hard disk size` | `"1 TB"` | string |
| `Screen size` | `7.9` | number |
| `Strap Colour` | `"Elderberry"` | string |
| `Case Size` | `"41mm"` | string |
| `Description` | `"High-performance wireless..."` | string |

> ⚠️ **Note:** The `data` field is entirely free-form. Key naming is inconsistent (mixed case, spaces in keys) and value types are not standardized — `price` may be a `number` in some objects and a quoted `string` in others.

#### Error Codes

| Status Code | Description |
|-------------|-------------|
| `200` | Success — array of objects returned |
| `400` | Bad request — invalid query parameters |
| `500` | Internal server error |

---

### `POST /objects` — Create a New Object

Creates a new object. The server assigns a unique `id` (typically a hex/UUID-style string) and returns the created object including a `createdAt` timestamp.

**Authentication:** Not required

#### Request Body (`application/json`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `string` | **Yes** | Human-readable name. Minimum 1 character. |
| `data` | `object` \| `null` | No | Free-form key/value device attributes |

#### Request Example

```http
POST https://api.restful-api.dev/objects
Content-Type: application/json

{
  "name": "Apple MacBook Pro 16",
  "data": {
    "year": 2023,
    "price": 2399.99,
    "CPU model": "Apple M2 Pro",
    "Hard disk size": "512 GB"
  }
}
```

#### Response — `200 OK`

```json
{
  "id": "ff808181932badb60195c3f7741c46b2",
  "name": "Apple MacBook Pro 16",
  "createdAt": "2026-04-10T15:13:22.123+00:00",
  "data": {
    "year": 2023,
    "price": 2399.99,
    "CPU model": "Apple M2 Pro",
    "Hard disk size": "512 GB"
  }
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | `string` | Server-assigned unique identifier |
| `name` | `string` | The provided name |
| `createdAt` | `string (date-time)` | ISO 8601 creation timestamp |
| `data` | `object` \| `null` | The provided data payload |

#### Error Codes

| Status Code | Description |
|-------------|-------------|
| `200` | Object created successfully |
| `400` | Bad request — missing `name` or malformed body |
| `500` | Internal server error |

---

### `GET /objects/{id}` — Retrieve a Single Object

Returns the object matching the specified `id`.

**Authentication:** Not required

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `string` | **Yes** | The unique identifier of the object |

#### Request Example

```http
GET https://api.restful-api.dev/objects/7
```

#### Response — `200 OK`

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

| Status Code | Description |
|-------------|-------------|
| `200` | Success — object returned |
| `404` | Object not found for the given ID |
| `500` | Internal server error |

#### 404 Error Body Example

```json
{
  "error": "Oject with id=99 was not found."
}
```

> ℹ️ Note: The word "Object" appears to be misspelled as "Oject" in the API's error messages — this is a known quirk of the upstream API.

---

### `PUT /objects/{id}` — Fully Replace an Object

Replaces all fields of an existing object with the provided data. Fields not included in the request body will be cleared/overwritten.

**Authentication:** Not required

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `string` | **Yes** | The unique identifier of the object to replace |

#### Request Body (`application/json`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `string` | **Yes** | New name for the object |
| `data` | `object` \| `null` | No | New data payload (replaces existing data entirely) |

#### Request Example

```http
PUT https://api.restful-api.dev/objects/7
Content-Type: application/json

{
  "name": "Apple MacBook Pro 16",
  "data": {
    "year": 2020,
    "price": 2049.99,
    "CPU model": "Intel Core i9",
    "Hard disk size": "2 TB"
  }
}
```

#### Response — `200 OK`

Returns the fully updated object, including an `updatedAt` timestamp.

```json
{
  "id": "7",
  "name": "Apple MacBook Pro 16",
  "updatedAt": "2026-04-10T16:00:00.000+00:00",
  "data": {
    "year": 2020,
    "price": 2049.99,
    "CPU model": "Intel Core i9",
    "Hard disk size": "2 TB"
  }
}
```

#### Error Codes

| Status Code | Description |
|-------------|-------------|
| `200` | Object replaced successfully |
| `400` | Bad request — invalid or missing fields |
| `404` | Object not found |
| `500` | Internal server error |

---

### `PATCH /objects/{id}` — Partially Update an Object

Applies a partial update to an existing object. Only the fields provided in the request body are updated; all other fields remain unchanged.

**Authentication:** Not required

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `string` | **Yes** | The unique identifier of the object to patch |

#### Request Body (`application/json`)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | `string` | No | Updated name for the object |
| `data` | `object` \| `null` | No | Updated data payload (merges with or replaces existing data) |

#### Request Example

```http
PATCH https://api.restful-api.dev/objects/7
Content-Type: application/json

{
  "name": "Apple MacBook Pro 16 (Refurbished)"
}
```

#### Response — `200 OK`

Returns the updated object including an `updatedAt` timestamp.

```json
{
  "id": "7",
  "name": "Apple MacBook Pro 16 (Refurbished)",
  "updatedAt": "2026-04-10T16:30:00.000+00:00",
  "data": {
    "year": 2019,
    "price": 1849.99,
    "CPU model": "Intel Core i9",
    "Hard disk size": "1 TB"
  }
}
```

#### Error Codes

| Status Code | Description |
|-------------|-------------|
| `200` | Object patched successfully |
| `400` | Bad request — malformed body |
| `404` | Object not found |
| `500` | Internal server error |

---

### `DELETE /objects/{id}` — Delete an Object

Permanently removes the object with the specified `id` from the system.

**Authentication:** Not required

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | `string` | **Yes** | The unique identifier of the object to delete |

#### Request Example

```http
DELETE https://api.restful-api.dev/objects/7
```

#### Response — `200 OK`

```json
{
  "message": "Object with id = 7 has been deleted."
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `message` | `string` | Confirmation message indicating the deleted object's ID |

#### Error Codes

| Status Code | Description |
|-------------|-------------|
| `200` | Object deleted successfully |
| `404` | Object not found |
| `500` | Internal server error |

---

## Schemas

### Object

```json
{
  "id": "string",
  "name": "string",
  "data": { "key": "value" } | null,
  "createdAt": "ISO 8601 date-time (POST only)",
  "updatedAt": "ISO 8601 date-time (PUT/PATCH only)"
}
```

### ObjectInput (POST / PUT body)

```json
{
  "name": "string (required, minLength: 1)",
  "data": { "key": "value" } | null
}
```

### ObjectPatchInput (PATCH body)

```json
{
  "name": "string (optional)",
  "data": { "key": "value" } | null
}
```

### ErrorResponse

```json
{
  "error": "string"
}
```

### DeleteResponse

```json
{
  "message": "string"
}
```

---

## Notes & Observations

1. **Free-form `data` field:** The `data` object has no enforced schema. Keys use inconsistent casing (e.g., `color` vs `Color` vs `Strap Colour`) and values may be strings, numbers, or booleans. Consumers should handle unexpected keys gracefully.
2. **Numeric vs string prices:** The `price` field appears as a `number` in some objects (e.g., `689.99`) and as a quoted `string` in others (e.g., `"419.99"`). Always handle both types.
3. **Null data:** Some objects have `"data": null` (e.g., object ID `"2"`). Consumers must handle null values.
4. **ID format:** Seed/built-in object IDs are short numeric strings (`"1"` through `"13"`). User-created object IDs are long hexadecimal strings.
5. **No authentication required:** All endpoints are publicly accessible without any API key, token, or session.
6. **CORS support:** The `Vary: Origin, Access-Control-Request-Method, Access-Control-Request-Headers` response header indicates CORS is supported, making this API browser-friendly.