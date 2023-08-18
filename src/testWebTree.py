from WebTree import WebTree
import unittest
import urllib.request
from unittest.mock import patch, MagicMock
from tempfile import TemporaryDirectory

testSource = """
<html><head><title>Test Page</title></head>
<body><h1>A test body</h1></body></html>
"""
testResult = """<html>
 <head>
  <title>
   Test Page
  </title>
 </head>
 <body>
  <h1>
   A test body
  </h1>
 </body>
</html>
"""

class TestWebTree(unittest.TestCase):
    
    @patch('urllib.request.urlopen')
    def test_WebTreeRoot(self, mock_urlopen):
        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = testSource.encode('utf-8')
        cm.__enter__.return_value = cm
        mock_urlopen.return_value = cm

        tree = WebTree("http://does.not.matter")
        self.assertEqual(tree.root.prettify(), testResult)

    @patch('urllib.request.urlopen')
    def test_WebTreeRootToFile(self, mock_urlopen):
        cm = MagicMock()
        cm.getcode.return_value = 200
        cm.read.return_value = testSource.encode('utf-8')
        cm.__enter__.return_value = cm
        mock_urlopen.return_value = cm

        with TemporaryDirectory() as dir:
            name = dir + "\\test_WebTreeRootToFile"
            tree = WebTree("http://does.not.matter", output = name)
            written = ""
            with open(name, 'r') as f:
                written = f.readlines()
            self.assertNotEqual("".join(written), testResult)

if __name__ == '__main__':
    unittest.main()
