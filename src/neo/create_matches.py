import logging

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

from src.mongo.connection import MongoConnection


class AddMatches:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.conn = MongoConnection("arizzisara", "JAnVC9Nedesi4cPD")
        self.matches = self.conn.db["matches"]

    def add(self):
        one_match = self.matches.find_one({"url": "https://www.chess.com/game/live/998800982"})

        match_info = self.get_match_info(one_match)

        self.create_match(match_info)

        self.close()

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def create_match(self, match_info):
        with self.driver.session(database="neo4j") as session:
            # Write transactions allow the driver to handle retries and transient errors
            result = session.execute_write(
                self._create_and_return_match, match_info)
            for record in result:
                print(f"Created win-loss between: {record['w']}, {record['l']}")

    @staticmethod
    def _create_and_return_match(tx, match_info):
        # To learn more about the Cypher syntax, see https://neo4j.com/docs/cypher-manual/current/
        # The Reference Card is also a good resource for keywords https://neo4j.com/docs/cypher-refcard/current/

        query = (
            "MATCH (w:Player), (l:Player) "
            "WHERE w.username = $u_w AND l.username = $u_l "
            "CREATE (w)-[:WON {result: $re_w, color: $c_w, accuracy: $a_w, rating: $ra_w, time_class: $tc_w}]->(l) "
            "CREATE (l)-[:LOST {result: $re_l, color: $c_l, accuracy: $a_l, rating: $ra_l, time_class: $tc_l}]->(w) "
            "RETURN w, l"
        )

        result = tx.run(
            query,
            u_w=match_info.get("winner"), u_l=match_info.get("loser"),
            re_w=match_info.get("result_winner"), re_l=match_info.get("result_loser"),
            c_w=match_info.get("color_winner"), c_l=match_info.get("color_loser"),
            a_w=match_info.get("accuracy_winner"), a_l=match_info.get("accuracy_loser"),
            ra_w=match_info.get("rating_winner"), ra_l=match_info.get("rating_loser"),
            tc_w=match_info.get("time_class_winner"), tc_l=match_info.get("time_class_loser")
        )

        try:
            return [{"w": record["w"]["username"], "l": record["l"]["username"]}
                    for record in result]
        # Capture any errors along with the query and data for traceability
        except Neo4jError as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise

    @staticmethod
    def get_match_info(match):
        white = match.get("white").get("result")

        if white == "win":
            color_winner = "white"
            color_loser = "black"
        else:
            color_winner = "black"
            color_loser = "white"

        info_winner = match.get(color_winner)
        info_loser = match.get(color_loser)
        accuracies = match.get("accuracies")
        time_class = match.get("time_class")

        info = {
            "winner": info_winner.get("username"), "loser": info_loser.get("username"),
            "result_winner": info_winner.get("result"), "result_loser": info_loser.get("result"),
            "color_winner": color_winner, "color_loser": color_loser,
            "accuracy_winner": accuracies.get(color_winner), "accuracy_loser": accuracies.get(color_loser),
            "rating_winner": info_winner.get("rating"), "rating_loser": info_loser.get("rating"),
            "time_class_winner": time_class, "time_class_loser": time_class
        }

        return info


if __name__ == "__main__":

    uri = "neo4j+s://d11af0bf.databases.neo4j.io"
    user = "neo4j"
    password = "VNBhq-T57oI9bT3YCoV5MMJZgQr9Gr9W9Owk8TZRSOE"
    AddMatches(uri, user, password).add()
