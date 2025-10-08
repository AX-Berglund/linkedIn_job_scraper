#!/usr/bin/env python3
"""
Interactive database viewer for job listings.
Quick way to view and explore your scraped jobs.
"""

import sys
import argparse
from datetime import datetime, timedelta
from database import JobDatabase


def print_job(job: dict, index: int = None):
    """Print a single job in a nice format."""
    prefix = f"[{index}] " if index is not None else ""
    expired_tag = " [EXPIRED]" if job.get('expired') else ""
    applied_tag = f" [APPLIED: {job['applied_on']}]" if job.get('applied_on') else ""
    
    print(f"\n{prefix}{'='*70}")
    print(f"Title:    {job['title']}{expired_tag}{applied_tag}")
    print(f"Company:  {job['company']}")
    print(f"Location: {job['location']}")
    print(f"Posted:   {job.get('date_posted', 'N/A')}")
    print(f"Last Seen: {job['last_seen']}")
    print(f"Status:   {job['status']}")
    print(f"Link:     {job['link']}")
    print(f"Job ID:   {job['job_id']}")


def cmd_stats(db: JobDatabase, args):
    """Show database statistics."""
    stats = db.get_job_stats()
    
    print("\n" + "="*60)
    print("📊 Job Database Statistics")
    print("="*60)
    print(f"Total jobs:       {stats['total']}")
    print(f"Active jobs:      {stats['active']}")
    print(f"Expired jobs:     {stats['expired']}")
    print(f"Applied to:       {stats['applied']}")
    print(f"Not yet applied:  {stats['not_applied']}")
    print("="*60 + "\n")


def cmd_list(db: JobDatabase, args):
    """List jobs with filters."""
    jobs = db.export_jobs_to_dict(active_only=args.active_only)
    
    if args.limit:
        jobs = jobs[:args.limit]
    
    if not jobs:
        print("\n📭 No jobs found matching criteria")
        return
    
    print(f"\n📋 Found {len(jobs)} job(s):\n")
    
    for i, job in enumerate(jobs, 1):
        if args.compact:
            expired = " ❌" if job.get('expired') else ""
            applied = " ✅" if job.get('applied_on') else ""
            print(f"{i:3}. {job['title'][:40]:40} | {job['company'][:25]:25}{expired}{applied}")
        else:
            print_job(job, i)


def cmd_recent(db: JobDatabase, args):
    """Show jobs added in the last N days."""
    cutoff_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")
    
    jobs = db.export_jobs_to_dict(active_only=True)
    recent_jobs = [j for j in jobs if j['last_seen'] >= cutoff_date]
    
    if not recent_jobs:
        print(f"\n📭 No jobs found in the last {args.days} day(s)")
        return
    
    print(f"\n📋 Jobs from the last {args.days} day(s): {len(recent_jobs)} found\n")
    
    for i, job in enumerate(recent_jobs, 1):
        print_job(job, i)


def cmd_search(db: JobDatabase, args):
    """Search jobs by keyword."""
    keyword = args.keyword.lower()
    jobs = db.export_jobs_to_dict(active_only=args.active_only)
    
    matching_jobs = [
        j for j in jobs
        if keyword in j['title'].lower() 
        or keyword in j['company'].lower()
        or keyword in j['location'].lower()
    ]
    
    if not matching_jobs:
        print(f"\n📭 No jobs found matching '{args.keyword}'")
        return
    
    print(f"\n🔍 Found {len(matching_jobs)} job(s) matching '{args.keyword}':\n")
    
    for i, job in enumerate(matching_jobs, 1):
        print_job(job, i)


def cmd_show(db: JobDatabase, args):
    """Show details for a specific job ID."""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs WHERE job_id = ?", (args.job_id,))
        row = cursor.fetchone()
        
        if not row:
            print(f"\n❌ Job ID '{args.job_id}' not found in database")
            return
        
        job = dict(row)
        print_job(job)
        print()


def cmd_export(db: JobDatabase, args):
    """Export jobs to JSON file."""
    import json
    
    jobs = db.export_jobs_to_dict(active_only=args.active_only)
    
    with open(args.output, 'w') as f:
        json.dump(jobs, f, indent=2)
    
    print(f"\n✅ Exported {len(jobs)} job(s) to {args.output}")


def main():
    """Main command-line interface."""
    parser = argparse.ArgumentParser(
        description="View and explore your LinkedIn job database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s stats                    # Show database statistics
  %(prog)s list --limit 10          # List first 10 active jobs
  %(prog)s list --compact           # Compact listing format
  %(prog)s recent --days 7          # Jobs from last 7 days
  %(prog)s search "python"          # Search for Python jobs
  %(prog)s show 1234567890          # Show specific job by ID
  %(prog)s export jobs.json         # Export all active jobs to JSON
        """
    )
    
    parser.add_argument(
        '--db',
        default='jobs.db',
        help='Path to database file (default: jobs.db)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Stats command
    subparsers.add_parser('stats', help='Show database statistics')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List all jobs')
    list_parser.add_argument('--limit', type=int, help='Limit number of results')
    list_parser.add_argument('--compact', action='store_true', help='Compact output')
    list_parser.add_argument('--active-only', action='store_true', default=True,
                           help='Show only active jobs (default: True)')
    list_parser.add_argument('--all', dest='active_only', action='store_false',
                           help='Show all jobs including expired')
    
    # Recent command
    recent_parser = subparsers.add_parser('recent', help='Show recently added jobs')
    recent_parser.add_argument('--days', type=int, default=7,
                             help='Number of days to look back (default: 7)')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search jobs by keyword')
    search_parser.add_argument('keyword', help='Keyword to search for')
    search_parser.add_argument('--active-only', action='store_true', default=True,
                              help='Search only active jobs (default: True)')
    search_parser.add_argument('--all', dest='active_only', action='store_false',
                              help='Search all jobs including expired')
    
    # Show command
    show_parser = subparsers.add_parser('show', help='Show specific job details')
    show_parser.add_argument('job_id', help='Job ID to display')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export jobs to JSON')
    export_parser.add_argument('output', help='Output file path')
    export_parser.add_argument('--active-only', action='store_true', default=True,
                              help='Export only active jobs (default: True)')
    export_parser.add_argument('--all', dest='active_only', action='store_false',
                              help='Export all jobs including expired')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize database
    try:
        db = JobDatabase(args.db)
    except Exception as e:
        print(f"❌ Error accessing database: {e}")
        return 1
    
    # Execute command
    commands = {
        'stats': cmd_stats,
        'list': cmd_list,
        'recent': cmd_recent,
        'search': cmd_search,
        'show': cmd_show,
        'export': cmd_export,
    }
    
    try:
        commands[args.command](db, args)
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

