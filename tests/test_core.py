import pytest
from src.recollapse.core import Recollapse


class TestRecollapse:
    def test_init_default_values(self):
        recollapse = Recollapse()
        assert recollapse.size == Recollapse.DEFAULT_SIZE
        assert recollapse.encoding == Recollapse.DEFAULT_ENCODING
        assert recollapse.range == Recollapse.DEFAULT_RANGE
        assert recollapse.modes == Recollapse.DEFAULT_MODES
        assert recollapse.input is None
        assert recollapse.file is None
        assert recollapse.normtable is False
        assert recollapse.trunctable is False
        assert recollapse.casetable is False
        assert recollapse.html is False
        assert recollapse.alphanum is False
        assert recollapse.maxnorm == Recollapse.DEFAULT_MAX_NORM

    def test_init_custom_values(self):
        recollapse = Recollapse(
            size=2,
            encoding=Recollapse.ENCODING_RAW,
            range=[1, 10],
            modes=[Recollapse.MODE_START],
            input="test",
            alphanum=True,
            maxnorm=5
        )
        assert recollapse.size == 2
        assert recollapse.encoding == Recollapse.ENCODING_RAW
        assert recollapse.range == [1, 10]
        assert recollapse.modes == [Recollapse.MODE_START]
        assert recollapse.input == "test"
        assert recollapse.alphanum is True
        assert recollapse.maxnorm == 5

    def test_generate_basic(self):
        recollapse = Recollapse(
            input="test",
            encoding=Recollapse.ENCODING_URL,
            modes=[Recollapse.MODE_START],
            range=[65, 66],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test")
        assert len(variants) > 0
        assert "%41test" in variants
        assert "%42test" in variants

    def test_generate_raw_encoding(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_RAW,
            modes=[Recollapse.MODE_START],
            range=[65, 66],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test")
        assert "Atest" in variants
        assert "Btest" in variants

    def test_generate_unicode_encoding(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_UNICODE,
            modes=[Recollapse.MODE_START],
            range=[65, 66],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test")
        assert "\\u0041test" in variants
        assert "\\u0042test" in variants

    def test_generate_double_url_encoding(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_DOUBLE_URL,
            modes=[Recollapse.MODE_START],
            range=[65, 66],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test")
        assert "%2541test" in variants
        assert "%2542test" in variants

    def test_mode_start(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_URL,
            modes=[Recollapse.MODE_START],
            range=[65, 65],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test")
        assert "%41test" in variants

    def test_mode_term(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_URL,
            modes=[Recollapse.MODE_TERM],
            range=[65, 65],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test")
        assert "test%41" in variants

    def test_mode_sep(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_URL,
            modes=[Recollapse.MODE_SEP],
            range=[65, 65],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test.example")
        assert "test%41.example" in variants
        assert "test.%41example" in variants

    def test_mode_re_meta(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_URL,
            modes=[Recollapse.MODE_RE_META],
            range=[65, 65],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test.example")
        assert "test%41example" in variants

    def test_alphanum_filtering(self):
        recollapse = Recollapse(
            modes=[Recollapse.MODE_START],
            range=[65, 90],
            size=1,
            alphanum=False
        )
        variants = recollapse.generate("test")
        for variant in variants:
            assert not any(c.isalnum() for c in variant.replace("test", "").replace("%", ""))

    def test_alphanum_including(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_URL,
            modes=[Recollapse.MODE_START],
            range=[65, 66],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test")
        assert "%41test" in variants
        assert "%42test" in variants

    def test_empty_input(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_URL,
            modes=[Recollapse.MODE_START],
            range=[65, 65],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("")
        assert "%41" in variants

    def test_variants_are_sorted_and_unique(self):
        recollapse = Recollapse(
            modes=[Recollapse.MODE_START, Recollapse.MODE_TERM],
            range=[65, 66],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test")
        assert variants == sorted(set(variants))

    def test_build_normalization_dict(self):
        recollapse = Recollapse()
        recollapse._build_normalization_dict()
        assert isinstance(recollapse.normalization_d, dict)
        assert len(recollapse.normalization_d) > 0

    def test_build_truncation_dict(self):
        recollapse = Recollapse()
        recollapse._build_truncation_dict()
        assert isinstance(recollapse.truncation_d, dict)
        assert len(recollapse.truncation_d) > 0


    def test_build_case_dict(self):
        recollapse = Recollapse()
        recollapse._build_case_dict()
        assert isinstance(recollapse.case_d, dict)
        assert len(recollapse.case_d) > 0

    def test_constants(self):
        assert Recollapse.ENCODING_URL == 1
        assert Recollapse.ENCODING_UNICODE == 2
        assert Recollapse.ENCODING_RAW == 3
        assert Recollapse.ENCODING_DOUBLE_URL == 4
        
        assert Recollapse.MODE_START == 1
        assert Recollapse.MODE_SEP == 2
        assert Recollapse.MODE_NORM == 3
        assert Recollapse.MODE_TERM == 4
        assert Recollapse.MODE_RE_META == 5
        assert Recollapse.MODE_CASE == 6
        assert Recollapse.MODE_TRUNC == 7

    def test_regex_metachars(self):
        expected = ".^$*+-?()[]{}\\|"
        assert Recollapse.REGEX_METACHARS == expected

    def test_run_with_no_input_no_file(self):
        recollapse = Recollapse(input=None, file=None)
        recollapse.run()

    def test_lazy_dict_builds(self):
        recollapse = Recollapse(modes=[Recollapse.MODE_NORM])
        Recollapse.normalization_d = {}
        variants = recollapse.generate("A")
        assert len(Recollapse.normalization_d) > 0

        recollapse = Recollapse(modes=[Recollapse.MODE_TRUNC])
        Recollapse.truncation_d = {}
        variants = recollapse.generate("A")
        assert len(Recollapse.truncation_d) > 0

        recollapse = Recollapse(modes=[Recollapse.MODE_CASE])
        Recollapse.case_d = {}
        variants = recollapse.generate("A")
        assert len(Recollapse.case_d) > 0
