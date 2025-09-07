import json

def extract_sombrero_entries(input_file, output_file=None):
    """Extract all entries where word == 'sombrero' from JSONL file."""
    sombrero_entries = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                entry = json.loads(line)
                if entry.get('word') == 'sombrero':
                    sombrero_entries.append(entry)
            except json.JSONDecodeError as e:
                print(f"Error parsing line {line_num}: {e}")
                continue
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sombrero_entries, f, ensure_ascii=False, indent=2)
        print(f"Found {len(sombrero_entries)} entries with word='sombrero'")
        print(f"Results saved to {output_file}")
    else:
        print(f"Found {len(sombrero_entries)} entries with word='sombrero':")
        for entry in sombrero_entries:
            print(json.dumps(entry, ensure_ascii=False, indent=2))
    
    return sombrero_entries

if __name__ == "__main__":
    input_file = "Español.jsonl"
    output_file = "sombrero_entries.json"
    
    extract_sombrero_entries(input_file, output_file)