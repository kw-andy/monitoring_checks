import unittest
import io
import textwrap

from cabourotte_autoconfig import ingress_cleaning
from cabourotte_autoconfig import routes_cleaning
from cabourotte_autoconfig import add_healthcheck
from cabourotte_autoconfig import remove_healthcheck




class TestCabourotte(unittest.TestCase):


    def test_ingress_cleaning(self):
        self.cleaned_ingress = ingress_cleaning('NAMESPACE                       NAME                                                           AGE\naberdeentotalgepi               aberdeentotalgepi-mlfgepi                                      167d\naeropostaleosui                 aeropostaleosui-mlfwordpress                                   167d\n')
        self.final_result_ingress = [['aberdeentotalgepi','aberdeentotalgepi-mlfgepi'],['aeropostaleosui','aeropostaleosui-mlfwordpress']]
        assert self.cleaned_ingress == self.final_result_ingress

    def test_routes_cleaning(self):
        self.cleaned_routes = routes_cleaning([['aberdeentotalgepi', 'aberdeentotalgepi-mlfgepi', '\nHost(`aberdeentotalgepi.dev.mlfmonde.org`)\n'], ['aeropostaleosui', 'aeropostaleosui-mlfwordpress', '\nHost(`aeropostaleosui.dev.mlfmonde.org`)\n']])
        self.final_result_routes = [['aberdeentotalgepi', 'aberdeentotalgepi-mlfgepi', 'aberdeentotalgepi.dev.mlfmonde.org'], ['aeropostaleosui', 'aeropostaleosui-mlfwordpress', 'aeropostaleosui.dev.mlfmonde.org']]
        assert self.cleaned_routes == self.final_result_routes


    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()    