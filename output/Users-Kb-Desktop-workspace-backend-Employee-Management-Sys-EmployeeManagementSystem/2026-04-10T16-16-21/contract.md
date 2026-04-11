# Employee Management System API

A REST API for managing employee records, supporting create, read, update, and delete operations on employee data.

## Overview

- **Base URL:** `http://localhost:8080`
- **Authentication:** None
- **Content Type:** `application/json`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/employee | Create a new employee |
| GET | /api/employee | Retrieve all employees |
| GET | /api/employee/{id} | Retrieve an employee by ID |
| PUT | /api/employee/{id} | Update an existing employee by ID |
| DELETE | /api/employee/{id} | Delete an employee by ID |

## Employee

### `POST /api/employee`

Creates a new employee record in the system.

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | No | Unique identifier of the employee |
| firstname | string | Yes | First name of the employee |
| lastname | string | No | Last name of the employee |
| email | string | Yes | Email address of the employee |

#### Responses

| Status | Description |
|--------|-------------|
| 201 | Employee created successfully, returns the created DtoEmployee object |

#### Implementation Details

- The incoming `DtoEmployee` DTO is mapped to an `Employee` entity via `MapperEmployee.mapTOEmployee()` before being persisted.
- After saving, the persisted entity is mapped back to `DtoEmployee` via `MapperEmployee.mapToDtoEmployee()` and returned.
- The `firstname` and `email` fields are marked `nullable = false` at the database column level; missing values may cause a persistence exception.

---

### `GET /api/employee`

Retrieves a list of all employee records.

#### Responses

| Status | Description |
|--------|-------------|
| 200 | Returns a JSON array of all DtoEmployee objects |

#### Implementation Details

- Fetches all `Employee` entities from the repository using `findAll()`.
- Each entity is transformed to a `DtoEmployee` via a stream and `MapperEmployee.mapToDtoEmployee()` before being returned.
- Returns an empty array if no employees exist.

---

### `GET /api/employee/{id}`

Retrieves a single employee record by their unique integer ID.

#### Parameters

| Name | In | Type | Required | Description |
|------|----|------|----------|-------------|
| id | path | integer | Yes | The unique identifier of the employee |

#### Responses

| Status | Description |
|--------|-------------|
| 200 | Employee found; returns the corresponding DtoEmployee object |
| 404 | Employee not found for the given ID |

#### Error Codes

| Code | Meaning |
|------|---------|
| 404 | No employee exists with the provided ID; `ExceptionEmployee` is thrown with the message "The Employee is not founded by this give Id{id}" |

#### Implementation Details

- Uses `repositoryEmployee.findById(id)` with `orElseThrow()` to retrieve the record.
- If no matching record is found, throws `ExceptionEmployee` (a `RuntimeException`) with a descriptive message including the requested ID.
- The found entity is mapped to `DtoEmployee` before being returned.

---

### `PUT /api/employee/{id}`

Updates an existing employee's details by their unique integer ID.

#### Parameters

| Name | In | Type | Required | Description |
|------|----|------|----------|-------------|
| id | path | integer | Yes | The unique identifier of the employee to update |

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | No | Identifier field (not used for update lookup) |
| firstname | string | Yes | Updated first name of the employee |
| lastname | string | No | Updated last name of the employee |
| email | string | Yes | Updated email address of the employee |

#### Responses

| Status | Description |
|--------|-------------|
| 200 | Employee updated successfully; returns the updated DtoEmployee object |
| 404 | Employee not found for the given ID |

#### Error Codes

| Code | Meaning |
|------|---------|
| 404 | No employee exists with the provided ID; `ExceptionEmployee` is thrown with the message "The Employee is not exist or found by given id{id}" |

#### Implementation Details

- Looks up the existing `Employee` entity by ID; throws `ExceptionEmployee` if not found.
- Only `firstname`, `lastname`, and `email` fields from the request body are applied to the existing entity — the path variable `id` is used exclusively as the lookup key.
- The updated entity is saved and mapped back to `DtoEmployee` before being returned.

---

### `DELETE /api/employee/{id}`

Deletes an employee record identified by their unique integer ID.

#### Parameters

| Name | In | Type | Required | Description |
|------|----|------|----------|-------------|
| id | path | integer | Yes | The unique identifier of the employee to delete |

#### Responses

| Status | Description |
|--------|-------------|
| 200 | Employee deleted successfully; returns a plain-text confirmation message |
| 404 | Employee not found for the given ID |

#### Error Codes

| Code | Meaning |
|------|---------|
| 404 | No employee exists with the provided ID; `ExceptionEmployee` is thrown with the message "The Employee is not exist or found by given id{id}" |

#### Implementation Details

- Looks up the `Employee` entity by ID before deletion; throws `ExceptionEmployee` if not found.
- Deletion is performed via `repositoryEmployee.delete(employee)` using the fetched entity object.
- On success, returns the string `"This Employee is Deleted successfully"` with HTTP 200.