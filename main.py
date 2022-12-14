from os import PathLike
from pathlib import Path
from typing import Union

from lxml import etree as ET
from tqdm import tqdm


def get_tree_count(pfin: Path) -> int:
    """Count the number of "alpino_ds" nodes in a given file. We use iterparse to avoid OOM issues but that makes
     it slow!

    :param pfin: input file to query for alpino_ds nodes
    :return: number of alpino_ds nodes in the given file
    """
    el_count = 0
    with pfin.open("rb") as fhin:
        for _, element in tqdm(ET.iterparse(fhin, tag="alpino_ds", events=("end", )),
                               unit="trees", leave=False, desc="Counting no. trees"):
            el_count += 1

            # Clean up to save memory
            element.clear()

    return el_count


def main(din: Union[str, PathLike], dout: Union[str, PathLike], xpath: Union[str, PathLike], exact_tqdm: bool = False):
    """Extract all sentences from given Alpino files that match with a given XPath query and write them to output files.

    :param din: input directory, all XML files in here will be processed
    :param dout: output directory, one file with matching sentences will be written per input file (if matches are found)
    :param xpath: the XPath to match. Either a string, or a file. If a file is given, its contents will be used as XPath
    :param exact_tqdm: whether to show an "exact" TQDM progress bar. This requires us to first scan for each file how
    many trees there are. This number can then be used in the progress bar. This is very slow, though (to avoid memory
    issues) as it will have to go over each file twice so it is recommended to keep this False except or when you
     _really_ like progress bars
    """
    if Path(xpath).exists():
        xpath = Path(xpath).read_text(encoding="utf-8").strip()

    # Make xpath query relative, because we will be executing it on subnodes if low_memory_usage
    # Cf. https://stackoverflow.com/a/74798156/1150683
    xpath = f".{xpath}"
    files = list(Path(din).glob("*.xml"))
    pdout = Path(dout).resolve()

    pdout.mkdir(exist_ok=True, parents=True)
    for pfin in tqdm(files, unit="file", position=0):
        pfout = pdout.joinpath(f"{pfin.stem}.txt")
        with pfout.open("w", encoding="utf-8") as fhout, pfin.open("rb") as fhin:
            n_total_trees = get_tree_count(pfin) if exact_tqdm else None
            for _, element in tqdm(ET.iterparse(fhin, tag="alpino_ds", events=("end", )),
                                   unit="tree", position=1, leave=False, total=n_total_trees):
                if element.xpath(xpath):
                    fhout.write(f"{element.find('sentence').text.strip()}\n")

                element.clear()

        # Remove file if we did not write anything to it
        if pfout.stat().st_size == 0:
            pfout.unlink()


if __name__ == "__main__":
    import argparse

    cparser = argparse.ArgumentParser(description="Extract all sentences from given Alpino files that match with a"
                                                  " given XPath query and write them to output files.")
    cparser.add_argument("din", help="Directory that contains XML files with Alpino parses in them."
                                     " All XML files in this directory will be queried against.")
    cparser.add_argument("dout", help="Directory to write results to. Will create one file per input file in "
                                      " this directory.")
    cparser.add_argument("xpath", help="XPath query to use. Can be a string or a path to a file. In case of a file, "
                                       " its contents will be used as an XPath query")

    cargs = cparser.parse_args()
    main(cargs.din, cargs.dout, cargs.xpath)
