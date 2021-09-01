from external_offers.entities.teams import Team, Role, Operator
import asyncpgsa
from simple_settings import settings
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import and_, delete, func, not_, select, update
from sqlalchemy.sql.expression import false, true
from external_offers import pg
from external_offers.enums.user_segment import UserSegment
from external_offers.repositories.postgresql.tables import (
    teams,
    operators,
    roles,
)
from external_offers.mappers.teams import (
    teams_mapper,
    operators_mapper,
    roles_mapper,
)



async def check_if_teamlead(user_id):
	# TODO: Затащить проверку на роль
	return True

async def operator_with_id_exists(id) -> bool:
	return


async def create_operator(*, id: int, name: str) -> None:
	pass














# async def update_operator_team(
#     *,
#     operator_id: int,
#     team_id: int,
# ) -> None:
#     query, params = asyncpgsa.compile_query(
#         update(
#             operators
#         ).values(
#             team_id=team_id
#         ).where(
#             operators.c.id == operator_id
#         )
#     )
#     await pg.get().execute(query, *params)


# async def update_team_segment(
#     *,
#     team_id: int,
#     segment: UserSegment,
# ) -> None:
#     query, params = asyncpgsa.compile_query(
#         update(
#             teams
#         ).values(
#             segment=segment
#         ).where(
#             teams.c.id == team_id
#         )
#     )
#     await pg.get().execute(query, *params)














# async def create_role(
#     *,
#     role: Role,
# ) -> None:
#     values = roles_mapper.map_to(role)
#     query, params = asyncpgsa.compile_query(
#         insert(
#             roles
#         ).values(
#             [values]
#         )
#     )
#     row = await pg.get().execute(query, *params)
#     return roles_mapper.map_from(row) if row else None


# async def update_role_by_id(
#     *,
#     role: Role,
# ) -> None:
#     values = roles_mapper.map_to(role)
#     query, params = asyncpgsa.compile_query(
#         update(
#             roles
#         ).where(
#             roles.c.id == role.id
#         ).values(
#             **values
#         )
#     )
#     await pg.get().execute(query, *params)


# async def get_role_by_id(
#     *,
#     id: int,
# ):
#     row = ...
#     return roles_mapper.map_from(row) if row else None


# async def get_roles():
#     rows = ...
#     return [roles_mapper.map_from(row) for row in rows]


# async def delete_role_by_id():
#     row = ...
#     return roles_mapper.map_from(row) if row else None


# async def delete_roles():
#     row = ...
#     return roles_mapper.map_from(row) if row else None







async def create_team(
    *,
    team: Team,
) -> None:
    values = teams_mapper.map_to(team)
    query, params = asyncpgsa.compile_query(
        insert(
            teams
        ).values(
            [values]
        )
    )
    await pg.get().execute(query, *params)


async def create_operator(
    *,
    operator: Operator,
) -> None:
    values = operators_mapper.map_to(operator)
    query, params = asyncpgsa.compile_query(
        insert(
            operators
        ).values(
            [values]
        )
    )
    await pg.get().execute(query, *params)


async def update_operator_by_id(
    *,
    operator: Operator,
) -> None:
    values = operators_mapper.map_to(operator)
    query, params = asyncpgsa.compile_query(
        update(
            operators
        ).where(
            operators.c.id == operator.id
        ).values(
            **values
        )
    )
    await pg.get().execute(query, *params)


async def update_team_by_id(
    *,
    team: Team,
) -> None:
    values = teams_mapper.map_to(team)
    query, params = asyncpgsa.compile_query(
        update(
            teams
        ).where(
            teams.c.id == team.id
        ).values(
            **values
        )
    )
    await pg.get().execute(query, *params)

