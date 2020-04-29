import datetime as dt
import graphene as g
import unittest as ut
from .. import db_functions as db
from .. import graphql as ql
from .. import utils as u

int_time = 1587852000
string_time_short = "2020-04-26"
string_time = string_time_short + " 00:00:00"

class TestDBFunctions(ut.TestCase):
    def setUp(self):
        db.recreate_db()

    def test_utilities(self):
        data = {"a": 1, "b": 2}
        columns = ["a", "b", "c"]
        self.assertEqual(db._get_values(data, columns), [1, 2])
        self.assertEqual(db._get_all_values(data, columns), [1, 2, None])
        self.assertEqual(db._update_query_string(data, columns),
                         "a = ?, b = ?")
        self.assertEqual(db._int_time_to_string(int_time), string_time)
        self.assertEqual(db._int_time_to_string(float(int_time)), string_time)
        self.assertEqual(db._string_time_to_int(string_time), int_time)
        self.assertEqual(db._string_time_to_int(string_time_short), int_time)

    def test_time_fns(self):
        summer_time_start = "2020-03-29"
        start_of_day_int = db._start_of_day(summer_time_start + " 11:11:11")
        start_of_day_str = db._int_time_to_string(start_of_day_int)
        next_day_int = db._get_next_date(summer_time_start)
        next_day_str = db._int_time_to_string(next_day_int)
        self.assertEqual(start_of_day_str, "2020-03-29 00:00:00")
        self.assertEqual(next_day_str, "2020-03-30 00:00:00")

    def test_matches(self):
        team_name = "SK Telecom"
        team_id = db.insert_team(team_name)
        game_id = db.insert_game("StarCraft: Brood War")
        game2_id = db.insert_game("StarCraft II")
        player1_id = db.insert_player({"name": "Light", "team_id": team_id,
                                       "game_ids": [game_id, game2_id]})
        player2_id = db.insert_player({"name": "Queen",
                                       "birthday": "2010-03-04",
                                       "from_nation": "South Korea"})
        tournament_id = db.insert_tournament("ASL Season 9")
        score = 123
        data = {"date": string_time_short,
                "game_id": game_id,
                "finished": False,
                "tournament_id": tournament_id,
                "team2_score": score,
                "teams": [[player1_id], [player2_id]]}
        db.insert_match(data)
        matches = db.get_matches_between(0, 2e9)
        expected_result = \
            {1: {'id': 1,
                 'date': dt.datetime(2020, 4, 26, 0, 0),
                 'game': 'StarCraft: Brood War',
                 'finished': 0,
                 'tournament': 'ASL Season 9',
                 'team1_score': 0,
                 'team2_score': 123,
                 'teams': [[{'id': 1,
                             'name': 'Light',
                             'birthday': None,
                             'from_nation': None,
                             'team': 'SK Telecom',
                             'games': ['StarCraft: Brood War',
                                       'StarCraft II']}],
                           [{'id': 2,
                             'name': 'Queen',
                             'birthday': dt.datetime(2010, 3, 4, 0, 0),
                             'from_nation': 'South Korea',
                             'team': None,
                             'games': []}]]}}
        self.assertEqual(matches, expected_result)
        with self.assertRaises(Exception):
            db.insert_match(u.new_dict(data, "date", "arst"))
        with self.assertRaises(Exception):
            db.insert_match(u.new_dict(data, "game_id", 123))
        with self.assertRaises(Exception):
            db.insert_match(u.new_dict(data, "tournament_id", 123))
        with self.assertRaises(Exception):
            db.insert_match(u.new_dict(data, "teams", [[123], [123]]))
        self.assertEqual(db.get_matches_on_day(string_time_short),
                         expected_result)
        self.assertEqual(db.get_matches_on_day(int_time), expected_result)
        self.assertEqual(db.get_matches_on_day(0), {})

    def test_getters(self):
        team_name = "SK Telecom"
        team_id = db.insert_team(team_name)
        tournament_name = "ASL Season 9"
        tournament_id = db.insert_tournament(tournament_name)
        game_name = "StarCraft: Brood War"
        game_id = db.insert_game(game_name)
        player1_id = db.insert_player({"name": "Light", "from_nation": "SK",
                                       "game_id": game_id, "team_id": team_id})
        player2_id = db.insert_player({"name": "Queen",
                                       "birthday": "2000-01-01"})
        def result(id, name):
            return {"id": id, "name": name}
        self.assertEqual(db.get_game(game_id), result(game_id, game_name))
        self.assertEqual(db.get_tournament(tournament_id),
                         result(tournament_id, tournament_name))
        self.assertEqual(db.get_players([player1_id, player2_id]),
                         {1: {'birthday': None,
                              'from_nation': 'SK',
                              'games': [],
                              'id': 1,
                              'name': 'Light',
                              'team': 'SK Telecom'},
                          2: {'birthday': dt.datetime(2000, 1, 1, 0, 0),
                              'from_nation': None,
                              'games': [],
                              'id': 2,
                              'name': 'Queen',
                              'team': None}})
        self.assertEqual(db.get_team(team_id), result(team_id, team_name))

class TestGraphQL(ut.TestCase):
    def setUp(self):
        db.recreate_db()

    def test_graphql(self):
        schema = g.Schema(query=ql.Query, mutation=ql.Mutation)
        queries = [
            '''mutation { createTeam(name: "SKT1")
                { team { id name } } }''',

            '''mutation { createTournament(name: "OSL Starleague")
                    { tournament { id name } } }''',

            '''mutation { createGame(name: "StarCraft: Brood War")
                    { game { id name } } }''',

            '''mutation { createGame(name: "QuakeLive")
                    { game { id name } } }''',

            '''mutation { createPlayer(
                data: {
                    name: "Bisu",
                    birthday: "1995-05-10",
                    fromNation: "South Korea",
                    teamId: 1,
                    gameIds: [1, 2]})
                    {
                        player {
                            id
                            name
                            birthday
                            fromNation
                            games
                            team
                        }}}''',

            '''mutation { createPlayer(
                data: {
                    name: "Rapha",
                    birthday: "1985-05-10",
                    fromNation: "USA",
                    teamId: 1,
                    gameIds: [2]})
                    {
                        player {
                            id
                            name
                            birthday
                            fromNation
                            games
                            team
                        }}}''',

            '''mutation { createMatch(
                data:
                {date: "2020-01-01T00:00:00",
                gameId: 1,
                finished: false,
                tournamentId: 1,
                team1Score: 123,
                team2Score: 0,
                teams: [[1], [2]]})
                    {
                        match {
                            id
                            game
                            date
                            finished
                            tournament
                            team1Score
                            team2Score
                            teams { name birthday fromNation id team games }
                        }}}''',

            '''mutation { updateMatch(
                data: {
                    id: 1,
                    gameId: 2,
                    team2Score: 1337,
                    teams: [[1, 2], []]})
                    {
                        match {
                            id
                            game
                            date
                            finished
                            tournament
                            team1Score
                            team2Score
                            teams { name birthday fromNation id team games }
                        }}}''']

        expected = [
            {'createTeam': {'team': {'id': 1, 'name': 'SKT1'}}},
            {'createTournament': {'tournament':
                                  {'id': 1, 'name': 'OSL Starleague'}}},
            {'createGame': {'game': {'id': 1, 'name': 'StarCraft: Brood War'}}},
            {'createGame': {'game': {'id': 2, 'name': 'QuakeLive'}}},
            {'createPlayer': {'player': {'birthday': '1995-05-10',
                                         'fromNation': 'South Korea',
                                         'games': ['StarCraft: Brood War',
                                                   'QuakeLive'],
                                         'id': '1',
                                         'name': 'Bisu',
                                         'team': 'SKT1'}}},
            {'createPlayer': {'player': {'birthday': '1985-05-10',
                                         'fromNation': 'USA',
                                         'games': ['QuakeLive'],
                                         'id': '2',
                                         'name': 'Rapha',
                                         'team': 'SKT1'}}},
            {'createMatch': {'match': {'date': '2020-01-01T00:00:00',
                                       'finished': False,
                                       'game': 'StarCraft: Brood War',
                                       'id': '1',
                                       'team1Score': 123,
                                       'team2Score': 0,
                                       'teams': [[{'birthday': '1995-05-10',
                                                   'fromNation': 'South Korea',
                                                   'games': ['StarCraft: Brood '
                                                             'War',
                                                             'QuakeLive'],
                                                   'id': '1',
                                                   'name': 'Bisu',
                                                   'team': 'SKT1'}],
                                                 [{'birthday': '1985-05-10',
                                                   'fromNation': 'USA',
                                                   'games': ['QuakeLive'],
                                                   'id': '2',
                                                   'name': 'Rapha',
                                                   'team': 'SKT1'}]],
                                       'tournament': 'OSL Starleague'}}},
            {'updateMatch': {'match': {'date': '2020-01-01T00:00:00',
                                       'finished': False,
                                       'game': 'QuakeLive',
                                       'id': '1',
                                       'team1Score': 123,
                                       'team2Score': 1337,
                                       'teams': [[{'birthday': '1995-05-10',
                                                   'fromNation': 'South Korea',
                                                   'games': ['StarCraft: Brood '
                                                             'War',
                                                             'QuakeLive'],
                                                   'id': '1',
                                                   'name': 'Bisu',
                                                   'team': 'SKT1'},
                                                  {'birthday': '1985-05-10',
                                                   'fromNation': 'USA',
                                                   'games': ['QuakeLive'],
                                                   'id': '2',
                                                   'name': 'Rapha',
                                                   'team': 'SKT1'}],
                                                 []],
                                       'tournament': 'OSL Starleague'}}}]
        result = list(map(lambda r: u.normal_dict(r.data),
                          map(schema.execute, queries)))
        self.assertEqual(result, expected)

        queries = ['{ matches(onDate: "2020-01-01") { date finished game } }',
                   '''{ matches(between: ["2020-01-01", "2030-01-01"])
                       { date finished teams { name } } }''',
                   '{ matches(ids: [1]) { date finished } }',
                   '{ players(ids: [1, 2]) { name birthday } }',
                   '''{ players(names: ["Bisu", "Rapha"])
                       { name birthday games } }''']
        expected = [{'matches': [{'date': '2020-01-01T00:00:00',
                                  'finished': False,
                                  'game': 'QuakeLive'}]},
                    {'matches': [{'date': '2020-01-01T00:00:00',
                                  'finished': False,
                                  'teams': [[{'name': 'Bisu'},
                                             {'name': 'Rapha'}],
                                            []]}]},
                    {'matches': [{'date': '2020-01-01T00:00:00',
                                  'finished': False}]},
                    {'players': [{'birthday': '1995-05-10', 'name': 'Bisu'},
                                 {'birthday': '1985-05-10', 'name': 'Rapha'}]},
                    {'players': [{'birthday': '1995-05-10',
                                  'games': ['StarCraft: Brood War',
                                            'QuakeLive'],
                                  'name': 'Bisu'},
                                 {'birthday': '1985-05-10',
                                  'games': ['QuakeLive'],
                                  'name': 'Rapha'}]}]

        result = list(map(lambda r: u.normal_dict(r.data),
                          map(schema.execute, queries)))
        self.assertEqual(result, expected)

if __name__ == "__main__":
    ut.main()
