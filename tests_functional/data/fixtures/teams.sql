INSERT INTO public.teams(
    id, lead_id, name, segment, settings
) VALUES 
('1', '1', 'team 1', NULL, NULL), 
('2', '2', 'team 2', NULL, NULL), 
('3', '3', 'team 3', NULL, NULL), 
('4', '4', 'team 4', NULL, NULL), 
('5', '5', 'team 5', NULL, NULL);

INSERT INTO public.operators(
    id, team_id, is_teamlead, name
) VALUES 
('73478905', '1', 't', 'operator 1'), 
('2', '2', 't', 'operator 2'), 
('3', '3', 't', 'operator 3'), 
('4', '4', 't', 'operator 4'), 
('5', '5', 't', 'operator 5'), 
('6', '1', 't', 'operator 6'), 
('7', '2', 'f', 'operator 7'), 
('8', '3', 'f', 'operator 8'), 
('9', '4', 'f', 'operator 9'), 
('11', '5', 'f', 'operator 11'), 
('12', '1', 'f', 'operator 12'), 
('13', '2', 'f', 'operator 13'), 
('14', '3', 'f', 'operator 14'), 
('15', '4', 'f', 'operator 15'), 
('16', '5', 'f', 'operator 16'), 
('17', '1', 'f', 'operator 17'), 
('18', '2', 'f', 'operator 18'), 
('19', '3', 'f', 'operator 19'), 
('20', '4', 'f', 'operator 20'), 
('21', '5', 'f', 'operator 21'), 
('22', '1', 'f', 'operator 22'), 
('23', '2', 'f', 'operator 23');

