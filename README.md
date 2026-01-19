# FEC Candidate Support Data ETL

## Table of Contents

1. [Overview](#overview)
2. [Data Sources](#data-sources)
3. [What This Pipeline Does](#what-this-pipeline-does)
4. [Installation and Setup](#installation-and-setup)
5. [How to Use](#how-to-use)
6. [Output Files Structure](#output-files-structure)
---

## Overview

This pipeline processes **FEC bulk transaction data** to create **candidate-level campaign finance datasets** for Senate and Presidential elections. It aggregates individual contributions, PAC contributions, and independent expenditures into clean, non-overlapping support categories. This repository already contains the extracted data for the 2001-2002, 2003-2004,...,2017-2018, 2019-2020 data sets.

> For more details, go to [FUNCTION.md](FUNCTION.md)

**Key Features:**
- Transaction-level data
- Non-overlapping support categories
- Separate outputs for Senate, Presidential, and totals
- Election-year restricted
- Fully reproducible from FEC bulk files

---

| Cycle Years | CYCLE_LABEL | TARGET_ELECTION_YR | Elections |
|-------------|-------------|-------------------|-----------|
| 2001-2002 | `02` | `2002` | Senate midterm |
| 2003-2004 | `04` | `2004` | Presidential + Senate |
| 2005-2006 | `06` | `2006` | Senate midterm |
| 2007-2008 | `08` | `2008` | Presidential + Senate |
| 2009-2010 | `10` | `2010` | Senate midterm |
| 2011-2012 | `12` | `2012` | Presidential + Senate |
| 2013-2014 | `14` | `2014` | Senate midterm |
| 2015-2016 | `16` | `2016` | Presidential + Senate |
| 2017-2018 | `18` | `2018` | Senate midterm |
| 2019-2020 | `20` | `2020` | Presidential + Senate |
| 2021-2022 | `22` | `2022` | Senate midterm |
| 2023-2024 | `24` | `2024` | Presidential + Senate |

---

## Data Sources

All data comes from the **Federal Election Commission (FEC) bulk data portal**:

**Source URL:** https://www.fec.gov/data/browse-data/?tab=bulk-data

### Required FEC Files (by cycle)

For each election cycle (e.g., 2015-2016 for the "16" cycle), download these files:

| File Type | FEC Name | Purpose | Our Usage |
|-----------|----------|---------|-----------|
| **Candidate Master** | `cn##.zip` | Candidate information, election year, office | Defines candidate universe, filters by office and year |
| **Committee Master** | `cm##.zip` | Committee information, types | Identifies PAC types (C=corporate, N=nonconnected) and Super PACs (O=IE-only) |
| **Candidate-Committee Linkages** | `ccl##.zip` | Links committees to candidates | Maps individual contributions (committee → candidate) |
| **Individual Contributions** | `indiv##.zip` | Itemized individual donations | Individual support category |
| **Committee Contributions & IEs** | `pas2##.zip` | PAC-to-candidate contributions and independent expenditures | PAC support and Super PAC IE support |

**Example for 2015-2016:**
- `cn16.zip` → Candidate master
- `cm16.zip` → Committee master
- `ccl16.zip` → Candidate-committee linkages
- `indiv16.zip` (also called `itcont16.zip`) → Individual contributions
- `pas216.zip` (also called `itpas216.zip`) → All other contributions and IEs

### File Structure After Download

```
FEC_Data/
└── 2015_2016/
    ├── cn16/
    │   └── cn.txt
    ├── cm16/
    │   └── cm.txt
    ├── ccl16/
    │   └── ccl.txt
    ├── indiv16/
    │   └── itcont.txt
    └── pas216/
        └── itpas2.txt
```

**Note:** The FEC uses `##` to denote the 2-digit cycle year (e.g., `16` for 2015-2016).

---

## Installation and Setup

### Prerequisites

**Software:**
- Python 3.8 or higher
- pip (Python package manager)

**Python packages:**
```bash
pip install pandas
```

**Disk space:**
- ~10 GB per cycle for raw FEC files (compressed)
- ~20 GB per cycle for unzipped files
- ~1 MB for outputs

---

### Setup Steps

#### 1. Clone or Download Pipeline

```bash
git clone https://github.com/shriyanyamali/fec-cn-support-etl.git
cd fec-cn-support-etl
```

---

#### 2. Create Directory Structure

```bash
mkdir -p FEC_Data/2015_2016/{cn16,cm16,ccl16,indiv16,pas216,outputs,Code}
```

For other cycles, adjust the year and cycle number (e.g., `2019_2020` and `20`).

---

#### 3. Download FEC Data

Visit: https://www.fec.gov/data/browse-data/?tab=bulk-data

**For 2015-2016 cycle:**

1. Download `cn16.zip` → Extract to `FEC_Data/2015_2016/cn16/`
2. Download `cm16.zip` → Extract to `FEC_Data/2015_2016/cm16/`
3. Download `ccl16.zip` → Extract to `FEC_Data/2015_2016/ccl16/`
4. Download `indiv16.zip` → Extract to `FEC_Data/2015_2016/indiv16/`
   - May be named `itcont16.zip`
5. Download `pas216.zip` → Extract to `FEC_Data/2015_2016/pas216/`
   - May be named `itpas216.zip`

**File naming:** The extracted `.txt` files are usually named after the file type (e.g., `cn.txt`, `cm.txt`). The pipeline auto-detects the largest `.txt` or `.dat` file in each directory.

---

#### 4. Place Code Files

Copy all `.py` files to `FEC_Data/Code/`:

```
FEC_Data/
└── Code/
    ├── config.py
    ├── superpac_ie_support.py
    ├── individual_support.py
    ├── pac_support_corp_union.py
    ├── merge_support.py
    ├── run_all.py
    ├── combine_csv.py
    └── validate_outputs.py
```

---

#### 5. Configure Pipeline

Edit `FEC_Data/Code/config.py`:

```python
BASE_DIR = Path(r"C:\Users\YourName\FEC_Data")  # Change this path
CYCLE_LABEL = "16"  # Two-digit cycle year
```

The pipeline will automatically:
- Set `TARGET_ELECTION_YR = 2016`
- Look for input folders: `cn16`, `cm16`, `ccl16`, `indiv16`, `pas216`
- Create output folders: `senate`, `presidential`, `total`

---

## How to Use

### Basic Usage

#### Run Complete Pipeline

```bash
cd FEC_Data/Code
python run_all.py
```

**What it does:**
1. Processes Senate candidates → `outputs/senate/`
2. Processes Presidential candidates → `outputs/presidential/`
3. Processes combined dataset → `outputs/total/`

**Expected runtime:** 10-30 minutes depending on hardware and cycle size

**Expected output:**
```
████████████████████████████████████████
█ PIPELINE: SENATE
████████████████████████████████████████
... [processing messages]
✓ SENATE pipeline completed successfully

████████████████████████████████████████
█ PIPELINE: PRESIDENTIAL  
████████████████████████████████████████
... [processing messages]
✓ PRESIDENTIAL pipeline completed successfully

████████████████████████████████████████
█ PIPELINE: TOTAL (SENATE + PRESIDENTIAL)
████████████████████████████████████████
... [processing messages]
✓ TOTAL pipeline completed successfully

█ ALL PIPELINES COMPLETED SUCCESSFULLY
```

---

#### Validate Outputs

```bash
python validate_outputs.py
```

**What it checks:**
- All 18 files exist
- No duplicates
- Office filters correct
- Totals calculated correctly
- Senate + Presidential = Total

**Expected output:**
```
✅ ALL VALIDATIONS PASSED
```

See validation section below for details.

---

#### Combine Multiple Cycles

If you have processed multiple cycles (e.g., 2012, 2014, 2016), combine them:

```bash
# Move final files to a central location first
mkdir FEC_Data/final_output_files
cp 2015_2016/outputs/senate/senate_final_support_table_16.csv final_output_files/
cp 2013_2014/outputs/senate/senate_final_support_table_14.csv final_output_files/
# ... etc.

# Combine all files
python combine_csv.py --input-dir final_output_files --output combined_all_cycles.csv --recursive
```

---

## What This Pipeline Does

### Input → Processing → Output

```
FEC Bulk Files (5 files)
         ↓
    Pipeline Processing
    - Filter candidates (Senate & Presidential only)
    - Filter to target election year
    - Classify contributions by type
    - Remove duplicates
    - Aggregate to candidate level
         ↓
    18 Output Files
    - 6 for Senate
    - 6 for Presidential  
    - 6 for Total (combined)
```

### Processing Steps

1. **Load Candidate Universe**
   - Read `cn.txt` (candidate master)
   - Filter to Senate (`CAND_OFFICE = 'S'`) and Presidential (`CAND_OFFICE = 'P'`)
   - Filter to target election year (e.g., `CAND_ELECTION_YR = 2016`)
   - Remove duplicate candidate records (keep best administrative record)

2. **Classify Committees**
   - Read `cm.txt` (committee master)
   - Identify Super PACs: `CMTE_TP = 'O'` (IE-only committees)
   - Identify regular PACs: `CMTE_TP IN ('Q', 'N')` (qualified/nonqualified)
   - Within PACs, classify by `ORG_TP`:
     - `'C'` = Corporate-connected
     - `''` (blank) = Nonconnected

3. **Process Individual Contributions**
   - Read `itcont.txt` (individual contributions)
   - Filter: `TRANSACTION_TP = '15'` AND `ENTITY_TP = 'IND'`
   - Map committee → candidate using `ccl.txt`
   - Sum by candidate

4. **Process PAC Contributions**
   - Read `itpas2.txt` (PAC contributions and IEs)
   - Exclude independent expenditures (`TRANSACTION_TP NOT IN ('24E', '24A')`)
   - Filter to PAC committees only
   - Split by corporate (`ORG_TP = 'C'`) vs nonconnected (`ORG_TP = ''`)
   - Sum by candidate

5. **Process Super PAC Independent Expenditures**
   - Read `itpas2.txt` again
   - Filter: `TRANSACTION_TP = '24E'` AND committee in Super PAC list
   - Sum by candidate

6. **Merge and Calculate Totals**
   - Join all support categories on candidate ID
   - Calculate `TOTAL_SUPPORT` = sum of all categories
   - Create flags and split into final output files

---

## Output Files Structure

### Directory Organization

```
outputs/
├── senate/
│   ├── senate_superpac_ie_support_##.csv
│   ├── senate_individual_support_##.csv
│   ├── senate_pac_support_corp_nonconnected_##.csv
│   ├── senate_final_support_table_##.csv
│   ├── senate_candidates_no_support_##.csv
│   └── senate_candidates_all_with_flag_##.csv
│
├── presidential/
│   ├── presidential_superpac_ie_support_##.csv
│   ├── presidential_individual_support_##.csv
│   ├── presidential_pac_support_corp_nonconnected_##.csv
│   ├── presidential_final_support_table_##.csv
│   ├── presidential_candidates_no_support_##.csv
│   └── presidential_candidates_all_with_flag_##.csv
│
└── total/
    ├── total_superpac_ie_support_##.csv
    ├── total_individual_support_##.csv
    ├── total_pac_support_corp_nonconnected_##.csv
    ├── total_final_support_table_##.csv
    ├── total_candidates_no_support_##.csv
    └── total_candidates_all_with_flag_##.csv
```

**Total: 18 output files** (6 per office + total type)

---

### File Descriptions

#### 1. `{prefix}_superpac_ie_support_{cycle}.csv`

**Purpose:** Intermediate file showing Super PAC IE support per candidate

**Columns:**
- `CAND_ID`: FEC candidate ID
- `SUPERPAC_IE_SUPPORT`: Total Super PAC independent expenditures
- `CAND_NAME`: Candidate name
- `CAND_PTY_AFFILIATION`: Party (DEM, REP, etc.)
- `CAND_ELECTION_YR`: Election year
- `CAND_OFFICE_ST`: State (for Senate) or blank (for Presidential)
- `CAND_OFFICE`: Office (S or P)
- Other candidate fields from `cn.txt`

---

#### 2. `{prefix}_individual_support_{cycle}.csv`

**Purpose:** Intermediate file showing individual contribution support per candidate

**Columns:**
- `CAND_ID`: FEC candidate ID
- `INDIVIDUAL_SUPPORT`: Total individual contributions
- Candidate info fields (name, party, state, etc.)

---

#### 3. `{prefix}_pac_support_corp_nonconnected_{cycle}.csv`

**Purpose:** Intermediate file showing PAC support per candidate (split by type)

**Columns:**
- `CAND_ID`: FEC candidate ID
- `CORP_PAC_SUPPORT`: Total corporate PAC contributions
- `NONCONNECTED_PAC_SUPPORT`: Total nonconnected PAC contributions
- Candidate info fields

---

#### 4. `{prefix}_final_support_table_{cycle}.csv` ⭐ **PRIMARY OUTPUT**

**Purpose:** **Main analysis file** - Complete support data for candidates who received money

**Columns:**
- `CAND_ID`: FEC candidate ID
- `CAND_ELECTION_YR`: Election year (e.g., 2016)
- `CAND_NAME`: Candidate name
- `CAND_PTY_AFFILIATION`: Party affiliation
- `CAND_OFFICE`: Office sought (S or P)
- `CAND_OFFICE_ST`: State (for Senate) or blank (Presidential)
- `INDIVIDUAL_SUPPORT`: Individual contributions total
- `CORP_PAC_SUPPORT`: Corporate PAC contributions total
- `NONCONNECTED_PAC_SUPPORT`: Nonconnected PAC contributions total
- `SUPERPAC_IE_SUPPORT`: Super PAC IE total
- `TOTAL_SUPPORT`: Sum of all support categories
- `HAS_MONEY`: 1 (always 1 in this file)

**Filtering:**
- Only candidates with `TOTAL_SUPPORT > 0`
- Sorted by state and total support (descending)

**Example rows (Senate 2016):**
```
CAND_ID      CAND_NAME              CAND_OFFICE  CAND_OFFICE_ST  TOTAL_SUPPORT  INDIVIDUAL_SUPPORT  CORP_PAC_SUPPORT
S0FL00338    RUBIO, MARCO           S            FL              24,785,695     18,234,521          2,456,789
S4PA00121    TOOMEY, PATRICK JOSEPH S            PA              24,075,292     16,890,443          3,112,654
```

---

#### 5. `{prefix}_candidates_no_support_{cycle}.csv`

**Purpose:** Candidates who ran but received zero financial support

**Columns:**
- Same as `final_support_table`
- All support columns = 0
- `HAS_MONEY` = 0

**Who uses this:**
- Researchers studying non-viable candidates
- Completeness checking
- Understanding full candidate field

**Filtering:**
- Only candidates with `TOTAL_SUPPORT = 0`

**Typical row count:**
- Senate: ~20-50 (fringe/late withdrawal candidates)
- Presidential: ~5-15 (fringe candidates)

**Why these candidates exist:**
- Filed with FEC but never fundraised
- Withdrew before raising money
- Very late entry candidates
- Fringe/protest candidates

---

#### 6. `{prefix}_candidates_all_with_flag_{cycle}.csv`

**Purpose:** Complete candidate universe (funded + unfunded)

**Columns:**
- Same as `final_support_table`
- `HAS_MONEY`: 1 if funded, 0 if unfunded

**Who uses this:**
- Researchers needing complete candidate counts
- Studies of candidate entry/viability
- Denominator for "% of candidates who raised money"

**Filtering:**
- All candidates from target election year and office

**Typical row count:**
- Senate: ~180-220 total candidates
- Presidential: ~30-50 total candidates

**Relationship:**
```
candidates_all = final_support_table + candidates_no_support
```