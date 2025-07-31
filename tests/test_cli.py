import argparse
import pytest
import sys
from unittest.mock import patch, mock_open
from src.recollapse.cli import parse_args, run_recollapse, main
from src.recollapse.core import Recollapse


class TestCLI:
    def test_parse_args_default(self):
        with patch.object(sys, 'argv', ['recollapse', 'test_input']):
            args = parse_args()
            assert args.input == 'test_input'
            assert args.modes == [1, 2, 3, 4, 5, 6, 7]
            assert args.encoding == 1
            assert args.range == [0, 255]
            assert args.size == 1
            assert args.file is None
            assert args.alphanum is False
            assert args.maxnorm == 3
            assert args.normtable is False
            assert args.trunctable is False
            assert args.casetable is False
            assert args.html is False

    def test_parse_args_with_options(self):
        with patch.object(sys, 'argv', [
            'recollapse', 'test_input',
            '-m', '1,2,3',
            '-e', '2',
            '-r', '10-20',
            '-s', '2',
            '-an',
            '-mn', '5',
            '--html'
        ]):
            args = parse_args()
            assert args.input == 'test_input'
            assert args.modes == [1, 2, 3]
            assert args.encoding == 2
            assert args.range == [10, 20]
            assert args.size == 2
            assert args.alphanum is True
            assert args.maxnorm == 5
            assert args.html is True

    def test_parse_args_hex_range(self):
        with patch.object(sys, 'argv', ['recollapse', 'test', '-r', '0x10,0x20']):
            args = parse_args()
            assert args.range == [16, 32]

    def test_parse_args_single_range_value(self):
        with patch.object(sys, 'argv', ['recollapse', 'test', '-r', '10']):
            args = parse_args()
            assert args.range == [10, 11]

    def test_parse_args_file_input(self):
        with patch.object(sys, 'argv', ['recollapse', '-f', 'test.txt']):
            args = parse_args()
            assert args.file == 'test.txt'
            assert args.input is None

    def test_parse_args_normtable(self):
        with patch.object(sys, 'argv', ['recollapse', '-nt']):
            args = parse_args()
            assert args.normtable is True

    def test_parse_args_trunctable(self):
        with patch.object(sys, 'argv', ['recollapse', '-tt']):
            args = parse_args()
            assert args.trunctable is True

    def test_parse_args_casetable(self):
        with patch.object(sys, 'argv', ['recollapse', '-ct']):
            args = parse_args()
            assert args.casetable is True

    def test_parse_args_version(self):
        with patch.object(sys, 'argv', ['recollapse', '--version']):
            with pytest.raises(SystemExit) as exc_info:
                parse_args()
            assert exc_info.value.code == 0

    def test_parse_args_invalid_modes(self):
        with patch.object(sys, 'argv', ['recollapse', 'test', '-m', 'invalid']):
            with pytest.raises(SystemExit) as exc_info:
                parse_args()
            assert exc_info.value.code == 1

    def test_parse_args_invalid_mode_number(self):
        with patch.object(sys, 'argv', ['recollapse', 'test', '-m', '1,8']):
            with pytest.raises(SystemExit) as exc_info:
                parse_args()
            assert exc_info.value.code == 1

    def test_parse_args_no_input_no_table_interactive(self):
        with patch.object(sys, 'argv', ['recollapse']):
            with patch.object(sys.stdin, 'isatty', return_value=True):
                with pytest.raises(SystemExit) as exc_info:
                    parse_args()
                assert exc_info.value.code == 1

    def test_parse_args_stdin_input(self):
        with patch.object(sys, 'argv', ['recollapse']):
            with patch.object(sys.stdin, 'isatty', return_value=False):
                with patch.object(sys.stdin, 'read', return_value='stdin_input\n'):
                    args = parse_args()
                    assert args.input == 'stdin_input'

    def test_run_recollapse_with_input(self):
        args = argparse.Namespace()
        args.input = 'test'
        args.modes = [1]
        args.encoding = 1
        args.range = [65, 65]
        args.size = 1
        args.file = None
        args.alphanum = True
        args.maxnorm = 3
        args.normtable = False
        args.trunctable = False
        args.casetable = False
        args.html = False
        
        with patch('builtins.print') as mock_print:
            run_recollapse(args)
            mock_print.assert_called()

    def test_run_recollapse_with_file(self):
        args = argparse.Namespace()
        args.input = None
        args.modes = [1]
        args.encoding = 1
        args.range = [65, 65]
        args.size = 1
        args.file = 'test.txt'
        args.alphanum = True
        args.maxnorm = 3
        args.normtable = False
        args.trunctable = False
        args.casetable = False
        args.html = False
        
        mock_file = mock_open(read_data="file_content\n")
        mock_file.return_value.readlines.return_value = ["file_content\n"]
        with patch("builtins.open", mock_file):
            with patch('builtins.print') as mock_print:
                run_recollapse(args)
                mock_print.assert_called()

    def test_run_recollapse_normtable(self):
        args = argparse.Namespace()
        args.input = None
        args.modes = [1]
        args.encoding = 1
        args.range = [65, 65]
        args.size = 1
        args.file = None
        args.alphanum = True
        args.maxnorm = 3
        args.normtable = True
        args.trunctable = False
        args.casetable = False
        args.html = False
        
        with patch('builtins.print') as mock_print:
            run_recollapse(args)
            mock_print.assert_called()

    def test_main_function(self):
        with patch.object(sys, 'argv', ['recollapse', 'test']):
            with patch('builtins.print') as mock_print:
                main()
                mock_print.assert_called()

    def test_encoding_choices(self):
        for encoding in [1, 2, 3, 4]:
            with patch.object(sys, 'argv', ['recollapse', 'test', '-e', str(encoding)]):
                args = parse_args()
                assert args.encoding == encoding

    def test_invalid_encoding_choice(self):
        with patch.object(sys, 'argv', ['recollapse', 'test', '-e', '5']):
            with pytest.raises(SystemExit):
                parse_args()

    def test_range_dash_separator(self):
        with patch.object(sys, 'argv', ['recollapse', 'test', '-r', '10-20']):
            args = parse_args()
            assert args.range == [10, 20]

    def test_main_entry_points(self):
        with patch('sys.argv', ['cli.py', '--version']):
            with pytest.raises(SystemExit) as exc_info:
                from src.recollapse.cli import main as cli_main
                cli_main()
            assert exc_info.value.code == 0

        with patch('sys.argv', ['__main__.py', '--version']):
            with pytest.raises(SystemExit) as exc_info:
                from src.recollapse.cli import main as main_func
                main_func()
            assert exc_info.value.code == 0

    def test_main_module_execution(self):
        import subprocess
        import sys
        import os
        env = os.environ.copy()
        env['PYTHONPATH'] = 'src'
        result = subprocess.run([sys.executable, '-m', 'recollapse', '--version'], 
                              capture_output=True, text=True, env=env)
        assert result.returncode == 0

    def test_cli_direct_execution(self):
        import subprocess
        import sys
        import os
        env = os.environ.copy()
        env['PYTHONPATH'] = 'src'
        result = subprocess.run([sys.executable, '-c', 
                               'import sys; sys.path.insert(0, "src"); from recollapse.cli import main; import sys; sys.argv=["cli.py", "--version"]; main()'], 
                              capture_output=True, text=True)
        assert result.returncode == 0
