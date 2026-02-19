# Optimization Test Problem

A challenging multi-dimensional bin packing problem for testing optimization agents.

## Problem Characteristics

- **200 items** to pack into **30 bins**
- **5 capacity dimensions** (weight, volume, etc.)
- **~60 conflict constraints** (some items cannot share a bin)
- **Big-M constraints** (intentionally weak formulation)
- **No symmetry breaking** (improvement opportunity)

## Expected Behavior

With default Gurobi parameters:
- Solve time: 30-120 seconds
- Nodes explored: 1000+
- Final gap: < 1%

## Running

```bash
pip install -r requirements.txt
python solve.py
```

## Improvement Opportunities

1. **Solver parameters**: MIPFocus, Cuts, Heuristics
2. **Big-M rescaling**: The large M values can be tightened
3. **Symmetry breaking**: Add constraints to prefer lower-indexed bins
4. **Cut generation**: Model structure allows effective cuts
