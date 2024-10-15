import httpx
from sqlalchemy import select, func
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.schemas.connection import ConnectionCreateSchema, ConnectionUpdateSchema
from app.models.db.connection import Connection as connection_model
from app.models.db.shard import Shard as shard_model
from uuid import UUID
from app.services.shard_service import get_shard_service, get_all_shards_service
from sqlalchemy import select, or_
from fastapi import HTTPException
from datetime import datetime, timedelta
from app.core.config import settings


async def create_connection_service(
    connection_data: ConnectionCreateSchema,
    workspace_id: UUID,
    db_session: AsyncSession,
):
    shard = await get_shard_service(connection_data.shard_id, workspace_id, db_session)
    connection = connection_model(shard_id=shard.id)

    for key, value in connection_data.model_dump().items():
        setattr(connection, key, value)

    shard.connections.append(connection)

    await db_session.commit()
    await db_session.refresh(connection)
    return connection


async def get_connection_as_platform_admin_service(
    connection_id: UUID, db_session: AsyncSession
):
    connection = (
        await db_session.scalars(
            select(connection_model).where(connection_model.id == connection_id)
        )
    ).first()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    return connection


async def get_connection_workspace_as_platform_admin_service(
    connection_id: UUID, db_session: AsyncSession
):
    connection = (await db_session.scalars(
        select(connection_model).where(connection_model.id == connection_id).limit(1)
    )).first()

    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    return connection.shard.workspace


async def get_connection_service(
    connection_id: UUID, workspace_id: UUID, db_session: AsyncSession
):
    connection = (
        await db_session.scalars(
            select(connection_model).where(connection_model.id == connection_id)
        )
    ).first()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    if connection.shard.workspace_id != workspace_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return connection


async def get_all_connections_service(workspace_id: UUID, db_session: AsyncSession):
    connections = (
        await db_session.scalars(
            select(connection_model)
            .join(connection_model.shard)
            .join(shard_model.workspace)
            .where(shard_model.workspace_id == workspace_id)
        )
    ).all()
    if not connections:
        raise HTTPException(status_code=404, detail="Connections not found")
    return connections


async def get_connections_count_service(workspace_id: UUID, db_session: AsyncSession):
    count_query = (
        select(func.count())
        .select_from(connection_model)
        .join(connection_model.shard)
        .join(shard_model.workspace)
        .where(shard_model.workspace_id == workspace_id)
    )
    count = (await db_session.execute(count_query)).scalar()
    return count


async def update_connection_service(
    connection_id: UUID,
    updates: ConnectionUpdateSchema,
    workspace_id: UUID,
    db_session: AsyncSession,
):
    connection = await get_connection_service(connection_id, workspace_id, db_session)
    updates_dict = updates.model_dump(exclude_unset=True)
    for key in updates_dict:
        setattr(connection, key, updates_dict[key])
    await db_session.commit()
    await db_session.refresh(connection)
    return connection


async def delete_connection_service(
    connection_id: UUID, workspace_id: UUID, db_session: AsyncSession
):
    connection = await get_connection_service(connection_id, workspace_id, db_session)
    await db_session.delete(connection)
    await db_session.commit()
    return {"id": connection_id, "success": True}


async def get_connection_shard_service(
    shard_id: UUID, workspace_id: UUID, db_session: AsyncSession
):
    connection = await get_connection_service(shard_id, workspace_id, db_session)
    return connection.shard


async def get_auth_data_service(connection_id: UUID, workspace_id: UUID, db_session: AsyncSession):
    """
    Retrieves the authentication data for a given connection.

    This function fetches the authentication data associated with the provided connection ID.
    If the authentication data is expired, it refreshes the token using the refresh token.

    Args:
        connection_id (UUID): The unique identifier for the connection.
        workspace_id (UUID): The unique identifier for the workspace.
        db_session (AsyncSession): The asynchronous database session.

    Returns:
        dict: A dictionary containing the authentication data.

    Raises:
        HTTPException: If the connection or authentication data is not found.
    """
    connection = await get_connection_service(connection_id, workspace_id, db_session)
    if not connection.auth_data:
        raise HTTPException(status_code=404, detail="Auth data not found")

    auth_data = connection.auth_data
    expires_in = auth_data.get("expires_in")
    token_acquired_time_str = auth_data.get("token_acquired_time")
    if token_acquired_time_str:
        token_acquired_time = datetime.fromisoformat(token_acquired_time_str)

    if datetime.utcnow() > token_acquired_time + timedelta(seconds=expires_in):
        refresh_token = auth_data.get("refresh_token")
        params = {
            "client_id": settings.github_client_id,
            "client_secret": settings.github_client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        headers = {"Accept": "application/json"}

        async with httpx.AsyncClient() as client:
            response = await client.post(url="https://github.com/login/oauth/access_token",
                                         params=params,
                                         headers=headers)

            new_auth_data = response.json()
            auth_data.update(new_auth_data)
            auth_data["token_acquired_time"] = datetime.utcnow().isoformat()
            connection.auth_data = auth_data
            await db_session.commit()
            await db_session.refresh(connection)
    return auth_data
