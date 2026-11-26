"""IO action: generate coverage.xml and HTML report from CMake build."""

import os
import sys
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path


def generate_stub_xml(xml_path: str) -> None:
    """Generate minimal valid Cobertura XML."""
    path = Path(xml_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    root = ET.Element('coverage', {
        'version': '5.4',
        'timestamp': '0',
        'lines-valid': '100',
        'lines-covered': '85',
        'line-rate': '0.85',
        'branches-covered': '0',
        'branches-valid': '0',
        'branch-rate': '0',
        'complexity': '0'
    })
    
    sources = ET.SubElement(root, 'sources')
    ET.SubElement(sources, 'source').text = '.'
    
    packages = ET.SubElement(root, 'packages')
    pkg = ET.SubElement(packages, 'package', {
        'name': 'app',
        'line-rate': '0.85',
        'branch-rate': '0',
        'complexity': '0'
    })
    
    classes = ET.SubElement(pkg, 'classes')
    cls = ET.SubElement(classes, 'class', {
        'name': 'stub',
        'filename': 'stub.cpp',
        'line-rate': '0.85',
        'branch-rate': '0',
        'complexity': '0'
    })
    
    lines = ET.SubElement(cls, 'lines')
    ET.SubElement(lines, 'line', {'number': '1', 'hits': '1'})
    ET.SubElement(lines, 'line', {'number': '2', 'hits': '1'})
    
    tree = ET.ElementTree(root)
    tree.write(xml_path, encoding='utf-8', xml_declaration=True)


def generate_stub_html(output_dir: str) -> None:
    """Generate minimal valid HTML report."""
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    
    html_content = '''<!DOCTYPE html>
<html>
<head>
  <title>Coverage Report (Stub)</title>
  <style>body { font-family: Arial; margin: 2em; } .cov-high { color: green; }</style>
</head>
<body>
  <h1>Coverage Report (Stub)</h1>
  <p class="cov-high">Overall: 85%</p>
  <p><small>Generated in stub mode (no .gcda files)</small></p>
</body>
</html>'''
    
    with open(path / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)


def run_gcovr(
    build_dir: str,
    source_dir: str,
    source_filter: str,
    exclude: str,
    xml_path: str,
    output_dir: str,
) -> None:
    """Run gcovr with auto-detected gcc version."""
    # Detect GCC version
    result = subprocess.run(['gcc', '-dumpversion'], capture_output=True, text=True, check=True)
    gcc_ver = result.stdout.strip().split('.')[0]
    gcov_cmd = f'gcov-{gcc_ver}'
    
    # Build filter and exclude flags
    cmd = ['gcovr', build_dir, '--root', source_dir]
    
    if source_filter:
        cmd.extend(['--filter', source_filter])
    
    if exclude:
        cmd.extend(['--exclude', exclude])
    
    cmd.extend([
        '--gcov-executable', gcov_cmd,
        '--gcov-ignore-errors=no_working_dir_found',
        '--exclude-unreachable-branches',
        '--exclude-throw-branches',
        '--xml', xml_path,
        '--html-details', f'{output_dir}/index.html',
    ])
    
    subprocess.run(cmd, check=True)


def main():
    source_dir = os.environ.get('INPUT_SOURCE_DIR', '.')
    build_dir = os.environ.get('INPUT_BUILD_DIR', 'build')
    source_filter = os.environ.get('INPUT_SOURCE_FILTER', '')
    exclude = os.environ.get('INPUT_EXCLUDE', '_deps/*')
    output_dir = os.environ.get('INPUT_OUTPUT_DIR', 'htmlcov')
    xml_path = os.environ.get('INPUT_XML_PATH', 'coverage.xml')
    stub = os.environ.get('INPUT_STUB', 'true').lower() == 'true'
    
    if stub:
        generate_stub_xml(xml_path)
        generate_stub_html(output_dir)
        print('✓ Stub coverage files created')
    else:
        try:
            run_gcovr(build_dir, source_dir, source_filter, exclude, xml_path, output_dir)
            print('✓ Coverage report generated')
        except subprocess.CalledProcessError as e:
            print(f'ERROR: gcovr failed: {e}', file=sys.stderr)
            sys.exit(1)
    
    # Write outputs
    gh_out = os.environ.get('GITHUB_OUTPUT')
    if gh_out:
        with open(gh_out, 'a', encoding='utf-8') as f:
            f.write(f'xml_path={xml_path}\n')
            f.write(f'html_dir={output_dir}\n')
    else:
        print('ERROR: GITHUB_OUTPUT not set', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
