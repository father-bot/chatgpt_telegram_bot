import json
import unittest
from datetime import datetime

import db_redis as database
import logging

logger = logging.getLogger(__name__)


class MyTestCase(unittest.TestCase):
    def test_utils(self):
        date_str = '09-19-2022'
        date_object = datetime.strptime(date_str, '%m-%d-%Y')
        logger.info("date_object: %s",date_object.second)
        timestamp = int(round(datetime.now().timestamp()))
        logger.info("timestamp: %d",timestamp)

    def test_messages(self):
        db = database.Database()
        db.client.hset("11111", 1, json.dumps({"msg_id":1}))
        db.client.hset("11111", 2, json.dumps({"msg_id": 2}))
        db.client.hset("11111",  4, json.dumps({"msg_id": 4}))
        db.client.hset("11111", 3, json.dumps({"msg_id": 3}))

        rows = db.client.hgetall("11111").values();
        msgs = [json.loads(msg) for msg in rows]
        msgs1 = sorted(msgs, key=lambda x: x['msg_id'])
        db.client.hdel("11111", "4")
        rows1 = db.client.hgetall("11111").values();
        logger.info("msgs: %s",msgs)
    def test_dialog(self):
        db = database.Database()
        logger.debug("redis version: %s",db.client.info()['redis_version'])
        db.check_if_user_exists(1)
        db.add_new_user(1,2,"user_name","fn","ln")
        user = db.client.get("user_%d".format(1))
        logger.debug("user: %s",user)
        self.assertEqual(db.check_if_user_exists(1), True)
        current_chat_mode = db.get_user_attribute(1, "current_chat_mode")
        self.assertEqual("assistant", current_chat_mode)
        dialog_id = db.start_new_dialog(1)
        self.assertEqual(dialog_id, db.get_user_attribute(1,"current_dialog_id"))
        user = db.client.get("user_%d".format(1))
        logger.debug("user: %s",user)


if __name__ == '__main__':
    unittest.main()
