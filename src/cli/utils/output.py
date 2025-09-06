"""Output formatting utilities for CLI commands."""

from typing import List, Any


def format_table(headers: List[str], rows: List[List[Any]]) -> str:
    """Format data as a table.
    
    Args:
        headers: Column headers
        rows: Data rows
        
    Returns:
        Formatted table string
    """
    if not rows:
        return "No data"
    
    # Calculate column widths
    widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(str(cell)))
    
    # Create format string
    format_str = "  ".join(f"{{:<{w}}}" for w in widths)
    
    # Build table
    lines = [format_str.format(*[str(h) for h in headers])]
    lines.append("  ".join("-" * w for w in widths))
    
    for row in rows:
        formatted_row = [str(cell) for cell in row]
        # Pad row if needed
        while len(formatted_row) < len(widths):
            formatted_row.append("")
        lines.append(format_str.format(*formatted_row[:len(widths)]))
    
    return "\n".join(lines)


def print_success(message: str) -> None:
    """Print success message with icon."""
    print(f"✅ {message}")


def print_error(message: str) -> None:
    """Print error message with icon."""
    print(f"❌ {message}")


def print_warning(message: str) -> None:
    """Print warning message with icon."""
    print(f"⚠️ {message}")


def print_info(message: str) -> None:
    """Print info message with icon."""
    print(f"ℹ️ {message}")


def format_list(items: List[str], indent: str = "  ") -> str:
    """Format a list of items.
    
    Args:
        items: List items
        indent: Indentation string
        
    Returns:
        Formatted list string
    """
    return "\n".join(f"{indent}- {item}" for item in items)


def format_key_value_pairs(pairs: List[tuple], indent: str = "") -> str:
    """Format key-value pairs.
    
    Args:
        pairs: List of (key, value) tuples
        indent: Indentation string
        
    Returns:
        Formatted key-value string
    """
    return "\n".join(f"{indent}{key}: {value}" for key, value in pairs)