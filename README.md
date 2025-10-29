# File Renamer

Intelligent file renaming using local language models. Analyzes document contents and images to generate clean, descriptive filenames in kebab-case format.

## Features

- **Content-aware renaming**: Analyzes file contents, not just filenames
- **Vision model support**: Detects brands and objects in images
- **Automatic batching**: Prevents system crashes with safe batch processing
- **Full undo support**: Every rename is tracked and reversible
- **Local models**: Privacy-first using LM Studio
- **Multiple file types**: PDF, DOCX, PPTX, JPG, PNG, and more

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start LM Studio

Load these models:
- **Text model**: `qwen3-4b-instruct-2507-mlx` (for documents)
- **Vision model**: `qwen/qwen3-vl-4b` (for images)

### 3. Configure

Copy and edit the config:

```bash
cp config.example.yaml config.yaml
```

### 4. Test Run (Dry-run)

```bash
# Preview document renames
python3 rename.py --path ~/Downloads --types docx,pdf

# Preview image renames
python3 rename.py --path ~/Downloads --types jpg,png
```

### 5. Execute Renames

```bash
# Rename documents
python3 rename.py --path ~/Downloads --types docx,pdf --execute --yes

# Rename images (batch size 10 recommended for vision)
python3 rename.py --path ~/Downloads --types jpg,png --batch-size 10 --execute --yes
```

## Naming Convention

Files are renamed following this pattern:
```
company-brand-project-type-yyyymmdd.extension
```

### Examples

```
Before: IC x Vans - Consumer Immersion - Screener 20251028.docx
After:  vans-consumer-immersion-screener-20251028.docx

Before: Nike Basketball Report Q4 2024.pdf
After:  nike-basketball-report-20241231.pdf

Before: IMG_1234.jpg (photo of Adidas shoes)
After:  adidas-sneakers-product-photo-20251028.jpg
```

## Safety Features

✅ **Automatic logging**: Every rename is logged to `~/.file-renamer/`
✅ **Full undo support**: Revert any session with `python3 undo.py`
✅ **Dry-run by default**: Preview before applying
✅ **Batch processing**: Prevents crashes with large file sets

### Undo Renames

```bash
# Show recent rename sessions
python3 undo.py --show

# Revert the last session (dry-run)
python3 undo.py

# Actually revert
python3 undo.py --execute
```

## Command Options

```bash
python3 rename.py \
  --path ~/Downloads \           # Directory to process
  --types docx,pdf,jpg \          # File types
  --batch-size 15 \               # Files per batch (10 for images)
  --execute \                     # Actually rename (not dry-run)
  --yes \                         # Skip confirmation
  --verbose                       # Show detailed output
```

## Recommended Batch Sizes

| File Type | Batch Size | Reason |
|-----------|-----------|---------|
| Documents (DOCX, PDF, PPTX) | 15-20 | Fast text processing |
| Images (JPG, PNG) | 10 | Vision model is slower |
| Mixed | 15 | Safe for all types |

## File Types Supported

**Documents** (text model):
- PDF, DOCX, PPTX, XLSX, TXT, MD, SRT

**Images** (vision model):
- JPG, PNG, GIF, WEBP, HEIC, BMP

## Configuration

Edit `config.yaml` to customize:

- **Models**: Change text/vision models
- **Naming**: Adjust case style, date format, max length
- **Processing**: Skip already-formatted files, recursive mode
- **Prompts**: Customize AI instructions

## Project Structure

```
file-renamer/
├── rename.py           # Main CLI
├── undo.py             # Undo tool
├── config.yaml         # Configuration
├── USAGE.md            # Detailed usage guide
├── src/
│   ├── extractors/     # Content extraction
│   ├── models/         # LM Studio client
│   ├── namers/         # Filename formatting
│   └── utils/          # Config & backup
└── ~/.file-renamer/    # Rename logs
```

## Documentation

- **USAGE.md**: Complete usage guide with examples
- **config.yaml**: Configuration options

## Requirements

- Python 3.8+
- LM Studio with models loaded
- Dependencies: `click`, `requests`, `PyPDF2`, `python-docx`, `python-pptx`, `openpyxl`, `tabulate`, `tqdm`

## License

MIT
