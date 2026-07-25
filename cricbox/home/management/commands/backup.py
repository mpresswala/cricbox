import sqlite3
import tarfile
import time
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create a consistent snapshot of the SQLite database and media files."

    def add_arguments(self, parser):
        parser.add_argument("--dest", default=None, help="Directory to write backups to.")
        parser.add_argument("--keep", type=int, default=14, help="Number of each backup type to keep.")

    def handle(self, *args, **options):
        db = settings.DATABASES["default"]
        if "sqlite" not in db["ENGINE"]:
            raise CommandError("backup only supports the SQLite database backend.")

        db_path = Path(db["NAME"])
        if not db_path.exists():
            raise CommandError(f"Database not found: {db_path}")

        default_dest = Path(getattr(settings, "DATA_DIR", db_path.parent)) / "backups"
        dest = Path(options["dest"]) if options["dest"] else default_dest
        dest.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%d-%H%M%S")

        # Consistent online snapshot — safe while the app is serving requests.
        db_backup = dest / f"db-{stamp}.sqlite3"
        source = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        try:
            target = sqlite3.connect(str(db_backup))
            try:
                source.backup(target)
            finally:
                target.close()
        finally:
            source.close()
        self.stdout.write(self.style.SUCCESS(f"Database -> {db_backup}"))

        # Uploaded media lives outside the database, so back it up too.
        media_root = Path(getattr(settings, "MEDIA_ROOT", "") or "")
        if media_root.is_dir() and any(media_root.iterdir()):
            media_backup = dest / f"media-{stamp}.tar.gz"
            with tarfile.open(media_backup, "w:gz") as tar:
                tar.add(media_root, arcname="media")
            self.stdout.write(self.style.SUCCESS(f"Media    -> {media_backup}"))

        self._prune(dest, "db-*.sqlite3", options["keep"])
        self._prune(dest, "media-*.tar.gz", options["keep"])

    def _prune(self, dest, pattern, keep):
        for old in sorted(dest.glob(pattern), reverse=True)[keep:]:
            old.unlink()
            self.stdout.write(f"Pruned {old.name}")
