---
name: claude-music-library
description: >
  Browse, search, and manage generated music in ~/Music/claude-music-output/.
  List recent generations, search by date, check disk usage, play files, clean up old output.
  Use when user says "library", "list songs", "browse music", "recent generations",
  "disk usage", "clean up", or wants to manage their music output.
allowed-tools:
  - Bash
  - Read
---

# claude-music-library — Output Management

## List Recent Generations

```bash
# Last 10 files, sorted by date
ls -lht ~/Music/claude-music-output/ | head -20

# Only FLAC files
ls -lht ~/Music/claude-music-output/*.flac 2>/dev/null | head -10

# With file sizes
du -sh ~/Music/claude-music-output/*  2>/dev/null | sort -rh | head -20
```

## Search by Date

```bash
# Today's generations
find ~/Music/claude-music-output/ -name "*.flac" -newermt "today" -ls

# This week
find ~/Music/claude-music-output/ -name "*.flac" -mtime -7 -ls
```

## Disk Usage

```bash
du -sh ~/Music/claude-music-output/
```

## Play a File

```bash
ffplay -nodisp -autoexit "/path/to/file.flac"
```

## File Info

```bash
ffprobe -v quiet -print_format json -show_format "/path/to/file.flac" | jq '{duration: .format.duration, size: .format.size, format: .format.format_name}'
```

## Cleanup

Always confirm before deleting:
```bash
# Show what would be deleted (files older than 30 days)
find ~/Music/claude-music-output/ -mtime +30 -ls

# Delete after user confirmation
find ~/Music/claude-music-output/ -mtime +30 -delete
```
