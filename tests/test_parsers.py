import os
import unittest

from lintly.parsers import PARSERS


def load_output(file_name):
    path = os.path.join(os.path.dirname(__file__), 'linter_output', file_name)
    with open(path) as f:
        return f.read()


class ESLintParserTests(unittest.TestCase):

    def setUp(self):
        self.parser = PARSERS['eslint']

    def test_parse(self):
        output = load_output('eslint.txt')

        violations = self.parser.parse_violations(output)

        self.assertEqual(len(violations), 2)

        assert '/Users/grant/project/file1.js' in violations
        assert len(violations['/Users/grant/project/file1.js']) == 3

        assert '/Users/grant/project/file2.js' in violations
        assert len(violations['/Users/grant/project/file2.js']) == 2