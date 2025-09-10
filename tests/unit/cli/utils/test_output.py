"""Unit tests for CLI output utilities."""

from src.cli.utils.output import (
    format_key_value_pairs,
    format_list,
    format_table,
    print_error,
    print_info,
    print_success,
    print_warning,
)


class TestFormatTable:
    """Test table formatting."""

    def test_format_table_basic(self):
        """Test basic table formatting."""
        headers = ["Name", "Age", "City"]
        rows = [
            ["Alice", 30, "New York"],
            ["Bob", 25, "Paris"],
            ["Charlie", 35, "Tokyo"],
        ]

        result = format_table(headers, rows)

        assert "Name" in result
        assert "Age" in result
        assert "City" in result
        assert "Alice" in result
        assert "Bob" in result
        assert "Charlie" in result
        assert "30" in result
        assert "25" in result
        assert "35" in result
        assert "New York" in result
        assert "Paris" in result
        assert "Tokyo" in result

    def test_format_table_empty_rows(self):
        """Test table formatting with no rows."""
        headers = ["Name", "Age", "City"]
        rows = []

        result = format_table(headers, rows)

        assert result == "No data"

    def test_format_table_varying_width(self):
        """Test table formatting with varying column widths."""
        headers = ["Short", "Very Long Header Name"]
        rows = [["A", "Short"], ["Very Long Cell Content", "B"]]

        result = format_table(headers, rows)

        # Check that columns are properly aligned
        lines = result.split("\n")
        assert len(lines) >= 4  # Headers, separator, and 2 data rows

        # Check header line and separator line have consistent structure
        separator_line = lines[1]

        # Check that separator uses dashes
        assert "-" in separator_line

    def test_format_table_uneven_rows(self):
        """Test table formatting with rows of uneven length."""
        headers = ["Col1", "Col2", "Col3"]
        rows = [
            ["A", "B"],  # Missing third column
            ["X", "Y", "Z", "Extra"],  # Extra column
        ]

        result = format_table(headers, rows)

        # Should handle gracefully without crashing
        assert "A" in result
        assert "B" in result
        assert "X" in result
        assert "Y" in result
        assert "Z" in result

    def test_format_table_numeric_data(self):
        """Test table formatting with numeric data."""
        headers = ["Item", "Price", "Quantity"]
        rows = [
            ["Apple", 1.50, 10],
            ["Banana", 0.75, 20],
            [123, 456.789, 0],  # All numeric
        ]

        result = format_table(headers, rows)

        assert "Apple" in result
        assert "1.5" in result or "1.50" in result
        assert "10" in result
        assert "456.789" in result

    def test_format_table_none_values(self):
        """Test table formatting with None values."""
        headers = ["Name", "Value"]
        rows = [["Test", None], [None, "Value"]]

        result = format_table(headers, rows)

        assert "None" in result
        assert "Test" in result
        assert "Value" in result

    def test_format_table_special_characters(self):
        """Test table formatting with special characters."""
        headers = ["Unicode", "Symbols"]
        rows = [["测试", "★☆♠♥"], ["Émojis", "🚀🎉"], ["Quotes", '"test"']]

        result = format_table(headers, rows)

        assert "测试" in result
        assert "★☆♠♥" in result
        assert "Émojis" in result
        assert '"test"' in result


class TestFormatList:
    """Test list formatting."""

    def test_format_list_basic(self):
        """Test basic list formatting."""
        items = ["apple", "banana", "cherry"]

        result = format_list(items)

        assert "- apple" in result
        assert "- banana" in result
        assert "- cherry" in result

    def test_format_list_empty(self):
        """Test formatting empty list."""
        items = []

        result = format_list(items)

        assert result == ""

    def test_format_list_single_item(self):
        """Test formatting list with single item."""
        items = ["single_item"]

        result = format_list(items)

        assert result == "  - single_item"

    def test_format_list_custom_indent(self):
        """Test list formatting with custom indentation."""
        items = ["item1", "item2"]

        result = format_list(items, indent="    ")

        assert "    - item1" in result
        assert "    - item2" in result

    def test_format_list_special_characters(self):
        """Test list formatting with special characters."""
        items = ["item with spaces", "item-with-dashes", "item_with_underscores"]

        result = format_list(items)

        assert "- item with spaces" in result
        assert "- item-with-dashes" in result
        assert "- item_with_underscores" in result

    def test_format_list_unicode(self):
        """Test list formatting with unicode characters."""
        items = ["测试", "Émojis 🚀", "Special™"]

        result = format_list(items)

        assert "- 测试" in result
        assert "- Émojis 🚀" in result
        assert "- Special™" in result


class TestFormatKeyValuePairs:
    """Test key-value pair formatting."""

    def test_format_key_value_pairs_basic(self):
        """Test basic key-value pair formatting."""
        pairs = [("Name", "Alice"), ("Age", "30"), ("City", "New York")]

        result = format_key_value_pairs(pairs)

        assert "Name: Alice" in result
        assert "Age: 30" in result
        assert "City: New York" in result

    def test_format_key_value_pairs_empty(self):
        """Test formatting empty pairs list."""
        pairs = []

        result = format_key_value_pairs(pairs)

        assert result == ""

    def test_format_key_value_pairs_single(self):
        """Test formatting single key-value pair."""
        pairs = [("Key", "Value")]

        result = format_key_value_pairs(pairs)

        assert result == "Key: Value"

    def test_format_key_value_pairs_with_indent(self):
        """Test key-value pair formatting with indentation."""
        pairs = [("Key1", "Value1"), ("Key2", "Value2")]

        result = format_key_value_pairs(pairs, indent="  ")

        assert "  Key1: Value1" in result
        assert "  Key2: Value2" in result

    def test_format_key_value_pairs_special_values(self):
        """Test key-value pair formatting with special values."""
        pairs = [
            ("String", "text"),
            ("Number", 42),
            ("Boolean", True),
            ("None", None),
            ("List", ["a", "b", "c"]),
        ]

        result = format_key_value_pairs(pairs)

        assert "String: text" in result
        assert "Number: 42" in result
        assert "Boolean: True" in result
        assert "None: None" in result
        assert "List: ['a', 'b', 'c']" in result

    def test_format_key_value_pairs_unicode(self):
        """Test key-value pair formatting with unicode."""
        pairs = [("测试", "值"), ("Emoji", "🚀"), ("Special", "Café™")]

        result = format_key_value_pairs(pairs)

        assert "测试: 值" in result
        assert "Emoji: 🚀" in result
        assert "Special: Café™" in result


class TestPrintFunctions:
    """Test print utility functions."""

    def test_print_success(self, capsys):
        """Test success message printing."""
        print_success("Operation completed successfully")

        captured = capsys.readouterr()
        assert "✅" in captured.out
        assert "Operation completed successfully" in captured.out

    def test_print_error(self, capsys):
        """Test error message printing."""
        print_error("An error occurred")

        captured = capsys.readouterr()
        assert "❌" in captured.out
        assert "An error occurred" in captured.out

    def test_print_warning(self, capsys):
        """Test warning message printing."""
        print_warning("This is a warning")

        captured = capsys.readouterr()
        assert "⚠️" in captured.out
        assert "This is a warning" in captured.out

    def test_print_info(self, capsys):
        """Test info message printing."""
        print_info("Here is some information")

        captured = capsys.readouterr()
        assert "ℹ️" in captured.out
        assert "Here is some information" in captured.out

    def test_print_functions_empty_message(self, capsys):
        """Test print functions with empty messages."""
        print_success("")
        print_error("")
        print_warning("")
        print_info("")

        captured = capsys.readouterr()
        # Should contain the emoji icons even with empty messages
        assert "✅" in captured.out
        assert "❌" in captured.out
        assert "⚠️" in captured.out
        assert "ℹ️" in captured.out

    def test_print_functions_multiline_message(self, capsys):
        """Test print functions with multiline messages."""
        message = "Line 1\nLine 2\nLine 3"

        print_success(message)

        captured = capsys.readouterr()
        assert "✅" in captured.out
        assert "Line 1" in captured.out
        assert "Line 2" in captured.out
        assert "Line 3" in captured.out

    def test_print_functions_unicode_message(self, capsys):
        """Test print functions with unicode messages."""
        print_success("成功")
        print_error("错误")
        print_warning("警告")
        print_info("信息")

        captured = capsys.readouterr()
        assert "成功" in captured.out
        assert "错误" in captured.out
        assert "警告" in captured.out
        assert "信息" in captured.out
