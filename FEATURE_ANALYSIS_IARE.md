# IARE Shapefile Analysis

## Original Request
Analyze the structure and columns of the IARE (Indigenous Areas) shapefile at `/home/asaabey/projects/tkc/tkc-locality-geocoding-cli-app/data/asgs/IARE_2021_AUST_GDA2020_SHP/IARE_2021_AUST_GDA2020.shp`

## Analysis Results

### 1. Basic Structure
- **Total features**: 431 IARE areas across Australia
- **Geometry type**: Polygon
- **Coordinate Reference System**: EPSG:7844 (GDA2020)
- **File format**: Shapefile with 13 columns

### 2. Column Structure
| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| `IAR_CODE21` | object | IARE Code (6-digit identifier) |
| `IAR_NAME21` | object | IARE Name |
| `IRE_CODE21` | object | Indigenous Region Code (3-digit parent) |
| `IRE_NAME21` | object | Indigenous Region Name |
| `STE_CODE21` | object | State/Territory Code |
| `STE_NAME21` | object | State/Territory Name |
| `AUS_CODE21` | object | Australia Code (AUS/ZZZ) |
| `AUS_NAME21` | object | Australia Name |
| `AREASQKM21` | float64 | Area in square kilometers |
| `LOCI_URI21` | object | Linked Data URI |
| `SHAPE_Leng` | float64 | Shape length (perimeter) |
| `SHAPE_Area` | float64 | Shape area |
| `geometry` | geometry | Polygon geometry |

### 3. Sample Data
```
IAR_CODE21 | IAR_NAME21 | IRE_CODE21 | IRE_NAME21 | STE_NAME21
101001     | Bogan      | 101        | Dubbo      | New South Wales
101002     | Dubbo      | 101        | Dubbo      | New South Wales
101003     | Gilgandra  | 101        | Dubbo      | New South Wales
```

### 4. Northern Territory Focus
**NT contains 64 IARE areas across 9 Indigenous Regions:**

| Indigenous Region | Code | IARE Areas |
|-------------------|------|------------|
| Darwin | 703 | 14 areas |
| Jabiru - Tiwi | 704 | 6 areas |
| Katherine | 705 | 9 areas |
| Nhulunbuy | 706 | 8 areas |
| Tennant Creek | 707 | 6 areas |
| Alice Springs | 708 | 2 areas |
| Apatula | 709 | 17 areas |
| No usual address (NT) | 794 | 1 area |
| Migratory - Offshore - Shipping (NT) | 797 | 1 area |

**Notable NT IARE Areas:**
- Largest: Barkly (302,710.8 sq km)
- Alice Springs split into: Town Camps (7.0 sq km) and Alice exc. Town Camps (320.7 sq km)
- Urban areas: Darwin suburbs, Palmerston, Katherine Town, Tennant Creek Town
- Remote communities: Yuendumu, Papunya, Hermannsburg, Kalkarindji, etc.

### 5. Hierarchical Structure
```
Australia (AUS_CODE21) 
  └── State/Territory (STE_CODE21)
      └── Indigenous Region (IRE_CODE21) 
          └── Indigenous Area (IAR_CODE21)
```

### 6. Key Fields for Geocoding Integration

**Essential columns for classification:**
1. `IAR_CODE21` - Primary IARE identifier
2. `IAR_NAME21` - Human-readable IARE name
3. `IRE_CODE21` - Parent Indigenous Region code
4. `IRE_NAME21` - Parent Indigenous Region name
5. `STE_CODE21` - State/Territory code for filtering
6. `AREASQKM21` - Area size for validation

**Recommended integration approach:**
- Use spatial join with Point-in-Polygon to classify CHC locations
- Add IARE columns to existing classification pipeline alongside SA1-SA4
- Filter to NT areas (`STE_CODE21 = '3'`) for performance
- Include both code and name fields for reporting

### 7. Data Quality
- **Missing geometries**: 19 features (4.4%) have null geometry
- **Complete coverage**: No missing data in key identifier columns
- **Spatial extent**: Covers entire Australian continent
- **NT bounding box**: [129.0, -26.0, 138.0, -10.9] (longitude, latitude)

### 8. Integration with Current System

The IARE layer can be integrated into the existing `classify.py` module by:
1. Adding IARE path to `settings.py` configuration
2. Extending `classify_points()` function to include IARE spatial join
3. Adding IARE columns to the result DataFrame structure
4. Following the same load_layer pattern used for SA1-SA4 boundaries

**Recommended new columns to add:**
- `IARE_CODE` (from `IAR_CODE21`)
- `IARE_NAME` (from `IAR_NAME21`) 
- `IREG_CODE` (from `IRE_CODE21`)
- `IREG_NAME` (from `IRE_NAME21`)

This would provide Indigenous Area classification alongside the existing ABS Statistical Area hierarchy for comprehensive geocoding coverage in the Northern Territory.