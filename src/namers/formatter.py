"""Filename formatting utilities."""

import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class FilenameFormatter:
    """Format and sanitize filenames."""

    def __init__(
        self,
        case_style: str = "kebab",
        date_format: str = "yyyymmdd",
        date_position: str = "end",
        max_length: int = 100,
    ):
        """
        Initialize filename formatter.

        Args:
            case_style: Case style (kebab, snake, camel, pascal, lower)
            date_format: Date format string
            date_position: Position of date (end, start, none)
            max_length: Maximum filename length
        """
        self.case_style = case_style
        self.date_format = date_format
        self.date_position = date_position
        self.max_length = max_length

    def format_components(self, components: Dict[str, Optional[str]], date: Optional[str] = None) -> str:
        """
        Format filename components into a single filename.

        Args:
            components: Dictionary with filename components
            date: Date string (optional, extracted or current)

        Returns:
            Formatted filename without extension
        """
        # Extract non-null components in order
        parts = []

        # Order: company, brand, project, type/subject, description
        for key in ["company", "brand", "project", "subject", "type", "description"]:
            if key in components and components[key]:
                # Skip null values (string "null" from LLM)
                if str(components[key]).lower() == "null":
                    continue

                part = self._sanitize_component(components[key])
                if part and part != "null":  # Double check after sanitization
                    parts.append(part)

        # Remove consecutive duplicates (e.g., ["nike", "nike"] -> ["nike"])
        parts = self._remove_consecutive_duplicates(parts)

        # Join parts
        if not parts:
            return "unnamed-file"

        filename = self._join_parts(parts)

        # Add date
        if self.date_position != "none" and date:
            filename = self._add_date(filename, date)

        # Truncate if needed
        if len(filename) > self.max_length:
            filename = filename[: self.max_length]

        return filename

    def _sanitize_component(self, text: str) -> str:
        """
        Sanitize a filename component.

        Args:
            text: Component text

        Returns:
            Sanitized text
        """
        # Convert to lowercase
        text = text.lower()

        # Remove special characters, keep alphanumeric and spaces
        text = re.sub(r"[^a-z0-9\s-]", "", text)

        # Replace multiple spaces with single space
        text = re.sub(r"\s+", " ", text)

        # Trim whitespace
        text = text.strip()

        return text

    def _remove_consecutive_duplicates(self, parts: list) -> list:
        """
        Remove consecutive duplicate parts.

        Args:
            parts: List of filename parts

        Returns:
            List with consecutive duplicates removed
        """
        if not parts:
            return parts

        result = [parts[0]]
        for part in parts[1:]:
            if part != result[-1]:
                result.append(part)

        return result

    def _join_parts(self, parts: list) -> str:
        """
        Join parts according to case style.

        Args:
            parts: List of sanitized parts

        Returns:
            Joined filename
        """
        if self.case_style == "kebab":
            # Replace spaces with hyphens
            parts = [part.replace(" ", "-") for part in parts]
            return "-".join(parts)

        elif self.case_style == "snake":
            # Replace spaces with underscores
            parts = [part.replace(" ", "_") for part in parts]
            return "_".join(parts)

        elif self.case_style == "camel":
            # First part lowercase, rest title case, no separators
            if not parts:
                return ""
            result = parts[0].replace(" ", "")
            for part in parts[1:]:
                result += part.title().replace(" ", "")
            return result

        elif self.case_style == "pascal":
            # All parts title case, no separators
            return "".join(part.title().replace(" ", "") for part in parts)

        elif self.case_style == "lower":
            # All lowercase, spaces become hyphens
            parts = [part.replace(" ", "-") for part in parts]
            return "-".join(parts)

        else:
            # Default to kebab
            parts = [part.replace(" ", "-") for part in parts]
            return "-".join(parts)

    def _add_date(self, filename: str, date: str) -> str:
        """
        Add date to filename.

        Args:
            filename: Base filename
            date: Date string

        Returns:
            Filename with date
        """
        separator = "-" if self.case_style in ["kebab", "snake", "lower"] else ""

        if self.date_position == "start":
            return f"{date}{separator}{filename}" if separator else f"{date}{filename}"
        else:  # end
            return f"{filename}{separator}{date}" if separator else f"{filename}{date}"

    def extract_date_from_filename(self, filename: str) -> Optional[str]:
        """
        Extract date from existing filename.

        Args:
            filename: Original filename

        Returns:
            Date string if found, None otherwise
        """
        # Try to find date patterns
        patterns = [
            r"(\d{8})",  # yyyymmdd or ddmmyyyy
            r"(\d{4}-\d{2}-\d{2})",  # yyyy-mm-dd
            r"(\d{6})",  # yymmdd or ddmmyy
        ]

        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                date_str = match.group(1)
                # Validate it's a reasonable date
                if self._is_valid_date(date_str):
                    return self._normalize_date(date_str)

        return None

    def _is_valid_date(self, date_str: str) -> bool:
        """
        Check if string is a valid date.

        Args:
            date_str: Date string

        Returns:
            True if valid date
        """
        # Basic validation
        if len(date_str) == 8:
            # yyyymmdd
            try:
                year = int(date_str[:4])
                month = int(date_str[4:6])
                day = int(date_str[6:8])
                return 1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31
            except ValueError:
                return False
        return True

    def _normalize_date(self, date_str: str) -> str:
        """
        Normalize date to configured format.

        Args:
            date_str: Date string

        Returns:
            Normalized date string
        """
        # For now, assume yyyymmdd and return as-is
        # More sophisticated conversion can be added
        return date_str.replace("-", "")

    def get_current_date(self) -> str:
        """
        Get current date in configured format.

        Returns:
            Formatted date string
        """
        now = datetime.now()

        if self.date_format == "yyyymmdd":
            return now.strftime("%Y%m%d")
        elif self.date_format == "yyyy-mm-dd":
            return now.strftime("%Y-%m-%d")
        elif self.date_format == "yymmdd":
            return now.strftime("%y%m%d")
        elif self.date_format == "ddmmyyyy":
            return now.strftime("%d%m%Y")
        else:
            return now.strftime("%Y%m%d")

    def is_already_formatted(self, filename: str) -> bool:
        """
        Check if filename already follows the convention.

        Args:
            filename: Filename to check

        Returns:
            True if already formatted
        """
        # Get filename without extension
        name = Path(filename).stem

        # Check for kebab-case pattern
        if self.case_style == "kebab":
            # Should be all lowercase with hyphens
            if re.match(r"^[a-z0-9]+(-[a-z0-9]+)*(-\d{8})?$", name):
                return True

        # Check for snake_case pattern
        elif self.case_style == "snake":
            if re.match(r"^[a-z0-9]+(_[a-z0-9]+)*(_\d{8})?$", name):
                return True

        return False
