import logging
import os

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

from src.mongo.connection import MongoConnection


class AddPlayers:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.conn = MongoConnection()
        self.players = self.conn.db["players"]

    def add(self):
        all_players = self.players.find({"username": {"$ne": None}})

        for player in all_players:
            self.create_player(player)

        self.close()

    def close(self):
        self.driver.close()

    def create_player(self, match_info):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
                self._create_and_return_player, match_info)
            for record in result:
                print(f"Created player: {record['p1']}")

    @staticmethod
    def _create_and_return_player(tx, player):

        query = (
            "CREATE (p1:Player { username: $username, fide_id: $fide_id }) "
            "RETURN p1"
        )
        result = tx.run(query, username=player.get("username"), fide_id=player.get("fide_id"))
        try:
            return [{"p1": record["p1"]["username"]} for record in result]
        except Neo4jError as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise


if __name__ == "__main__":

    db_uri = os.getenv("NEO_HOST")
    db_user = os.getenv("NEO_USER")
    db_password = os.getenv("NEO_PSW")
    AddPlayers(db_uri, db_user, db_password).add()
