import unittest
import sys
import subprocess
import inspect
import json
import sofine.runner as runner


class RunnerFromCliTestCase(unittest.TestCase):

    def test_runner_main(self):
        # NOTE: Piped (and single non-piped) command lines need to enclose the 
        #  entire set of piped calls in quotes, which here are single quotes 
        path = './sofine/tests/fixtures/file_source_test_data.txt'
        cmd_get_data = "python ./sofine/runner.py '--SF-s file_source --SF-g standard -p {0}'".format(path)
        # NOTE: This call failed with this error message: "sys.excepthook is missing.
        #  lost sys.stderr" until adding stderr arg to Popen() call
        proc = subprocess.Popen(cmd_get_data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = proc.stdout.read()
        out = json.loads(out)
        self.assertTrue(len(out.keys()) == 2)
        self.assertTrue(set(out.keys()) == set(['AAPL', 'MSFT']))


    def test_runner_main_pipe(self):
        path = './sofine/tests/fixtures/file_source_test_data.txt'
        path_2 = './sofine/tests/fixtures/file_source_test_data_2.txt'
        cmd_get_data = "python ./sofine/runner.py '--SF-s file_source --SF-g standard -p {0}".format(path)
        cmd_get_data += " | "
        cmd_get_data += "--SF-s file_source --SF-g standard -p {0}'".format(path_2)
        proc = subprocess.Popen(cmd_get_data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = proc.stdout.read()
        out = json.loads(out)
        self.assertTrue(len(out.keys()) == 4)
        self.assertTrue(set(out.keys()) == set(['AAPL', 'MSFT', 'MCO', 'TWTR']))


    def test_runner_main_pipeline(self):
        path = './sofine/tests/fixtures/file_source_test_data.txt'
        path_2 = './sofine/tests/fixtures/file_source_test_data_2.txt'
        path_3 = './sofine/tests/fixtures/file_source_test_data_3.txt'
        cmd_get_data = "python ./sofine/runner.py '--SF-s file_source --SF-g standard -p {0}".format(path)
        cmd_get_data += " | "
        cmd_get_data += "--SF-s file_source --SF-g standard -p {0}".format(path_2)
        cmd_get_data += " | "
        cmd_get_data += "--SF-s file_source --SF-g standard -p {0}".format(path_3)
        cmd_get_data += " | "
        cmd_get_data += "--SF-s ystockquotelib_mock --SF-g mock'"
        proc = subprocess.Popen(cmd_get_data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = proc.stdout.read()
        out = json.loads(out)
        self.assertTrue(len(out.keys()) == 6)
        self.assertTrue(set(out.keys()) == set(['AAPL', 'MSFT', 'MCO', 'TWTR', 'IBM', 'ORCL']))
        # Assert that the final output has values from ystockquotelib_mock for 
        #  keys added by file_source
        for k in out.keys():
            attr_keys = out[k].keys()
            self.assertTrue(len(attr_keys))
            for ak in attr_keys:
                self.assertTrue(out[k][ak] is not None)


    def test_runner_main_get_schema(self):
        cmd_get_schema = "python ./sofine/runner.py '--SF-s ystockquotelib_mock --SF-g mock --SF-a get_schema'"
        proc = subprocess.Popen(cmd_get_schema, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        schema_out = proc.stdout.read()
        schema_out = json.loads(schema_out)
        schema_attr_keys = set(schema_out['schema'])

        cmd_get_data = "echo '{\"TWTR\" : {}}'"
        cmd_get_data += " | "
        cmd_get_data += "python ./sofine/runner.py '--SF-s ystockquotelib_mock --SF-g mock'"
        proc = subprocess.Popen(cmd_get_data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        data_out = proc.stdout.read()
        data_out = json.loads(data_out)
        data_attr_keys = set(data_out['TWTR'].keys())
        
        self.assertTrue(schema_attr_keys == data_attr_keys)

    
    def test_runner_main_adds_keys(self):
        cmd = "python ./sofine/runner.py '--SF-s file_source --SF-g standard --SF-a adds_keys'"
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = proc.stdout.read()
        out = json.loads(out)
        self.assertTrue(out['adds_keys'])


    def test_runner_main_parse_args(self):
        path = './sofine/tests/fixtures/file_source_test_data.txt'
        cmd = "python ./sofine/runner.py '--SF-s file_source --SF-g standard --SF-a parse_args -p {0}'".format(path)
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = proc.stdout.read()
        out = json.loads(out) 
        self.assertTrue(out['is_valid'] and out['parsed_args'] == [path])


    def test_runner_main_piped_input(self):
        path = './sofine/tests/fixtures/file_source_test_data.txt'
        cmd = "echo '{\"TWTR\" : {}}'"
        cmd += " | "
        cmd += "python ./sofine/runner.py '--SF-s file_source --SF-g standard -p {0}'".format(path)
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out = proc.stdout.read()
        out = json.loads(out) 
        self.assertTrue(set(out.keys()) == set(['TWTR', 'AAPL', 'MSFT']))


if __name__ == '__main__':
    unittest.main()
