import logging
import numpy as np

from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

from src.mongo.connection import MongoConnection


class AddMatches:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.conn = MongoConnection("arizzisara", "JAnVC9Nedesi4cPD")
        self.matches = self.conn.db["matches"]

    def add(self):

        chunks = range(0, self.matches.count_documents({}), 2000)
        num_chunks = len(chunks)
        count_chunk = 0
        for i in range(1, num_chunks + 1):
            count_chunk += 1

            if i < num_chunks:
                to_process = self.matches.find({})[chunks[i - 1]:chunks[i]]
            else:
                to_process = self.matches.find({})[chunks[i - 1]:chunks.stop]

            count = 0
            for match in to_process:
                count += 1
                m_info = self.get_match_info(match)
                self.create_match(m_info)
                if count % 100 == 0:
                    print(f"chunk {count_chunk} progressing ... {np.round(count / 2000 * 100, 2)}")

            print(f"Chunk Ended - Completed {np.round(count_chunk / num_chunks * 100, 2)}")

        self.close()
        print("DONE")

    def close(self):
        self.driver.close()

    def create_match(self, match_info):
        with self.driver.session(database="neo4j") as session:
            session.execute_write(self._create_and_return_match, match_info)
            # for record in result:
            # print(f"Created win-loss between: {record['w']}, {record['l']}")

    @staticmethod
    def _create_and_return_match(tx, match_info):

        # create relationship
        query = (
            "MATCH (w:Player {username: $u_w}), (l:Player {username: $u_l}) "
            "CREATE (w)-[:WON {url_match: $url, result: $re_w, color: $c_w, accuracy: $a_w, rating: $ra_w, time_class: $tc}]->(l) "
            "CREATE (l)-[:LOST {url_match: $url, result: $re_l, color: $c_l, accuracy: $a_l, rating: $ra_l, time_class: $tc}]->(w) "
            "RETURN w, l"
        )

        result = tx.run(
            query,
            u_w=match_info.get("winner"), u_l=match_info.get("loser"),
            re_w=match_info.get("result_winner"), re_l=match_info.get("result_loser"),
            c_w=match_info.get("color_winner"), c_l=match_info.get("color_loser"),
            a_w=match_info.get("accuracy_winner"), a_l=match_info.get("accuracy_loser"),
            ra_w=match_info.get("rating_winner"), ra_l=match_info.get("rating_loser"),
            tc=match_info.get("time_class"), url=match_info.get("url_match")
        )

        try:
            return [{"w": record["w"]["username"], "l": record["l"]["username"]} for record in result]
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
        accuracies = match.get("accuracies", {"white": None, "black": None})
        time_class = match.get("time_class", None)

        info = {
            "winner": info_winner.get("username"), "loser": info_loser.get("username"),
            "result_winner": info_winner.get("result"), "result_loser": info_loser.get("result"),
            "color_winner": color_winner, "color_loser": color_loser,
            "accuracy_winner": accuracies.get(color_winner), "accuracy_loser": accuracies.get(color_loser),
            "rating_winner": info_winner.get("rating"), "rating_loser": info_loser.get("rating"),
            "time_class": time_class,
            "url_match": match.get("url")
        }

        return info


if __name__ == "__main__":

    db_uri = "neo4j+s://d11af0bf.databases.neo4j.io"
    db_user = "neo4j"
    db_password = "VNBhq-T57oI9bT3YCoV5MMJZgQr9Gr9W9Owk8TZRSOE"
    AddMatches(db_uri, db_user, db_password).add()
