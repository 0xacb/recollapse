import argparse
import sys
from .core import Recollapse
from ._version import __version__ as VERSION


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="REcollapse is a helper tool for black-box regex fuzzing to bypass validations and discover normalizations in web applications")

    parser.add_argument("-m", "--modes", "-p", "--positions",
                        help="variation modes. Example: 1,2,3,4,5,6,7 (default). 1: starting, 2: separator, 3: normalization, 4: termination, 5: regex metacharacters, 6: case folding/upper/lower, 7: byte truncation",
                        required=False,
                        default=",".join(map(str, Recollapse.DEFAULT_MODES)),
                        type=str)
    parser.add_argument("-e", "--encoding",
                        help="1: URL-encoded format (default), 2: Unicode format, 3: Raw format, 4: Double URL-encoded format",
                        required=False,
                        default=Recollapse.DEFAULT_ENCODING_CLI,
                        type=int,
                        choices=range(1, 5))
    parser.add_argument("-r", "--range",
                        help="range of bytes for fuzzing. Example: 0,0xff (default)",
                        required=False,
                        default="0,0xff",
                        type=str)
    parser.add_argument("-s", "--size",
                        help="number of fuzzing bytes (default: 1)",
                        required=False,
                        default=Recollapse.DEFAULT_SIZE,
                        type=int)
    parser.add_argument("-f", "--file",
                        help="read input from file",
                        required=False)
    parser.add_argument("-an", "--alphanum",
                        help="include alphanumeric bytes in fuzzing range",
                        required=False,
                        default=False,
                        action="store_true")
    parser.add_argument("-mn", "--maxnorm",
                        help="maximum number of normalizations (default: 3)",
                        default=Recollapse.DEFAULT_MAX_NORM,
                        type=int)
    parser.add_argument("-mt", "--maxtrunc",
                        help="maximum number of truncations (default: 3)",
                        default=Recollapse.DEFAULT_MAX_TRUNC,
                        type=int)
    parser.add_argument("-nt", "--normtable",
                        help="print normalization table",
                        required=False,
                        default=False,
                        action="store_true")
    parser.add_argument("-tt", "--trunctable",
                        help="print truncation table",
                        required=False,
                        default=False,
                        action="store_true")
    parser.add_argument("-ct", "--casetable",
                        help="print case table",
                        required=False,
                        default=False,
                        action="store_true")
    parser.add_argument("--html",
                        help="output tables in HTML format",
                        required=False,
                        default=False,
                        action="store_true")
    parser.add_argument("input",
                        help="original input",
                        nargs="?")
    parser.add_argument("--version",
                        help="show recollapse version",
                        required=False,
                        action="store_true")
    args = parser.parse_args()

    if args.version:
        print(f"recollapse {VERSION}")
        sys.exit(0)

    del args.version
    
    if args.range:
        base = 0
        sep = ","
        if "0x" in args.range:
            base = 16
        if "-" in args.range:
            sep = "-"
        args.range = [int(x, base) for x in args.range.split(sep)]
        if len(args.range) == 1:
            args.range.append(args.range[0]+1)

    if args.modes:
        try:
            args.modes = [int(x) for x in args.modes.split(",")]
        except ValueError:
            print("Invalid modes provided")
            sys.exit(1)

        for mode in args.modes:
            if not 0 < mode <= 7:
                print("Invalid modes provided")
                sys.exit(1)

    args.size = int(args.size)

    if not args.input and not args.file and not \
        (args.normtable or args.trunctable or args.casetable):
        if not sys.stdin.isatty():
            args.input = sys.stdin.read().rstrip()
        else:
            parser.print_help()
            sys.exit(1)
    
    return args


def run_recollapse(args: argparse.Namespace) -> None:
    recollapse = Recollapse(**vars(args))
    recollapse.run()


def main() -> None:
    args = parse_args()
    run_recollapse(args)


if __name__ == "__main__":
    main()
