# Repository Content Dumper for LLM Prompts

## Overview

This tool is designed to dump the contents of a Git repository into a single file, making it easier to use in Retrieval-Augmented Generation (RAG) systems or as part of prompts for Large Language Models (LLMs). By consolidating your codebase into one file, you can more easily pass context to an LLM or integrate it into a RAG pipeline.

## Features

- Dumps entire repository content into a single file
- Respects .gitignore patterns to exclude unnecessary files
- Generates a tree-like directory structure for easy navigation
- Includes file contents for all non-excluded files
- Customizable file type filtering

## Use Cases

1. **RAG Systems**: Use the dumped content as a knowledge base for retrieval-augmented generation, allowing LLMs to access and reference your codebase accurately.

2. **LLM Prompts**: Include relevant parts of your codebase in prompts to give LLMs more context about your project structure and implementation details.

3. **Code Analysis**: Quickly get an overview of your entire project in a single file, making it easier to analyze or search through your codebase.

4. **Documentation**: Generate comprehensive documentation that includes both the structure and content of your project.

## Usage

```
python dump.py <start_path> <output_file> [exclusion_file] [file_extensions...]
```

- `<start_path>`: The root directory of your repository
- `<output_file>`: The file where the dumped content will be saved
- `[exclusion_file]`: Optional. A file containing exclusion patterns (e.g., .gitignore)
- `[file_extensions...]`: Optional. Specific file extensions to include (e.g., .py .js .tsx)

Example:
```
python dump.py /path/to/your/repo output.txt .gitignore py js tsx
```

## Output Format

The output file will contain:

1. A tree-like representation of your directory structure
2. The contents of each included file, preceded by its relative path

Example:
```
Directory Structure:
-------------------
/ 
├── .env.local
├── package.json
├── next.config.js
├── tsconfig.json
├── public/
│   └── images/
│       ├── astro.png
│       └── astro-logo.svg
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── tools/
...

File Contents:
--------------
File: .env.local
--------------------------------------------------
Content of .env.local:
API_KEY=your_api_key_here
...

File: package.json
--------------------------------------------------
Content of package.json:
{
  "name": "your-project",
  "version": "1.0.0",
  ...
}

...
```

## Benefits for LLM Integration

1. **Contextual Understanding**: By providing the entire codebase structure and content, LLMs can better understand the context of your project.

2. **Improved Code Generation**: LLMs can generate more accurate and context-aware code suggestions when they have access to your full project structure.

3. **Enhanced Debugging**: When asking LLMs for help with debugging, providing the full context allows for more precise problem identification and solution suggestions.

4. **Architecture Analysis**: LLMs can provide insights on your project's architecture and suggest improvements when they can see the entire structure.

5. **Documentation Generation**: Use the dumped content to ask LLMs to generate or improve project documentation.

## Best Practices

1. Be mindful of sensitive information. Use .gitignore or the exclusion file to omit sensitive data.
2. For large repositories, consider dumping only relevant sections to stay within LLM token limits.
3. When using the dumped content in LLM prompts, clearly specify which parts of the codebase are relevant to your question or task.

## Contributing

Contributions to improve this tool are welcome! Please submit issues or pull requests on our GitHub repository.