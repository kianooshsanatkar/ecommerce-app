from unittest import TestCase

from core.exceptions import ValueException, TypeException


class ExceptionTests(TestCase):

    def test_is_value_exception_raise(self):
        def raise_exception():
            raise ValueException("value exception!")
        self.assertRaises(ValueException, raise_exception)

    def test_does_value_exception_text_appears(self):
        with self.assertRaises(ValueException) as context:
            raise ValueException("Value exception!")
        self.assertEqual("Value exception!", str(context.exception))

    def test_is_type_exception_raise(self):
        def raise_exception():
            raise TypeException("value exception!")
        self.assertRaises(TypeException, raise_exception)

    def test_does_type_exception_text_appears(self):
        with self.assertRaises(TypeException) as context:
            raise TypeException("Type exception!")
        self.assertEqual("Type exception!", str(context.exception))
