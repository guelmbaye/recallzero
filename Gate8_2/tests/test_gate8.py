import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from gate8 import safe_image, load_replay

class G8Tests(unittest.TestCase):
    def test_escape_rejected(self):
        with tempfile.TemporaryDirectory() as p:
            root=Path(p)
            with self.assertRaises(ValueError): safe_image(root,'../secret.jpg')
            with self.assertRaises(ValueError): safe_image(root,'evidence/../../secret.jpg')
    def test_missing_seal_rejected(self):
        with tempfile.TemporaryDirectory() as p:
            with self.assertRaisesRegex(ValueError,'Missing Gate 7 seal'):load_replay(p)

if __name__=='__main__': unittest.main()
