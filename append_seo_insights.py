import os

# Define memory file
memory_file_path = "synthesized_memory.md"
if not os.path.exists(memory_file_path):
    with open(memory_file_path, "w", encoding="utf-8") as f:
        f.write("# Synthesized Memory\n\n")

# Define SEO-focused script files
seo_scripts = {
    "Keyword Clustering": "check_keyword_clusters.py",
    "Ranking Paths": "check_ranking_paths.py",
    "Funding Knowledge": "check_funding_knowledge.py",
    "Knowledge Base": "check_knowledge_base.py",
    "Collections Intelligence": "check_collections.py"
}

# Define agent folder
agent_folder = "Tools"

# Loop through each file and append output
for category, script_file in seo_scripts.items():
    script_path = os.path.join(agent_folder, script_file)
    print(f"\n📌 Appending SEO insight from {category}...")

    # Run the script and capture output
    stream = os.popen(f'python "{script_path}"')
    output = stream.read()

    # Append to memory with tag and heading
    with open(memory_file_path, "a", encoding="utf-8") as f:
        f.write(f"\n\n### {category} (SEO Agent)\n")
        f.write(f"#SEO #Category:{category.replace(' ', '_')}\n\n")
        f.write(output.strip() + "\n")

print("\n✅ All SEO intelligence has been successfully appended to synthesized_memory.md")
