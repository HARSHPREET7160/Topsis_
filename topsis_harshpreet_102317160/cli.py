from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from .core import InputError, parse_weights, parse_impacts, topsis


USAGE = (
    "Usage:\n"
    "  python topsis.py <InputDataFile> <Weights> <Impacts> <OutputResultFileName>\n"
    "Example:\n"
    "  python topsis.py data.csv \"1,1,1,2,1\" \"+,+,-,+,+\" output-result.csv\n"
)


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if len(argv) != 4:
        print("Error: Incorrect number of parameters.\n")
        print(USAGE)
        return 1

    input_file, weights_raw, impacts_raw, output_file = argv

    try:
        weights = parse_weights(weights_raw)
        impacts = parse_impacts(impacts_raw)

        in_path = Path(input_file)
        if not in_path.exists():
            print("Error: File not found.")
            return 1

        df = pd.read_csv(in_path)

        result = topsis(df, weights, impacts).dataframe

        out_path = Path(output_file)
        result.to_csv(out_path, index=False)

        print(f"Success: Result written to {out_path}")
        return 0

    except FileNotFoundError:
        print("Error: File not found.")
        return 1
    except pd.errors.EmptyDataError:
        print("Error: Input file is empty or invalid CSV.")
        return 1
    except InputError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print("Error: Unexpected failure.")
        print(str(e))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
