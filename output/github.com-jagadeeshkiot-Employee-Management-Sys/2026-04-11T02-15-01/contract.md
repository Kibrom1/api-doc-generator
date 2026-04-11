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
| PUT | /api/employee/{id} | Update an existing employee |
| DELETE | /api/employee/{id} | Delete an employee by ID |

## Employee

### `POST /api/employee`

Creates a new employee record in the system.

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | No | The unique identifier of the employee |
| firstname | string | Yes | First name of the employee |
| lastname | string | No | Last name of the employee |
| email | string | Yes | Email address of the employee |

#### Responses

| Status | Description |
|--------|-------------|
| 201 | Employee created successfully, returns the created DtoEmployee object |

#### Implementation Details

- The incoming `DtoEmployee` DTO is mapped to an `Employee` entity using `MapperEmployee.mapTOEmployee()` before being persisted.
- After saving, the persisted entity is mapped back to a `DtoEmployee` using `MapperEmployee.mapToDtoEmployee()` and returned.
- The `firstname` and `email` fields are marked `nullable = false` at the database level; supplying null values for these fields will result in a database constraint violation.

---

### `GET /api/employee`

Retrieves a list of all employee records stored in the system.

#### Responses

| Status | Description |
|--------|-------------|
| 200 | Returns an array of all DtoEmployee objects |

#### Implementation Details

- Fetches all `Employee` entities via `repositoryEmployee.findAll()`.
- Each entity is transformed to a `DtoEmployee` using a stream and `MapperEmployee.mapToDtoEmployee()`.
- Returns an empty array if no employees exist.

---

### `GET /api/employee/{id}`

Retrieves a single employee by their unique integer ID.

#### Parameters

| Name | In | Type | Required | Description |
|------|----|------|----------|-------------|
| id | path | integer | Yes | The unique identifier of the employee |

#### Responses

| Status | Description |
|--------|-------------|
| 200 | Employee found; returns the corresponding DtoEmployee object |
| 404 | No employee found for the given ID |

#### Error Codes

| Code | Meaning |
|------|---------|
| 404 | ExceptionEmployee thrown: "The Employee is not founded by this give Id {id}" |

#### Implementation Details

- Uses `repositoryEmployee.findById(id)` with an `orElseThrow` to raise an `ExceptionEmployee` (a `RuntimeException` subclass) if no record is found.
- The found entity is mapped to `DtoEmployee` before being returned.

---

### `PUT /api/employee/{id}`

Updates the details of an existing employee identified by the given ID.

#### Parameters

| Name | In | Type | Required | Description |
|------|----|------|----------|-------------|
| id | path | integer | Yes | The unique identifier of the employee to update |

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | No | The unique identifier of the employee |
| firstname | string | Yes | Updated first name of the employee |
| lastname | string | No | Updated last name of the employee |
| email | string | Yes | Updated email address of the employee |

#### Responses

| Status | Description |
|--------|-------------|
| 200 | Employee updated successfully; returns the updated DtoEmployee object |
| 404 | No employee found for the given ID |

#### Error Codes

| Code | Meaning |
|------|---------|
| 404 | ExceptionEmployee thrown: "The Employee is not exist or found by given id {id}" |

#### Implementation Details

- Looks up the existing `Employee` entity by ID; throws `ExceptionEmployee` if not found.
- Directly sets `firstname`, `lastname`, and `email` on the found entity using values from the request body DTO.
- Saves the updated entity and maps the result back to `DtoEmployee` before returning.
- The `id` field in the request body is not used for the update target; the path variable `id` determines which record is updated.

---

### `DELETE /api/employee/{id}`

Deletes the employee record identified by the given ID.

#### Parameters

| Name | In | Type | Required | Description |
|------|----|------|----------|-------------|
| id | path | integer | Yes | The unique identifier of the employee to delete |

#### Responses

| Status | Description |
|--------|-------------|
| 200 | Employee deleted successfully; returns the plain string "This Employee is Deleted successfully" |
| 404 | No employee found for the given ID |

#### Error Codes

| Code | Meaning |
|------|---------|
| 404 | ExceptionEmployee thrown: "The Employee is not exist or found by given id {id}" |

#### Implementation Details

- Looks up the `Employee` entity by ID using `orElseThrow`; raises `ExceptionEmployee` if not found.
- Calls `repositoryEmployee.delete(employee)` on the retrieved entity to perform the deletion.
- Returns a plain-text success message string upon successful deletion.