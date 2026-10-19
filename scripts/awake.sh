#!/bin/bash
# awake — keep macOS awake for one session, and only that session.
#
#   awake on [HOURS] [--pid PID]   caffeinate tied to the calling session
#   awake off        [--pid PID]   stop this session's caffeinate, and only it
#   awake ls                       every caffeinate on the machine, and its owner
#
# Each session gets its own `caffeinate -dims -t SECS -w OWNER`. Assertions
# add up, so several sessions coexist. -w releases it when the owner exits:
# a session that dies or forgets `awake off` cannot leave the Mac awake, and
# -t bounds one that stays alive. OWNER is the first ancestor that is not a
# shell: the `claude` or Gemini CLI process for an agent, `login` for a
# terminal tab. Never stop caffeinate (or openmsx) by name or pattern
# (killall / pkill -f): that kills every other session's too.

set -u

DIR="$HOME/.cache/awake"
SHELLS=' bash zsh sh dash fish login-shell awake awake.sh nohup env '

usage() {
    sed -n '2,6p' "$0" | sed 's/^# \{0,1\}//'
    exit 2
}

comm_of() {     # basename of a process's executable, without a login dash
    local c
    c=$(ps -o comm= -p "$1" 2>/dev/null) || return 1
    c=${c##*/}
    echo "${c#-}"
}

owner_pid() {   # first ancestor of this script that is not a shell
    local p c
    p=$PPID
    while [ -n "$p" ] && [ "$p" -gt 1 ]; do
        c=$(comm_of "$p") || break
        case "$SHELLS" in
            *" $c "*) p=$(ps -o ppid= -p "$p" | tr -d ' ') ;;
            *) echo "$p"; return 0 ;;
        esac
    done
    echo "$PPID"
}

is_ours() {     # is PID a caffeinate waiting on OWNER?
    local args
    args=$(ps -o args= -p "$1" 2>/dev/null) || return 1
    case "$args" in
        caffeinate*" -w $2"*) return 0 ;;
    esac
    return 1
}

cmd=${1:-}; [ $# -gt 0 ] && shift
hours=4
owner=""
while [ $# -gt 0 ]; do
    case "$1" in
        --pid) owner=${2:-}; shift 2 ;;
        [0-9]*) hours=$1; shift ;;
        *) usage ;;
    esac
done

case "$cmd" in
on)
    [ -n "$owner" ] || owner=$(owner_pid)
    kill -0 "$owner" 2>/dev/null || { echo "awake: no process $owner" >&2; exit 1; }
    mkdir -p "$DIR"
    pidf="$DIR/$owner.pid"
    if [ -f "$pidf" ] && is_ours "$(cat "$pidf")" "$owner"; then
        old=$(cat "$pidf")
        kill "$old" 2>/dev/null     # a new `on` resets the time limit
    fi
    secs=$(awk -v h="$hours" 'BEGIN { printf "%d", h * 3600 }')
    nohup caffeinate -dims -t "$secs" -w "$owner" >/dev/null 2>&1 &
    pid=$!
    disown "$pid" 2>/dev/null
    echo "$pid" > "$pidf"
    echo "awake: caffeinate $pid for $(comm_of "$owner") $owner, ${hours} h"
    ;;
off)
    [ -n "$owner" ] || owner=$(owner_pid)
    pidf="$DIR/$owner.pid"
    if [ ! -f "$pidf" ]; then
        echo "awake: nothing on for $owner"
        exit 0
    fi
    pid=$(cat "$pidf")
    if is_ours "$pid" "$owner"; then
        kill "$pid" && echo "awake: stopped caffeinate $pid ($owner)"
    else
        echo "awake: caffeinate $pid already gone"
    fi
    rm -f "$pidf"
    ;;
ls)
    found=0
    while read -r pid etime args; do
        [ -n "$pid" ] || continue
        found=1
        w=$(echo "$args" | sed -n 's/.*-w \([0-9]*\).*/\1/p')
        if [ -n "$w" ]; then
            who="owner $w $(comm_of "$w" || echo '(gone)')"
        else
            who="no owner (not started by awake)"
        fi
        echo "$pid  up $etime  $who  [$args]"
    done < <(ps -axo pid=,etime=,args= | awk '$3 == "caffeinate" || $3 ~ /\/caffeinate$/')
    [ "$found" = 1 ] || echo "awake: no caffeinate running"
    ;;
*)
    usage ;;
esac
