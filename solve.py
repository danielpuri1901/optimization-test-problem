#!/usr/bin/env python3
"""
Entry point for solving the multi-dimensional bin packing problem.

This script generates a challenging problem instance and solves it.
The optimization agent can analyze this to find improvements.
"""

from problem import generate_problem, create_model, solve_model


def main():
    print("=" * 60)
    print("Multi-Dimensional Bin Packing Optimizer")
    print("=" * 60)

    # Generate a moderately challenging problem instance
    # Sized to solve in 30-60 seconds with default parameters
    print("\nGenerating problem instance...")
    data = generate_problem(
        n_items=100,    # 100 items (reduced from 200)
        n_bins=15,      # 15 bins (reduced from 30)
        n_dimensions=3, # 3 capacity dimensions (reduced from 5)
        seed=42,        # Reproducible
    )

    print(f"  Items: {data['n_items']}")
    print(f"  Bins: {data['n_bins']}")
    print(f"  Dimensions: {data['n_dimensions']}")
    print(f"  Conflicts: {len(data['conflicts'])}")

    # Create and solve the model
    print("\nCreating Gurobi model...")
    model = create_model(data)
    print(f"  Variables: {model.NumVars}")
    print(f"  Constraints: {model.NumConstrs}")
    print(f"  Binary vars: {model.NumBinVars}")

    print("\nSolving...")
    print("-" * 60)

    result = solve_model(model, time_limit=300.0)

    print("-" * 60)
    print("\nResults:")
    print(f"  Status: {result['status']}")
    print(f"  Objective: {result['obj_value']}")
    print(f"  Gap: {result['gap']:.2%}" if result['gap'] else "  Gap: N/A")
    print(f"  Runtime: {result['runtime']:.2f}s")
    print(f"  Nodes: {result['node_count']}")


if __name__ == "__main__":
    main()
