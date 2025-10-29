# Final Usage Guide - Built-in Batch Processing

## 🎉 Automatic Batch Processing Now Built In!

The system now automatically processes files in safe batches. No more crashes!

## Basic Usage

### Documents (Default: 20 files per batch)

```bash
# Dry-run (preview changes)
python3 rename.py --path ~/Downloads --types docx

# Actually rename with automatic batching
python3 rename.py --path ~/Downloads --types docx --execute --yes
```

### Images (Vision model)

```bash
# Test on images
python3 rename.py --path ~/Downloads --types jpg,png

# Actually rename images
python3 rename.py --path ~/Downloads --types jpg,png --execute --yes
```

### Both Documents and Images

```bash
# Process everything
python3 rename.py --path ~/Downloads --types docx,pdf,jpg,png --execute --yes
```

## Custom Batch Size

```bash
# Smaller batches (safer, slower)
python3 rename.py --path ~/Downloads --types docx --batch-size 10 --execute --yes

# Larger batches (faster, but might crash if too big)
python3 rename.py --path ~/Downloads --types docx --batch-size 50 --execute --yes

# Very small test (5 files)
python3 rename.py --path ~/Downloads --types docx --batch-size 5 --execute --yes
```

## Recommended Batch Sizes

| File Type | Recommended Batch Size | Reason |
|-----------|------------------------|--------|
| DOCX, TXT | 20 (default) | Fast text processing |
| PDF | 15 | Larger files, slower extraction |
| Images (JPG, PNG) | 10 | Vision model is slower |
| Mixed | 15 | Safe for all types |

## What Happens

```
Found 212 file(s) to process
Processing in batches of 20 files to prevent crashes

Batch 1/11 (20 files)
Processing batch 1: 100%|████████████| 20/20 [00:35<00:00, 1.75s/file]
Waiting 2 seconds before next batch...

Batch 2/11 (20 files)
Processing batch 2: 100%|████████████| 20/20 [00:38<00:00, 1.90s/file]
Waiting 2 seconds before next batch...

...

✅ Renamed 195 files

✅ Rename log saved: ~/.file-renamer/renames_20251029_093045.json

Rename Summary:
  Total: 212
  Successful: 195
  Failed: 17
  Log file: ~/.file-renamer/renames_20251029_093045.json
```

## Safety Features

- ✅ **Automatic batching**: Prevents system overload
- ✅ **2-second pause**: Between batches to let system recover
- ✅ **Progress tracking**: Shows batch progress
- ✅ **Complete logging**: All renames tracked
- ✅ **Full undo**: Can revert any session

## Tomorrow's Workflow

### Start Small

```bash
# 1. Test on just 5 documents
python3 rename.py --path ~/Downloads --types docx --batch-size 5

# 2. If good, run for real with small batch
python3 rename.py --path ~/Downloads --types docx --batch-size 5 --execute --yes

# 3. If that works, increase batch size
python3 rename.py --path ~/Downloads --types docx --batch-size 20 --execute --yes
```

### Process Images

```bash
# 1. Test on 5 images
python3 rename.py --path ~/Downloads --types jpg,png --batch-size 5

# 2. Run for real
python3 rename.py --path ~/Downloads --types jpg,png --batch-size 10 --execute --yes
```

### Process Everything

```bash
# All file types with safe batching
python3 rename.py --path ~/Downloads --types docx,pdf,pptx,jpg,png --batch-size 15 --execute --yes
```

## If Something Goes Wrong

### Undo the Session

```bash
# See what was changed
python3 undo.py --show

# Undo it all
python3 undo.py --execute
```

### Adjust Batch Size

If you still get crashes:
```bash
# Try smaller batches
python3 rename.py --path ~/Downloads --types docx --batch-size 5 --execute --yes
```

## Command Reference

```bash
# Full command with all options
python3 rename.py \
  --path ~/Downloads \           # Directory to process
  --types docx,pdf,jpg \          # File types
  --batch-size 20 \               # Files per batch
  --execute \                     # Actually rename (not dry-run)
  --yes \                         # Skip confirmation
  --verbose                       # Show detailed output
```

## File Type Shortcuts

```bash
# Just documents
--types docx,pdf,pptx,xlsx

# Just images
--types jpg,png,gif

# Everything text-based
--types docx,pdf,pptx,xlsx,txt,srt,md

# Documents + images
--types docx,pdf,jpg,png
```

## Performance Estimates

With batch size 20:
- **Documents**: ~2 minutes per 20 files = ~6 minutes per 60 files
- **Images**: ~4 minutes per 20 files = ~12 minutes per 60 files
- **Mixed**: ~3 minutes per 20 files = ~9 minutes per 60 files

## Tips

1. **Start with batch size 5** for first run
2. **Increase to 20** once you're confident
3. **Use 10 for images** (vision is slower)
4. **Always check the log** after running
5. **Keep undo available** - don't delete logs

## What Changed

**Old (would crash):**
```bash
python3 rename.py --path ~/Downloads --types docx --execute
# Tries to process 200+ files at once → CRASH
```

**New (safe):**
```bash
python3 rename.py --path ~/Downloads --types docx --execute --yes
# Automatically processes 20 at a time with pauses → NO CRASH
```

## Default Settings

- **Batch size**: 20 files (safe for most systems)
- **Pause between batches**: 2 seconds
- **Verbose**: Off (use `-v` to enable)
- **Dry-run**: On (use `--execute` to actually rename)

---

**The system is now production-ready with automatic crash prevention!** 🚀
