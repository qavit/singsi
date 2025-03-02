"""Test script for document parsers."""

import argparse
import asyncio
import json
import os
import sys
import time
import warnings
from pathlib import Path
from typing import Any

# Filter out deprecation warnings from SWIG
warnings.filterwarnings('ignore', category=DeprecationWarning, module='sys')
warnings.filterwarnings('ignore', message='.*__module__.*')
warnings.filterwarnings('ignore', message='.*swigvarlink.*')
warnings.filterwarnings('ignore', message='.*SwigPy.*')

# Ensure modules can be imported from the project root
sys.path.insert(0, str(Path(__file__).parents[4]))

from app.services.document.parsers import (  # noqa: E402
    DocxParser,
    ImageParser,
    PDFParser,
)

# Conditionally import MarkitdownParser
try:
    from app.services.document.parsers import MarkitdownParser

    MARKITDOWN_AVAILABLE = True
except ImportError:
    print('Markitdown parser not available, will skip testing it.')
    MARKITDOWN_AVAILABLE = False

# ANSI color codes for pretty output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'


class TestResults:
    """Store test results for final report."""

    def __init__(self):
        self.successful = []
        self.failed = []
        self.skipped = []

    def add_success(self, parser_name: str):
        self.successful.append(parser_name)

    def add_failure(self, parser_name: str):
        self.failed.append(parser_name)

    def add_skipped(self, parser_name: str):
        self.skipped.append(parser_name)

    def print_summary(self):
        print(f'\n{BOLD}===== TEST SUMMARY ====={RESET}')
        print(
            f'{GREEN}✓ Successful:{RESET} '
            f'{", ".join(self.successful) if self.successful else "None"}'
        )
        print(
            f'{RED}✗ Failed:{RESET} {", ".join(self.failed) if self.failed else "None"}'
        )
        print(
            f'{YELLOW}⚠ Skipped:{RESET} '
            f'{", ".join(self.skipped) if self.skipped else "None"}'
        )

        total = len(self.successful) + len(self.failed)
        if total > 0:
            success_rate = len(self.successful) / total * 100
            print(
                f'\n{BOLD}Success rate:{RESET} '
                f'{success_rate:.1f}% ({len(self.successful)}/{total})'
            )


async def test_parser(
    parser_class, file_path: str, test_results: TestResults
) -> dict[str, Any]:
    """Test a specific parser with a file."""
    parser_name = parser_class.__name__
    print(f'\n{BLUE}{BOLD}[TESTING] {parser_name}{RESET} with {file_path}')
    start_time = time.time()

    # Read file content
    with open(file_path, 'rb') as f:
        content = f.read()

    print(f'File size: {len(content) / 1024:.1f} KB')

    # Create parser instance
    parser = parser_class()

    try:
        # Parse file
        print(f'{YELLOW}Parsing...{RESET}')
        result = await parser.parse(content, filename=os.path.basename(file_path))

        # Calculate parsing time
        elapsed = time.time() - start_time

        if result.success:
            print(f'{GREEN}✓ Parsing succeeded in {elapsed:.2f} seconds!{RESET}')
            test_results.add_success(parser_name)
        else:
            print(
                f'{RED}✗ Parsing completed with errors in {elapsed:.2f} seconds: '
                f'{result.error}{RESET}'
            )
            test_results.add_failure(parser_name)

        # Return results dict
        return result.to_dict()

    except Exception as e:
        elapsed = time.time() - start_time
        print(
            f'{RED}✗ Parser failed with exception in {elapsed:.2f} seconds: '
            f'{e!s}{RESET}'
        )
        test_results.add_failure(parser_name)
        return {'text': '', 'error': str(e), 'success': False}


def get_parser_class(parser_name: str):
    """Get parser class by name."""
    parsers = {
        'pdf': PDFParser,
        'docx': DocxParser,
        'image': ImageParser,
    }

    if MARKITDOWN_AVAILABLE:
        parsers['markitdown'] = MarkitdownParser

    return parsers.get(parser_name.lower())


def get_file_extension_for_parser(parser_name: str) -> list[str]:
    """Get file extensions for specified parser type."""
    extensions = {
        'pdf': ['.pdf'],
        'docx': ['.docx', '.doc'],
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.tiff', '.bmp'],
        'markitdown': [
            '.pdf',
            '.docx',
            '.doc',
            '.pptx',
            '.xlsx',
            '.jpg',
            '.png',
            '.txt',
            '.html',
        ],
    }

    return extensions.get(parser_name.lower(), [])


def find_test_files(directory: Path, extensions: list[str]) -> list[Path]:
    """Find files with the given extensions in the directory."""
    files = []
    for ext in extensions:
        files.extend(directory.glob(f'*{ext}'))
    return files


def setup_test_environment() -> tuple[Path, Path]:
    """Set up test environment and return paths to test files and results."""
    # Get the sample files directory path - 修正路径
    test_files_dir = Path(__file__).parent / 'sample_files'

    if not test_files_dir.exists():
        test_files_dir.mkdir(parents=True)
        print(f'{YELLOW}Created sample files directory: {test_files_dir}{RESET}')
        print(f'{BOLD}Please add sample files to this directory and run again.{RESET}')

    print(f'Looking for test files in: {test_files_dir}\n')

    # Create results output directory
    results_dir = Path(__file__).parent / 'test_results'
    results_dir.mkdir(exist_ok=True)
    print(f'Results will be saved in: {results_dir}\n')

    return test_files_dir, results_dir


async def process_specific_file(
    file_path: str,
    parser_type: str | None,
    test_results: TestResults,
    results_dir: Path,
    verbose: bool,
) -> bool:
    """Process a specific file with appropriate parser."""
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        print(f'{RED}File not found: {file_path_obj}{RESET}')
        return False

    # Choose parser based on file extension if not specified
    selected_parser = parser_type
    if not selected_parser:
        extension = file_path_obj.suffix.lower()
        extension_map = {
            '.pdf': 'pdf',
            '.docx': 'docx',
            '.doc': 'docx',
        }

        for ext, parser in extension_map.items():
            if extension == ext:
                selected_parser = parser
                break

        # Handle image files
        if not selected_parser and extension in [
            '.jpg',
            '.jpeg',
            '.png',
            '.gif',
            '.tiff',
            '.bmp',
        ]:
            selected_parser = 'image'

        # Default to markitdown if available
        if not selected_parser and MARKITDOWN_AVAILABLE:
            selected_parser = 'markitdown'

        if not selected_parser:
            print(f'{RED}Could not determine parser for file: {file_path_obj}{RESET}')
            return False

    parser_class = get_parser_class(selected_parser)
    if not parser_class:
        print(f'{RED}Parser not available: {selected_parser}{RESET}')
        return False

    result = await test_parser(parser_class, str(file_path_obj), test_results)
    save_result(result, results_dir / f'{selected_parser}_result.json', verbose=verbose)
    return True


async def test_all_parsers(
    parser_type: str | None,
    test_files_dir: Path,
    test_results: TestResults,
    results_dir: Path,
    verbose: bool,
) -> None:
    """Test all available parsers or a specific parser."""
    # Determine which parsers to test
    parsers_to_test = []
    if parser_type:
        parser_class = get_parser_class(parser_type)
        if parser_class:
            parsers_to_test.append((parser_type, parser_class))
        else:
            print(f'{RED}Parser not available: {parser_type}{RESET}')
            return
    else:
        # Test all parsers
        parsers_to_test = [
            ('pdf', PDFParser),
            ('docx', DocxParser),
            ('image', ImageParser),
        ]
        if MARKITDOWN_AVAILABLE:
            parsers_to_test.append(('markitdown', MarkitdownParser))

    # Test each parser with appropriate files
    for name, parser_class in parsers_to_test:
        extensions = get_file_extension_for_parser(name)
        test_files = find_test_files(test_files_dir, extensions)

        if test_files:
            # Use the first file found
            result = await test_parser(parser_class, str(test_files[0]), test_results)
            save_result(result, results_dir / f'{name}_result.json', verbose=verbose)
        else:
            print(
                f'{YELLOW}⚠ No suitable files found for {name} parser - '
                f'skipping test{RESET}'
            )
            test_results.add_skipped(parser_class.__name__)


async def main(
    parser_type: str | None = None,
    specific_file: str | None = None,
    verbose: bool = False,
):
    """Run parser tests on sample files."""
    print(f'\n{BOLD}📄 DOCUMENT PARSER TEST SUITE{RESET}')
    print(f'{BLUE}=====================================\n{RESET}')

    test_results = TestResults()
    test_files_dir, results_dir = setup_test_environment()

    # Process based on input parameters
    if specific_file:
        await process_specific_file(
            specific_file, parser_type, test_results, results_dir, verbose
        )
    else:
        await test_all_parsers(
            parser_type, test_files_dir, test_results, results_dir, verbose
        )

    # Print test summary
    test_results.print_summary()


def save_result(result: dict, output_file: Path, verbose: bool = False) -> None:
    """Save parsing result to a JSON file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f'{BLUE}Results saved to {output_file}{RESET}')

    # Show result summary
    if result['success']:
        print(f'{GREEN}{BOLD}Content extracted successfully{RESET}')
    else:
        print(f'{RED}{BOLD}Content extraction had errors{RESET}')
        print(f'Error: {result["error"]}')

    # Text preview - control verbosity
    preview_length = 500 if verbose else 300
    text_preview = (
        result['text'][:preview_length] + '...'
        if len(result['text']) > preview_length
        else result['text']
    )
    print(f'\n{BOLD}Text preview:{RESET}\n{text_preview}\n')

    # Metadata
    print(f'{BOLD}Metadata:{RESET}')
    for key, value in result['metadata'].items():
        if isinstance(value, str) and len(value) > 50 and not verbose:  # noqa: PLR2004
            value = value[:50] + '...'  # noqa: PLW2901
        print(f'  {key}: {value}')

    # Pages
    print(f'\n{BOLD}Pages:{RESET} {result["pages"]}')

    # Structure info preview - show more details in verbose mode
    if verbose and result['structure']:
        print(f'{BOLD}Structure details:{RESET}')
        print(json.dumps(result['structure'], indent=2, ensure_ascii=False))
    else:
        print(f'{BOLD}Structure info:{RESET} {len(result["structure"])} elements')

    print(f'{BLUE}{"=" * 60}{RESET}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test document parsers')

    parser.add_argument(
        '--parser',
        '-p',
        choices=['pdf', 'docx', 'image', 'markitdown'],
        help='Specify which parser to test (pdf, docx, image, markitdown)',
    )

    parser.add_argument('--file', '-f', help='Specify a file path to test')

    parser.add_argument(
        '--verbose', '-v', action='store_true', help='Show more detailed output'
    )

    # TODO: Add more specialized test options:
    # - Batch testing of multiple files
    # - Performance benchmarking
    # - Comparison of results between different parsers
    # - Export test results to CSV or other formats

    args = parser.parse_args()

    asyncio.run(
        main(parser_type=args.parser, specific_file=args.file, verbose=args.verbose)
    )
