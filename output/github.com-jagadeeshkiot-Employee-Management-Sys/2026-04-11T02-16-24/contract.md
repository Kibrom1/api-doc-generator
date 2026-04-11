# Employee Management System API

A RESTful API for managing employee records, providing full CRUD operations including create, retrieve, update, and delete functionality.

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

Creates a new employee record and persists it to the database.

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | Yes | Unique identifier for the employee |
| firstname | string | Yes | First name of the employee |
| lastname | string | No | Last name of the employee |
| email | string | Yes | Email address of the employee |

#### Responses

| Status | Description |
|--------|-------------|
| 201 | Employee created successfully; returns the created DtoEmployee object |

#### Implementation Details

- The DTO is mapped to an `Employee` entity via `MapperEmployee.mapTOEmployee` before persistence.
- After saving, the persisted entity is mapped back to a `DtoEmployee` via `MapperEmployee.mapToDtoEmployee` and returned.
- `firstname` and `email` are marked as non-nullable at the database column level; supplying null values will result in a constraint violation.

---

### `GET /api/employee`

Retrieves a list of all employee records from the database.

#### Responses

| Status | Description |
|--------|-------------|
| 200 | Returns an array of all DtoEmployee objects |

#### Implementation Details

- Fetches all `Employee` entities via `repositoryEmployee.findAll()`.
- Each entity is transformed to a `DtoEmployee` using `MapperEmployee.mapToDtoEmployee` through a stream collector.
- Returns an empty list if no employees exist.

---

### `GET /api/employee/{id}`

Retrieves a single employee record identified by the given integer ID.

#### Parameters

| Name | In | Type | Required | Description |
|------|----|------|----------|-------------|
| id | path | integer | Yes | Unique integer identifier of the employee |

#### Responses

| Status | Description |
|--------|-------------|
| 200 | Employee found; returns the corresponding DtoEmployee object |
| 404 | Employee not found for the given ID |

#### Error Codes

| Code | Meaning |
|------|---------|
| 404 | No employee exists with the specified ID; `ExceptionEmployee` is thrown with message "The Employee is not founded by this give Id{id}" |

#### Implementation Details

- Uses `repositoryEmployee.findById(id)` with an `orElseThrow` that raises `ExceptionEmployee` if no record is found.
- The found entity is mapped to `DtoEmployee` before being returned.

---

### `PUT /api/employee/{id}`

Updates the `firstname`, `lastname`, and `email` fields of an existing employee identified by the given ID.

#### Parameters

| Name | In | Type | Required | Description |
|------|----|------|----------|-------------|
| id | path | integer | Yes | Unique integer identifier of the employee to update |

#### Request Body

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | Yes | Identifier of the employee (used for mapping) |
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
| 404 | No employee exists with the specified ID; `ExceptionEmployee` is thrown with message "The Employee is not exist or found by given id{id}" |

#### Implementation Details

- Retrieves the existing employee via `repositoryEmployee.findById(id)`, throwing `ExceptionEmployee` if absent.
- Selectively updates only `firstname`, `lastname`, and `email` fields on the retrieved entity before saving.
- The updated entity is saved and mapped back to `DtoEmployee` before being returned.

---

### `DELETE /api/employee/{id}`

Deletes the employee record identified by the given ID.

#### Parameters

| Name | In | Type | Required | Description |
|------|----|------|----------|-------------|
| id | path | integer | Yes | Unique integer identifier of the employee to delete |

#### Responses

| Status | Description |
|--------|-------------|
| 200 | Employee deleted successfully; returns the string "This Employee is Deleted successfully" |
| 404 | Employee not found for the given ID |

#### Error Codes

| Code | Meaning |
|------|---------|
| 404 | No employee exists with the specified ID; `ExceptionEmployee` is thrown with message "The Employee is not exist or found by given id{id}" |

#### Implementation Details

- Retrieves the employee entity via `repositoryEmployee.findById(id)` with `orElseThrow`; throws `ExceptionEmployee` if not found.
- Deletes the full entity object via `repositoryEmployee.delete(employee)`.
- Returns a plain string confirmation message on success.