#!/usr/bin/env python3
"""
Entity Registry Validator
Validates that all entity refs in graph.yml files are registered in _shared/entities.yml
"""

import os
import yaml
from pathlib import Path
from collections import defaultdict

def load_shared_entities(shared_path: Path) -> set:
    """Load all registered entity IDs from _shared/entities.yml"""
    with open(shared_path / "entities.yml", "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    entities = data.get("entities", [])
    return {e["id"] for e in entities if "id" in e}

def find_all_graph_files(senario_path: Path) -> list:
    """Find all graph.yml files in senario directory"""
    return list(senario_path.rglob("graph.yml"))

def extract_entity_refs(graph_file: Path) -> tuple:
    """Extract entity refs and inline entities from a graph.yml file"""
    with open(graph_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    schema_version = data.get("schema_version", "1.0")
    scenario_id = data.get("scenario_id", "unknown")
    entities = data.get("entities", [])
    
    refs = []
    inline_ids = []
    
    for entity in entities:
        if "ref" in entity:
            refs.append(entity["ref"])
        elif "id" in entity:
            inline_ids.append(entity["id"])
    
    return {
        "file": str(graph_file),
        "scenario_id": scenario_id,
        "schema_version": schema_version,
        "refs": refs,
        "inline_ids": inline_ids
    }

def main():
    base_path = Path(__file__).parent
    shared_path = base_path / "_shared"
    senario_path = base_path / "senario"
    
    # Load registered entities
    registered = load_shared_entities(shared_path)
    print(f"=== Entity Registry Validator ===\n")
    print(f"📦 Registered entities in _shared/entities.yml: {len(registered)}")
    print(f"   IDs: {sorted(registered)}\n")
    
    # Find and analyze all graph files
    graph_files = find_all_graph_files(senario_path)
    print(f"📁 Found {len(graph_files)} graph.yml files\n")
    
    # Analyze
    v1_count = 0
    v2_count = 0
    all_refs = defaultdict(list)  # ref -> list of scenarios using it
    all_inline = defaultdict(list)  # inline_id -> list of scenarios using it
    unregistered = defaultdict(list)  # unregistered ref -> list of scenarios
    
    for graph_file in sorted(graph_files):
        result = extract_entity_refs(graph_file)
        
        if result["schema_version"] == "1.0":
            v1_count += 1
        else:
            v2_count += 1
        
        for ref in result["refs"]:
            all_refs[ref].append(result["scenario_id"])
            if ref not in registered:
                unregistered[ref].append(result["scenario_id"])
        
        for inline_id in result["inline_ids"]:
            all_inline[inline_id].append(result["scenario_id"])
    
    # Report
    print("=" * 60)
    print("📊 SCHEMA VERSION SUMMARY")
    print("=" * 60)
    print(f"  v1.0 (inline entities): {v1_count} files")
    print(f"  v2.0 (ref-based):       {v2_count} files")
    print(f"  Total:                  {len(graph_files)} files")
    print()
    
    print("=" * 60)
    print("🔗 ENTITY REF USAGE (v2.0 scenarios)")
    print("=" * 60)
    for ref, scenarios in sorted(all_refs.items(), key=lambda x: -len(x[1])):
        status = "✅" if ref in registered else "❌"
        print(f"  {status} {ref}: {len(scenarios)} scenarios")
    print()
    
    if unregistered:
        print("=" * 60)
        print("⚠️  UNREGISTERED ENTITY REFS")
        print("=" * 60)
        for ref, scenarios in sorted(unregistered.items()):
            print(f"  ❌ '{ref}' used in: {', '.join(scenarios)}")
        print()
        print("👉 Add these to _shared/entities.yml to resolve warnings")
        print()
    else:
        print("=" * 60)
        print("✅ ALL ENTITY REFS ARE REGISTERED")
        print("=" * 60)
        print("  No unregistered entity refs found!")
        print()
    
    # Inline entities that could be promoted
    print("=" * 60)
    print("📝 INLINE ENTITIES (candidates for promotion)")
    print("=" * 60)
    common_inline = {k: v for k, v in all_inline.items() if len(v) >= 2}
    if common_inline:
        print("  These inline entities are used in 2+ scenarios:")
        for inline_id, scenarios in sorted(common_inline.items(), key=lambda x: -len(x[1])):
            if inline_id not in registered:
                print(f"  📌 '{inline_id}': {len(scenarios)} scenarios ({', '.join(scenarios[:3])}{'...' if len(scenarios) > 3 else ''})")
    else:
        print("  No commonly reused inline entities found.")
    print()
    
    print("=" * 60)
    print("📈 MIGRATION PROGRESS")
    print("=" * 60)
    migration_pct = (v2_count / len(graph_files) * 100) if graph_files else 0
    print(f"  {migration_pct:.1f}% of scenarios use ref-based entities (v2.0)")
    bar_len = 40
    filled = int(bar_len * migration_pct / 100)
    bar = "█" * filled + "░" * (bar_len - filled)
    print(f"  [{bar}]")
    print()

if __name__ == "__main__":
    main()
