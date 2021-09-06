# import json


# async def test_update_operator_team(
#     pg,
#     http,
#     runtime_settings,
# ):
#     # arrange
#     user_id = 1
#     # act
#     response = await http.request(
#         'POST',
#         '/api/admin/v1/update-operator-team/',
#         json={
#             # 'offerId': offer_id,
#             # # wrong parameters
#             # 'termType': 'daily',
#             # 'categoryType': 'land',
#             # 'dealType': 'sale',
#             # 'offerType': 'suburban',
#         },
#         headers={
#             'X-Real-UserId': user_id
#         },
#         expected_status=200
#     )

#     offer_for_call_after_api_call = await pg.fetchrow(
#         """
#         SELECT * FROM offers_for_call WHERE id=$1;
#         """,
#         # [offer_id, ]
#     )
#     parsed_offer_after_api_call = await pg.fetchrow(
#         """
#         SELECT * FROM parsed_offers WHERE id=$1;
#         """,
#         # [offer_for_call_after_api_call['parsed_id']]
#     )
#     body = json.loads(response.body.decode('utf-8'))
#     # assert
#     assert True


# async def test_update_operators_team(
#     pg,
#     http,
#     runtime_settings,
# ):
#     # arrange
#     user_id = '123'
#     # act
#     response = await http.request(
#         'POST',
#         '/api/admin/v1/update-operators-team/',
#         json={
#         },
#         headers={
#             'X-Real-UserId': user_id
#         },
#         expected_status=200
#     )
#     # assert
#     assert True


# # test render teams.jinja2
# # test render team_card.jinja2
# # test render operator_card.jinja2
