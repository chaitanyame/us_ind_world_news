#!/usr/bin/env python3
"""
News Fetching CLI Script

Fetches news bulletins from Perplexity API and saves them as JSON files.
Supports multiple regions (usa, india, world) and periods (morning, evening).

Usage:
    python fetch_news.py --region usa --period morning
    python fetch_news.py --region india --period evening --date 2025-12-15
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.fetchers.perplexity_client import PerplexityClient
from src.fetchers.json_formatter import JSONFormatter
from src.models.bulletin import BulletinWrapper
from src.utils.logger import logger
from src.utils.retry_logic import MaxRetriesExceeded


class NewsFetcher:
    """Main CLI application for fetching and saving news bulletins."""
    
    VALID_REGIONS = ['usa', 'india', 'world']
    VALID_PERIODS = ['morning', 'evening']
    
    def __init__(self, region: str, period: str, date: Optional[str] = None, workflow_run_id: Optional[str] = None):
        """
        Initialize news fetcher.
        
        Args:
            region: Region code (usa, india, world)
            period: Time period (morning, evening)
            date: Optional date in YYYY-MM-DD format (defaults to today)
            workflow_run_id: Optional GitHub Actions workflow run ID
        """
        self.region = region.lower()
        self.period = period.lower()
        self.date = date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        self.workflow_run_id = workflow_run_id
        
        # Validate inputs
        if self.region not in self.VALID_REGIONS:
            raise ValueError(f"Invalid region: {region}. Must be one of {self.VALID_REGIONS}")
        
        if self.period not in self.VALID_PERIODS:
            raise ValueError(f"Invalid period: {period}. Must be one of {self.VALID_PERIODS}")
        
        # Initialize components
        self.client = PerplexityClient()
        self.formatter = JSONFormatter()
        
        # Set up paths
        self.repo_root = Path(__file__).parent.parent.parent
        self.data_dir = self.repo_root / 'data' / self.region
        self.contracts_dir = self.repo_root / 'specs' / '1-global-news-brief' / 'contracts'
        
        logger.info(
            "NewsFetcher initialized",
            extra={
                "region": self.region,
                "period": self.period,
                "date": self.date,
                "workflow_run_id": self.workflow_run_id
            }
        )
    
    def load_prompt_template(self) -> tuple[str, str]:
        """
        Load system and user prompts from contract files.
        
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        template_file = self.contracts_dir / f"perplexity-prompt-{self.region}-{self.period}.md"
        
        if not template_file.exists():
            logger.warning(
                f"Prompt template not found: {template_file}",
                extra={"fallback": "using default prompts"}
            )
            # Fall back to client defaults
            return (
                self.client.get_default_system_prompt(self.region),
                self.client.get_default_user_prompt(self.region, self.period, self.date)
            )
        
        logger.info(f"Loading prompt template from {template_file}")
        
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse markdown to extract prompts
        system_prompt = self._extract_prompt_section(content, "System Prompt")
        user_prompt = self._extract_prompt_section(content, "User Prompt Template")
        
        # Inject date into user prompt
        user_prompt = user_prompt.replace('{DATE}', self.date)
        
        return system_prompt, user_prompt
    
    def _extract_prompt_section(self, content: str, section_name: str) -> str:
        """Extract a prompt section from markdown content."""
        lines = content.split('\n')
        in_section = False
        in_code_block = False
        prompt_lines = []
        
        for line in lines:
            if section_name in line:
                in_section = True
                continue
            
            if in_section:
                if line.strip().startswith('```'):
                    if in_code_block:
                        # End of code block
                        break
                    else:
                        # Start of code block
                        in_code_block = True
                        continue
                
                if in_code_block:
                    prompt_lines.append(line)
        
        return '\n'.join(prompt_lines).strip()
    
    def fetch_bulletin(self) -> BulletinWrapper:
        """
        Fetch news bulletin from Perplexity API.
        
        Returns:
            BulletinWrapper containing validated bulletin data
        """
        logger.info("Fetching bulletin from Perplexity API")
        
        try:
            # Load prompts
            system_prompt, user_prompt = self.load_prompt_template()
            
            # Fetch from API
            response = self.client.fetch_news(
                region=self.region,
                period=self.period,
                date=self.date,
                system_prompt=system_prompt,
                user_prompt=user_prompt
            )
            
            logger.info(
                "API response received",
                extra={
                    "content_length": len(response.get('content', '')),
                    "citations_count": len(response.get('citations', []))
                }
            )
            
            # Format to Bulletin
            bulletin = self.formatter.format(
                response_data=response,
                region=self.region,
                period=self.period,
                date=self.date,
                workflow_run_id=self.workflow_run_id
            )
            
            logger.info(
                "Bulletin formatted successfully",
                extra={
                    "article_count": len(bulletin.bulletin.articles),
                    "bulletin_id": bulletin.bulletin.id
                }
            )
            
            return bulletin
            
        except MaxRetriesExceeded as e:
            logger.error(
                "Failed to fetch bulletin after max retries",
                extra={"error": str(e)}
            )
            raise
        
        except Exception as e:
            logger.error(
                "Unexpected error fetching bulletin",
                extra={"error": str(e), "type": type(e).__name__}
            )
            raise
    
    def save_bulletin(self, bulletin: BulletinWrapper) -> Path:
        """
        Save bulletin to JSON file.
        
        Args:
            bulletin: BulletinWrapper to save
            
        Returns:
            Path to saved file
        """
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Construct filename
        filename = f"{self.date}-{self.period}.json"
        filepath = self.data_dir / filename
        
        logger.info(f"Saving bulletin to {filepath}")
        
        try:
            # Convert to JSON with pretty printing
            bulletin_json = bulletin.model_dump_json(indent=2, exclude_none=True)
            
            # Write atomically (write to temp file, then rename)
            temp_filepath = filepath.with_suffix('.json.tmp')
            
            with open(temp_filepath, 'w', encoding='utf-8') as f:
                f.write(bulletin_json)
            
            # Atomic rename
            temp_filepath.replace(filepath)
            
            logger.info(
                "Bulletin saved successfully",
                extra={
                    "filepath": str(filepath),
                    "size_bytes": filepath.stat().st_size
                }
            )
            
            return filepath
            
        except Exception as e:
            logger.error(
                "Failed to save bulletin",
                extra={"filepath": str(filepath), "error": str(e)}
            )
            # Clean up temp file if it exists
            if temp_filepath.exists():
                temp_filepath.unlink()
            raise
    
    def update_index(self, filepath: Path):
        """
        Update data/index.json with the new bulletin entry.
        
        Args:
            filepath: Path to the saved bulletin file
        """
        index_file = self.repo_root / 'data' / 'index.json'
        
        try:
            # Load existing index
            if index_file.exists():
                with open(index_file, 'r', encoding='utf-8') as f:
                    index = json.load(f)
            else:
                index = {}
            
            # Ensure region exists
            if self.region not in index:
                index[self.region] = {}
            
            # Ensure date exists
            if self.date not in index[self.region]:
                index[self.region][self.date] = {}
            
            # Add entry
            index[self.region][self.date][self.period] = {
                "filepath": f"{self.region}/{filepath.name}",
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Write atomically
            temp_index = index_file.with_suffix('.json.tmp')
            with open(temp_index, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2)
            
            temp_index.replace(index_file)
            
            logger.info("Index updated successfully")
            
        except Exception as e:
            logger.error(f"Failed to update index: {e}")
            # Don't fail the entire operation if index update fails
    
    def run(self) -> int:
        """
        Execute the full news fetching workflow.
        
        Returns:
            Exit code (0 = success, 1 = failure)
        """
        start_time = datetime.now(timezone.utc)
        
        logger.info(
            "=== NEWS FETCH STARTED ===",
            extra={
                "region": self.region,
                "period": self.period,
                "date": self.date,
                "start_time": start_time.isoformat()
            }
        )
        
        try:
            # Fetch bulletin
            bulletin = self.fetch_bulletin()
            
            # Save to file
            filepath = self.save_bulletin(bulletin)
            
            # Update index
            self.update_index(filepath)
            
            # Calculate duration
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            logger.info(
                "=== NEWS FETCH COMPLETED ===",
                extra={
                    "status": "success",
                    "filepath": str(filepath),
                    "article_count": len(bulletin.bulletin.articles),
                    "duration_seconds": duration,
                    "end_time": end_time.isoformat()
                }
            )
            
            print(f"✅ Bulletin saved: {filepath}")
            print(f"   Articles: {len(bulletin.bulletin.articles)}")
            print(f"   Duration: {duration:.2f}s")
            
            return 0
            
        except Exception as e:
            end_time = datetime.now(timezone.utc)
            duration = (end_time - start_time).total_seconds()
            
            logger.error(
                "=== NEWS FETCH FAILED ===",
                extra={
                    "status": "failure",
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "duration_seconds": duration,
                    "end_time": end_time.isoformat()
                }
            )
            
            print(f"❌ Failed to fetch bulletin: {e}", file=sys.stderr)
            
            return 1


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Fetch news bulletins from Perplexity API and save to JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --region usa --period morning
  %(prog)s --region india --period evening --date 2025-12-15
  %(prog)s --region world --period morning --workflow-run-id 12345678
        """
    )
    
    parser.add_argument(
        '--region',
        required=True,
        choices=['usa', 'india', 'world'],
        help='Region for news bulletin'
    )
    
    parser.add_argument(
        '--period',
        required=True,
        choices=['morning', 'evening'],
        help='Time period for bulletin'
    )
    
    parser.add_argument(
        '--date',
        help='Date in YYYY-MM-DD format (defaults to today)'
    )
    
    parser.add_argument(
        '--workflow-run-id',
        help='GitHub Actions workflow run ID (for tracking)'
    )
    
    args = parser.parse_args()
    
    try:
        fetcher = NewsFetcher(
            region=args.region,
            period=args.period,
            date=args.date,
            workflow_run_id=args.workflow_run_id
        )
        
        exit_code = fetcher.run()
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"❌ Fatal error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
