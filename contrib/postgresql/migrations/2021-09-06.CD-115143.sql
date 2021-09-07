alter table parsed_offers
	add external_offer_type VARCHAR;

alter table offers_for_call
	add external_offer_type VARCHAR;