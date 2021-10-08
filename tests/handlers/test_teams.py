import pytest
from cian_test_utils import future


@pytest.mark.gen_test
async def test_teams_page_handler(mocker, http_client, base_url):
    user_id = '1'
    current_operator = mocker.MagicMock()
    operators = mocker.MagicMock(value=[])
    teams = mocker.MagicMock(value=[])
    mocker.patch(
        'external_offers.web.handlers.admin.create_operators_from_cian',
        return_value=future(None),
    )
    mocker.patch(
        'external_offers.web.handlers.admin.get_latest_operator_updating',
        return_value=future(None),
    )
    mocker.patch(
        'external_offers.web.handlers.admin.get_or_create_operator',
        return_value=future(None),
    )
    mocker.patch(
        'external_offers.web.handlers.admin.get_enriched_operator_by_id',
        return_value=future(current_operator)
    )
    mocker.patch(
        'external_offers.services.operator_roles.get_or_create_operator',
        return_value=future(current_operator)
    )
    get_enriched_operators_mock = mocker.patch(
        'external_offers.web.handlers.admin.get_enriched_operators',
        return_value=future(operators)
    )
    get_teams_mock = mocker.patch(
        'external_offers.web.handlers.admin.get_teams',
        return_value=future(teams)
    )
    mocker.patch(
        'external_offers.web.handlers.admin.get_teams_page_html',
        return_value=''
    )
    # act
    await http_client.fetch(
        base_url+'/admin/teams/',
        method='GET',
        headers={
            'X-Real-UserId': user_id,
        },
    )

    # assert
    get_enriched_operators_mock.assert_called_once_with()
    get_teams_mock.assert_called_once_with()


@pytest.mark.gen_test
async def test_operator_card_page_handler(mocker, http_client, base_url):
    user_id = '1'
    operator_id = '2'
    current_operator = mocker.MagicMock()
    operator = mocker.MagicMock()
    operators = mocker.MagicMock(value=[])
    teams = mocker.MagicMock(value=[])
    mocker.patch(
        'external_offers.web.handlers.admin.get_enriched_operator_by_id',
        side_effect=[
            future(current_operator),
            future(operator),
        ]
    )
    mocker.patch(
        'external_offers.services.operator_roles.get_enriched_operator_by_id',
        return_value=future(current_operator)
    )
    get_enriched_operators_mock = mocker.patch(
        'external_offers.web.handlers.admin.get_enriched_operators',
        return_value=future(operators)
    )
    get_teams_mock = mocker.patch(
        'external_offers.web.handlers.admin.get_teams',
        return_value=future(teams)
    )
    mocker.patch(
        'external_offers.web.handlers.admin.get_operator_card_html',
        return_value=''
    )
    # act
    await http_client.fetch(
        base_url+f'/admin/operator-card/{operator_id}/',
        method='GET',
        headers={
            'X-Real-UserId': user_id,
        },
    )

    # assert
    get_enriched_operators_mock.assert_called_once_with()
    get_teams_mock.assert_called_once_with()


@pytest.mark.gen_test
async def test_team_card_page_handler(mocker, http_client, base_url):
    user_id = '1'
    team_id = 2
    current_operator = mocker.MagicMock()
    team = mocker.MagicMock()
    operators = mocker.MagicMock(value=[])
    teams = mocker.MagicMock(value=[])
    mocker.patch(
        'external_offers.web.handlers.admin.get_enriched_operator_by_id',
        return_value=future(current_operator),
    )
    get_team_by_id_mock = mocker.patch(
        'external_offers.web.handlers.admin.get_team_by_id',
        return_value=future(team),
    )
    mocker.patch(
        'external_offers.services.operator_roles.get_enriched_operator_by_id',
        return_value=future(current_operator)
    )
    mocker.patch(
        'external_offers.services.operator_roles.get_or_create_operator',
        return_value=future(current_operator)
    )
    get_enriched_operators_mock = mocker.patch(
        'external_offers.web.handlers.admin.get_enriched_operators',
        return_value=future(operators)
    )
    get_teams_mock = mocker.patch(
        'external_offers.web.handlers.admin.get_teams',
        return_value=future(teams)
    )
    get_team_card_html_mock = mocker.patch(
        'external_offers.web.handlers.admin.get_team_card_html',
        return_value=''
    )
    # act
    await http_client.fetch(
        base_url+f'/admin/team-card/{team_id}/',
        method='GET',
        headers={
            'X-Real-UserId': user_id,
        },
    )

    # assert
    get_team_by_id_mock.assert_called_once_with(team_id=team_id)
    get_enriched_operators_mock.assert_called_once_with()
    get_teams_mock.assert_called_once_with()
    get_team_card_html_mock.assert_has_calls(
        [
            mocker.call(
                current_operator=current_operator,
                team=team,
                operators=operators,
                teams=teams,
            )
        ]
    )
