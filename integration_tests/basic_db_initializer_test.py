from unittest import TestCase
from sqlalchemy.engine import Engine
from sqlalchemy.orm.session import Session

from domain.models import DBInitializer


class DBInitializerTest(TestCase):

    def test_engine_check(self):
        engine = DBInitializer.get_engine()
        self.assertTrue(isinstance(engine, Engine))
        self.assertEqual(engine, DBInitializer.get_engine())

    def test_session_check(self):
        session = DBInitializer.get_session()
        self.assertTrue(isinstance(session, Session))
        self.assertNotEqual(session, DBInitializer.get_session())

