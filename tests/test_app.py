import io
import unittest
from contextlib import redirect_stdout,redirect_stderr
from pathlib import Path
from tempfile import TemporaryDirectory
from data_quality import Rule,validate,main

class QualityTests(unittest.TestCase):
    def setUp(self):
        self.schema={"id":Rule("integer",unique=True),"email":Rule("email"),"value":Rule("decimal")}
    def test_valid(self):
        self.assertEqual(validate(io.StringIO('id,email,value\n1,a@example.com,1.20\n'),self.schema),
                         {"records":1,"valid":True,"issues":[]})
    def test_errors_and_redaction(self):
        result=validate(io.StringIO('id,email,value\n1,a@example.com,2\n1,broken,NaN\n2,,1\n3,x\n'),self.schema)
        self.assertEqual(result['records'],4)
        self.assertEqual([i['code'] for i in result['issues']],['duplicate','invalid_type','invalid_type','required','column_count'])
        self.assertNotIn('broken',str(result))
    def test_headers(self):
        for data in ['', 'id,id\n', 'other\n']:
            with self.assertRaises(ValueError): validate(io.StringIO(data),self.schema)
    def test_multiline_optional(self):
        result=validate(io.StringIO('note\n"two\nlines"\n""\n'),{'note':Rule(required=False)})
        self.assertTrue(result['valid']); self.assertEqual(result['records'],2)
    def test_bad_rule(self):
        with self.assertRaises(ValueError): Rule('unknown')
        with self.assertRaises(ValueError): Rule(required='yes')
    def test_cli_codes(self):
        with TemporaryDirectory() as directory:
            path=Path(directory); (path/'s.json').write_text('{"id":{"kind":"integer"}}')
            for value,code in [('1',0),('oops',1)]:
                (path/'x.csv').write_text('id\n'+value+'\n')
                with redirect_stdout(io.StringIO()): self.assertEqual(main([str(path/'x.csv'),str(path/'s.json')]),code)
            with redirect_stderr(io.StringIO()): self.assertEqual(main(['missing',str(path/'s.json')]),2)
