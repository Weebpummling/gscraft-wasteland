#!/usr/bin/env bash
# AFTER tools/live_deploy.py has finished and live is up on the new jar - never before (a client must not update ahead of its
# server). The client pack rebuilt with the new mod jar (it carries the notebook pages, the new item and the lang lines), its
# version bumped, committed and pushed; then the jar in the `pack-files` release replaced. Owner's word naming live needed.
#   cd /g/GSCraft/repo && bash tools/live_pack.sh 2026.09.19.1
set -e
V="${1:?give the pack version, e.g. 2026.09.19.1}"
cd "$(dirname "$0")/.."
H=G:/GSCraft/server/config/hordes-common.toml
sed -i 's/pauseEventServer = false/pauseEventServer = true/' "$H"
python tools/packwiz_build.py --tag client-installer-2026-09-10 --version "$V" --files-tag pack-files 2>&1 | tail -1
sed -i 's/pauseEventServer = true/pauseEventServer = false/' "$H"
echo "local hordes pause restored to false: $(grep -c 'pauseEventServer = false' "$H")"
git add build/packwiz
git commit -q -m "Pack $V: the mod jar of the full deploy (loot system, upgrades, Superb Warfare kit)

Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>"
git push -q
gh release upload pack-files mod/build/libs/gscraft-0.1.0.jar --clobber -R Weebpummling/gscraft-wasteland | tail -1
gh release view pack-files -R Weebpummling/gscraft-wasteland --json assets --jq '.assets[] | select(.name=="gscraft-0.1.0.jar") | "\(.name) \(.size) \(.updatedAt)"'
grep -n "^version" build/packwiz/pack.toml
