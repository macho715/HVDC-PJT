import os, subprocess, json, pathlib, sys
from datetime import datetime
from openai import OpenAI

PATH = pathlib.Path(__file__).resolve().parents[1]

def git(*args):
    subprocess.check_call(["git", *args])

def read_repo(path="src"):
    p = PATH / path
    files = [str(f) for f in p.rglob("*.py") if f.is_file()]
    contents = {f: open(f, "r", encoding="utf-8").read() for f in files}
    return contents

def apply_patch(unified_diff: str):
    p = subprocess.Popen(["git", "apply", "-p0", "--whitespace=fix"], stdin=subprocess.PIPE)
    p.communicate(unified_diff.encode("utf-8"))
    if p.returncode != 0:
        raise SystemExit("Patch apply failed")

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default="src")
    ap.add_argument("--task", default="fix mypy errors")
    ap.add_argument("--max-diff", type=int, default=8000)
    args = ap.parse_args()

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    repo_snapshot = read_repo(args.path)
    prompt = {
        "task": args.task,
        "guidelines": [
            "Keep changes minimal; prefer adding __init__.py and correct imports.",
            "If file is found under different module names, fix package layout and imports.",
            "Pass mypy with --ignore-missing-imports.",
        ],
        "files": repo_snapshot,
    }

    # 요청: unified diff로만 반환하도록 강제
    messages = [
        {"role":"system","content":"You return ONLY unified diffs starting with '*** Begin Patch' and ending with '*** End Patch'."},
        {"role":"user","content": json.dumps(prompt)}
    ]
    rsp = client.chat.completions.create(model="gpt-4.1-mini", messages=messages)  # 모델은 환경에 맞게
    text = rsp.choices[0].message.content

    diff = text.split("*** Begin Patch")[-1].split("*** End Patch")[0].strip()
    diff = "*** Begin Patch\n" + diff + "\n*** End Patch"
    # 실제 git apply용으로 가공
    unified = diff.replace("*** Begin Patch\n", "").replace("\n*** End Patch", "")
    apply_patch(unified)

    git("config", "user.email", "ci-bot@example.com")
    git("config", "user.name", "codex-bot")
    git("checkout", "-B", f"codex/{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}")
    git("add", ".")
    git("commit", "-m", f"codex: {args.task}")

if __name__ == "__main__":
    main()
