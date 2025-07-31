import pytest
from unittest.mock import patch
from src.recollapse.core import Recollapse


class TestFuzzingModes:
    def test_mode_start_single_byte(self):
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
        assert len([v for v in variants if v.startswith("%41") or v.startswith("%42")]) == 2

    def test_mode_start_multiple_bytes(self):
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

    def test_mode_sep_with_punctuation(self):
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

    def test_mode_sep_multiple_punctuation(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_URL,
            modes=[Recollapse.MODE_SEP],
            range=[65, 65],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test.example-case")
        punctuation_positions = [4, 12]
        for pos in punctuation_positions:
            expected_before = f"test.example-case"[:pos] + "%41" + f"test.example-case"[pos:]
            expected_after = f"test.example-case"[:pos+1] + "%41" + f"test.example-case"[pos+1:]
            assert expected_before in variants
            assert expected_after in variants

    def test_mode_sep_no_punctuation(self):
        recollapse = Recollapse(
            modes=[Recollapse.MODE_SEP],
            range=[65, 65],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("testexample")
        assert len(variants) == 0

    def test_mode_term_basic(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_URL,
            modes=[Recollapse.MODE_TERM],
            range=[65, 66],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test")
        assert "test%41" in variants
        assert "test%42" in variants

    def test_mode_term_empty_string(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_URL,
            modes=[Recollapse.MODE_TERM],
            range=[65, 65],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("")
        assert "%41" in variants

    def test_mode_re_meta_basic(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_URL,
            modes=[Recollapse.MODE_RE_META],
            range=[65, 65],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test.example")
        assert "test%41example" in variants

    def test_mode_re_meta_all_metachars(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_URL,
            modes=[Recollapse.MODE_RE_META],
            range=[65, 65],
            size=1,
            alphanum=True
        )
        metachars = ".^$*+-?()[]{}\\|"
        for char in metachars:
            variants = recollapse.generate(f"test{char}example")
            assert f"test%41example" in variants, f"Failed for metachar: {char}"

    def test_mode_re_meta_no_metachars(self):
        recollapse = Recollapse(
            modes=[Recollapse.MODE_RE_META],
            range=[65, 65],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("testexample")
        assert len(variants) == 0

    def test_mode_norm_basic(self):
        recollapse = Recollapse(
            modes=[Recollapse.MODE_NORM],
            maxnorm=1
        )
        recollapse._build_normalization_dict()
        if 'A' in recollapse.normalization_d and recollapse.normalization_d['A']:
            variants = recollapse.generate("testAexample")
            assert len(variants) > 0

    def test_mode_norm_maxnorm_limit(self):
        recollapse = Recollapse(
            modes=[Recollapse.MODE_NORM],
            maxnorm=2
        )
        recollapse._build_normalization_dict()
        if 'A' in recollapse.normalization_d and len(recollapse.normalization_d['A']) >= 2:
            variants = recollapse.generate("A")
            unique_variants = set(variants)
            assert len(unique_variants) <= 3

    def test_mode_case_basic(self):
        recollapse = Recollapse(
            modes=[Recollapse.MODE_CASE]
        )
        recollapse._build_case_dict()
        variants = recollapse.generate("testAexample")
        if 'A' in recollapse.case_d and recollapse.case_d['A']:
            assert len(variants) > 0

    def test_mode_trunc_basic(self):
        recollapse = Recollapse(
            modes=[Recollapse.MODE_TRUNC]
        )
        recollapse._build_truncation_dict()
        variants = recollapse.generate("testAexample")
        if 'A' in recollapse.truncation_d and recollapse.truncation_d['A']:
            assert len(variants) > 0

    def test_multiple_modes_combined(self):
        recollapse = Recollapse(
            encoding=Recollapse.ENCODING_URL,
            modes=[Recollapse.MODE_START, Recollapse.MODE_TERM],
            range=[65, 65],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test")
        assert "%41test" in variants
        assert "test%41" in variants

    def test_all_modes_combined(self):
        recollapse = Recollapse(
            modes=Recollapse.MODES_ALL,
            range=[65, 65],
            size=1,
            alphanum=True,
            maxnorm=1
        )
        variants = recollapse.generate("test.example")
        assert len(variants) > 0

    def test_no_modes_selected(self):
        recollapse = Recollapse(
            modes=[],
            range=[65, 65],
            size=1,
            alphanum=True
        )
        variants = recollapse.generate("test")
        assert len(variants) == 0

    def test_mode_constants(self):
        assert Recollapse.MODES_ALL == [
            Recollapse.MODE_START,
            Recollapse.MODE_SEP,
            Recollapse.MODE_NORM,
            Recollapse.MODE_TERM,
            Recollapse.MODE_RE_META,
            Recollapse.MODE_CASE,
            Recollapse.MODE_TRUNC
        ]

    def test_alphanum_filtering_in_modes(self):
        recollapse = Recollapse(
            modes=[Recollapse.MODE_START],
            range=[65, 90],
            size=1,
            alphanum=False
        )
        variants = recollapse.generate("test")
        assert len(variants) == 0

    def test_replacement_vs_insertion(self):
        recollapse_replace = Recollapse(
            encoding=Recollapse.ENCODING_URL,
            modes=[Recollapse.MODE_RE_META],
            range=[65, 65],
            size=1,
            alphanum=True
        )
        recollapse_insert = Recollapse(
            encoding=Recollapse.ENCODING_URL,
            modes=[Recollapse.MODE_START],
            range=[65, 65],
            size=1,
            alphanum=True
        )
        
        input_text = "test.example"
        variants_replace = recollapse_replace.generate(input_text)
        variants_insert = recollapse_insert.generate(input_text)
        
        assert "test%41example" in variants_replace
        assert "%41test.example" in variants_insert
