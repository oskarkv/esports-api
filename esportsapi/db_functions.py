import datetime
import dateutil.parser as dup
import os
import sqlite3
import time
from . import utils as u

db_name = "database.db"

def load_sql(filename):
    with open(filename, 'r') as s:
        script = s.read()
    conn = sqlite3.connect(db_name)
    conn.executescript(script)
    conn.commit()

def recreate_db():
    if os.path.exists(db_name):
        os.remove(db_name)
    load_sql("sql/tables.sql")

def load_example_data():
    load_sql("sql/some_data.sql")

def create_db_if_nonexistent():
    if not os.path.exists(db_name):
        recreate_db()

def _db_query(f):
    def inner(*args, **kwargs):
        try:
            conn = sqlite3.connect(db_name)
            # conn.set_trace_callback(print)
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()
            result = f(conn, cursor, *args, **kwargs)
            conn.commit()
            return result if result is not None else cursor.lastrowid
        except:
            conn.rollback()
            raise
        finally:
            conn.close()
    return inner

def _get_values(data, columns):
    return [data[k] for k in columns if k in data]

def _get_all_values(data, columns):
    return [data.get(k, None) for k in columns]

def _int_time_to_string(seconds):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(seconds))

def _string_time_to_int(time_string):
    t = time_string if isinstance(time_string,
                                  (datetime.datetime, datetime.date)) \
        else dup.parse(time_string)
    return int(time.mktime(t.timetuple()))

def _to_int_time(date):
    if date is not None:
        return int(date) if isinstance(date, (int, float)) \
            else _string_time_to_int(date)

def _to_string_time(date):
    if date is not None:
        return date if isinstance(date, str) else _int_time_to_string(date)

def _to_string_date(date):
    if date is not None:
        return _to_string_time(date).split()[0]

@_db_query
def insert_game(conn, cursor, name):
    cursor.execute("INSERT INTO games VALUES (null, ?)", (name,))

@_db_query
def insert_team(conn, cursor, name):
    cursor.execute("INSERT INTO teams VALUES (null, ?)", (name,))

@_db_query
def insert_tournament(conn, cursor, name):
    cursor.execute("INSERT INTO tournaments VALUES (null, ?)", (name,))

def _simple_getter(table):
    @_db_query
    def getter(conn, cursor, id):
        fields = "id, name"
        cursor.execute(f"SELECT {fields} FROM {table} WHERE id = ?", [id])
        return u.zipmap(fields.split(", "), cursor.fetchone())
    return getter

get_game = _simple_getter("games")
get_tournament = _simple_getter("tournaments")
get_team = _simple_getter("teams")

@_db_query
def insert_player(conn, cursor, data):
    data = u.update(data, "birthday", _to_int_time)
    data = u.update(data, "game_ids", lambda x: x or [])
    values = _get_all_values(data, ["name", "birthday", "from_nation",
                                    "team_id"])
    cursor.execute("INSERT INTO players VALUES (null, ?, ?, ?, ?);", values)
    pid = cursor.lastrowid
    for gid in data["game_ids"]:
        cursor.execute("INSERT INTO player_games VALUES (null, ?, ?);",
                       (pid, gid))
    return pid

def _prepare_teams_data(teams, match_id):
    if teams:
        result = []
        team_number = 0
        for team in teams:
            team_number += 1
            for player_id in team:
                result.append((team_number, match_id, player_id))
        return result

_match_columns = ["date", "game_id", "finished", "tournament_id",
                  "team1_score", "team2_score"]

@_db_query
def insert_match(conn, cursor, data):
    def none_to_0(x):
        return 0 if x is None else x
    data = u.update(data, "team1_score", none_to_0)
    data = u.update(data, "team2_score", none_to_0)
    data = u.update(data, "date", _to_int_time)
    data = u.update(data, "finished", lambda x: False if x is None else x)
    values = _get_all_values(data, _match_columns)
    cursor.execute("INSERT INTO matches VALUES (null, ?, ?, ?, ?, ?, ?);",
                   values)
    match_id = cursor.lastrowid
    tuples = _prepare_teams_data(data["teams"], match_id)
    for t in tuples:
        cursor.execute("INSERT INTO match_teams VALUES (null, ?, ?, ?);", t)
    return match_id

def _update_query_string(data, columns):
    qs = [k + " = ?" for k in columns if k in data]
    return ", ".join(qs)

@_db_query
def update_match(conn, cursor, data):
    id = data["id"]
    values = _get_values(data, _match_columns)
    qstring = _update_query_string(data, _match_columns)
    query = f"UPDATE matches SET {qstring} WHERE id = ?;"
    cursor.execute(query, values + [id])
    if "teams" in data:
        cursor.execute("DELETE FROM match_teams WHERE match_id = ?", [id])
        tuples = _prepare_teams_data(data["teams"], id)
        for t in tuples:
            cursor.execute("INSERT INTO match_teams VALUES (null, ?, ?, ?);", t)
    return id

def _match_dict(rows):
    idpos = 8
    player_id = u.getter(idpos)
    team_number = u.getter(7)
    player_ids = list(map(player_id, rows))
    players = get_players(player_ids)
    match = u.zipmap(["id", "date", "game", "finished", "tournament",
                      "team1_score", "team2_score"],
                     rows[0])
    match = u.update(match, "date", datetime.datetime.fromtimestamp)
    def get_player(id):
        return players[id]
    def team_list(rows):
        return list(map(get_player, set(map(player_id, rows))))
    teams = u.fmap(team_list, u.group_by(rows, team_number))
    match["teams"] = [teams.get(1, []), teams.get(2, [])]
    return match

def _matches_dict(rows):
    return u.fmap(_match_dict, u.group_by(rows, u.first))

_match_query = """
    SELECT m.id, m.date, g.name, m.finished, t.name,
        m.team1_score, m.team2_score,
        mt.team_number, p.id
    FROM matches m
    LEFT JOIN tournaments t ON m.tournament_id == t.id
    LEFT JOIN games g ON m.game_id == g.id
    LEFT JOIN match_teams mt ON mt.match_id == m.id
    LEFT JOIN players p ON mt.player_id == p.id"""

@_db_query
def get_matches_between(conn, cursor, starttime, endtime):
    starttime = _to_int_time(starttime)
    endtime = _to_int_time(endtime)
    cursor.execute(_match_query + " WHERE date >= ? AND date < ?;",
                   (starttime, endtime))
    return _matches_dict(cursor.fetchall())

@_db_query
def get_matches(conn, cursor, ids):
    qs = ", ".join("?"*len(ids))
    cursor.execute(_match_query + f" WHERE m.id IN ({qs});", ids)
    return _matches_dict(cursor.fetchall())

@_db_query
def get_matches_by_tournament_name(conn, cursor, name):
    cursor.execute(_match_query + " WHERE t.name == ?;", [name])
    return _matches_dict(cursor.fetchall())

@_db_query
def get_matches_by_tournament_id(conn, cursor, id):
    cursor.execute(_match_query + " WHERE t.id == ?;", [id])
    return _matches_dict(cursor.fetchall())

def _players_dict(rows):
    player_rows = u.group_by(rows, u.first)
    def make_player(pid):
        rows = player_rows[pid]
        pmap = u.zipmap(["id", "name", "birthday", "from_nation", "team"],
                        rows[0])
        if pmap["birthday"] is not None:
            pmap = u.update(pmap, "birthday", datetime.datetime.fromtimestamp)
        pmap["games"] = list(filter(None, map(u.last, rows)))
        return pmap
    return {id: make_player(id) for id in player_rows}

def _players_getter(by_column):
    @_db_query
    def getter(conn, cursor, args):
        qs = ", ".join("?"*len(args))
        cursor.execute(f"""
            SELECT p.id, p.name, p.birthday, p.from_nation, t.name,
                g.name
            FROM players p
            LEFT JOIN teams t ON p.team_id == t.id
            LEFT JOIN player_games pg ON pg.player_id == p.id
            LEFT JOIN games g ON pg.game_id = g.id
            WHERE {by_column} IN ({qs});""",
                       args)
        return _players_dict(cursor.fetchall())
    return getter

get_players = _players_getter("p.id")
get_players_by_names = _players_getter("p.name")

def _start_of_day(date):
    """Takes a date in string, datetime, or int format, and returns the int
    representing the start of the day."""
    date = _to_int_time(date)
    struct = time.localtime(date)
    day_dt = datetime.datetime(*struct[:3])
    return time.mktime(day_dt.timetuple())

def _get_next_date(date):
    day = _start_of_day(date)
    # ensure day is at start of day and handle daylight saving time
    day_dt = datetime.datetime.fromtimestamp(day)
    next_day_dt = day_dt + datetime.timedelta(days=1)
    return time.mktime(next_day_dt.timetuple())

def get_matches_on_day(day):
    day = _to_int_time(day)
    # ensure day is at start of day and handle daylight saving time
    struct = time.localtime(day)
    day_dt = datetime.datetime(*struct[:3])
    day = time.mktime(day_dt.timetuple())
    next_day_dt = day_dt + datetime.timedelta(days=1)
    next_day = time.mktime(next_day_dt.timetuple())
    return get_matches_between(day, next_day)
