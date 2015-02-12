import ast
import sys
import json
from subprocess import Popen, PIPE
import unittest

from scrapy.utils.test import get_testenv


class CmdlineTest(unittest.TestCase):

    def setUp(self):
        self.env = get_testenv()
        self.env['SCRAPY_SETTINGS_MODULE'] = 'tests.test_cmdline.settings'

    def _execute(self, *new_args, **kwargs):
        args = (sys.executable, '-m', 'scrapy.cmdline') + new_args
        proc = Popen(args, stdout=PIPE, stderr=PIPE, env=self.env, **kwargs)
        comm = proc.communicate()
        return comm[0].strip()

    def test_default_settings(self):
        self.assertEqual(self._execute('settings', '--get', 'TEST1'),
                         'default')

    def test_override_settings_using_set_arg(self):
        self.assertEqual(self._execute('settings', '--get', 'TEST1', '-s',
                                       'TEST1=override'),
                         'override')

    def test_override_settings_using_envvar(self):
        self.env['SCRAPY_TEST1'] = 'override'
        self.assertEqual(self._execute('settings', '--get', 'TEST1'),
                         'override')

    def test_json_settings(self):
        # All strings must be unicode to compare with json.loads output
        test_values = (
            [u'first', 2, {u"third": True}],
            {u'key': u'value', u'list': [u'test1', u'test2']},
            u'just-a-string',
            1234,
            True,
            None,
        )
        for value in test_values:
            output = self._execute('settings', '--get', 'TEST1',
                                   '--set-json',
                                   'TEST1=%s' % json.dumps(value))
            # If setting is a string, no quotes are printed. Let's add them.
            if isinstance(value, basestring):
                output = "'%s'" % output
            output_obj = ast.literal_eval(output)
            # Dumping to JSON is a simple way to compare nested dicts
            self.assertEqual(json.dumps(output_obj, sort_keys=True),
                             json.dumps(value, sort_keys=True))

    def test_incorrect_json_settings(self):
        test_values = (
            '{"unfinished-dict"',
            '"unfinished-string'
        )
        for value in test_values:
            # When printing usage, first line is empty
            self.assertEqual('', self._execute('settings', '--get', 'TEST1',
                                               '--set-json',
                                               'TEST1=%s' % value))
