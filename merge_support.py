## 05

import pandas as pd
from pathlib import Path
from config import OUT_DIR, CN_DIR, CN_COLS, VALID_OFFICES

def _find_file(folder: Path, startswith: str) -> Path:
    for ext in ("*.txt", "*.dat"):
        for p in folder.glob(ext):
            if p.name.lower().startswith(startswith.lower()):
                return p
    cands = list(folder.glob("*.txt")) + list(folder.glob("*.dat"))
    if not cands:
        raise FileNotFoundError(f"No data files found in {folder}")
    return max(cands, key=lambda p: p.stat().st_size)

def _safe_read_csv(path: Path, cols: list, dtypes=None) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=cols)
    df = pd.read_csv(path, dtype=dtypes)
    for c in cols:
        if c not in df.columns:
            df[c] = pd.Series(dtype="float64" if c != "CAND_ID" else "object")
    return df[cols]

def main():
    superpac_path = OUT_DIR / "superpac_ie_support.csv"
    indiv_path = OUT_DIR / "individual_support.csv"
    pac_path = OUT_DIR / "pac_support_corp_nonconnected.csv"

    cn_path = _find_file(CN_DIR, "cn")

    print("[merge_support] Reading:")
    print("  cn:", cn_path)
    print("  superpac:", superpac_path)
    print("  indiv:", indiv_path)
    print("  pac:", pac_path)

    cn = pd.read_csv(
        cn_path, sep="|", header=None, names=CN_COLS,
        dtype=str, encoding_errors="ignore"
    )

    # ✅ Restrict universe to Senate + Presidential (no House)
    cn = cn[cn["CAND_OFFICE"].isin(VALID_OFFICES)].copy()

    cn_labels = cn[
        ["CAND_ID", "CAND_NAME", "CAND_PTY_AFFILIATION", "CAND_OFFICE", "CAND_OFFICE_ST"]
    ].drop_duplicates("CAND_ID")

    superpac = _safe_read_csv(
        superpac_path,
        cols=["CAND_ID", "SUPERPAC_IE_SUPPORT"],
        dtypes={"CAND_ID": str}
    )
    indiv = _safe_read_csv(
        indiv_path,
        cols=["CAND_ID", "INDIVIDUAL_SUPPORT"],
        dtypes={"CAND_ID": str}
    )
    pac = _safe_read_csv(
        pac_path,
        cols=["CAND_ID", "CORP_PAC_SUPPORT", "NONCONNECTED_PAC_SUPPORT"],
        dtypes={"CAND_ID": str}
    )

    merged = (
        cn_labels
        .merge(indiv, on="CAND_ID", how="left")
        .merge(pac, on="CAND_ID", how="left")
        .merge(superpac, on="CAND_ID", how="left")
    )

    support_cols = [
        "INDIVIDUAL_SUPPORT",
        "CORP_PAC_SUPPORT",
        "NONCONNECTED_PAC_SUPPORT",
        "SUPERPAC_IE_SUPPORT",
    ]
    for col in support_cols:
        merged[col] = pd.to_numeric(merged[col], errors="coerce").fillna(0.0)

    merged["TOTAL_SUPPORT"] = merged[support_cols].sum(axis=1)
    merged["HAS_MONEY"] = (merged["TOTAL_SUPPORT"] > 0).astype(int)

    merged_sorted = merged.sort_values(["CAND_OFFICE_ST", "TOTAL_SUPPORT"], ascending=[True, False])

    with_money = merged_sorted[merged_sorted["HAS_MONEY"] == 1].copy()
    no_money = merged_sorted[merged_sorted["HAS_MONEY"] == 0].copy()

    out_with_money = OUT_DIR / "final_support_table.csv"
    out_no_money = OUT_DIR / "candidates_no_support.csv"
    out_all_flag = OUT_DIR / "candidates_all_with_flag.csv"

    with_money.to_csv(out_with_money, index=False)
    no_money.to_csv(out_no_money, index=False)
    merged_sorted.to_csv(out_all_flag, index=False)

    print("[merge_support] Wrote:")
    print("  ", out_with_money)
    print("  ", out_no_money)
    print("  ", out_all_flag)

    print(
        f"[merge_support] Counts: "
        f"with_money={len(with_money):,} | "
        f"no_money={len(no_money):,} | "
        f"total={len(merged_sorted):,}"
    )

    print("\n[merge_support] Preview:")
    print(with_money.head(25).to_string(index=False))

if __name__ == "__main__":
    main()
