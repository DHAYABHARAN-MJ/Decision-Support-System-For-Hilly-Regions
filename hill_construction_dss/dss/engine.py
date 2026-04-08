# dss/engine.py  — Hill Construction DSS v3
# New: SPT N-value → bearing capacity calculator
# New: Real numeric inputs for elevation (metres), moisture (%), building load (kN/m2)
# Source: IS Codes (BIS), NBC 2016, NDMA/GSI Guidelines


class DSSEngine:

    # ── SPT N-VALUE → BEARING CAPACITY ──────────────────────
    # Source: IS 6403, IS 1888
    @staticmethod
    def spt_to_bearing(n_value: float, depth_m: float = 1.5, soil_type: str = "sandy") -> dict:
        """Convert SPT N-value at given depth to safe bearing capacity (kN/m2)."""
        s = soil_type.lower()
        if s == "rock":
            # Rock: use RQD correlation
            if n_value >= 50:
                bc = 440 + (n_value - 50) * 8
            else:
                bc = n_value * 8.8
        elif s == "clay":
            # Undrained shear strength Cu = (N/15) * 100 kPa approx
            # Net safe bearing capacity = (5.14 * Cu) / FOS
            cu = (n_value / 15.0) * 100
            bc = (5.14 * cu) / 3.0
        else:
            # Sandy soil: Terzaghi correlation
            # qa = N * 10 kPa for shallow depth, adjusted for depth
            bc = n_value * 10 * (1 + 0.2 * min(depth_m, 3.0))

        bc = max(10, round(bc))
        return {
            "n_value": n_value,
            "depth_m": depth_m,
            "soil_type": soil_type,
            "bearing_capacity_kNm2": bc,
            "formula_used": f"IS 6403 / IS 1888 — {soil_type} soil at {depth_m}m depth",
            "note": f"Calculated safe bearing capacity: {bc} kN/m2. Use this value in the bearing capacity field."
        }

    # ── 1. SLOPE ANGLE ──────────────────────────────────────
    @staticmethod
    def score_slope(slope: float) -> dict:
        if slope <= 15:
            return dict(score=0, label="Suitable", status="ok",
                action="No slope treatment required.",
                remedial="Maintain natural ground cover. Provide toe drains at plot boundary per IS 4111.",
                source="NBC 2016, IS 14458")
        elif slope <= 30:
            return dict(score=-8, label="Caution — slope analysis needed", status="warn",
                action="Slope stability analysis mandatory before construction.",
                remedial="Carry out slope stability analysis (FOS >= 1.5) per IS 14680. Construct stone pitching on exposed slope face. Provide stepped contour bunds at every 2 m vertical interval. Install geotextile reinforcement on loose surface soil.",
                source="IS 14680, IS 14458")
        elif slope <= 45:
            return dict(score=-20, label="Steep — major earthworks needed", status="warn",
                action="Retaining wall and slope cutting compulsory before any foundation work.",
                remedial="Construct RCC retaining wall with weep holes at 3 m spacing per IS 14458. Carry out controlled slope cutting with 1:1 cut slope. Apply shotcrete on exposed cut face. Provide subsurface drainage behind retaining wall.",
                source="IS 14458, NBC hillside guidelines")
        else:
            return dict(score=-30, label="Not suitable — extreme slope", status="danger",
                action="Construction must not proceed on slopes above 45 degrees without major geotechnical intervention.",
                remedial="Site requires full geotechnical investigation and slope stabilisation. Options: soil nailing (IS 14458), rock anchors, mass retaining structures. Obtain licensed geotechnical engineer certification. Consider alternate site.",
                source="NBC hillside guidelines, IS 14458")

    # ── 2. ELEVATION — NOW REAL METRES ──────────────────────
    # Source: IS 875 Part 3, NBC 2016 Part 6
    # Real input: metres above mean sea level (AMSL)
    @staticmethod
    def score_elevation(elevation_m: float) -> dict:
        if elevation_m < 600:
            return dict(score=0, label=f"Low altitude ({elevation_m}m AMSL) — suitable", status="ok",
                action="Standard design applies. No special altitude provisions required.",
                remedial="No special elevation measures. Standard DPC at plinth level is sufficient.",
                source="NBC 2016 Part 6")
        elif elevation_m < 1500:
            return dict(score=-5, label=f"Medium altitude ({elevation_m}m AMSL) — wind load check", status="warn",
                action="Wind load analysis required per IS 875 Part 3.",
                remedial=f"Design for increased wind pressure at {elevation_m}m altitude per IS 875 Part 3 Basic Wind Speed map. Provide wind bracing in roof truss. Anchor roof sheets with J-bolts or cleat angles. Reduce window-to-wall ratio to minimise wind pressure.",
                source="IS 875 Part 3")
        else:
            return dict(score=-10, label=f"High altitude ({elevation_m}m AMSL) — enhanced design", status="warn",
                action="Enhanced wind load, snow load, and access constraints apply.",
                remedial=f"At {elevation_m}m AMSL: Apply enhanced wind and snow load per IS 875 Parts 3 and 4. Use frost-resistant OPC 43 grade cement to prevent freeze-thaw. Insulate water pipes and foundation walls. Provide access road minimum 3.5 m width. Design steep-pitch roof (minimum 30 degree pitch) for snow shedding.",
                source="IS 875 Part 3 and 4, NBC 2016")

    # ── 3. LANDSLIDE RISK ZONE ──────────────────────────────
    @staticmethod
    def score_landslide(landslide: str) -> dict:
        l = landslide.lower()
        if l == "low":
            return dict(score=0, label="Suitable", status="ok",
                action="Standard construction practice is acceptable.",
                remedial="No landslide mitigation required. Maintain vegetation cover on upslope area.",
                source="NDMA Hazard Zonation")
        elif l == "medium":
            return dict(score=-10, label="Caution — mitigation required", status="warn",
                action="Landslide mitigation measures mandatory before construction.",
                remedial="Install subsurface drainage curtain on uphill side. Construct debris barrier wall at slope base per NDMA guidelines. Avoid construction within 5 m of active slope crest. Plant deep-rooted vetiver grass on exposed slopes. Monthly slope monitoring during monsoon.",
                source="IS 14458, NDMA Guidelines")
        else:
            return dict(score=-25, label="High risk — GIR mandatory", status="danger",
                action="Full Geotechnical Investigation Report (GIR) and slope stabilisation certificate required.",
                remedial="Commission full GIR from licensed geotechnical engineer. Install rock bolts or soil nails per IS 14458. Construct RC debris retention wall. Install inclinometers for slope movement monitoring. Obtain NDMA / GSI landslide clearance certificate before any work.",
                source="NDMA, GSI Landslide Atlas, IS 14458")

    # ── 4. SOIL TYPE ────────────────────────────────────────
    @staticmethod
    def score_soil_type(soil_type: str) -> dict:
        s = soil_type.lower()
        if s == "rock":
            return dict(score=+5, label="Excellent — rock foundation", status="ok",
                action="Ideal foundation base. All foundation types suitable.",
                remedial="No soil treatment. Clean rock surface before placing concrete. Provide step-cut key into rock for foundation grip.",
                source="IS 1498, IS 6403")
        elif s == "clay":
            return dict(score=-5, label="Moderate — swelling/shrinkage risk", status="warn",
                action="Expansive clay treatment needed before foundation work.",
                remedial="Replace top 300-500 mm of expansive clay with compacted granular fill (IS 1498). Use sand-cement mix 1:8 as sub-grade treatment. Install moisture barriers. Use under-reamed pile foundation (IS 2911 Part 3) for expansive clay. Monitor moisture quarterly for 2 years.",
                source="IS 1498, IS 2911 Part 3")
        else:
            return dict(score=-10, label="Weak — liquefaction risk", status="danger",
                action="Sandy soil requires compaction and pile foundation — liquefaction risk during earthquake.",
                remedial="Carry out vibro-compaction to densify sandy soil (IS 1498). Provide pile foundation to firm strata. Install stone columns or cement grouting per IS 9451. Avoid shallow foundation entirely. Check liquefaction potential per IS 1893 Annex F for seismic zones 3 and above.",
                source="IS 1498, IS 1893, IS 9451")

    # ── 5. BEARING CAPACITY — REAL kN/m² ────────────────────
    @staticmethod
    def score_bearing_capacity(bearing: float) -> dict:
        if bearing < 50:
            return dict(score=-25, label=f"Very weak ({bearing} kN/m²) — soil improvement mandatory", status="danger",
                action=f"Bearing capacity {bearing} kN/m² is critically low. Cannot be safely founded without improvement.",
                remedial=f"Mandatory soil improvement for {bearing} kN/m²: (1) Cement stabilisation — mix 5-8% OPC cement into top 500 mm of soil and compact per IS 4332. (2) Stone column installation to transfer load to deeper firm layer per IS 9451. (3) Pile foundation to bedrock per IS 2911. Retest after treatment — must reach minimum 100 kN/m² before proceeding.",
                source="IS 6403, IS 1888, IS 9451")
        elif bearing < 100:
            return dict(score=-12, label=f"Weak ({bearing} kN/m²) — raft or pile required", status="warn",
                action=f"Bearing capacity {bearing} kN/m² is insufficient for isolated footing. Use raft or pile foundation.",
                remedial=f"For {bearing} kN/m² bearing capacity: Use raft foundation (IS 2950) to spread load, or short bored piles (IS 2911) to firmer layer. Provide M10 lean concrete blinding 75 mm thick below raft. Carry out consolidation settlement analysis per IS 8009.",
                source="IS 6403, IS 2950, IS 2911")
        elif bearing < 200:
            return dict(score=0, label=f"Acceptable ({bearing} kN/m²) — standard foundation", status="ok",
                action=f"Bearing capacity {bearing} kN/m² is adequate for standard residential construction.",
                remedial="Proceed with standard isolated footing per IS 1904. Ensure minimum 1.5 m foundation depth from natural ground level.",
                source="IS 6403")
        elif bearing < 300:
            return dict(score=+3, label=f"Good ({bearing} kN/m²) — wide options", status="ok",
                action=f"Good bearing capacity {bearing} kN/m². Wide range of foundation options available.",
                remedial="All standard foundation types applicable. No special treatment required.",
                source="IS 6403")
        else:
            return dict(score=+5, label=f"Excellent ({bearing} kN/m²) — strong ground", status="ok",
                action=f"Excellent bearing capacity {bearing} kN/m². All foundation types are suitable.",
                remedial="Strong ground condition. Direct foundation on natural ground acceptable. Verify with SPT N-value confirmation test.",
                source="IS 6403, IS 1888")

    # ── 6. SOIL MOISTURE — NOW REAL % ───────────────────────
    # Source: IS 8009, IS 1904
    # Real input: soil moisture content as percentage (%)
    @staticmethod
    def score_moisture(moisture_pct: float) -> dict:
        if moisture_pct < 15:
            return dict(score=0, label=f"Low moisture ({moisture_pct}%) — suitable", status="ok",
                action="Soil moisture is within safe range. No moisture treatment required.",
                remedial="Standard DPC at plinth level is sufficient. No special moisture treatment needed.",
                source="IS 8009")
        elif moisture_pct < 30:
            return dict(score=-5, label=f"Moderate moisture ({moisture_pct}%) — drainage needed", status="warn",
                action=f"Moisture content {moisture_pct}% indicates seasonal variation risk. Improved drainage required.",
                remedial=f"At {moisture_pct}% moisture: Provide French drain or rubble-filled trench drain around foundation perimeter. Apply bituminous waterproofing coat on outer foundation surface. Lay 250 micron polythene sheet as vapour barrier below ground floor slab. Monitor seasonal moisture variation over one full year.",
                source="IS 8009, IS 1904")
        else:
            return dict(score=-15, label=f"High moisture ({moisture_pct}%) — major risk", status="danger",
                action=f"Soil moisture {moisture_pct}% critically reduces bearing capacity and triggers instability.",
                remedial=f"At {moisture_pct}% moisture content: Install deep subsurface drainage — perforated HDPE pipe drains at 1.5 m depth connected to outlet drain per IS 4111. Carry out full soil consolidation analysis per IS 8009. Apply cement-grouting or lime stabilisation. Delay foundation construction until post-monsoon. Provide minimum 500 mm granular sub-base under all foundation elements.",
                source="IS 8009, IS 1904, IS 4111")

    # ── 7. NUMBER OF FLOORS ─────────────────────────────────
    @staticmethod
    def score_floors(floors: int) -> dict:
        if floors <= 2:
            return dict(score=0, label="Suitable — low-rise", status="ok",
                action="Standard low-rise residential design applicable.",
                remedial="Ensure minimum lintel band and roof band per IS 4326 for seismic resistance.",
                source="NBC 2016 Part 6")
        elif floors <= 5:
            return dict(score=-5, label="Medium-rise — structural review needed", status="warn",
                action="Structural engineer design and review mandatory for 3-5 storey buildings.",
                remedial="Commission licensed structural engineer for RCC frame design per IS 456. Provide earthquake-resistant ductile detailing per IS 13920. Carry out wind load analysis per IS 875 Part 3.",
                source="NBC 2016 Part 6, IS 13920")
        elif floors <= 10:
            return dict(score=-12, label="High-rise — deep foundation mandatory", status="warn",
                action="Pile foundation and full structural design with seismic analysis mandatory.",
                remedial="Pile foundation (IS 2911) is mandatory for 6-10 floors on hill terrain. Carry out dynamic seismic analysis per IS 1893. Design shear walls or cross bracing for lateral load resistance. Obtain structural stability certificate.",
                source="IS 2911, IS 1893, NBC 2016")
        else:
            return dict(score=-20, label="Specialist design required", status="danger",
                action="Buildings above 10 floors on hill sites require specialist geotechnical and structural design.",
                remedial="Commission full geotechnical investigation (borehole to 30 m minimum). Design deep pile foundation with pile load testing per IS 2911. Time-history seismic analysis per IS 1893. Wind tunnel study recommended. Obtain NBC 2016 Part 7 special structure approval.",
                source="IS 2911, IS 1893, NBC 2016 Part 7")

    # ── 8. FOUNDATION TYPE ──────────────────────────────────
    @staticmethod
    def score_foundation(foundation: str) -> dict:
        f = foundation.lower()
        if f == "pile":
            return dict(score=+8, label="Excellent — pile foundation", status="ok",
                action="Best foundation for hill terrain. Transfers load to deep firm strata.",
                remedial="Design pile diameter and length per IS 2911 from soil boring data. Carry out initial pile load test at 1.5 times design load before mass piling. Provide pile cap minimum 300 mm thick.",
                source="IS 2911")
        elif f == "raft":
            return dict(score=+5, label="Good — raft foundation", status="ok",
                action="Suitable for uniform soil conditions. Distributes load evenly.",
                remedial="Design raft thickness minimum 300 mm with two-way reinforcement per IS 2950. Provide 75 mm lean concrete blinding below raft. Extend raft minimum 300 mm beyond outer wall face.",
                source="IS 2950")
        elif f == "stepped":
            return dict(score=+5, label="Suitable — stepped foundation", status="ok",
                action="Ideal for sloped sites. Each step adapts to natural contour.",
                remedial="Ensure each step height does not exceed 600 mm per IS 1904. Provide horizontal RCC tie beam connecting all steps. Compact fill between steps to 95% Proctor density.",
                source="IS 1904, NBC hillside guidelines")
        elif f == "isolated":
            return dict(score=0, label="Acceptable — isolated footing", status="ok",
                action="Suitable for flat sites with good bearing capacity only.",
                remedial="Ensure minimum 1.5 m depth from natural ground level per IS 1904. Only suitable for bearing capacity above 100 kN/m² on flat or gentle slopes (below 15°).",
                source="IS 1904")
        elif f == "combined":
            return dict(score=+2, label="Good — combined footing", status="ok",
                action="Combined footing distributes load from adjacent columns.",
                remedial="Design combined footing per IS 1904. Ensure uniform bearing pressure distribution. Use when column spacing is close or soil is moderately weak.",
                source="IS 1904")
        elif f == "under_reamed":
            return dict(score=+6, label="Excellent — under-reamed pile", status="ok",
                action="Specifically designed for expansive clay soils common in hill stations.",
                remedial="Under-reamed pile (IS 2911 Part 3) is ideal for expansive clay soils. Provides anchorage against uplift forces from soil swelling. Design bell diameter 2.5 to 3 times shaft diameter.",
                source="IS 2911 Part 3")
        else:
            return dict(score=-10, label="Inadequate — shallow foundation risky", status="danger",
                action="Shallow foundation is unsuitable for hill terrain. Must be upgraded immediately.",
                remedial="Immediately upgrade to pile, raft, or stepped foundation. Shallow foundation on slopes risks overturning, sliding, and bearing failure during heavy rain or seismic event. Redesign per IS 2911 or IS 2950 before any construction commences.",
                source="IS 1904, IS 2911")

    # ── 9. BUILDING LOAD — NOW REAL kN/m² ───────────────────
    # Source: NBC 2016 Part 6, IS 875 Part 2
    # Real input: total floor load in kN/m² (dead + live load)
    @staticmethod
    def score_building_load(load_kn: float) -> dict:
        if load_kn <= 5:
            return dict(score=+3, label=f"Light load ({load_kn} kN/m²) — low risk", status="ok",
                action="Low structural load suitable for most hill site conditions.",
                remedial="Use lightweight roofing material (Mangalore tile or metal sheet) to further reduce load. Avoid heavy granite or marble flooring on upper floors.",
                source="NBC 2016 Part 6, IS 875 Part 2")
        elif load_kn <= 10:
            return dict(score=0, label=f"Medium load ({load_kn} kN/m²) — standard design", status="ok",
                action="Standard structural design is appropriate.",
                remedial="Standard structural design per IS 456 is adequate. Verify column sizes and footing dimensions with structural engineer.",
                source="NBC 2016 Part 6")
        elif load_kn <= 20:
            return dict(score=-5, label=f"Moderate-heavy load ({load_kn} kN/m²) — check required", status="warn",
                action=f"Load of {load_kn} kN/m² requires detailed foundation and soil interaction check.",
                remedial=f"At {load_kn} kN/m²: Commission structural engineer to verify bearing pressure against safe bearing capacity. Consider raft foundation to distribute load. Avoid on sandy or weak clay soil without improvement.",
                source="NBC 2016, IS 875 Part 2")
        else:
            return dict(score=-10, label=f"Heavy load ({load_kn} kN/m²) — soil check mandatory", status="danger",
                action=f"Heavy structural load {load_kn} kN/m² on hill terrain significantly increases foundation and slope failure risk.",
                remedial=f"For heavy load {load_kn} kN/m²: Conduct detailed bearing capacity test and settlement analysis per IS 8009. Provide deep pile foundation per IS 2911. Reduce dead load by using hollow block masonry. Consider splitting into two smaller structures on terraced levels.",
                source="NBC 2016 Part 6, IS 1904, IS 875 Part 2")

    # ── 10. CONSTRUCTION MATERIAL ───────────────────────────
    @staticmethod
    def score_material(material: str) -> dict:
        m = material.lower()
        if m == "concrete":
            return dict(score=+5, label="Excellent — RCC construction", status="ok",
                action="Reinforced concrete is the most suitable material for hill station construction.",
                remedial="Use M20 minimum grade concrete per IS 456. Ensure minimum 40 mm cover for all reinforcement to resist moisture-induced corrosion in hill station environment.",
                source="IS 456, NBC 2016")
        elif m == "steel":
            return dict(score=+5, label="Good — steel structure", status="ok",
                action="Steel frame is flexible and seismic-resistant — suitable for hill sites.",
                remedial="Apply anti-corrosion treatment (hot-dip galvanising or epoxy paint) on all exposed structural steel members. Design connections for seismic loads per IS 800.",
                source="IS 800")
        else:
            return dict(score=-5, label="Weak — wood not recommended", status="warn",
                action="Timber construction is not suitable for high moisture or seismic conditions in hill stations.",
                remedial="Replace wood structural elements with RCC or steel frame. If traditional timber is mandatory for heritage reasons, treat all timber with preservative per IS 401 (CCA treatment). Avoid timber in seismic zones 3 and above.",
                source="IS 883, IS 401, NBC 2016")

    # ── 11. WALL TYPE ───────────────────────────────────────
    @staticmethod
    def score_wall_type(wall_type: str) -> dict:
        w = wall_type.lower()
        if w == "reinforced":
            return dict(score=+5, label="Excellent — reinforced walls", status="ok",
                action="Reinforced masonry or RCC walls provide best seismic and lateral load resistance.",
                remedial="Provide minimum 8 mm diameter vertical reinforcement at 450 mm spacing per IS 13920. Ensure horizontal bond beams at lintel and sill levels.",
                source="IS 456, IS 13920")
        elif w == "brick":
            return dict(score=0, label="Acceptable — brick masonry", status="ok",
                action="Brick masonry acceptable for low seismic zones with proper bands.",
                remedial="Provide seismic bands (lintel, sill, roof) per IS 4326. Use Class A bricks minimum 7.5 N/mm2 per IS 1077. Provide minimum 200 mm RCC columns at all corners.",
                source="IS 1905, IS 4326")
        else:
            return dict(score=-5, label="Weak — lightweight not suitable", status="warn",
                action="Lightweight walls lack lateral strength for hill terrain wind and seismic loads.",
                remedial="Replace lightweight wall panels with reinforced masonry or RCC walls at all external and structural wall positions. Use only as non-load-bearing internal partitions.",
                source="NBC 2016 Part 6, IS 4326")

    # ── 12. RETAINING WALL ──────────────────────────────────
    @staticmethod
    def score_retaining_wall(retaining: str, slope: float) -> dict:
        r = retaining.lower()
        if r == "yes":
            return dict(score=+5, label="Retaining wall present — slope protected", status="ok",
                action="Retaining wall stabilises the slope and protects the foundation.",
                remedial="Ensure retaining wall design complies with IS 14458. Provide weep holes at 3 m horizontal and 1.5 m vertical spacing. Inspect for cracks or bulging post-monsoon.",
                source="IS 14458")
        elif r == "no" and slope <= 15:
            return dict(score=0, label="No retaining wall needed", status="ok",
                action="Gentle slope — retaining wall not required.",
                remedial="Provide toe drain along lower boundary of plot to collect surface runoff.",
                source="IS 14458")
        else:
            return dict(score=-12, label="Retaining wall absent — slope failure risk", status="danger",
                action="Retaining wall is mandatory for slope above 15 degrees. Construction must not start without it.",
                remedial="Construct RCC cantilever retaining wall (height up to 6 m) or gravity retaining wall (up to 3 m) BEFORE any construction per IS 14458. Provide weep holes every 3 m. Backfill with granular material behind wall. Wall design certified by structural engineer. Wall must be fully cured before adjacent foundation excavation begins.",
                source="IS 14458, NBC hillside guidelines")

    # ── 13. DRAINAGE ────────────────────────────────────────
    @staticmethod
    def score_drainage(drainage: str) -> dict:
        d = drainage.lower()
        if d == "yes":
            return dict(score=+3, label="Drainage available — good", status="ok",
                action="Drainage system controls waterlogging and slope erosion.",
                remedial="Ensure drain capacity is adequate for 1-in-50-year storm rainfall. Clean drains before every monsoon. Inspect for blockages quarterly.",
                source="IS 4111, NBC 2016")
        else:
            return dict(score=-10, label="No drainage — serious risk", status="danger",
                action="Absence of drainage on a hill site causes waterlogging, soil erosion, and foundation failure.",
                remedial="Provide comprehensive drainage before construction: (1) Brick-lined surface drain around plot perimeter with minimum 1% gradient per IS 4111. (2) Perforated 100 mm dia HDPE pipe at 1.5 m depth connected to outfall. (3) Roof downpipes discharging away from foundation. (4) French drain on uphill side of retaining wall. Complete drainage system before foundation excavation begins.",
                source="IS 4111, IS 1904, NBC 2016")

    # ── 14. SEISMIC ZONE ────────────────────────────────────
    @staticmethod
    def score_seismic_zone(zone: int) -> dict:
        if zone in [1, 2]:
            return dict(score=0, label=f"Zone {zone} — low seismic risk", status="ok",
                action="Standard construction with basic earthquake-resistant features.",
                remedial="Provide minimum seismic bands (lintel, sill, roof) in masonry per IS 4326 even in low seismic zones.",
                source="IS 1893 Part 1")
        elif zone == 3:
            return dict(score=-6, label="Zone 3 — moderate seismic zone", status="warn",
                action="Earthquake-resistant design per IS 1893 is mandatory.",
                remedial="Design all structural elements for seismic forces per IS 1893 Zone 3 (Z=0.16). Provide ductile detailing of beams and columns per IS 13920. Use shear walls or cross bracing for buildings above 2 floors. Avoid soft storey design.",
                source="IS 1893 Part 1, IS 13920")
        elif zone == 4:
            return dict(score=-12, label="Zone 4 — high seismic zone", status="danger",
                action="Full ductile RCC design per IS 13920 is legally mandatory in Zone 4.",
                remedial="Mandatory for Zone 4: (1) Full ductile detailing per IS 13920. (2) Seismic base shear per IS 1893 (Z=0.24). (3) Shear walls in both directions above G+1. (4) No unreinforced masonry load-bearing walls. (5) Pile or raft foundation only. (6) Structural audit before permit submission.",
                source="IS 1893 Part 1, IS 13920")
        else:
            return dict(score=-12, label="Zone 5 — very high seismic zone", status="danger",
                action="Zone 5 requires highest level of earthquake engineering — specialist design mandatory.",
                remedial="Zone 5 mandatory: (1) Dynamic seismic analysis per IS 1893. (2) Full ductile detailing per IS 13920. (3) Base isolation recommended for buildings above 3 floors. (4) No brick masonry — only RCC frame. (5) Independent peer review by IIT or SERC certified engineer. (6) Liquefaction assessment if sandy soil present.",
                source="IS 1893 Part 1, IS 13920")

    # ── 15. BUILDING USAGE ──────────────────────────────────
    @staticmethod
    def score_usage(usage: str, landslide: str, seismic_zone: int) -> dict:
        u = usage.lower()
        if u == "residential":
            return dict(score=0, label="Residential — standard norms", status="ok",
                action="Standard residential construction norms apply.",
                remedial="Comply with NBC 2016 Part 4 residential occupancy requirements.",
                source="NBC 2016 Part 4")
        else:
            in_hazard = (landslide.lower() == "high" or seismic_zone >= 4)
            if in_hazard:
                return dict(score=-5, label="Commercial in hazard zone — extra checks", status="warn",
                    action="Commercial buildings in high hazard zones require additional regulatory approval.",
                    remedial="Obtain Environmental Impact Assessment (EIA) clearance. Carry out structural audit per NBC 2016 Part 4. Provide emergency evacuation plan. Obtain fire NOC from local fire authority before occupancy.",
                    source="NBC 2016 Part 4, IS 1893")
            else:
                return dict(score=0, label="Commercial — standard norms", status="ok",
                    action="Standard commercial construction norms apply.",
                    remedial="Comply with NBC 2016 Part 4 commercial occupancy requirements.",
                    source="NBC 2016 Part 4")

    # ── COMPOUND RULES ──────────────────────────────────────
    @staticmethod
    def apply_compound_rules(p: dict) -> list:
        slope      = p["slope_angle"]
        landslide  = p["landslide_risk"].lower()
        soil_type  = p["soil_type"].lower()
        moisture   = p["moisture_content"]   # now a float %
        floors     = p["num_floors"]
        foundation = p["foundation_type"].lower()
        load       = p["building_load"]      # now a float kN/m2
        material   = p["material"].lower()
        wall_type  = p["wall_type"].lower()
        retaining  = p["retaining_wall"].lower()
        drainage   = p["drainage"].lower()
        seismic    = p["seismic_zone"]
        elevation  = p["elevation"]          # now a float metres

        triggered = []
        def add(rule, score, reason, remedial, source, rtype):
            triggered.append(dict(rule=rule, score=score, reason=reason, remedial=remedial, source=source, type=rtype))

        if load > 10 and soil_type == "sandy":
            add("Heavy load + Sandy soil", -15,
                f"Load {load} kN/m² on sandy soil — liquefaction risk during earthquake.",
                "Mandatory pile foundation to bedrock. Liquefaction potential assessment per IS 1893 Annex F. Stone columns or vibro-compaction per IS 9451 before piling.",
                "IS 1893, IS 2911, IS 9451", "danger")

        if floors > 5 and foundation in ("shallow", "isolated"):
            add(f"Floors > 5 + {foundation.title()} foundation", -20,
                f"{floors} floors with {foundation} foundation — differential settlement and structural failure risk.",
                f"Replace {foundation} foundation with bored cast-in-situ piles (IS 2911) minimum 450 mm diameter. Pile load test at 1.5 times design load mandatory.",
                "IS 2911", "danger")

        if moisture > 30 and drainage == "no":
            add(f"High moisture ({moisture}%) + No drainage", -10,
                "Saturated soil with zero drainage — chronic bearing capacity loss and slope instability.",
                "Install full subsurface drainage before any foundation work. Perforated HDPE pipe at 1.5 m depth around full plot perimeter. Sump pit with automatic pump. No construction until moisture reduces below 30%.",
                "IS 8009, IS 1904, IS 4111", "danger")

        if seismic >= 3 and material == "wood":
            add("Seismic zone 3+ + Wood construction", -10,
                "Timber has poor earthquake resistance — collapse risk in moderate to high seismic zones.",
                "Replace all structural timber with RCC frame per IS 456. All connections must be bolted and gusset-plated, not nailed, per IS 883.",
                "IS 883, IS 1893", "danger")

        if landslide == "high" and retaining == "no":
            add("High landslide zone + No retaining wall", -12,
                "High landslide risk without retaining wall — imminent slope failure threat.",
                "Construct retaining wall and obtain slope stability certificate BEFORE any foundation excavation. Install slope movement monitoring (inclinometers). Obtain NDMA clearance.",
                "IS 14458, NDMA", "danger")

        if soil_type == "sandy" and moisture > 20:
            add(f"Sandy soil + High moisture ({moisture}%)", -8,
                "Saturated sandy soil loses bearing capacity and liquefies during vibration.",
                "Site dewatering before construction. Install well point dewatering system around proposed foundation area. Retest bearing capacity after dewatering — minimum 100 kN/m² required.",
                "IS 1498, IS 8009", "danger")

        if elevation > 1500 and load > 10:
            add(f"High altitude ({elevation}m) + Heavy load ({load} kN/m²)", -8,
                "Heavy structure at high altitude faces amplified wind loads and access constraints.",
                "Reduce dead load by using lightweight precast panels or steel frame. Enhanced wind load analysis per IS 875 Part 3 for high altitude.",
                "IS 875 Part 3", "warn")

        if seismic >= 4 and wall_type == "brick":
            add("Seismic zone 4/5 + Brick walls", -8,
                "Unreinforced brick masonry catastrophically fails in high seismic zones.",
                "Mandatory replacement of load-bearing brick walls with RCC frame and reinforced masonry infill per IS 13920.",
                "IS 1905, IS 13920, IS 1893", "danger")

        if slope > 30 and retaining == "no":
            add(f"Slope {slope}° + No retaining wall", -12,
                "Steep slope without lateral support — risk of slope failure and structure sliding downhill.",
                "No construction activity to begin until RCC retaining wall is constructed and cured per IS 14458 with FOS >= 1.5.",
                "IS 14458", "danger")

        if floors > 10 and seismic >= 4:
            add("Floors > 10 + Seismic zone 4/5", -15,
                "Tall buildings in high seismic zones require specialist earthquake engineering.",
                "Commission specialist earthquake engineering consultancy. Time-history dynamic analysis. Base isolation recommended. Independent peer review by IIT or SERC certified engineer mandatory.",
                "IS 1893, IS 2911", "danger")

        if foundation in ("pile", "under_reamed") and soil_type == "rock":
            add("Pile foundation + Rock soil", +5,
                "Pile-on-rock is the strongest possible foundation combination for hill terrain.",
                "Ensure pile tip socketed minimum 300 mm into sound rock. Rock core sampling to confirm RQD > 50%.",
                "IS 2911, IS 6403", "ok")

        if material == "concrete" and wall_type == "reinforced":
            add("RCC frame + Reinforced walls", +5,
                "Ideal structural combination for seismic and slope load resistance.",
                "Ensure all reinforcement laps, hooks, and splices comply with IS 456 and IS 13920. M20 minimum concrete grade.",
                "IS 456, IS 13920", "ok")

        if drainage == "yes" and moisture > 20:
            add(f"Drainage present + High moisture ({moisture}%)", +5,
                "Drainage system actively mitigates the high moisture risk.",
                "Verify drainage capacity for peak monsoon discharge. Clean and maintain drains before each monsoon season.",
                "IS 4111, IS 8009", "ok")

        if seismic <= 2 and load <= 5:
            add("Low seismic zone + Light load", +3,
                "Safest possible combination for hill station residential construction.",
                "Maintain light structural load — avoid heavy flooring or water tanks on upper floors.",
                "IS 1893, NBC 2016", "ok")

        return triggered

    # ── DESIGN RECOMMENDATION ───────────────────────────────
    @staticmethod
    def get_design_recommendation(p: dict, score: int) -> dict:
        slope    = p["slope_angle"]
        soil     = p["soil_type"].lower()
        seismic  = p["seismic_zone"]
        material = p["material"].lower()
        elevation= p["elevation"]

        if slope <= 15:
            typology = "Conventional flat-terrain residential design"
            typology_detail = "Standard single or multi-storey RCC frame with isolated or combined footing. No special slope adaptation required."
            foundation_rec = "Isolated column footing (IS 1904) for light loads. Combined footing or raft (IS 2950) if soil is clay or sandy. Under-reamed pile (IS 2911 Part 3) if expansive clay soil is present."
        elif slope <= 30:
            typology = "Split-level design with stepped foundation"
            typology_detail = "Building footprint is terraced into the hillside at two or more levels. Each level steps down the slope by 1-2 m. This reduces cutting and filling and integrates naturally with the contour."
            foundation_rec = "Stepped foundation (IS 1904) following the natural contour with horizontal RCC tie beams connecting all steps. Pile foundation (IS 2911) recommended if soil is clay or sandy."
        elif slope <= 45:
            typology = "Stilted / platform design with deep foundation"
            typology_detail = "Building sits on stilts (columns) that follow the slope — the floor level is held horizontal while column heights vary with the terrain below. Avoids major earthworks and minimises slope disturbance."
            foundation_rec = "Deep pile foundation (IS 2911) mandatory. Columns of varying height support a flat structural platform. Pile tips must reach stable strata below slope failure plane."
        else:
            typology = "Site not suitable for design — stabilise slope first"
            typology_detail = "Slope above 45° is too steep for any conventional residential building design. Major slope stabilisation and geotechnical certification mandatory before design can be considered."
            foundation_rec = "No foundation type appropriate until slope is stabilised and certified by a licensed geotechnical engineer."

        seismic_system = ("Standard RCC frame with seismic bands (IS 4326)." if seismic <= 2
            else "RCC frame with ductile detailing per IS 13920. Shear walls recommended for buildings above 2 floors." if seismic == 3
            else "Fully ductile RCC special moment-resisting frame per IS 13920. Shear walls in both directions mandatory. Seismic base isolation recommended for buildings above 3 floors.")

        roof_rec = ("Steep-pitch roof (minimum 30° pitch) with metal sheet or Mangalore tile. Roof anchored against high-altitude wind uplift per IS 875 Part 3." if elevation > 1500
            else "Sloped roof (15-25° pitch) with wind-resistant anchoring. Avoid flat roofs due to rain accumulation risk." if elevation > 600
            else "Standard sloped roof (10-15° pitch). Flat roof acceptable if waterproofed with APP membrane per IS 13707.")

        material_note = ("Timber not recommended for hill station construction. Replace with RCC frame with optional timber cladding per IS 883." if material == "wood"
            else "Steel frame suitable. Apply anti-corrosion coating — minimum 80 micron DFT epoxy primer per IS 800 for hill station humidity." if material == "steel"
            else "RCC construction using M20 minimum grade concrete per IS 456. Use OPC 43 grade cement in high-altitude or high-moisture sites.")

        overall = ("Site is suitable. Proceed with detailed structural design using the recommended typology." if score >= 75
            else "Site is conditionally suitable. Address all flagged issues and obtain structural engineer approval before submitting building plans." if score >= 50
            else "Site requires significant remediation. Complete all remedial works and obtain geotechnical clearance before engaging a structural designer." if score >= 30
            else "Site is currently unsuitable. Do not commission building design until site conditions are fundamentally improved.")

        return {"typology": typology, "typology_detail": typology_detail,
                "foundation_recommendation": foundation_rec, "seismic_design_system": seismic_system,
                "roof_recommendation": roof_rec, "material_note": material_note,
                "overall_design_guidance": overall}

    # ── VERDICT ─────────────────────────────────────────────
    @staticmethod
    def get_verdict(score: int) -> dict:
        if score >= 75:
            return dict(verdict="Feasible", color="green",
                action="Proceed with detailed structural design and building permit application.",
                description="Site conditions are suitable for residential construction. Commission a licensed structural engineer to prepare building plans.")
        elif score >= 50:
            return dict(verdict="Feasible with conditions", color="amber",
                action="Complete all remedial measures below before submitting building plans.",
                description="Construction is possible but specific risks must be mitigated first. Obtain structural engineer sign-off on each remedial measure.")
        elif score >= 30:
            return dict(verdict="High risk — expert review mandatory", color="orange",
                action="Mandatory geotechnical investigation and structural expert review before any site work.",
                description="Multiple high-risk parameters identified. Do not proceed until a licensed geotechnical engineer certifies the site.")
        else:
            return dict(verdict="Not recommended", color="red",
                action="Do NOT construct. Obtain geotechnical clearance and complete major remediation first.",
                description="Site conditions present fundamental safety risks. A comprehensive geotechnical investigation and site remediation programme must be completed.")

    # ── MAIN ASSESS ─────────────────────────────────────────
    @classmethod
    def assess(cls, p: dict) -> dict:
        individual = {
            "slope_angle":      cls.score_slope(p["slope_angle"]),
            "elevation":        cls.score_elevation(p["elevation"]),
            "landslide_risk":   cls.score_landslide(p["landslide_risk"]),
            "soil_type":        cls.score_soil_type(p["soil_type"]),
            "bearing_capacity": cls.score_bearing_capacity(p["bearing_capacity"]),
            "moisture_content": cls.score_moisture(p["moisture_content"]),
            "num_floors":       cls.score_floors(p["num_floors"]),
            "foundation_type":  cls.score_foundation(p["foundation_type"]),
            "building_load":    cls.score_building_load(p["building_load"]),
            "material":         cls.score_material(p["material"]),
            "wall_type":        cls.score_wall_type(p["wall_type"]),
            "retaining_wall":   cls.score_retaining_wall(p["retaining_wall"], p["slope_angle"]),
            "drainage":         cls.score_drainage(p["drainage"]),
            "seismic_zone":     cls.score_seismic_zone(p["seismic_zone"]),
            "usage":            cls.score_usage(p["usage"], p["landslide_risk"], p["seismic_zone"]),
        }
        compound    = cls.apply_compound_rules(p)
        ind_total   = sum(v["score"] for v in individual.values())
        comp_total  = sum(r["score"] for r in compound)
        final_score = max(0, min(100, 100 + ind_total + comp_total))
        verdict     = cls.get_verdict(final_score)
        flags       = {k: v for k, v in individual.items() if v["status"] in ("warn", "danger")}
        comp_flags  = [r for r in compound if r["type"] in ("warn", "danger")]
        design      = cls.get_design_recommendation(p, final_score)

        # Risk heatmap data
        category_scores = {
            "terrain":    sum(individual[k]["score"] for k in ["slope_angle","elevation","landslide_risk"]),
            "soil":       sum(individual[k]["score"] for k in ["soil_type","bearing_capacity","moisture_content"]),
            "structural": sum(individual[k]["score"] for k in ["num_floors","foundation_type","building_load"]),
            "material":   sum(individual[k]["score"] for k in ["material","wall_type"]),
            "safety":     sum(individual[k]["score"] for k in ["retaining_wall","drainage","seismic_zone"]),
            "functional": individual["usage"]["score"],
        }

        return {
            "score": final_score,
            "score_breakdown": {"base": 100, "individual_total": ind_total, "compound_total": comp_total},
            "verdict": verdict,
            "individual_results": individual,
            "compound_rules_triggered": compound,
            "flags": flags,
            "compound_flags": comp_flags,
            "design_recommendation": design,
            "category_scores": category_scores,
            "input_parameters": p,
            "disclaimer": (
                "This DSS provides preliminary screening only. All thresholds are based on "
                "IS Codes (BIS), NBC 2016, and NDMA/GSI guidelines. Final construction "
                "decisions must be validated by a licensed structural and geotechnical "
                "engineer with site-specific SIR, SPT, and IS 1893 seismic zone verification."
            ),
        }
