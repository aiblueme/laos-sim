#!/usr/bin/env python3
"""
Image crawler for laos-sim project.
Downloads, converts to WebP, resizes, deduplicates, and generates thumbnails.
Uses icrawler with anti-bot mitigations.
"""

import os
import time
import random
import logging
import hashlib
from pathlib import Path
from PIL import Image
import io

# ── Configure logging ──────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
RAW_DIR    = BASE_DIR / "images" / "_raw"
FULL_DIR   = BASE_DIR / "images" / "full"
THUMB_DIR  = BASE_DIR / "images" / "thumbs"

for d in (RAW_DIR, FULL_DIR, THUMB_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ── Browser UA rotation list ──────────────────────────────────────────────────
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.119 Mobile Safari/537.36",
]

# ── Search keywords ────────────────────────────────────────────────────────────
KEYWORDS = [
    "Laos SIM card tourist",
    "Unitel Laos network",
    "LTC Laos telecom",
    "ETL Laos mobile",
    "Laos travel mobile data",
    "Vientiane phone shop SIM",
    "Laos eSIM international",
    "Laos coverage map mobile",
    "tourist buying SIM card Southeast Asia",
    "Luang Prabang travel phone",
]

MAX_PER_KEYWORD = 10   # keep under rate-limit radar
THROTTLE        = (2.0, 6.0)  # random delay range in seconds


def crawl_keyword(keyword: str, engine: str, save_dir: Path) -> int:
    """Run a single icrawler search. Returns number of files written."""
    from icrawler.builtin import BingImageCrawler, BaiduImageCrawler

    ua = random.choice(USER_AGENTS)
    feeder_threads  = 1
    parser_threads  = 1
    downloader_threads = 1

    crawler_kwargs = dict(
        feeder_threads=feeder_threads,
        parser_threads=parser_threads,
        downloader_threads=downloader_threads,
        storage={"root_dir": str(save_dir)},
    )

    try:
        if engine == "bing":
            crawler = BingImageCrawler(**crawler_kwargs)
        elif engine == "baidu":
            crawler = BaiduImageCrawler(**crawler_kwargs)
        else:
            raise ValueError(f"Unknown engine: {engine}")

        # Patch user-agent via session headers if possible
        try:
            crawler.downloader.session.headers.update({"User-Agent": ua})
        except AttributeError:
            pass

        crawler.crawl(
            keyword=keyword,
            max_num=MAX_PER_KEYWORD,
            min_size=(200, 150),
            file_idx_offset="auto",
        )
        files = list(save_dir.glob("*.*"))
        return len(files)

    except Exception as exc:
        log.warning("Crawl failed [%s / %s]: %s", engine, keyword, exc)
        return 0


def random_sleep():
    t = random.uniform(*THROTTLE)
    log.info("Sleeping %.1fs …", t)
    time.sleep(t)


def image_signature(path: Path) -> str:
    """Return a cheap dedup key: (file_size, width, height)."""
    try:
        with Image.open(path) as img:
            return f"{path.stat().st_size}_{img.width}_{img.height}"
    except Exception:
        return hashlib.md5(path.read_bytes()).hexdigest()


def convert_and_resize(src: Path, dest: Path, max_bytes: int = 1_000_000) -> bool:
    """Convert image to WebP, resize iteratively until under max_bytes."""
    try:
        with Image.open(src) as img:
            # Normalise colour mode
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")
            elif img.mode == "RGBA":
                bg = Image.new("RGB", img.size, (255, 255, 255))
                bg.paste(img, mask=img.split()[3])
                img = bg

            quality = 85
            while quality >= 40:
                buf = io.BytesIO()
                img.save(buf, format="WEBP", quality=quality)
                if buf.tell() <= max_bytes:
                    dest.write_bytes(buf.getvalue())
                    return True
                # Downscale by 10 % and retry
                new_w = int(img.width * 0.9)
                new_h = int(img.height * 0.9)
                img = img.resize((new_w, new_h), Image.LANCZOS)
                quality -= 5

            # Last resort: save at lowest quality
            buf = io.BytesIO()
            img.save(buf, format="WEBP", quality=40)
            dest.write_bytes(buf.getvalue())
            return True

    except Exception as exc:
        log.warning("Could not convert %s: %s", src.name, exc)
        return False


def make_thumbnail(src: Path, dest: Path, size=(300, 200)) -> bool:
    try:
        with Image.open(src) as img:
            if img.mode not in ("RGB", "RGBA"):
                img = img.convert("RGB")
            img.thumbnail(size, Image.LANCZOS)
            # Pad to exact size
            thumb = Image.new("RGB", size, (245, 230, 200))  # warm sand bg
            offset = ((size[0] - img.width) // 2, (size[1] - img.height) // 2)
            if img.mode == "RGBA":
                thumb.paste(img, offset, mask=img.split()[3])
            else:
                thumb.paste(img, offset)
            thumb.save(dest, format="WEBP", quality=80)
            return True
    except Exception as exc:
        log.warning("Thumbnail failed for %s: %s", src.name, exc)
        return False


def process_raw_images():
    """Convert all raw downloads → full/ and thumbs/."""
    raw_files = [
        f for f in RAW_DIR.rglob("*")
        if f.is_file() and f.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}
    ]
    log.info("Processing %d raw images …", len(raw_files))

    seen_sigs: set[str] = set()
    kept = 0

    for i, src in enumerate(raw_files):
        sig = image_signature(src)
        if sig in seen_sigs:
            log.info("  Duplicate skipped: %s", src.name)
            continue
        seen_sigs.add(sig)

        full_dest  = FULL_DIR  / f"laos_{i:04d}.webp"
        thumb_dest = THUMB_DIR / f"laos_{i:04d}.webp"

        ok = convert_and_resize(src, full_dest)
        if ok:
            make_thumbnail(full_dest, thumb_dest)
            kept += 1

    log.info("Kept %d unique images (full + thumbs).", kept)
    return kept


def main():
    log.info("=== Laos SIM image crawler starting ===")

    # ── Phase 1: Bing crawl ───────────────────────────────────────────────────
    log.info("--- Bing crawl ---")
    for kw in KEYWORDS:
        log.info("Bing: %s", kw)
        kw_dir = RAW_DIR / "bing" / kw.replace(" ", "_")[:40]
        kw_dir.mkdir(parents=True, exist_ok=True)
        try:
            crawl_keyword(kw, "bing", kw_dir)
        except Exception as exc:
            log.warning("Bing failed for '%s': %s", kw, exc)
        random_sleep()

    # ── Phase 2: Baidu crawl (sequential, after Bing) ─────────────────────────
    log.info("--- Baidu crawl ---")
    for kw in KEYWORDS:
        log.info("Baidu: %s", kw)
        kw_dir = RAW_DIR / "baidu" / kw.replace(" ", "_")[:40]
        kw_dir.mkdir(parents=True, exist_ok=True)
        try:
            crawl_keyword(kw, "baidu", kw_dir)
        except Exception as exc:
            log.warning("Baidu failed for '%s': %s", kw, exc)
        random_sleep()

    # ── Phase 3: Process images ───────────────────────────────────────────────
    kept = process_raw_images()
    if kept == 0:
        log.warning("No images were successfully processed. Site will use CSS placeholder backgrounds.")
    else:
        log.info("Done. %d images ready in images/full/ and images/thumbs/", kept)


if __name__ == "__main__":
    main()
