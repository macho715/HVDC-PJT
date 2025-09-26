#!/usr/bin/env python3
"""
Codex Fix Tool for HVDC Project
Automated code fixing using OpenAI GPT-4 with unified diff generation
"""

import os
import subprocess
import json
import pathlib
import sys
import argparse
from datetime import datetime
from typing import Dict, List, Optional
from openai import OpenAI

# Project root path
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]

def git(*args) -> None:
    """Execute git command with error handling"""
    try:
        subprocess.check_call(["git", *args], cwd=PROJECT_ROOT)
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {' '.join(['git'] + list(args))}")
        print(f"Error: {e}")
        raise SystemExit(1)

def read_repo(path: str = "src") -> Dict[str, str]:
    """Read all Python files from specified directory"""
    target_path = PROJECT_ROOT / path
    if not target_path.exists():
        print(f"Warning: Path {target_path} does not exist")
        return {}
    
    files = [str(f) for f in target_path.rglob("*.py") if f.is_file()]
    contents = {}
    
    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                contents[file_path] = f.read()
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
            continue
    
    print(f"Read {len(contents)} Python files from {path}")
    return contents

def apply_patch(unified_diff: str) -> bool:
    """Apply unified diff using git apply"""
    try:
        p = subprocess.Popen(
            ["git", "apply", "-p0", "--whitespace=fix"], 
            stdin=subprocess.PIPE,
            cwd=PROJECT_ROOT
        )
        p.communicate(unified_diff.encode("utf-8"))
        
        if p.returncode != 0:
            print("Patch apply failed")
            return False
        
        print("Patch applied successfully")
        return True
    except Exception as e:
        print(f"Error applying patch: {e}")
        return False

def create_hvdc_prompt(task: str, files: Dict[str, str], max_diff: int) -> Dict:
    """Create HVDC-specific prompt for OpenAI"""
    return {
        "task": task,
        "project_context": "HVDC Project - Samsung C&T Logistics & ADNOC·DSV Partnership",
        "guidelines": [
            "Keep changes minimal; prefer adding __init__.py and correct imports.",
            "If file is found under different module names, fix package layout and imports.",
            "Pass mypy with --ignore-missing-imports --explicit-package-bases.",
            "Maintain HVDC project structure and naming conventions.",
            "Preserve existing business logic and data processing functions.",
            "Ensure compatibility with MACHO-GPT v3.4-mini integration.",
            f"Maximum diff size: {max_diff} characters",
        ],
        "file_count": len(files),
        "files": files,
        "max_diff_size": max_diff
    }

def call_openai_api(prompt: Dict, api_key: str) -> str:
    """Call OpenAI API with HVDC-specific system prompt"""
    client = OpenAI(api_key=api_key)
    
    system_prompt = """You are a senior software engineer specializing in logistics systems for the HVDC Project.
Your task is to fix code issues while maintaining the project's logistics domain expertise and MACHO-GPT integration.

CRITICAL REQUIREMENTS:
1. Return ONLY unified diffs starting with '*** Begin Patch' and ending with '*** End Patch'
2. Keep changes minimal and focused on the specific task
3. Maintain HVDC project structure and naming conventions
4. Preserve existing business logic and data processing functions
5. Ensure compatibility with MACHO-GPT v3.4-mini integration
6. Follow TDD principles and Kent Beck's "Tidy First" approach

RESPONSE FORMAT:
*** Begin Patch
[unified diff content]
*** End Patch"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(prompt, indent=2)}
    ]
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Updated to current model
            messages=messages,
            max_tokens=4000,
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API error: {e}")
        raise SystemExit(1)

def extract_diff_from_response(response: str) -> Optional[str]:
    """Extract unified diff from OpenAI response"""
    try:
        # Find diff between markers
        start_marker = "*** Begin Patch"
        end_marker = "*** End Patch"
        
        start_idx = response.find(start_marker)
        end_idx = response.find(end_marker)
        
        if start_idx == -1 or end_idx == -1:
            print("Warning: Could not find diff markers in response")
            return None
        
        diff = response[start_idx + len(start_marker):end_idx].strip()
        
        if not diff:
            print("Warning: Empty diff found")
            return None
        
        return diff
    except Exception as e:
        print(f"Error extracting diff: {e}")
        return None

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Codex Fix Tool for HVDC Project")
    parser.add_argument("--path", default="src", help="Target directory path")
    parser.add_argument("--task", default="fix mypy errors", help="Task description")
    parser.add_argument("--max-diff", type=int, default=8000, help="Maximum diff size")
    parser.add_argument("--dry-run", action="store_true", help="Show diff without applying")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Check for required environment variable
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)
    
    if args.verbose:
        print(f"Codex Fix Tool - HVDC Project")
        print(f"Target path: {args.path}")
        print(f"Task: {args.task}")
        print(f"Max diff: {args.max_diff}")
        print(f"Project root: {PROJECT_ROOT}")
    
    # Read repository files
    repo_snapshot = read_repo(args.path)
    if not repo_snapshot:
        print("No Python files found in target directory")
        sys.exit(1)
    
    # Create prompt
    prompt = create_hvdc_prompt(args.task, repo_snapshot, args.max_diff)
    
    if args.verbose:
        print(f"Created prompt with {len(repo_snapshot)} files")
    
    # Call OpenAI API
    print("Calling OpenAI API...")
    response = call_openai_api(prompt, api_key)
    
    # Extract diff
    diff = extract_diff_from_response(response)
    if not diff:
        print("No valid diff found in response")
        sys.exit(1)
    
    print(f"Generated diff ({len(diff)} characters)")
    
    if args.dry_run:
        print("\n--- DRY RUN: Generated Diff ---")
        print(diff)
        print("--- End Diff ---")
        return
    
    # Apply patch
    print("Applying patch...")
    if not apply_patch(diff):
        print("Failed to apply patch")
        sys.exit(1)
    
    # Configure git and commit
    print("Configuring git...")
    git("config", "user.email", "codex-bot@hvdc-project.com")
    git("config", "user.name", "HVDC Codex Bot")
    
    # Check if there are changes to commit
    try:
        git("diff", "--quiet", "HEAD")
        print("No changes to commit")
        return
    except subprocess.CalledProcessError:
        # Exit code 1 means there are changes
        pass
    
    # Create branch and commit
    branch_name = f"codex/{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    print(f"Creating branch: {branch_name}")
    
    git("checkout", "-B", branch_name)
    git("add", ".")
    git("commit", "-m", f"codex: {args.task}")
    
    print(f"Changes committed to branch: {branch_name}")
    print("Codex fix completed successfully!")

if __name__ == "__main__":
    main()
