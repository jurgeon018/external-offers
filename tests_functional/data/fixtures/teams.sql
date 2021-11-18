INSERT INTO public.teams(
    team_id, lead_id, team_name, segment, settings
) VALUES 
('1', '1', 'team 1', NULL, NULL), 
('2', '2', 'team 2', NULL, NULL), 
('3', '3', 'team 3', NULL, NULL), 
('4', '4', 'team 4', NULL, NULL), 
('5', '5', 'team 5', NULL, NULL);

INSERT INTO public.operators(
    operator_id, team_id, is_teamlead, full_name, created_at, updated_at
) VALUES 
('73478905', '1', 't', 'operator 1', 'now()', 'now()'), 
('2', '2', 't', 'operator 2', 'now()', 'now()'), 
('3', '3', 't', 'operator 3', 'now()', 'now()'), 
('4', '4', 't', 'operator 4', 'now()', 'now()'), 
('5', '5', 't', 'operator 5', 'now()', 'now()'), 
('6', '1', 't', 'operator 6', 'now()', 'now()'), 
('7', '2', 'f', 'operator 7', 'now()', 'now()'), 
('8', '3', 'f', 'operator 8', 'now()', 'now()'), 
('9', '4', 'f', 'operator 9', 'now()', 'now()'), 
('11', '5', 'f', 'operator 11', 'now()', 'now()'), 
('12', '1', 'f', 'operator 12', 'now()', 'now()'), 
('13', '2', 'f', 'operator 13', 'now()', 'now()'), 
('14', '3', 'f', 'operator 14', 'now()', 'now()'), 
('15', '4', 'f', 'operator 15', 'now()', 'now()'), 
('16', '5', 'f', 'operator 16', 'now()', 'now()'), 
('17', '1', 'f', 'operator 17', 'now()', 'now()'), 
('18', '2', 'f', 'operator 18', 'now()', 'now()'), 
('19', '3', 'f', 'operator 19', 'now()', 'now()'), 
('20', '4', 'f', 'operator 20', 'now()', 'now()'), 
('21', '5', 'f', 'operator 21', 'now()', 'now()'), 
('22', '1', 'f', 'operator 22', 'now()', 'now()'), 
('23', '2', 'f', 'operator 23', 'now()', 'now()');

