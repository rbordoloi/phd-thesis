import re
from pathlib import Path
import sys
import yaml

def createGlossaryTex(glossary):
    texFile = (Path('.') / 'glossary.tex').resolve()

    with open(texFile, 'w+') as f:
        for term, defn in glossary.items():
            lines = [
                f'\\newglossaryentry{{{term.lower().replace(' ', '_')}}}\n',
                '{\n',
                f'\tname={term},\n',
                f'\tdescription={{{defn.rstrip()}}}\n',
                '}\n'
            ]
            f.writelines(lines)

def convert_glossary_tags(directories):
    # Matches {{< glossary "anything" >}} and {{<glossary "anything">}}
    # Captures the text inside the quotes
    pattern = re.compile(r'\{\{<\s*glossary\s+"([^"]+)"\s*>\}\}')

    total_replacements = 0
    files_modified = 0

    for dir_path in directories:
        path = Path(dir_path)

        if not path.is_dir():
            print(f"Skipping invalid directory: {dir_path}")
            continue

        for qmd_file in path.rglob("*.qmd"):
            try:
                content = qmd_file.read_text(encoding="utf-8")

                matches = pattern.findall(content)
                if matches:
                    # \1 refers to the captured term inside the quotes
                    # We use double backslashes to output a literal \gls
                    new_content = pattern.sub(lambda m: f"\\gls{{{m.group(1).lower().replace(' ', '_')}}}", content)
                    qmd_file.write_text(new_content, encoding="utf-8")

                    match_count = len(matches)
                    total_replacements += match_count
                    files_modified += 1
                    print(f"Reverted {match_count} tags in: {qmd_file}")

            except UnicodeDecodeError:
                print(f"Encoding error reading {qmd_file}, ensure it is UTF-8.", file=sys.stderr)
            except Exception as e:
                print(f"Error processing {qmd_file}: {e}", file=sys.stderr)

    print(f"\nFinished: Converted {total_replacements} tags across {files_modified} files.")


if __name__ == "__main__":

    target_directories = [
        ".",
        "preface",
        "main",
        "appendix"
    ]

    # Run the conversion
    convert_glossary_tags(target_directories)

    glossaryFile = (Path('.') / 'glossary.yml').resolve()
    with open(glossaryFile, 'r') as f:
        glossary = yaml.safe_load(f)
    createGlossaryTex(glossary)
