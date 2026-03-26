#!/bin/bash

set -eu

SCRIPT_NAME="$0"
BASE_DIR="$( cd "$(dirname "$0")" ; pwd -P )"

target_base_dir=""
project_dir=""
name=""
preset=""
platform="ios"


GODOT="/Applications/Godot.app/Contents/MacOS/Godot"
GODOT_EDITOR="${GODOT_EDITOR:-}"
if [ "$GODOT_EDITOR" != "" ] && [ -x "$GODOT_EDITOR" ]
then
    GODOT="$GODOT_EDITOR"
fi

if [ ! -x "$GODOT" ]
then
    echo "Could not find a working Godot Editor binary. Please use the GODOT_EDITOR environment variable to provide one."
    exit 1
fi

function usage() {
    echo "Usage: $SCRIPT_NAME [--target <target base dir>] [--project <project dir>] [--name <pck / dir name>] [--preset <preset>] [--platform <ios|android>]"
    exit 1
}

while [ "${1:-}" != "" ]
do
    case "$1" in
        --target)
            shift
            target_base_dir="${1:-}"
        ;;
        --project)
            shift
            project_dir="${1:-}"
        ;;
        --name)
            shift
            name="${1:-}"
        ;;
        --preset)
            shift
            preset="${1:-}"
        ;;
        --platform)
            shift
            platform="${1:-}"
        ;;
        *)
        usage
        ;;
    esac
    shift
done

if [ "$project_dir" = "" ] || [ "$target_base_dir" = "" ] || [ "$preset" = "" ] || [ "$name" = "" ]
then
    usage
fi

host_arch="$(uname -m)"

"$GODOT" --headless --path "$project_dir" --import
"$GODOT" --headless --path "$project_dir" --import

if [ "$platform" = "ios" ]
then
    ASSETS_BASE_DIR="$target_base_dir/ios"
    mkdir -p $ASSETS_BASE_DIR
    "$GODOT" --headless --path "$project_dir" --export-pack "$preset" "$ASSETS_BASE_DIR/${name}.pck"
elif [ "$platform" = "android" ]
then
    ASSETS_BASE_DIR="$target_base_dir/android/app/src/main/assets"
    mkdir -p $ASSETS_BASE_DIR
    TARGET_DIR="$ASSETS_BASE_DIR/${name}"
    "$GODOT" --headless --path "$project_dir" --export-pack "$preset" "$ASSETS_BASE_DIR/${name}.zip"
    rm -rf "$TARGET_DIR"
    mkdir -p "$TARGET_DIR"
    cd "$TARGET_DIR"
    unzip "$ASSETS_BASE_DIR/${name}.zip"
    rm -rf "$ASSETS_BASE_DIR/${name}.zip"
else
    echo "Unsupported platform: $platform"
    exit 1
fi
