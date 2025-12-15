#!/usr/bin/env python3
"""
Cleanup Old Data Script

Enforces 7-day retention policy by removing bulletins older than 7 days.

Usage:
    python cleanup_old_data.py
    python cleanup_old_data.py --dry-run
"""

import argparse
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.logger import logger


class DataCleanup:
    """Cleanup old bulletin data files."""
    
    RETENTION_DAYS = 7
    REGIONS = ['usa', 'india', 'world']
    
    def __init__(self, dry_run: bool = False):
        """
        Initialize cleanup manager.
        
        Args:
            dry_run: If True, only print what would be deleted without actually deleting
        """
        self.dry_run = dry_run
        self.repo_root = Path(__file__).parent.parent.parent
        self.data_dir = self.repo_root / 'data'
        self.cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.RETENTION_DAYS)
        
        logger.info(
            "DataCleanup initialized",
            extra={
                "retention_days": self.RETENTION_DAYS,
                "cutoff_date": self.cutoff_date.strftime("%Y-%m-%d"),
                "dry_run": self.dry_run
            }
        )
    
    def find_old_files(self, region: str) -> List[Tuple[Path, str]]:
        """
        Find bulletin files older than retention period.
        
        Args:
            region: Region to scan (usa, india, world)
            
        Returns:
            List of (filepath, date) tuples for files to delete
        """
        region_dir = self.data_dir / region
        
        if not region_dir.exists():
            return []
        
        old_files = []
        
        for filepath in region_dir.glob('*.json'):
            # Parse date from filename (YYYY-MM-DD-period.json)
            filename = filepath.stem  # Remove .json
            
            try:
                # Extract date part (YYYY-MM-DD)
                date_str = filename.rsplit('-', 1)[0]  # Remove period suffix
                file_date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
                
                if file_date < self.cutoff_date:
                    old_files.append((filepath, date_str))
                    
            except ValueError as e:
                logger.warning(
                    f"Could not parse date from filename: {filename}",
                    extra={"error": str(e)}
                )
                continue
        
        return old_files
    
    def cleanup_region(self, region: str) -> Tuple[int, List[str]]:
        """
        Cleanup old files for a specific region.
        
        Args:
            region: Region to cleanup
            
        Returns:
            Tuple of (deleted_count, deleted_dates)
        """
        logger.info(f"Cleaning up {region} region")
        
        old_files = self.find_old_files(region)
        
        if not old_files:
            logger.info(f"No old files found in {region} region")
            return 0, []
        
        deleted_dates = set()
        
        for filepath, date_str in old_files:
            deleted_dates.add(date_str)
            
            if self.dry_run:
                logger.info(
                    f"[DRY RUN] Would delete: {filepath.relative_to(self.repo_root)}",
                    extra={"date": date_str}
                )
            else:
                try:
                    filepath.unlink()
                    logger.info(
                        f"Deleted: {filepath.relative_to(self.repo_root)}",
                        extra={"date": date_str}
                    )
                except Exception as e:
                    logger.error(
                        f"Failed to delete: {filepath.relative_to(self.repo_root)}",
                        extra={"error": str(e)}
                    )
        
        return len(old_files), sorted(deleted_dates)
    
    def update_index(self, deleted_dates_by_region: dict):
        """
        Update data/index.json to remove deleted entries.
        
        Args:
            deleted_dates_by_region: Dict of {region: [deleted_dates]}
        """
        index_file = self.data_dir / 'index.json'
        
        if not index_file.exists():
            logger.warning("Index file not found, skipping index update")
            return
        
        if self.dry_run:
            logger.info("[DRY RUN] Would update index.json")
            return
        
        try:
            with open(index_file, 'r', encoding='utf-8') as f:
                index = json.load(f)
            
            # Remove deleted dates from index
            for region, deleted_dates in deleted_dates_by_region.items():
                if region in index:
                    for date in deleted_dates:
                        if date in index[region]:
                            del index[region][date]
                            logger.info(f"Removed {region}/{date} from index")
            
            # Write updated index
            temp_index = index_file.with_suffix('.json.tmp')
            with open(temp_index, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2)
            
            temp_index.replace(index_file)
            
            logger.info("Index updated successfully")
            
        except Exception as e:
            logger.error(f"Failed to update index: {e}")
    
    def run(self) -> int:
        """
        Execute cleanup workflow.
        
        Returns:
            Exit code (0 = success, 1 = failure)
        """
        logger.info(
            "=== DATA CLEANUP STARTED ===",
            extra={
                "retention_days": self.RETENTION_DAYS,
                "cutoff_date": self.cutoff_date.strftime("%Y-%m-%d"),
                "dry_run": self.dry_run
            }
        )
        
        try:
            total_deleted = 0
            deleted_dates_by_region = {}
            
            for region in self.REGIONS:
                count, dates = self.cleanup_region(region)
                total_deleted += count
                if dates:
                    deleted_dates_by_region[region] = dates
            
            # Update index
            if deleted_dates_by_region:
                self.update_index(deleted_dates_by_region)
            
            logger.info(
                "=== DATA CLEANUP COMPLETED ===",
                extra={
                    "status": "success",
                    "total_deleted": total_deleted,
                    "deleted_dates": deleted_dates_by_region
                }
            )
            
            if self.dry_run:
                print(f"[DRY RUN] Would delete {total_deleted} files")
            else:
                print(f"✅ Deleted {total_deleted} old bulletin files")
            
            for region, dates in deleted_dates_by_region.items():
                print(f"   {region}: {', '.join(dates)}")
            
            return 0
            
        except Exception as e:
            logger.error(
                "=== DATA CLEANUP FAILED ===",
                extra={"error": str(e)}
            )
            print(f"❌ Cleanup failed: {e}", file=sys.stderr)
            return 1


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Cleanup old bulletin data (7-day retention)"
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Print what would be deleted without actually deleting'
    )
    
    args = parser.parse_args()
    
    try:
        cleanup = DataCleanup(dry_run=args.dry_run)
        exit_code = cleanup.run()
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
