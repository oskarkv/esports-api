PRAGMA foreign_keys = ON;

INSERT INTO games VALUES
(null, 'StarCraft: Brood War'),
(null, 'StarCraft II'),
(null, 'QuakeLive'),
(null, 'Quake Champions'),
(null, 'DOTA 2');

INSERT INTO teams VALUES
(null, 'TeamLiquid'),
(null, 'KT Rolster'),
(null, 'OG'),
(null, 'Moo'),
(null, 'Team Nigma');

INSERT INTO tournaments VALUES
(null, 'ASL Season 9'),
(null, 'The International 2021'),
(null, 'QuakeCon 2016');

INSERT INTO players VALUES
(null, 'Rapha', 606006000, 'USA', 1),
(null, 'Evil', 577663200, 'Russia', null),
(null, 'Flash', 710287200, 'South Korea', 2),
(null, 'Queen', 635295600, 'South Korea', 4),
(null, 'Light', 638575200, 'South Korea', 4),
(null, 'Topson', 892504800, 'Finland', 3),
(null, 'Miracle-', 866764800, 'Jordan', 3);

INSERT INTO player_games VALUES
(null, 1, 3),
(null, 1, 4),
(null, 2, 3),
(null, 3, 1),
(null, 3, 2),
(null, 4, 1),
(null, 5, 1),
(null, 6, 5),
(null, 7, 5);

INSERT INTO matches VALUES
(null, 1587888000, 1, 1, 1, 4, 1),
(null, 1467907200, 3, 1, 3, 3, 2),
(null, 1586686800, 1, 1, 1, 3, 2),
(null, 1628553600, 5, 0, 2, 0, 0);

INSERT INTO match_teams VALUES
(null, 1, 1, 4),
(null, 2, 1, 5),
(null, 1, 2, 1),
(null, 2, 2, 2),
(null, 1, 3, 4),
(null, 2, 3, 3),
(null, 1, 4, 6),
(null, 2, 4, 7);
