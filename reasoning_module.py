import json

def load_and_process_memory():
    """
    Load memory entries from tagged_memory.json, sort by score, and display top 3.
    """
    try:
        # Load memory entries from JSON file
        with open('tagged_memory.json', 'r', encoding='utf-8') as file:
            memory_entries = json.load(file)
        
        # Validate that we have a list of entries
        if not isinstance(memory_entries, list):
            print("Error: Expected a list of memory entries in tagged_memory.json")
            return
        
        # Filter entries with complete required fields
        required_fields = ['score', 'category', 'question', 'answer']
        valid_entries = []
        
        for entry in memory_entries:
            if isinstance(entry, dict) and all(field in entry for field in required_fields):
                # Check that none of the required fields are None or empty strings
                if all(entry[field] is not None and str(entry[field]).strip() != '' for field in required_fields):
                    valid_entries.append(entry)
        
        if not valid_entries:
            print("No valid entries found in tagged_memory.json")
            return
        
        # Sort entries by score in descending order
        try:
            sorted_entries = sorted(valid_entries, key=lambda x: float(x['score']), reverse=True)
        except (ValueError, TypeError) as e:
            print("Error: Invalid score values found in entries")
            return
        
        # Select top 3 entries
        top_entries = sorted_entries[:3]
        
        # Print each priority in the specified format
        for i, entry in enumerate(top_entries, 1):
            print(f"--- Priority #{i} ---")
            print(f"Score: {entry['score']}")
            print(f"Category: {entry['category']}")
            print(f"Question: {entry['question']}")
            print(f"Answer: {entry['answer']}")
            if i < len(top_entries):  # Add blank line between entries, but not after the last one
                print()
    
    except FileNotFoundError:
        print("Error: tagged_memory.json file not found")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in tagged_memory.json - {e}")
    except Exception as e:
        print(f"Error: An unexpected error occurred - {e}")

if __name__ == "__main__":
    load_and_process_memory()