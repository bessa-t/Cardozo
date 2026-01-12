# DXF Input Specifications for Structural Analysis

## 1. Overview
This document outlines the geometric and layering standards required for DXF files to be successfully processed by the Biaxial Bending Diagram analysis engine. Adherence to these specifications is mandatory to ensure correct material mapping and geometric discretization.

## 2. General Requirements
* **File Format:** DXF (ASCII format recommended, e.g., AutoCAD 2010/2013 DXF).
* **Units:** The coordinates in the DXF file must be consistent. The software interprets unitless coordinates directly (e.g., if drawn in centimeters, results will be in centimeters).
* **Clean Geometry:** The file should be free of unused blocks, construction lines (xlines), or dimensions in the computation layers.

## 3. Layer Specifications

### 3.1. Concrete Cross-Section
Defines the boundary of the structural concrete element.

| Attribute | Requirement |
| :--- | :--- |
| **Layer Name** | `concrete` |
| **Entity Type** | `LWPOLYLINE` (Polylines) |
| **Topology** | **Closed Loop.** The start point and end point must coincide. |
| **Constraints** | Must not be self-intersecting. Only one outer boundary is allowed per analysis. |

> **Note:** Do not use "Lines" or "Arcs" exploded. The geometry must be joined into a single Polyline entity.

### 3.2. Steel Reinforcement
Defines the longitudinal reinforcement bars.

| Attribute | Requirement |
| :--- | :--- |
| **Layer Name** | `steel bars` |
| **Entity Type** | `CIRCLE` |
| **Topology** | Closed circular geometry. |
| **Constraints** | Blocks or points are **not** supported. Bars must be drawn as actual circles representing the bar diameter. |

## 4. Common Errors to Avoid
1.  **Open Polylines:** Even if the gap is microscopic, `ezdxf` may fail to calculate the area. Ensure the "Closed" property is set to "Yes" in the CAD properties.
2.  **Wrong Layer Names:** Layer names are case-sensitive in some parsers. Ensure strictly lower-case naming as specified: `concrete` and `steel bars`.
3.  **Exploded Geometries:** A square drawn as 4 separate lines will not be recognized as a concrete section. It must be a Polyline.