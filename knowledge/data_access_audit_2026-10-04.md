# External-data access check — 2026-10-04

## Purpose

Check whether a free official point-cloud source can support the preregistered H31-B raw-return hypothesis, and distinguish source-page/catalogue evidence from a downloaded and inspected binary. This work did not access DrivenData, its leaderboard, its data endpoint, or a submission endpoint.

## Official records reviewed

1. [GDR 1501 — GeoDAWN West Central Nevada EarthMRI Data, DOI 10.15121/1992093](https://gdr.openei.org/submissions/1501). The USGS-authored release page identifies OPR and LiDAR point-cloud data, a coverage-map PDF, and work-unit 1–6 USGS LAS/LAZ and OPR directory links. The page displays CC-BY 4.0.
2. [USGS 3DEP Products & Services](https://www.usgs.gov/3d-elevation-program/about-3dep-products-services). USGS says 3DEP products are free and without use restrictions, and describes lidar point clouds and OPR DEMs as source products. The GDR page's CC-BY 4.0 display and USGS's free/no-use-restriction wording are not identical; attribute conservatively and do not infer a different license for third-party derivatives.
3. [TNM Access API documentation](https://tnmaccess.nationalmap.gov/api/v1/docs) and the official `/products` endpoint.

## TNM Access API observations

- Dataset catalogue lists **Lidar Point Cloud (LPC)**, format LAS/LAZ.
- Targeted query: [`LPC` products in −118.0, 39.0 to −117.9, 39.1](https://tnmaccess.nationalmap.gov/api/v1/products?datasets=Lidar%20Point%20Cloud%20%28LPC%29&bbox=-118.0%2C39.0%2C-117.9%2C39.1&max=5). The API response reported `total=96` and included `USGS_LPC_NV_Southern_D23_11SMD150210.laz`:
  - sourceId `6848df6cd4be02423f6ab9db`;
  - format LAZ; listed size 1,300,744 bytes;
  - reported extent `[-117.9718300924, -117.9706228616] × [39.0411991411, 39.0430308974]`;
  - publication date 2025-06-07; last updated 2025-06-10;
  - official download URL: [exact LAZ product](https://rockyweb.usgs.gov/vdelivery/Datasets/Staged/Elevation/LPC/Projects/NV_Southern_D23/NV_Southern_1_D23/LAZ/USGS_LPC_NV_Southern_D23_11SMD150210.laz);
  - metadata URL from the API: [USGS XML metadata record](https://thor-f5.er.usgs.gov/ngtoc/metadata/waf/elevation/lidar_point_cloud/laz/NV_Southern_1_D23/USGS_LPC_NV_Southern_D23_11SMD150210.xml).
- A local check transformed a 7×7 grid of sample coordinates over the reported product bbox to the owner-mirror sample-submission CRS/grid. All 49/49 sample points landed on finite template-footprint cells. The bbox is therefore inside the mirrored footprint at these checked locations; this is not an exact full-geometry overlay and does not establish coverage of the whole challenge region.
- A targeted 1-meter DEM query for the same central 0.1° box returned eight records, including `NV_Southern_D23` and `NV_WestCentral_EarthMRI_2020_D20` tiles. A broad 1-meter DEM query over the rectangular geographic envelope used for the whole competition returned `total=1856`; its pages were not fully enumerated and no exact study-footprint intersection count was computed. Neither count is reported as full-grid coverage.
- A broad LPC query returned a very large catalog count and initial records from projects near the western edge; that result is not used to infer exact whole-footprint coverage. The targeted sub-area result above is the limited positive coverage evidence.

## Retrieval and attributes

The exact listed LAZ download URL was requested from the sandbox with `curl`; TLS terminated with `SSL_ERROR_SYSCALL` before any bytes were received. The exact USGS XML metadata URL returned a temporary maintenance page through the web reader. **No LAZ binary was downloaded, hashed, or parsed. No point-header fields, intensity distributions, return-number/count distributions, classification schema, CRS, point density, or acquisition quality were inspected.** The API description says the product is LAZ point-cloud data, but generic collection prose is not a substitute for sample-tile attribute verification.

The official source is real and publicly described, and at least one product record has an extent inside the challenge's owner-mirror footprint. H31-B is nevertheless **not yet holdout-testable** because the actual binary/attributes and full footprint coverage remain unverified. Do not report a geologic feature result or add an LAZ-derived model column until the data are retrieved, attribution/licensing recorded, per-tile hashes captured, point fields checked, and coverage assessed across the validation folds.

## Result for this sprint

- Free official source identified and catalog query executed.
- One in-footprint LAZ product record identified; direct retrieval failed.
- Full-coverage/attribute test blocked; no raw point-cloud data included in Git or claimed as downloaded.
- H31-A remains the only currently executable preregistered candidate because it uses existing hash-pinned owner-mirror input bands. Its evidence, if run, remains conditional on that mirror and is not organizer-authenticated.
