# Restful API Dev — Objects API Documentation

## Overview

The **Restful API Dev Objects API** is a publicly accessible, no-authentication REST API for managing a collection of objects representing consumer electronics and devices (smartphones, tablets, laptops, headphones, etc.).

- **Base URL:** `https://api.restful-api.dev`
- **Authentication:** None required
- **Content Type:** `application/json;charset=UTF-8`
- **Caching:** Responses are not cached (`no-cache, no-store`)
- **Security Headers:** `X-Content-Type-Options: nosniff`, `X-XSS-Protection: 1; mode=block`, `X-Frame-Options: DENY`

Each **Object** resource has:
| Field  | Type              | Description                                                                 |
|--------|-------------------|-----------------------------------------------------------------------------|
| `id`   | `string`          | Server-assigned unique identifier                                           |
| `name` | `string`          | Human-readable name of the device                                           |
| `data` | `object` or `null`| Flexible, schema-less metadata. Keys/value types vary per object. May be `null`. |

The `data` field is intentionally flexible and contains arbitrary key-value pairs. Common keys observed across objects include:

| Key             | Type              | Example                                      |
|-----------------|-------------------|----------------------------------------------|
| `color`         | string            | `"Cloudy White"`, `"Purple"`, `"Brown"`      |
| `Color`         | string            | `"Red"`                                      |
| `capacity`      | string            | `"128 GB"`                                   |
| `Capacity`      | string            | `"64 GB"`, `"254 GB"`                        |
| `capacity GB`   | number (integer)  | `512`                                        |
| `price`         | number (float)    | `389.99`, `689.99`, `120`                    |
| `Price`         | string            | `"419.99"`, `"519.99"`                       |
| `generation`    | string            | `"3rd"`                                      |
| `Generation`    | string            | `"4th"`                                      |
| `year`          | number (integer)  | `2019`                                       |
| `CPU model`     | string            | `"Intel Core i9"`                            |
| `Hard disk size`| string            | `"1 TB"`                                     |
| `Strap Colour`  | string            | `"Elderberry"`                               |
| `Case Size`     | string            | `"41mm"`                                     |
| `Description`   | string            | `"High-performance wireless noise cancelling headphones"` |
| `Screen size`   | number (float)    | `7.9`                                        |

> ⚠️ **Note:** Key casing is inconsistent across objects (e.g., `color` vs `Color`, `capacity` vs `Capacity`, `price` vs `Price`). Consumers should handle both cases.

---

## Endpoints Summary

| Method   | Path            | Description                         | Auth Required |
|----------|-----------------|-------------------------------------|---------------|
| `GET`    | `/objects`      | List all objects                    | No            |
| `POST`   | `/objects`      | Create a new object                 | No            |
| `GET`    | `/objects/{id}` | Retrieve a single object by ID      | No            |
| `PUT`    | `/objects/{id}` | Fully replace an object             | No            |
| `PATCH`  | `/objects/{id}` | Partially update an object          | No            |
| `DELETE` | `/objects/{id}` | Delete an object                    | No            |

---

## Endpoints

---

### `GET /objects` — List All Objects

Returns an array of all object resources currently stored in the system.

#### Authentication
None required.

#### Query Parameters

| Parameter | Type            | Required | Description                                                                                       |
|-----------|-----------------|----------|---------------------------------------------------------------------------------------------------|
| `id`      | array of strings| No       | Filter results to specific object IDs. Repeat the parameter for multiple IDs (e.g., `?id=1&id=2`) |

#### Request Example

```http
GET https://api.restful-api.dev/objects
```

#### Request Headers
No special headers required.

#### Response — `200 OK`

Returns a JSON array of objects.

**Response Body Schema:**

| Field       | Type              | Description                            |
|-------------|-------------------|----------------------------------------|
| `id`        | string            | Unique identifier of the object        |
| `name`      | string            | Display name of the object             |
| `data`      | object \| null    | Flexible metadata; may be null         |

**Example Response Body:**
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

| Status Code | Description                              |
|-------------|------------------------------------------|
| `400`       | Bad Request — invalid query parameters   |
| `404`       | Not Found — no objects found             |
| `500`       | Internal Server Error                    |

---

### `POST /objects` — Create a New Object

Creates a new object. The server assigns a unique `id` and records a `createdAt` timestamp.

#### Authentication
None required.

#### Request Body

Content-Type: `application/json`

| Field  | Type           | Required | Description                                             |
|--------|----------------|----------|---------------------------------------------------------|
| `name` | string         | **Yes**  | Display name of the object. Minimum 1 character.        |
| `data` | object \| null | No       | Flexible metadata key-value pairs. May be null/omitted. |

**Example Request Body:**
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

Returns the newly created object including the server-assigned `id` and `createdAt` timestamp.

| Field       | Type     | Description                             |
|-------------|----------|-----------------------------------------|
| `id`        | string   | Server-assigned unique identifier       |
| `name`      | string   | Display name of the object              |
| `data`      | object \| null | Metadata payload                  |
| `createdAt` | string (ISO 8601) | Timestamp of creation          |

**Example Response Body:**
```json
{
  "id": "ff8081818f5f6b7a018f5fc36e050001",
  "name": "Apple iPhone 15 Pro",
  "data": {
    "color": "Natural Titanium",
    "capacity": "256 GB",
    "price": 999.99
  },
  "createdAt": "2026-04-10T15:11:38.000Z"
}
```

#### Error Codes

| Status Code | Description                                          |
|-------------|------------------------------------------------------|
| `400`       | Bad Request — malformed JSON or missing `name` field |
| `500`       | Internal Server Error                                |

---

### `GET /objects/{id}` — Retrieve a Single Object

Returns the full representation of a single object by its unique `id`.

#### Authentication
None required.

#### Path Parameters

| Parameter | Type   | Required | Description                         |
|-----------|--------|----------|-------------------------------------|
| `id`      | string | **Yes**  | The unique identifier of the object |

#### Request Example

```http
GET https://api.restful-api.dev/objects/7
```

#### Response — `200 OK`

Returns a single object resource.

| Field  | Type           | Description                       |
|--------|----------------|-----------------------------------|
| `id`   | string         | Unique identifier                 |
| `name` | string         | Display name                      |
| `data` | object \| null | Flexible metadata; may be null    |

**Example Response Body:**
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

| Status Code | Description                                    |
|-------------|------------------------------------------------|
| `404`       | Not Found — object with the given ID not found |
| `500`       | Internal Server Error                          |

**Example 404 Error Body:**
```json
{
  "error": "Oject with id=99 was not found."
}
```

> ⚠️ Note: The typo `"Oject"` (missing 'b') appears to be present in the actual API error messages.

---

### `PUT /objects/{id}` — Replace an Object (Full Update)

Fully replaces an existing object identified by `id`. The entire resource must be provided in the request body. Returns the updated object with an `updatedAt` timestamp.

#### Authentication
None required.

#### Path Parameters

| Parameter | Type   | Required | Description                         |
|-----------|--------|----------|-------------------------------------|
| `id`      | string | **Yes**  | The unique identifier of the object |

#### Request Body

Content-Type: `application/json`

| Field  | Type           | Required | Description                                             |
|--------|----------------|----------|---------------------------------------------------------|
| `name` | string         | **Yes**  | New display name. Minimum 1 character.                  |
| `data` | object \| null | No       | New metadata payload. May be null/omitted.              |

**Example Request Body:**
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

Returns the fully updated object with an `updatedAt` timestamp.

| Field       | Type              | Description                          |
|-------------|-------------------|--------------------------------------|
| `id`        | string            | Unique identifier (unchanged)        |
| `name`      | string            | Updated display name                 |
| `data`      | object \| null    | Updated metadata                     |
| `updatedAt` | string (ISO 8601) | Timestamp of the update              |

**Example Response Body:**
```json
{
  "id": "7",
  "name": "Apple iPhone 15 Pro Max",
  "data": {
    "color": "Black Titanium",
    "capacity": "512 GB",
    "price": 1199.99
  },
  "updatedAt": "2026-04-10T15:11:38.000Z"
}
```

#### Error Codes

| Status Code | Description                                          |
|-------------|------------------------------------------------------|
| `400`       | Bad Request — malformed JSON or missing `name` field |
| `404`       | Not Found — object with the given ID not found       |
| `500`       | Internal Server Error                                |

---

### `PATCH /objects/{id}` — Partially Update an Object

Partially updates an existing object. Only fields included in the request body are updated. Returns the updated object with an `updatedAt` timestamp.

#### Authentication
None required.

#### Path Parameters

| Parameter | Type   | Required | Description                         |
|-----------|--------|----------|-------------------------------------|
| `id`      | string | **Yes**  | The unique identifier of the object |

#### Request Body

Content-Type: `application/json`

| Field  | Type           | Required | Description                                                  |
|--------|----------------|----------|--------------------------------------------------------------|
| `name` | string         | No       | New display name. Minimum 1 character. Omit to keep current. |
| `data` | object \| null | No       | New or updated metadata. Omit to keep current value.         |

**Example Request Body (name only):**
```json
{
  "name": "Apple iPhone 15 Pro (Updated)"
}
```

#### Response — `200 OK`

Returns the updated object with an `updatedAt` timestamp.

| Field       | Type              | Description                          |
|-------------|-------------------|--------------------------------------|
| `id`        | string            | Unique identifier (unchanged)        |
| `name`      | string            | Updated or existing display name     |
| `data`      | object \| null    | Updated or existing metadata         |
| `updatedAt` | string (ISO 8601) | Timestamp of the update              |

**Example Response Body:**
```json
{
  "id": "7",
  "name": "Apple iPhone 15 Pro (Updated)",
  "data": {
    "year": 2019,
    "price": 1849.99,
    "CPU model": "Intel Core i9",
    "Hard disk size": "1 TB"
  },
  "updatedAt": "2026-04-10T15:11:38.000Z"
}
```

#### Error Codes

| Status Code | Description                                    |
|-------------|------------------------------------------------|
| `400`       | Bad Request — malformed JSON                   |
| `404`       | Not Found — object with the given ID not found |
| `500`       | Internal Server Error                          |

---

### `DELETE /objects/{id}` — Delete an Object

Deletes the object identified by `id`. Returns a confirmation message upon success.

#### Authentication
None required.

#### Path Parameters

| Parameter | Type   | Required | Description                         |
|-----------|--------|----------|-------------------------------------|
| `id`      | string | **Yes**  | The unique identifier of the object |

#### Request Example

```http
DELETE https://api.restful-api.dev/objects/7
```

#### Response — `200 OK`

Returns a JSON object with a confirmation message.

| Field     | Type   | Description                       |
|-----------|--------|-----------------------------------|
| `message` | string | Confirmation of deletion          |

**Example Response Body:**
```json
{
  "message": "Object with id = 7 has been deleted."
}
```

#### Error Codes

| Status Code | Description                                    |
|-------------|------------------------------------------------|
| `404`       | Not Found — object with the given ID not found |
| `500`       | Internal Server Error                          |

**Example 404 Error Body:**
```json
{
  "error": "Oject with id=99 was not found."
}
```

---

## Data Models

### Object

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

| Field  | Type           | Nullable | Description                                  |
|--------|----------------|----------|----------------------------------------------|
| `id`   | string         | No       | Server-assigned unique identifier            |
| `name` | string         | No       | Display name, minimum 1 character            |
| `data` | object \| null | Yes      | Flexible metadata; structure varies per item |

### ObjectCreated (POST response)

Extends `Object` with:

| Field       | Type              | Description               |
|-------------|-------------------|---------------------------|
| `createdAt` | string (ISO 8601) | Timestamp of creation     |

### ObjectUpdated (PUT/PATCH response)

Extends `Object` with:

| Field       | Type              | Description               |
|-------------|-------------------|---------------------------|
| `updatedAt` | string (ISO 8601) | Timestamp of last update  |

### DeleteConfirmation

| Field     | Type   | Description                 |
|-----------|--------|-----------------------------|
| `message` | string | Deletion confirmation text  |

### Error

| Field   | Type   | Description                      |
|---------|--------|----------------------------------|
| `error` | string | Human-readable error description |

---

## Notes & Observations

1. **No Authentication:** All endpoints are publicly accessible with no API key or token required.
2. **Flexible `data` field:** The `data` field is schema-less — both keys and value types differ across objects. Applications must handle dynamic/unknown keys and mixed value types (strings, numbers, null).
3. **Inconsistent key casing:** The same semantic property may appear with different casing in different objects (e.g., `price` vs `Price`, `color` vs `Color`, `capacity` vs `Capacity`).
4. **`data` can be null:** As seen with object `id: "2"`, the `data` field can explicitly be `null`.
5. **IDs are strings:** Although the IDs appear numeric in the sample data (`"1"` through `"13"`), they are typed as strings. Server-generated IDs for created objects may be UUID-like strings.
6. **Typo in error messages:** The API returns `"Oject"` (missing the letter 'b') in 404 error messages — this appears to be a known quirk of the live API.
7. **No pagination:** The `GET /objects` endpoint appears to return all objects in a single response with no pagination support observed.