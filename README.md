# DeepModel API 🚀

## Overview
DeepModel API serves as a backend for a React/Redux web application. It leverages FastAPI, PostgreSQL, and SQLAlchemy 2.0. The API ensures security through protected routes, accessible only with proper authentication and authorization, and supports Single Sign-On (SSO). Initial authentication uses username and password, with planned future support for Azure Active Directory, Google, etc. 🔐

## Models
The first sprint includes the following models:

### 1. Workspace 🏢
- **Description**: Acts as a container for items. Automatically created for new sign-ups or assigned from an inviter.
- **Relationships**: 1:n with users.
- **Attributes**: 
  - `name`

### 2. User 👤
- **Description**: Represents a user with a specific role (`admin`, `contributor`, `consumer`).
- **Functionality**: Can authenticate with the API.
- **Attributes**: 
  - `first_name`
  - `last_name`
  - `email` (used as username)

### 3. Connection 🔗
- **Description**: An instance of a connection template within a workspace. Connection templates define the connection mechanism to third-party applications (e.g. Salesforce, Hubspot, Box) including whether the connection is based on webhook or scheduled fetch.
- **Relationships**: n:1 with shards.
- **Attributes**:
  - `template_ref`
  - `name`
  - `auth_method`
  - `auth_credentials`
  - `fetch_module`
  - `process_module`

### 4. Shard 💠
- **Description**: Logical grouping of connections, managing user data access.
- **Relationships**: 1:n with users, n:1 with workspaces.
- **Attributes**:
  - `name`
  - `description`

### 5. Module 🧩
- **Description**: Represents a code module for user-defined activities.
- **Relationships**: n:1 with workspaces.
- **Attributes**:
  - `name`
  - `description`
  - `language` (e.g., py, ts)
  - `is_custom`
  - `algorithm` (code blob)
  - `method_type` (fetch, process)

### 6. Document Type 📄
- **Description**: Defines types of documents pulled into the system.
- **Attributes**:
  - `name`
  - `description`
  - `metadata` (jsonb for metadata fields)
