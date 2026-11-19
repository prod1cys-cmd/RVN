"""Extract cited illustrations from the exact source editions used for Book 3."""

import argparse
import hashlib
from pathlib import Path
import zipfile

import fitz


def verify(path, expected):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != expected:
        raise ValueError(f"Source edition mismatch for {path}: SHA-256 {digest}")


def extract_pdf(path, edition, page, bounds, dpi, destination):
    verify(path, edition)
    with fitz.open(path) as pdf:
        clip = fitz.Rect(*bounds)
        pdf[page - 1].get_pixmap(dpi=dpi, clip=clip, alpha=False).save(destination)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for source in ("ad8367", "ksz9893r", "book2_part3"):
        parser.add_argument(source, type=Path)
    args = parser.parse_args()
    output = Path(__file__).resolve().parent
    extract_pdf(args.ad8367,
                "7e1bfd7650058da281c2bc500f3ea2ae4c3823cd1541628aca4ddbb569818719",
                12, (319, 75, 553, 249), 450, output / "AD8367-fig30.png")
    extract_pdf(args.ksz9893r,
                "85af76600c5f7d90a3d87ec0ad50c1fa926f9ec317185f816324e41f40016d52",
                8, (78, 416, 553, 709), 350, output / "KSZ9893R-fig2-1.png")
    verify(args.book2_part3, "2a8d5336853603c0286ae1a2e57a69844bb039e5f3c51ec71fb77d553eaedd4f")
    with zipfile.ZipFile(args.book2_part3) as docx:
        (output / "book2-part3-fig-J5.png").write_bytes(docx.read("word/media/image10.png"))


if __name__ == "__main__":
    main()
