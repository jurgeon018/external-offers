from datetime import datetime, timedelta

from cian_core.runtime_settings import runtime_settings
from sqlalchemy import and_, nullslast, or_
from sqlalchemy.sql.functions import coalesce

from external_offers.entities.teams import TeamInfo
from external_offers.enums.operator_role import OperatorRole
from external_offers.enums.teams import TeamType
from external_offers.repositories.postgresql.tables import clients, offers_for_call, parsed_offers


_NO_OFFER_CATEGORY = ''


def get_team_type_clauses(
    *,
    team_info: TeamInfo,
):
    if not runtime_settings.get('ENABLE_TEAM_TYPES', True):
        team_type_clauses = []
        joined_tables = clients.join(
            offers_for_call,
            offers_for_call.c.client_id == clients.c.client_id
        )
    else:
        team_type = team_info.team_type
        if runtime_settings.get('USE_PARSED_OFFERS_FOR_CALLTRACKING_FILTRATION', True):
            table_with_ct_flag = parsed_offers
            joined_tables = clients.join(
                offers_for_call.join(parsed_offers, offers_for_call.c.parsed_id == parsed_offers.c.id),
                offers_for_call.c.client_id == clients.c.client_id
            )
        else:
            table_with_ct_flag = offers_for_call
            joined_tables = clients.join(
                offers_for_call,
                offers_for_call.c.client_id == clients.c.client_id
            )
        if team_type == TeamType.attractor:
            only_hunted_ct_team_ids = runtime_settings.get('ONLY_HUNTED_CT_ATTRACTOR_TEAM_ID', [])
            only_unhunted_ct_team_ids = runtime_settings.get('ONLY_UNHUNTED_CT_ATTRACTOR_TEAM_ID', [])
            print('only_unhunted_ct_team_ids', only_unhunted_ct_team_ids)
            if team_info.team_id and int(team_info.team_id) in only_hunted_ct_team_ids:
                team_type_clauses = [
                    and_(
                        # все колтрекинговые обьявки, которые прошли через этап хантинга,
                        # (т.е те, у которых уже есть дата хантинга и реальный номер)
                        table_with_ct_flag.c.is_calltracking.is_(True),
                        clients.c.real_phone_hunted_at.isnot(None),
                        clients.c.real_phone_hunted_at <= (datetime.now() - timedelta(
                            days=team_info.team_settings['return_to_queue_days_after_hunted']
                        )),
                    )
                ]
            elif team_info.team_id and int(team_info.team_id) in only_unhunted_ct_team_ids:
                team_type_clauses = [
                    and_(
                        table_with_ct_flag.c.is_calltracking.is_(True),
                        clients.c.real_phone_hunted_at.is_(None),
                    )
                ]
            else:
                team_type_clauses = [
                    or_(
                        # выдает в работу аттракторам все неколтрекинговые обьявки, или...
                        table_with_ct_flag.c.is_calltracking.is_(False),
                        and_(
                            # ...все колтрекинговые обьявки, которые прошли через этап хантинга,
                            # (т.е те, у которых уже есть дата хантинга и реальный номер)
                            table_with_ct_flag.c.is_calltracking.is_(True),
                            clients.c.real_phone_hunted_at.isnot(None),
                            clients.c.real_phone_hunted_at <= (datetime.now() - timedelta(
                                days=team_info.team_settings['return_to_queue_days_after_hunted']
                            )),
                        ),
                    )
                ]
        elif team_type == TeamType.hunter:
            team_type_clauses = [
                and_(
                    # выдает в работу хантерам все колтрекинговые обьявки, которые еще не прошли через этап хантинга,
                    # (т.е те, у которых еще нет даты хантинга и реального номера)
                    table_with_ct_flag.c.is_calltracking.is_(True),
                    clients.c.real_phone_hunted_at.is_(None),
                )
            ]
    return joined_tables, team_type_clauses


async def get_priority_ordering(
    *,
    team_info: TeamInfo,
    operator_roles: list,
):
    if runtime_settings.ENABLE_TEAM_PRIORITIES and team_info.team_id:
        priority_ordering = (
            nullslast(offers_for_call.c.team_priorities[str(team_info.team_id)].asc())
        )
        offer_category_clause = []
    else:
        is_commercial_moderator = OperatorRole.commercial_prepublication_moderator.value in operator_roles
        commercial_category_clause = (
            coalesce(offers_for_call.c.category, _NO_OFFER_CATEGORY)
            .in_(runtime_settings.COMMERCIAL_OFFER_TASK_CREATION_CATEGORIES)
        )
        offer_category_clause = [
            commercial_category_clause
            if is_commercial_moderator
            else ~commercial_category_clause
        ]
        priority_ordering = nullslast(offers_for_call.c.priority.asc())
    return priority_ordering, offer_category_clause
