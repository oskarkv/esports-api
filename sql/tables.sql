PRAGMA foreign_keys = ON;

CREATE TABLE games (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT UNIQUE NOT NULL);

CREATE TABLE teams (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT UNIQUE NOT NULL);

CREATE TABLE tournaments (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT UNIQUE NOT NULL);

CREATE TABLE players (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL,
birthday INTEGER,
from_nation TEXT,
team_id INTEGER,
FOREIGN KEY (team_id) REFERENCES teams ON DELETE SET NULL);

CREATE TABLE player_games (
id INTEGER PRIMARY KEY AUTOINCREMENT,
player_id INTEGER,
game_id INTEGER,
FOREIGN KEY (player_id) REFERENCES players,
FOREIGN KEY (game_id) REFERENCES games);

CREATE TABLE matches (
id INTEGER PRIMARY KEY AUTOINCREMENT,
date INTEGER NOT NULL,
game_id INTEGER,
finished INTEGER,
tournament_id INTEGER,
team1_score INTEGER DEFAULT 0,
team2_score INTEGER DEFAULT 0,
FOREIGN KEY (game_id) REFERENCES games ON DELETE SET NULL,
FOREIGN KEY (tournament_id) REFERENCES tournaments ON DELETE SET NULL);

CREATE TABLE match_teams (
id INTEGER PRIMARY KEY AUTOINCREMENT,
team_number INTEGER CHECK(team_number == 1 OR team_number == 2),
match_id INTEGER NOT NULL,
player_id INTEGER NOT NULL,
FOREIGN KEY (match_id) REFERENCES matches ON DELETE CASCADE,
FOREIGN KEY (player_id) REFERENCES players ON DELETE SET NULL);

CREATE INDEX matchs_date_index ON matches (date);
CREATE INDEX matchteams_match_index ON match_teams (match_id);
CREATE INDEX matchteams_player_index ON match_teams (player_id);
