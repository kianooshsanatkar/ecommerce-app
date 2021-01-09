import unittest

test_package_list = [
    'core/tests',
    'domain/tests',
    'handlers/tests',
    'integration_tests'
]

if __name__ == '__main__':

    tests = unittest.TestSuite()

    for module in test_package_list:
        tests.addTest(unittest.TestLoader().discover(module, '*test.py'))

    unittest.TextTestRunner(verbosity=2).run(tests)
