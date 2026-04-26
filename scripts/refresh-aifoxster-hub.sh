#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOLUTION_PATH="$ROOT_DIR/AIFoxsterDevHub.sln"

SOLUTION_FOLDER_TYPE="{2150E333-8FDC-42A3-9474-1A3956D46DE8}"
CSHARP_PROJECT_TYPE="{FAE04EC0-301F-11D3-BF4B-00C04F79EFBC}"

WORKSPACE_GUID="{3C98D1EF-41B4-4A9E-9B73-A3C9775B6D0B}"
AIROOT_GUID="{51C4B647-27C8-44D0-8266-364C0E155D2C}"
CCP_GUID="{4AFEE5EB-64AA-4E2E-85DE-988885DBE7FE}"
CCP_AUTHORING_GUID="{2F4D3FE8-8CC7-4D80-93D4-A2E89244F1A8}"
CCP_WORKSPACES_GUID="{D8E8B807-5E4D-4C8B-BE27-1476A9DB944B}"
DAS_GUID="{1E7A85AE-0909-4A12-B129-49B4F3E89E61}"
DAS_AUTHORING_GUID="{CB7099F2-5E96-4901-82AB-DFFAF8A2A9E0}"
DAS_CONSUMERS_GUID="{B65C2E75-3607-4D86-8CBA-A8544841C6F2}"
DAS_DEMO_GUID="{54014667-7B86-40E9-9C1F-74D157AC30DA}"
DAS_WORKSPACES_GUID="{7D8C0D2A-BE39-4AF8-9272-52B085B78E84}"

PROJECT_SPECS=(
  "ConnectivityCheckerPro/Authoring|ConnectivityCheckerPro/ConnectivityCheckerPro_Publish/ConnectivityCheckerPro.Runtime.csproj"
  "ConnectivityCheckerPro/Authoring|ConnectivityCheckerPro/ConnectivityCheckerPro_Publish/ConnectivityCheckerPro.Samples.csproj"
  "ConnectivityCheckerPro/Authoring|ConnectivityCheckerPro/ConnectivityCheckerPro_Publish/ConnectivityCheckerPro.Tests.csproj"
  "ConnectivityCheckerPro/Authoring|ConnectivityCheckerPro/ConnectivityCheckerPro_Publish/ConnectivityCheckerPro.PlayMode.Tests.csproj"
  "DevAccelerationSystem/Authoring|DevAccelerationSystem/DevAccelerationSystem/DevAccelerationSystem.Core.csproj"
  "DevAccelerationSystem/Authoring|DevAccelerationSystem/DevAccelerationSystem/DevAccelerationSystem.ProjectCompilationCheck.csproj"
  "DevAccelerationSystem/Authoring|DevAccelerationSystem/DevAccelerationSystem/DevAccelerationSystem.Editor.Tests.csproj"
  "DevAccelerationSystem/Consumers/DemoProject|DevAccelerationSystem/DevAccelerationSystem.DemoProject/TheBestLoggerSample.csproj"
  "DevAccelerationSystem/Consumers/DemoProject|DevAccelerationSystem/DevAccelerationSystem.DemoProject/TheBestLogger.Integration.Tests.csproj"
)

WORKSPACE_ITEMS=(
  "LFS_MIGRATION_PLAN.md"
  "WORKSPACE.md"
  "scripts/refresh-aifoxster-hub.sh"
)

AIROOT_ITEMS=(
  "AIRoot/README.md"
  "AIRoot/INTEGRATION.md"
  "AIRoot/Modules/XUUnity/README.md"
  "AIRoot/Design/XUUNITY_PRODUCT_PROTOCOLS_DESIGN.md"
)

CCP_WORKSPACE_ITEMS=(
  "ConnectivityCheckerPro/ConnectivityCheckerPro_Publish/ConnectivityCheckerPro_Publish.sln"
  "ConnectivityCheckerPro/ConnectivityCheckerPro_Publish/Assets/ConnectivityCheckerPro/package.json"
  "ConnectivityCheckerPro/ConnectivityCheckerPro_Sample2021/Packages/manifest.json"
  "ConnectivityCheckerPro/ConnectivityCheckerPro_Sample2022/Packages/manifest.json"
  "ConnectivityCheckerPro/ConnectivityCheckerPro_Sample6000/ConnectivityCheckerPro_Sample6000.sln"
  "ConnectivityCheckerPro/ConnectivityCheckerPro_Sample6000/Packages/manifest.json"
  "ConnectivityCheckerPro/ConnectivityCheckerPro_Sample6000_3_2f1/ConnectivityCheckerPro_Sample6000_3_2f1.sln"
  "ConnectivityCheckerPro/ConnectivityCheckerPro_Sample6000_3_2f1/Packages/manifest.json"
)

DAS_WORKSPACE_ITEMS=(
  "DevAccelerationSystem/DevAccelerationSystem/DevAccelerationSystem.sln"
  "DevAccelerationSystem/DevAccelerationSystem/Assets/DevAccelerationSystem/package.json"
  "DevAccelerationSystem/DevAccelerationSystem/Assets/TheBestLogger/package.json"
  "DevAccelerationSystem/DevAccelerationSystem.DemoProject/DevAccelerationSystem.DemoProject.sln"
  "DevAccelerationSystem/DevAccelerationSystem.DemoProject/Packages/manifest.json"
  "DevAccelerationSystem/DAS.LocalProject/DAS.LocalProject.sln"
  "DevAccelerationSystem/DAS.LocalProject/Packages/manifest.json"
)

to_windows_path() {
  printf '%s\n' "${1//\//\\}"
}

project_guid() {
  local project_path="$1"
  local guid

  guid="$(
    sed -n 's/.*<ProjectGuid>{\([^}]*\)}.*/\1/p' "$ROOT_DIR/$project_path" \
      | tr '[:lower:]' '[:upper:]'
  )"

  if [[ -z "$guid" ]]; then
    printf 'Missing <ProjectGuid> in %s\n' "$project_path" >&2
    exit 1
  fi

  printf '{%s}\n' "$guid"
}

project_name() {
  basename "$1" .csproj
}

discover_thebestlogger_project_specs() {
  local project_dir="$ROOT_DIR/DevAccelerationSystem/DevAccelerationSystem"
  local project_path basename

  while IFS= read -r project_path; do
    basename="$(basename "$project_path")"

    case "$basename" in
      Assembly-CSharp*.csproj|*.Player.csproj)
        continue
        ;;
    esac

    if rg -q 'Assets/TheBestLogger/' "$project_path"; then
      printf 'DevAccelerationSystem/Authoring|%s\n' "${project_path#"$ROOT_DIR/"}"
    fi
  done < <(find "$project_dir" -maxdepth 1 -name '*.csproj' | sort)
}

emit_solution_folder() {
  local name="$1"
  local guid="$2"
  shift 2

  printf 'Project("%s") = "%s", "%s", "%s"\n' "$SOLUTION_FOLDER_TYPE" "$name" "$name" "$guid"
  if [[ $# -gt 0 ]]; then
    printf '\tProjectSection(SolutionItems) = preProject\n'
    local item
    for item in "$@"; do
      local windows_item
      windows_item="$(to_windows_path "$item")"
      printf '\t\t%s = %s\n' "$windows_item" "$windows_item"
    done
    printf '\tEndProjectSection\n'
  fi
  printf 'EndProject\n'
}

emit_project() {
  local project_path="$1"
  local name guid

  name="$(project_name "$project_path")"
  guid="$(project_guid "$project_path")"

  printf 'Project("%s") = "%s", "%s", "%s"\n' \
    "$CSHARP_PROJECT_TYPE" \
    "$name" \
    "$(to_windows_path "$project_path")" \
    "$guid"
  printf 'EndProject\n'
}

emit_project_configurations() {
  local project_path="$1"
  local guid

  guid="$(project_guid "$project_path")"

  printf '\t\t%s.Debug|Any CPU.ActiveCfg = Debug|Any CPU\n' "$guid"
  printf '\t\t%s.Debug|Any CPU.Build.0 = Debug|Any CPU\n' "$guid"
  printf '\t\t%s.Release|Any CPU.ActiveCfg = Release|Any CPU\n' "$guid"
  printf '\t\t%s.Release|Any CPU.Build.0 = Release|Any CPU\n' "$guid"
}

emit_nested_project() {
  local child_guid="$1"
  local parent_guid="$2"
  printf '\t\t%s = %s\n' "$child_guid" "$parent_guid"
}

assert_paths_exist() {
  local item

  for item in "${WORKSPACE_ITEMS[@]}" "${AIROOT_ITEMS[@]}" "${CCP_WORKSPACE_ITEMS[@]}" "${DAS_WORKSPACE_ITEMS[@]}"; do
    [[ -e "$ROOT_DIR/$item" ]] || {
      printf 'Missing solution item: %s\n' "$item" >&2
      exit 1
    }
  done

  for item in "${PROJECT_SPECS[@]}"; do
    local project_path="${item#*|}"
    [[ -f "$ROOT_DIR/$project_path" ]] || {
      printf 'Missing project: %s\n' "$project_path" >&2
      exit 1
    }
  done
}

assert_paths_exist

while IFS= read -r item; do
  [[ -n "$item" ]] && PROJECT_SPECS+=("$item")
done < <(discover_thebestlogger_project_specs)

{
  printf 'Microsoft Visual Studio Solution File, Format Version 12.00\n'
  printf '# Visual Studio Version 17\n'

  emit_solution_folder "Workspace" "$WORKSPACE_GUID" "${WORKSPACE_ITEMS[@]}"
  emit_solution_folder "AIRoot" "$AIROOT_GUID" "${AIROOT_ITEMS[@]}"
  emit_solution_folder "ConnectivityCheckerPro" "$CCP_GUID"
  emit_solution_folder "Authoring" "$CCP_AUTHORING_GUID"
  emit_solution_folder "Workspaces" "$CCP_WORKSPACES_GUID" "${CCP_WORKSPACE_ITEMS[@]}"
  emit_solution_folder "DevAccelerationSystem" "$DAS_GUID"
  emit_solution_folder "Authoring" "$DAS_AUTHORING_GUID"
  emit_solution_folder "Consumers" "$DAS_CONSUMERS_GUID"
  emit_solution_folder "DemoProject" "$DAS_DEMO_GUID"
  emit_solution_folder "Workspaces" "$DAS_WORKSPACES_GUID" "${DAS_WORKSPACE_ITEMS[@]}"

  spec=""
  for spec in "${PROJECT_SPECS[@]}"; do
    emit_project "${spec#*|}"
  done

  printf 'Global\n'
  printf '\tGlobalSection(SolutionConfigurationPlatforms) = preSolution\n'
  printf '\t\tDebug|Any CPU = Debug|Any CPU\n'
  printf '\t\tRelease|Any CPU = Release|Any CPU\n'
  printf '\tEndGlobalSection\n'
  printf '\tGlobalSection(ProjectConfigurationPlatforms) = postSolution\n'
  for spec in "${PROJECT_SPECS[@]}"; do
    emit_project_configurations "${spec#*|}"
  done
  printf '\tEndGlobalSection\n'
  printf '\tGlobalSection(NestedProjects) = preSolution\n'
  emit_nested_project "$CCP_AUTHORING_GUID" "$CCP_GUID"
  emit_nested_project "$CCP_WORKSPACES_GUID" "$CCP_GUID"
  emit_nested_project "$DAS_AUTHORING_GUID" "$DAS_GUID"
  emit_nested_project "$DAS_CONSUMERS_GUID" "$DAS_GUID"
  emit_nested_project "$DAS_DEMO_GUID" "$DAS_CONSUMERS_GUID"
  emit_nested_project "$DAS_WORKSPACES_GUID" "$DAS_GUID"

  for spec in "${PROJECT_SPECS[@]}"; do
    folder_path="${spec%%|*}"
    project_path="${spec#*|}"
    parent_guid=""

    case "$folder_path" in
      "ConnectivityCheckerPro/Authoring") parent_guid="$CCP_AUTHORING_GUID" ;;
      "DevAccelerationSystem/Authoring") parent_guid="$DAS_AUTHORING_GUID" ;;
      "DevAccelerationSystem/Consumers/DemoProject") parent_guid="$DAS_DEMO_GUID" ;;
      *)
        printf 'Unknown solution folder: %s\n' "$folder_path" >&2
        exit 1
        ;;
    esac

    emit_nested_project "$(project_guid "$project_path")" "$parent_guid"
  done

  printf '\tEndGlobalSection\n'
  printf 'EndGlobal\n'
} > "$SOLUTION_PATH"

printf 'Refreshed %s\n' "$SOLUTION_PATH"
