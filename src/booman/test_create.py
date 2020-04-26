import unittest

from packaging.version import Version

from booman.create import build_package_filename, parse_package_filename


class TestCreate(unittest.TestCase):

    def test_build_package_filename(self):
        ls = [
            ('foo.bar', '1.0', 'foo.bar.1.0.boop'),
            ('foo.bar', '2.30.1', 'foo.bar.2.30.1.boop'),
            ('foo.bar.baz', '9.8.1', 'foo.bar.baz.9.8.1.boop'),
        ]
        for (pkgname, pkgvers, result) in ls:
            pkgvers = Version(pkgvers)
            val = build_package_filename(pkgname, pkgvers)
            self.assertEqual(val, result)

    def test_parse_package_filename(self):
        ls = [
            ('foo.bar', '1.0', 'foo.bar.1.0.boop'),
            ('foo.bar', '1.0', 'FOO.BAR.1.0.BOOP'),
            ('foo.bar', '2.30.1', 'foo.bar.2.30.1.boop'),
            ('foo', '1.2.3', 'foo.1.2.3.boop'),
            ('hello.a.string', '12.95', 'hello.a.string.12.95.boop'),
            ('foo.bar', '1.0', 'foo.bar.boop'),
            ('foo.bar', '2.0', 'foo.bar.2.0.boop'),
            ('foo.bar.baz', '9.8.1', 'foo.bar.baz.9.8.1.boop'),
        ]

        for (pkgname, pkgvers, result) in ls:
            (resname, resvers) = parse_package_filename(result)
            self.assertEqual(resname, pkgname)
            self.assertEqual(str(resvers), pkgvers)

    def test_parse_package_filename_assume(self):
        (_, resvers) = parse_package_filename('foo.boop')
        self.assertEqual(str(resvers), '1.0')
        (_, resvers) = parse_package_filename('foo.boop', False)
        self.assertEqual(resvers, None)

        (_, resvers) = parse_package_filename('foo.1.0.boop')
        self.assertEqual(str(resvers), '1.0')
        (_, resvers) = parse_package_filename('foo.1.0.boop', False)
        self.assertEqual(str(resvers), '1.0')

        (_, resvers) = parse_package_filename('foo.2.5.boop')
        self.assertEqual(str(resvers), '2.5')
        (_, resvers) = parse_package_filename('foo.2.5.boop', False)
        self.assertEqual(str(resvers), '2.5')

    def test_parse_package_filename_bad(self):
        ls = [
            ('', ValueError),
            ('fooboop', ValueError),
            ('.boop', ValueError),
            ('!.boop', ValueError),
            ('hel lo.boop', ValueError),
            ('foo. boop', ValueError),
            ('1.2.3.boop', ValueError),
            ('1.2.$.boop', ValueError),
            ('foo.1.$.boop', ValueError),
            ('foo.$.boop', ValueError),
            ('foo.1._.boop', ValueError),
            ('foo..boop', ValueError),
            ('foo..1.boop', ValueError),
            ('foo.1..2.boop', ValueError),
            ('front^caret.boop', ValueError),
            ('mis.1.0.caret^.boop', ValueError),
            ('mis.1.0.^1.boop', ValueError),
            ('mis.1.0.^^x.boop', ValueError),
            ('mis.1.0.bo^op', ValueError),
        ]

        for val, exc in ls:
            self.assertRaises(exc, parse_package_filename, val)
