#!/usr/bin/env python3
from pathlib import Path
import json, os, sys
ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(".").resolve()
src=json.loads((ROOT/"PROJECT_STATE.json").read_text(encoding="utf-8"))
src["git_commit_sha"]=os.environ["BUILD_SHA"]
src["source_branch"]=os.environ["BUILD_BRANCH"]
out=ROOT/"app/src/main/assets/v20/project_state.json"
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(src,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(src)
