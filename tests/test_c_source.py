import os
import unittest

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

import asn1tools


CODECS_AND_MODULES = [
    ('oer', asn1tools.c_source.oer),
    ('uper', asn1tools.c_source.uper)
]


class Asn1ToolsCSourceTest(unittest.TestCase):

    def test_compile_error_unsupported_type(self):
        for codec, module in CODECS_AND_MODULES:
            foo = asn1tools.compile_string(
                'Foo DEFINITIONS AUTOMATIC TAGS ::= BEGIN '
                '    A ::= OBJECT IDENTIFIER '
                'END',
                codec)

            with self.assertRaises(asn1tools.errors.Error) as cm:
                module.generate(foo, 'foo')

            self.assertEqual(str(cm.exception),
                             "Foo.A: Unsupported type 'OBJECT IDENTIFIER'.")

    def test_compile_error_unsupported_type_in_sequence(self):
        for codec, module in CODECS_AND_MODULES:
            foo = asn1tools.compile_string(
                'Foo DEFINITIONS AUTOMATIC TAGS ::= BEGIN '
                '    A ::= SEQUENCE { '
                '        a NumericString '
                '    } '
                'END',
                codec)

            with self.assertRaises(asn1tools.errors.Error) as cm:
                module.generate(foo, 'foo')

            self.assertEqual(str(cm.exception),
                             "Foo.A.a: Unsupported type 'NumericString'.")

    def test_compile_error_integer_no_minimum_nor_maximum(self):
        for codec, module in CODECS_AND_MODULES:
            foo = asn1tools.compile_string(
                'Foo DEFINITIONS AUTOMATIC TAGS ::= BEGIN '
                '    A ::= INTEGER '
                'END',
                codec)

            with self.assertRaises(asn1tools.errors.Error) as cm:
                module.generate(foo, 'foo')

            self.assertEqual(str(cm.exception),
                             "Foo.A: INTEGER has no minimum value.")

    def test_compile_error_integer_no_minimum(self):
        for codec, module in CODECS_AND_MODULES:
            foo = asn1tools.compile_string(
                'Foo DEFINITIONS AUTOMATIC TAGS ::= BEGIN '
                '    A ::= INTEGER (MIN..10) '
                'END',
                codec)

            with self.assertRaises(asn1tools.errors.Error) as cm:
                module.generate(foo, 'foo')

            self.assertEqual(str(cm.exception),
                             "Foo.A: INTEGER has no minimum value.")

    def test_compile_error_integer_no_maximum(self):
        for codec, module in CODECS_AND_MODULES:
            foo = asn1tools.compile_string(
                'Foo DEFINITIONS AUTOMATIC TAGS ::= BEGIN '
                '    A ::= INTEGER (1..MAX) '
                'END',
                codec)

            with self.assertRaises(asn1tools.errors.Error) as cm:
                module.generate(foo, 'foo')

            self.assertEqual(str(cm.exception),
                             "Foo.A: INTEGER has no maximum value.")

    def test_compile_error_integer_over_64_bits(self):
        for codec, module in CODECS_AND_MODULES:
            foo = asn1tools.compile_string(
                'Foo DEFINITIONS AUTOMATIC TAGS ::= BEGIN '
                '    A ::= INTEGER (0..18446744073709551616) '
                'END',
                codec)

            with self.assertRaises(asn1tools.errors.Error) as cm:
                module.generate(foo, 'foo')

            self.assertEqual(str(cm.exception),
                             "Foo.A: Type does not fit in 64 bits.")

    def test_compile_error_octet_string_no_size(self):
        for codec, module in CODECS_AND_MODULES:
            foo = asn1tools.compile_string(
                'Foo DEFINITIONS AUTOMATIC TAGS ::= BEGIN '
                '    A ::= OCTET STRING '
                'END',
                codec)

            with self.assertRaises(asn1tools.errors.Error) as cm:
                module.generate(foo, 'foo')

            self.assertEqual(str(cm.exception),
                             "Foo.A: OCTET STRING has no maximum length.")

    def test_compile_error_octet_string_no_maximum(self):
        for codec, module in CODECS_AND_MODULES:
            foo = asn1tools.compile_string(
                'Foo DEFINITIONS AUTOMATIC TAGS ::= BEGIN '
                '    A ::= OCTET STRING (SIZE(1..MAX)) '
                'END',
                codec)

            with self.assertRaises(asn1tools.errors.Error) as cm:
                module.generate(foo, 'foo')

            self.assertEqual(str(cm.exception),
                             "Foo.A: OCTET STRING has no maximum length.")

    def test_compile_error_sequence_of_no_size(self):
        for codec, module in CODECS_AND_MODULES:
            foo = asn1tools.compile_string(
                'Foo DEFINITIONS AUTOMATIC TAGS ::= BEGIN '
                '    A ::= SEQUENCE OF BOOLEAN '
                'END',
                codec)

            with self.assertRaises(asn1tools.errors.Error) as cm:
                module.generate(foo, 'foo')

            self.assertEqual(str(cm.exception),
                             "Foo.A: SEQUENCE OF has no maximum length.")

    def test_compile_error_sequence_of_no_maximum(self):
        for codec, module in CODECS_AND_MODULES:
            foo = asn1tools.compile_string(
                'Foo DEFINITIONS AUTOMATIC TAGS ::= BEGIN '
                '    A ::= SEQUENCE (SIZE(1..MAX)) OF BOOLEAN '
                'END',
                codec)

            with self.assertRaises(asn1tools.errors.Error) as cm:
                module.generate(foo, 'foo')

            self.assertEqual(str(cm.exception),
                             "Foo.A: SEQUENCE OF has no maximum length.")

    def test_compile_error_oer_real_not_ieee754(self):
        foo = asn1tools.compile_string(
            'Foo DEFINITIONS AUTOMATIC TAGS ::= BEGIN '
            '    A ::= REAL '
            'END',
            'oer')

        with self.assertRaises(asn1tools.errors.Error) as cm:
            asn1tools.c_source.oer.generate(foo, 'foo')

        self.assertEqual(str(cm.exception),
                         "Foo.A: REAL not IEEE 754 binary32 or binary64.")

    def test_compile_error_members_backtrace(self):
        for codec, module in CODECS_AND_MODULES:
            foo = asn1tools.compile_string(
                'Foo DEFINITIONS AUTOMATIC TAGS ::= BEGIN '
                '    A ::= SEQUENCE { '
                '        a CHOICE { '
                '            b INTEGER '
                '        } '
                '    } '
                'END',
                codec)

            with self.assertRaises(asn1tools.errors.Error) as cm:
                module.generate(foo, 'foo')

            self.assertEqual(str(cm.exception),
                             "Foo.A.a.b: INTEGER has no minimum value.")


if __name__ == '__main__':
    unittest.main()
