from WebTree import WebTree
import unittest
import urllib.request
from unittest.mock import patch, MagicMock

class TestWebTree(unittest.TestCase):

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)
    @patch('urllib.request.urlopen')
    def test_cm(self, mock_urlopen):
        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = 'contents'
        cm.__enter__.return_value = cm
        mock_urlopen.return_value = cm

        with urllib.request.urlopen('http://foo') as response:
            self.assertEqual(response.getcode(), 200)
            self.assertEqual(response.read(), 'contents')

    @patch('urllib.request.urlopen')
    def test_no_cm(self, mock_urlopen):
        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = 'contents'
        mock_urlopen.return_value = cm

        response = urllib.request.urlopen('http://foo')
        self.assertEqual(response.getcode(), 200)
        self.assertEqual(response.read(), 'contents')
        response.close()


if __name__ == '__main__':
    unittest.main()
""" 
if __name__ == "__main__":
    # simple test of a known source page
    tree = WebTree("https://www.moravian.org/the-daily-texts/")
    tree.show()
 """