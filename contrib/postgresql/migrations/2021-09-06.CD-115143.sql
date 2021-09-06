alter table parsed_offers
	add external_offer_type int;

alter table offers_for_call
	add external_offer_type int;