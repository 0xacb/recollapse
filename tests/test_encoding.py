import pytest
from src.recollapse.core import Recollapse


class TestEncodingModes:
    def test_url_encoding_basic(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_URL,
            modes=[Recollapse.MODE_START],
            range=[65, 65],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test")
        assert "%41test" in variants

    def test_url_encoding_special_chars(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_URL,
            modes=[Recollapse.MODE_START],
            range=[32, 32],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test")
        assert "%20test" in variants

    def test_raw_encoding_basic(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_RAW,
            modes=[Recollapse.MODE_START],
            range=[65, 65],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test")
        assert "Atest" in variants

    def test_raw_encoding_filtered_chars(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_RAW,
            modes=[Recollapse.MODE_START],
            range=[10, 12],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test")
        for variant in variants:
            assert "\n" not in variant
            assert "\r" not in variant

    def test_raw_encoding_escape_char_filtered(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_RAW,
            modes=[Recollapse.MODE_START],
            range=[27, 27],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test")
        for variant in variants:
            assert "\x1b" not in variant

    def test_unicode_encoding_basic(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_UNICODE,
            modes=[Recollapse.MODE_START],
            range=[65, 65],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test")
        assert "\\u0041test" in variants

    def test_unicode_encoding_high_values(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_UNICODE,
            modes=[Recollapse.MODE_START],
            range=[1024, 1024],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test")
        assert "\\u0400test" in variants

    def test_double_url_encoding_basic(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_DOUBLE_URL,
            modes=[Recollapse.MODE_START],
            range=[65, 65],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test")
        assert "%2541test" in variants

    def test_double_url_encoding_special_chars(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_DOUBLE_URL,
            modes=[Recollapse.MODE_START],
            range=[32, 32],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test")
        assert "%2520test" in variants

    def test_url_encoding_high_byte_values(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_URL,
            modes=[Recollapse.MODE_START],
            range=[256, 256],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test")
        for variant in variants:
            assert variant.startswith("%") or variant == "test"

    def test_encoding_with_replacement_mode(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_URL,
            modes=[Recollapse.MODE_RE_META],
            range=[65, 65],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test.example")
        assert "test%41example" in variants

    def test_encoding_with_multiple_bytes(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_URL,
            modes=[Recollapse.MODE_START],
            range=[65, 66],
            size=2,
            alphanum=True
        )
        variants = recollapse.generate("test")
        assert "%41%41test" in variants
        assert "%41%42test" in variants
        assert "%42%41test" in variants
        assert "%42%42test" in variants

    def test_raw_encoding_unicode_error_handling(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_RAW,
            modes=[Recollapse.MODE_START],
            range=[0xD800, 0xD800],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test")
        assert len(variants) == 0 or all("test" in v for v in variants)

    def test_all_encodings_produce_variants(self):
        for encoding in [
            Recollapse.ENCODING_URL,
            Recollapse.ENCODING_UNICODE,
            Recollapse.ENCODING_RAW,
            Recollapse.ENCODING_DOUBLE_URL
        ]:
            recollapse = Recollapse(
                encoding=encoding,
                modes=[Recollapse.MODE_START],
                range=[65, 65],
                size=1,
                alphanum=True
            )
            variants = recollapse.generate("test")
            assert len(variants) > 0

    def test_double_url_encoding_high_byte(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_DOUBLE_URL,
            modes=[Recollapse.MODE_START],
            range=[256, 256],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test")
        assert len(variants) > 0
