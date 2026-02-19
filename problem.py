"""
Challenging Multi-Dimensional Bin Packing Problem

This problem is designed to be hard enough to trigger the optimization agent:
- 500+ binary variables
- Weak LP relaxation (forces branch-and-bound, many nodes)
- Big-M constraints (triggers rescaling analysis)
- Takes 30-120 seconds to solve with default parameters
"""

import gurobipy as gp
from gurobipy import GRB
import numpy as np


def generate_problem(
    n_items: int = 200,
    n_bins: int = 30,
    n_dimensions: int = 5,
    seed: int = 42,
) -> dict:
    """
    Generate a challenging multi-dimensional bin packing instance.

    Args:
        n_items: Number of items to pack
        n_bins: Number of available bins
        n_dimensions: Number of capacity dimensions (weight, volume, etc.)
        seed: Random seed for reproducibility

    Returns:
        Problem data dictionary
    """
    np.random.seed(seed)

    # Item properties: random weights in each dimension
    item_weights = np.random.randint(10, 100, size=(n_items, n_dimensions))

    # Item values (profit for packing)
    item_values = np.random.randint(50, 200, size=n_items)

    # Bin capacities (slightly constrained to make it challenging)
    total_weight_per_dim = item_weights.sum(axis=0)
    bin_capacities = (total_weight_per_dim / n_bins * 1.2).astype(int)

    # Incompatibility matrix: some items cannot be in the same bin
    # This weakens the LP relaxation significantly
    n_conflicts = n_items // 3
    conflicts = []
    for _ in range(n_conflicts):
        i, j = np.random.choice(n_items, 2, replace=False)
        if i != j:
            conflicts.append((int(min(i, j)), int(max(i, j))))
    conflicts = list(set(conflicts))  # Remove duplicates

    # Big-M values (intentionally large, can be tightened)
    big_m = 10000

    return {
        "n_items": n_items,
        "n_bins": n_bins,
        "n_dimensions": n_dimensions,
        "item_weights": item_weights.tolist(),
        "item_values": item_values.tolist(),
        "bin_capacities": bin_capacities.tolist(),
        "conflicts": conflicts,
        "big_m": big_m,
    }


def create_model(data: dict) -> gp.Model:
    """
    Create the Gurobi model for the bin packing problem.

    This model has intentionally suboptimal formulation choices:
    - Uses big-M constraints instead of tighter formulations
    - No symmetry breaking
    - Default solver parameters
    """
    n_items = data["n_items"]
    n_bins = data["n_bins"]
    n_dims = data["n_dimensions"]
    weights = np.array(data["item_weights"])
    values = np.array(data["item_values"])
    capacities = np.array(data["bin_capacities"])
    conflicts = data["conflicts"]
    big_m = data["big_m"]

    model = gp.Model("MultiDimBinPacking")

    # Decision variables
    # x[i,b] = 1 if item i is assigned to bin b
    x = model.addVars(n_items, n_bins, vtype=GRB.BINARY, name="x")

    # y[b] = 1 if bin b is used
    y = model.addVars(n_bins, vtype=GRB.BINARY, name="y")

    # Objective: maximize total value of packed items minus bin usage cost
    model.setObjective(
        gp.quicksum(values[i] * x[i, b] for i in range(n_items) for b in range(n_bins))
        - gp.quicksum(10 * y[b] for b in range(n_bins)),
        GRB.MAXIMIZE,
    )

    # Constraint 1: Each item can be in at most one bin
    for i in range(n_items):
        model.addConstr(
            gp.quicksum(x[i, b] for b in range(n_bins)) <= 1,
            name=f"item_assign_{i}",
        )

    # Constraint 2: Capacity constraints for each bin and dimension
    for b in range(n_bins):
        for d in range(n_dims):
            model.addConstr(
                gp.quicksum(weights[i, d] * x[i, b] for i in range(n_items))
                <= capacities[d] * y[b],
                name=f"capacity_{b}_{d}",
            )

    # Constraint 3: Conflict constraints using big-M (intentionally weak)
    # If items i and j conflict, they cannot both be in the same bin
    for i, j in conflicts:
        for b in range(n_bins):
            # Big-M formulation: x[i,b] + x[j,b] <= 1 + M*(1 - some_indicator)
            # Simplified: just add direct conflict constraint
            model.addConstr(
                x[i, b] + x[j, b] <= 1,
                name=f"conflict_{i}_{j}_{b}",
            )

    # Constraint 4: Linking constraint with big-M (intentionally weak formulation)
    # Use big-M instead of tight indicator constraints
    for b in range(n_bins):
        model.addConstr(
            gp.quicksum(x[i, b] for i in range(n_items)) <= big_m * y[b],
            name=f"link_bigm_{b}",
        )

    # Constraint 5: Symmetry (no breaking - intentionally left for agent to find)
    # Items should be assigned to lower-indexed bins first
    # NOT ADDED - this is an improvement opportunity

    # Valid Inequality 1: Minimum bins required per dimension
    for d in range(n_dims):
        total_weight_d = sum(weights[i, d] for i in range(n_items))
        min_bins_needed = int(np.ceil(total_weight_d / capacities[d]))
        model.addConstr(
            gp.quicksum(y[b] for b in range(n_bins)) >= min_bins_needed,
            name=f"min_bins_dim_{d}"
        )

    model.update()
    return model


def solve_model(model: gp.Model, time_limit: float = 300.0) -> dict:
    """
    Solve the model and return results.
    """
    model.setParam("TimeLimit", time_limit)
    model.setParam("OutputFlag", 1)

    model.optimize()

    return {
        "status": model.Status,
        "obj_value": model.ObjVal if model.SolCount > 0 else None,
        "gap": model.MIPGap if model.SolCount > 0 else None,
        "runtime": model.Runtime,
        "node_count": int(model.NodeCount),
    }
