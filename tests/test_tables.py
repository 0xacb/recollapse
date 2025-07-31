import pytest
from unittest.mock import patch
from src.recollapse.core import Recollapse


class TestTableGeneration:
    def test_build_normalization_dict_structure(self):
        recollapse = Recollapse()
        recollapse._build_normalization_dict()
        
        assert isinstance(recollapse.normalization_d, dict)
        assert len(recollapse.normalization_d) > 0
        
        for key, value in recollapse.normalization_d.items():
            assert isinstance(key, str)
            assert len(key) == 1
            assert isinstance(value, list)
            assert 0x20 <= ord(key) <= 0x7f

    def test_build_truncation_dict_structure(self):
        recollapse = Recollapse()
        recollapse._build_truncation_dict()
        
        assert isinstance(recollapse.truncation_d, dict)
        assert len(recollapse.truncation_d) > 0
        
        for key, value in recollapse.truncation_d.items():
            assert isinstance(key, str)
            assert len(key) == 1
            assert isinstance(value, list)

    def test_build_case_dict_structure(self):
        recollapse = Recollapse()
        recollapse._build_case_dict()
        
        assert isinstance(recollapse.case_d, dict)
        assert len(recollapse.case_d) > 0
        
        for key, value in recollapse.case_d.items():
            assert isinstance(key, str)
            assert len(key) == 1
            assert isinstance(value, list)

    def test_print_normalization_table_text(self):
        recollapse = Recollapse()
        recollapse._build_normalization_dict()
        
        with patch('builtins.print') as mock_print:
            recollapse.print_normalization_table()
            mock_print.assert_called()

    def test_print_truncation_table_text(self):
        recollapse = Recollapse()
        recollapse._build_truncation_dict()
        
        with patch('builtins.print') as mock_print:
            recollapse.print_truncation_table()
            mock_print.assert_called()

    def test_print_case_table_text(self):
        recollapse = Recollapse()
        recollapse._build_case_dict()
        
        with patch('builtins.print') as mock_print:
            recollapse.print_case_table()
            mock_print.assert_called()

    def test_print_normalization_table_html(self):
        recollapse = Recollapse(html=True)
        recollapse._build_normalization_dict()
        
        with patch('builtins.print') as mock_print:
            recollapse.print_normalization_table()
            mock_print.assert_called()
            
            call_args_list = [str(call) for call in mock_print.call_args_list]
            html_content = ''.join(call_args_list)
            assert 'DOCTYPE html' in html_content
            assert '<html>' in html_content
            assert '</html>' in html_content

    def test_print_truncation_table_html(self):
        recollapse = Recollapse(html=True)
        recollapse._build_truncation_dict()
        
        with patch('builtins.print') as mock_print:
            recollapse.print_truncation_table()
            mock_print.assert_called()
            
            call_args_list = [str(call) for call in mock_print.call_args_list]
            html_content = ''.join(call_args_list)
            assert 'DOCTYPE html' in html_content

    def test_print_case_table_html(self):
        recollapse = Recollapse(html=True)
        recollapse._build_case_dict()
        
        with patch('builtins.print') as mock_print:
            recollapse.print_case_table()
            mock_print.assert_called()
            
            call_args_list = [str(call) for call in mock_print.call_args_list]
            html_content = ''.join(call_args_list)
            assert 'DOCTYPE html' in html_content

    def test_run_with_normtable_flag(self):
        recollapse = Recollapse(normtable=True)
        
        with patch('builtins.print') as mock_print:
            recollapse.run()
            mock_print.assert_called()

    def test_run_with_trunctable_flag(self):
        recollapse = Recollapse(trunctable=True)
        
        with patch('builtins.print') as mock_print:
            recollapse.run()
            mock_print.assert_called()

    def test_run_with_casetable_flag(self):
        recollapse = Recollapse(casetable=True)
        
        with patch('builtins.print') as mock_print:
            recollapse.run()
            mock_print.assert_called()

    def test_table_dictionaries_are_class_variables(self):
        recollapse1 = Recollapse()
        recollapse2 = Recollapse()
        
        recollapse1._build_normalization_dict()
        
        assert recollapse1.normalization_d is recollapse2.normalization_d
        assert len(recollapse2.normalization_d) > 0

    def test_normalization_dict_content_sample(self):
        recollapse = Recollapse()
        recollapse._build_normalization_dict()
        
        for ascii_char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if ascii_char in recollapse.normalization_d:
                normalizations = recollapse.normalization_d[ascii_char]
                for norm_char in normalizations:
                    assert norm_char != ascii_char

    def test_case_dict_content_sample(self):
        recollapse = Recollapse()
        recollapse._build_case_dict()
        
        if 'A' in recollapse.case_d:
            case_variants = recollapse.case_d['A']
            for variant in case_variants:
                assert variant != 'A'

    def test_print_table_empty_dict(self):
        recollapse = Recollapse()
        empty_dict = {}
        
        with patch('builtins.print') as mock_print:
            try:
                recollapse.print_table(empty_dict)
            except (ValueError, ZeroDivisionError, KeyError):
                pass
            else:
                mock_print.assert_called()

    def test_case_dict_warning_output(self):
        recollapse = Recollapse()
        
        with patch('builtins.print') as mock_print:
            recollapse._build_case_dict()
            
            warning_calls = [call for call in mock_print.call_args_list 
                           if len(call.args) > 0 and 'Warning:' in str(call.args[0])]
            
            for call in warning_calls:
                assert 'more than one character' in str(call.args[0])

    def test_table_generation_performance(self):
        recollapse = Recollapse()
        
        import time
        start_time = time.time()
        recollapse._build_normalization_dict()
        norm_time = time.time() - start_time
        
        start_time = time.time()
        recollapse._build_case_dict()
        case_time = time.time() - start_time
        
        start_time = time.time()
        recollapse._build_truncation_dict()
        trunc_time = time.time() - start_time
        
        assert norm_time < 10
        assert case_time < 10
        assert trunc_time < 10

    def test_conditional_table_builds(self):
        recollapse = Recollapse()
        Recollapse.truncation_d = {}
        recollapse.trunctable = True
        recollapse.run()
        assert len(Recollapse.truncation_d) > 0

        recollapse = Recollapse()
        Recollapse.case_d = {}
        recollapse.casetable = True
        recollapse.run()
        assert len(Recollapse.case_d) > 0

    def test_unicode_error_handling(self):
        from unittest.mock import patch
        recollapse = Recollapse()
        
        original_chr = chr
        def mock_chr(x):
            if x == 0xdc00:
                raise UnicodeEncodeError('test', '', 0, 1, 'test error')
            return original_chr(x)
        
        with patch('builtins.chr', mock_chr):
            recollapse._build_truncation_dict()
