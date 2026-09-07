"""
Seed the database with:
  1. Real, public administrative facts: Maharashtra -> Solapur -> the 11
     Solapur talukas. These are geographic/administrative facts, not
     statistics, so they are not marked DEMO.
  2. Demonstration data for villages, businesses, markets, and prices -
     explicitly marked data_status='DEMO'. This is structurally realistic
     data for exercising the platform end-to-end, NOT verified real-world
     Solapur statistics. Replace via the admin CSV import pipeline (see
     app/data_ingestion) once verified government datasets are available.
  3. Loan/subsidy schemes (PMEGP, CMEGP, Mudra tiers, Stand-Up India, NABARD)
     seeded with real published parameters as of the date in
     last_verified_date, marked data_status='ESTIMATED' because bank-set
     interest rates vary by lender/category - re-verify against the official
     source_url before relying on these for an actual loan application.

Run with:  python -m scripts.seed_database
"""
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Works in two layouts:
#  - local dev: <repo_root>/scripts/seed_database.py, backend code at
#    <repo_root>/backend/app/
#  - Docker container: /app/scripts/seed_database.py, backend code at
#    /app/app/ (backend/ contents copied directly into /app - see
#    backend/Dockerfile)
_here = Path(__file__).resolve()
for _candidate in (_here.parents[1] / "backend", _here.parents[1]):
    if (_candidate / "app").is_dir():
        sys.path.insert(0, str(_candidate))
        break

from geoalchemy2.elements import WKTElement  # noqa: E402

from app.database.session import SessionLocal  # noqa: E402
from app.models.business import (  # noqa: E402
    Business,
    BusinessCategory,
    BusinessCostTemplate,
    BusinessRevenueAssumption,
    InfrastructureStatistics,
    Market,
    Product,
    ProductPrice,
)
from app.models.config import FinancialAssumptionConfig, ScoringWeightConfig  # noqa: E402
from app.models.data_sources import DataSource  # noqa: E402
from app.models.geography import District, State, Taluka, Village  # noqa: E402
from app.models.schemes import LoanScheme  # noqa: E402
from app.models.users import User, UserProfile  # noqa: E402
from app.auth.security import hash_password  # noqa: E402

random.seed(42)

# Real, public administrative facts (Government of Maharashtra taluka list)
SOLAPUR_TALUKAS = [
    {"name": "North Solapur", "hq": "Solapur"},
    {"name": "South Solapur", "hq": "Solapur"},
    {"name": "Akkalkot", "hq": "Akkalkot"},
    {"name": "Barshi", "hq": "Barshi"},
    {"name": "Pandharpur", "hq": "Pandharpur"},
    {"name": "Mangalwedha", "hq": "Mangalwedha"},
    {"name": "Sangola", "hq": "Sangola"},
    {"name": "Mohol", "hq": "Mohol"},
    {"name": "Madha", "hq": "Madha"},
    {"name": "Karmala", "hq": "Karmala"},
    {"name": "Malshiras", "hq": "Malshiras"},
]

# Approximate taluka headquarters coordinates (public geographic reference
# points, used only as a center to scatter DEMO villages around).
TALUKA_CENTERS = {
    "North Solapur": (17.72, 75.90),
    "South Solapur": (17.55, 75.95),
    "Akkalkot": (17.53, 76.21),
    "Barshi": (18.24, 75.70),
    "Pandharpur": (17.68, 75.33),
    "Mangalwedha": (17.53, 75.46),
    "Sangola": (17.44, 75.20),
    "Mohol": (17.78, 75.65),
    "Madha": (18.02, 75.50),
    "Karmala": (18.41, 75.20),
    "Malshiras": (17.90, 75.00),
}

BUSINESS_CATEGORIES = [
    ("Dairy", "AGRI", 50000, 300000),
    ("Poultry", "AGRI", 40000, 250000),
    ("Goat Farming", "AGRI", 30000, 150000),
    ("Sheep Farming", "AGRI", 30000, 150000),
    ("Agriculture Input Shop", "RETAIL", 100000, 500000),
    ("Seed Business", "RETAIL", 80000, 400000),
    ("Fertilizer Business", "RETAIL", 100000, 500000),
    ("Grocery/Kirana", "RETAIL", 50000, 300000),
    ("Tailoring", "SERVICE", 20000, 100000),
    ("Mobile Repair", "SERVICE", 30000, 120000),
    ("Electrical Repair", "SERVICE", 25000, 100000),
    ("Farm Equipment Rental", "SERVICE", 200000, 1500000),
    ("Food Processing", "MANUFACTURING", 150000, 800000),
    ("Flour Mill", "MANUFACTURING", 100000, 400000),
    ("Dal Mill", "MANUFACTURING", 150000, 600000),
    ("Oil Extraction", "MANUFACTURING", 200000, 900000),
    ("Dairy Product Processing", "MANUFACTURING", 150000, 700000),
    ("Fruit/Vegetable Trading", "RETAIL", 40000, 250000),
    ("Agricultural Produce Trading", "RETAIL", 100000, 600000),
    ("Transport Services", "SERVICE", 300000, 1200000),
    ("Welding/Fabrication", "MANUFACTURING", 80000, 350000),
    ("Carpentry", "SERVICE", 40000, 200000),
    ("Small Manufacturing", "MANUFACTURING", 150000, 800000),
    ("Solar Services", "SERVICE", 100000, 500000),
    ("Irrigation Equipment Services", "SERVICE", 80000, 400000),
]

PRODUCTS = [
    ("Jowar", "quintal"),
    ("Bajra", "quintal"),
    ("Wheat", "quintal"),
    ("Sugarcane", "tonne"),
    ("Tur (Pulses)", "quintal"),
    ("Groundnut (Oilseed)", "quintal"),
    ("Onion", "quintal"),
    ("Milk", "litre"),
]

VILLAGE_NAME_POOL = [
    "Wadala", "Hatid", "Kegaon", "Vairag", "Kumbhari", "Akola", "Boramani",
    "Anjangaon", "Degaon", "Nannaj", "Tirhe", "Vaduj", "Shelgaon", "Kondi",
    "Nandani", "Bavi", "Pangaon", "Halkarni", "Kambi", "Ausa Road", "Wangi",
    "Bhose", "Kasegaon", "Malshiras Rural", "Velapur",
]


def point(lat, lng):
    return WKTElement(f"POINT({lng} {lat})", srid=4326)


def rand_offset(center, max_km=8):
    # crude degree-per-km approximation, fine for scattering demo points
    d_lat = random.uniform(-max_km, max_km) / 111.0
    d_lng = random.uniform(-max_km, max_km) / (111.0 * 0.95)
    return round(center[0] + d_lat, 6), round(center[1] + d_lng, 6)


def run():
    db = SessionLocal()
    try:
        existing = db.query(Village).count()
        if existing > 0:
            print(f"Seed skipped: {existing} villages already present in the database.")
            print("Delete the data (or the Docker volume) first if you want to reseed from scratch.")
            return

        print("Seeding data_sources ...")
        demo_source = DataSource(
            source_name="Platform Demonstration Dataset",
            source_url=None,
            dataset_name="solapur_rural_demo_v1",
            collection_date=datetime.utcnow(),
            geographic_coverage="Solapur District, Maharashtra (rural talukas)",
            data_type="mixed",
            license="Internal demo use only",
            reliability="LOW",
            verification_status="UNVERIFIED",
        )
        db.add(demo_source)
        db.flush()

        print("Seeding Maharashtra / Solapur / talukas (real administrative facts) ...")
        state = State(state_name="Maharashtra", state_code="MH")
        db.add(state)
        db.flush()

        district = District(state_id=state.id, district_name="Solapur", official_name="Solapur District")
        db.add(district)
        db.flush()

        taluka_objs = {}
        for t in SOLAPUR_TALUKAS:
            center = TALUKA_CENTERS[t["name"]]
            taluka = Taluka(
                district_id=district.id,
                name=t["name"],
                headquarters=t["hq"],
                latitude=center[0],
                longitude=center[1],
                active=True,
                source_id=demo_source.id,
            )
            db.add(taluka)
            db.flush()
            taluka_objs[t["name"]] = taluka

        print("Seeding business categories ...")
        category_objs = {}
        for name, sector, min_inv, max_inv in BUSINESS_CATEGORIES:
            cat = BusinessCategory(
                name=name, sector=sector, typical_min_investment=min_inv, typical_max_investment=max_inv
            )
            db.add(cat)
            db.flush()
            category_objs[name] = cat

            db.add(
                BusinessCostTemplate(
                    category_id=cat.id,
                    item_name=f"{name} - initial setup",
                    estimated_cost=(min_inv + max_inv) / 2,
                    cost_type="CAPITAL",
                    data_status="DEMO",
                )
            )
            db.add(
                BusinessRevenueAssumption(
                    category_id=cat.id,
                    monthly_revenue_low=(min_inv + max_inv) / 2 * 0.05,
                    monthly_revenue_high=(min_inv + max_inv) / 2 * 0.12,
                    expected_margin_pct=random.uniform(12, 35),
                    seasonality_score=random.uniform(0.1, 0.7),
                    data_status="DEMO",
                )
            )

        print("Seeding villages, infrastructure, businesses, markets ...")
        village_objs = []
        for t_name, taluka in taluka_objs.items():
            center = TALUKA_CENTERS[t_name]
            n_villages = random.randint(3, 5)
            chosen_names = random.sample(VILLAGE_NAME_POOL, n_villages)
            for vname in chosen_names:
                lat, lng = rand_offset(center)
                population = random.randint(800, 6000)
                households = round(population / random.uniform(4.2, 5.5))
                village = Village(
                    district_id=district.id,
                    taluka_id=taluka.id,
                    village_name=f"{vname} ({t_name})",
                    gram_panchayat=f"{vname} Gram Panchayat",
                    latitude=lat,
                    longitude=lng,
                    geometry=point(lat, lng),
                    area_type="RURAL",
                    population=population,
                    households=households,
                    literacy_rate=round(random.uniform(55, 82), 1),
                    agricultural_area=round(random.uniform(200, 2000), 1),
                    source_id=demo_source.id,
                    source_date=datetime.utcnow(),
                    verification_status="UNVERIFIED",
                    data_status="DEMO",
                )
                db.add(village)
                db.flush()
                village_objs.append(village)

                db.add(
                    InfrastructureStatistics(
                        village_id=village.id,
                        road_access=random.random() > 0.15,
                        electricity=random.random() > 0.05,
                        internet=random.random() > 0.3,
                        drinking_water=random.random() > 0.1,
                        bank_available=random.random() > 0.6,
                        atm_available=random.random() > 0.75,
                        primary_health_center=random.random() > 0.4,
                        school_available=random.random() > 0.1,
                        source="Platform Demonstration Dataset",
                        data_status="DEMO",
                    )
                )

                # Scatter a handful of existing demo businesses around each village
                for _ in range(random.randint(0, 3)):
                    cat_name = random.choice(list(category_objs.keys()))
                    blat, blng = rand_offset((lat, lng), max_km=4)
                    db.add(
                        Business(
                            village_id=village.id,
                            category_id=category_objs[cat_name].id,
                            business_name=f"{cat_name} Enterprise - {vname}",
                            owner_name=None,
                            latitude=blat,
                            longitude=blng,
                            geometry=point(blat, blng),
                            status="ACTIVE",
                            source="Platform Demonstration Dataset",
                            verified=False,
                            data_status="DEMO",
                            source_date=datetime.utcnow(),
                        )
                    )

            # one market per taluka
            mlat, mlng = rand_offset(center, max_km=2)
            market = Market(
                market_name=f"{t_name} APMC Market Yard",
                taluka_id=taluka.id,
                latitude=mlat,
                longitude=mlng,
                geometry=point(mlat, mlng),
                market_type="APMC",
                source="Platform Demonstration Dataset",
                data_status="DEMO",
                source_date=datetime.utcnow(),
            )
            db.add(market)
            db.flush()

            product_objs = {}
            for pname, unit in PRODUCTS:
                product = db.query(Product).filter(Product.name == pname).first()
                if not product:
                    product = Product(name=pname, unit=unit, category="agri")
                    db.add(product)
                    db.flush()
                product_objs[pname] = product

            for pname, product in product_objs.items():
                base = random.uniform(1500, 6000)
                db.add(
                    ProductPrice(
                        product_id=product.id,
                        market_id=market.id,
                        minimum_price=round(base * 0.85, 2),
                        average_price=round(base, 2),
                        maximum_price=round(base * 1.2, 2),
                        price_date=datetime.utcnow() - timedelta(days=random.randint(0, 10)),
                        source="Platform Demonstration Dataset",
                        confidence="LOW",
                        data_status="DEMO",
                    )
                )

        print("Seeding loan schemes (real published parameters, ESTIMATED where lender-set rates vary) ...")
        _scheme_verified = datetime(2026, 9, 1)
        db.add(
            LoanScheme(
                scheme_name="PMEGP (Prime Minister's Employment Generation Programme)",
                provider="KVIC / Ministry of MSME, Government of India",
                minimum_project_cost=0,
                maximum_project_cost=5_000_000,
                loan_percentage=0.90,
                beneficiary_contribution=0.10,
                maximum_loan=4_500_000,
                interest_rate=8.5,
                tenure_years=7,
                moratorium_months=6,
                repayment_frequency="MONTHLY",
                eligibility=(
                    "New micro-enterprises only (no expansion of existing units); first-generation "
                    "entrepreneurs, 18+ years. Margin-money subsidy of 15-35% of project cost "
                    "(higher for rural/special-category applicants: SC/ST, women, ex-servicemen, "
                    "differently abled, NER/hill areas) bridges the gap between the bank loan and the "
                    "beneficiary's own 5-10% contribution. Eligible project cost up to Rs. 50 lakh for "
                    "manufacturing and Rs. 20 lakh for services/trading. 8th-standard pass required only "
                    "for projects above Rs. 10 lakh (manufacturing) / Rs. 5 lakh (services)."
                ),
                source="KVIC PMEGP revised guidelines (Dec 2023)",
                source_url="https://www.kviconline.gov.in/pmegp/",
                effective_date=datetime(2023, 12, 1),
                last_verified_date=_scheme_verified,
                data_status="ESTIMATED",
            )
        )
        db.add(
            LoanScheme(
                scheme_name="CMEGP (Chief Minister's Employment Generation Programme, Maharashtra)",
                provider="Directorate of Industries / Maharashtra State KVIB, Government of Maharashtra",
                minimum_project_cost=0,
                maximum_project_cost=10_000_000,
                loan_percentage=0.90,
                beneficiary_contribution=0.10,
                maximum_loan=9_000_000,
                interest_rate=8.5,
                tenure_years=7,
                moratorium_months=6,
                repayment_frequency="MONTHLY",
                eligibility=(
                    "Maharashtra's state-level equivalent of PMEGP for new micro/small enterprises in "
                    "rural and urban areas. Back-end subsidy of 15-35% of project cost (general/rural 25%, "
                    "special category/rural 35%; special category includes SC/ST, women, ex-servicemen, "
                    "differently abled); own contribution 5-10%, balance financed by an empanelled bank. "
                    "Since April 2025, eligible project cost is up to Rs. 1 crore for manufacturing and "
                    "Rs. 50 lakh for service/agri-allied activities. Applicants must not have already "
                    "availed PMEGP or another Central/State subsidy scheme."
                ),
                source="Directorate of Industries, Government of Maharashtra (maha-cmegp.gov.in)",
                source_url="https://maha-cmegp.gov.in/",
                effective_date=datetime(2025, 4, 1),
                last_verified_date=_scheme_verified,
                data_status="ESTIMATED",
            )
        )
        db.add(
            LoanScheme(
                scheme_name="Mudra Loan - Shishu",
                provider="MUDRA (PMMY) / Scheduled Banks, RRBs, NBFCs, MFIs",
                minimum_project_cost=0,
                maximum_project_cost=50_000,
                loan_percentage=1.0,
                beneficiary_contribution=0.0,
                maximum_loan=50_000,
                interest_rate=10.5,
                tenure_years=5,
                moratorium_months=0,
                repayment_frequency="MONTHLY",
                eligibility=(
                    "Collateral-free loans for non-corporate, non-farm micro/small enterprises just "
                    "starting out. Rate shown is a representative mid-point; public sector banks "
                    "typically charge 9-12% p.a., set by each lender against its own MCLR/base rate "
                    "(no fixed government rate). No processing fee."
                ),
                source="Pradhan Mantri MUDRA Yojana (PMMY) guidelines, Ministry of Finance",
                source_url="https://www.mudra.org.in/",
                last_verified_date=_scheme_verified,
                data_status="ESTIMATED",
            )
        )
        db.add(
            LoanScheme(
                scheme_name="Mudra Loan - Kishor",
                provider="MUDRA (PMMY) / Scheduled Banks, RRBs, NBFCs, MFIs",
                minimum_project_cost=50_001,
                maximum_project_cost=500_000,
                loan_percentage=1.0,
                beneficiary_contribution=0.0,
                maximum_loan=500_000,
                interest_rate=12.0,
                tenure_years=5,
                moratorium_months=3,
                repayment_frequency="MONTHLY",
                eligibility=(
                    "For enterprises that have moved past the startup stage and need more working "
                    "capital or equipment finance. Rate shown is a representative mid-point of the "
                    "typical 11-15% p.a. range; each lender sets its own rate, usually with a ~0.5% "
                    "processing fee."
                ),
                source="Pradhan Mantri MUDRA Yojana (PMMY) guidelines, Ministry of Finance",
                source_url="https://www.mudra.org.in/",
                last_verified_date=_scheme_verified,
                data_status="ESTIMATED",
            )
        )
        db.add(
            LoanScheme(
                scheme_name="Mudra Loan - Tarun",
                provider="MUDRA (PMMY) / Scheduled Banks, RRBs, NBFCs, MFIs",
                minimum_project_cost=500_001,
                maximum_project_cost=1_000_000,
                loan_percentage=1.0,
                beneficiary_contribution=0.0,
                maximum_loan=1_000_000,
                interest_rate=13.5,
                tenure_years=7,
                moratorium_months=3,
                repayment_frequency="MONTHLY",
                eligibility=(
                    "For established micro-enterprises seeking growth capital. Rate shown is a "
                    "representative mid-point of the typical 12-16% p.a. range; collateral-free, "
                    "covered under the Credit Guarantee Fund for Micro Units (CGFMU)."
                ),
                source="Pradhan Mantri MUDRA Yojana (PMMY) guidelines, Ministry of Finance",
                source_url="https://www.mudra.org.in/",
                last_verified_date=_scheme_verified,
                data_status="ESTIMATED",
            )
        )
        db.add(
            LoanScheme(
                scheme_name="Mudra Loan - Tarun Plus",
                provider="MUDRA (PMMY) / Scheduled Banks, RRBs, NBFCs, MFIs",
                minimum_project_cost=1_000_001,
                maximum_project_cost=2_000_000,
                loan_percentage=1.0,
                beneficiary_contribution=0.0,
                maximum_loan=2_000_000,
                interest_rate=14.0,
                tenure_years=7,
                moratorium_months=3,
                repayment_frequency="MONTHLY",
                eligibility=(
                    "Introduced in the Union Budget 2024-25 (raising the PMMY ceiling from Rs. 10 lakh "
                    "to Rs. 20 lakh); only available to entrepreneurs who have already taken and fully "
                    "repaid a Tarun-category loan. Collateral-free, covered under CGFMU; rate is "
                    "lender-determined, similar to the Tarun band."
                ),
                source="Pradhan Mantri MUDRA Yojana (PMMY) guidelines, Ministry of Finance",
                source_url="https://www.mudra.org.in/",
                effective_date=datetime(2024, 10, 1),
                last_verified_date=_scheme_verified,
                data_status="ESTIMATED",
            )
        )
        db.add(
            LoanScheme(
                scheme_name="Stand-Up India",
                provider="SIDBI / Scheduled Commercial Banks",
                minimum_project_cost=1_333_333,
                maximum_project_cost=13_333_333,
                loan_percentage=0.75,
                beneficiary_contribution=0.25,
                maximum_loan=10_000_000,
                interest_rate=10.0,
                tenure_years=7,
                moratorium_months=18,
                repayment_frequency="MONTHLY",
                eligibility=(
                    "For women, SC, and ST entrepreneurs (18+) setting up a new/greenfield enterprise "
                    "(manufacturing, services, trading, or agri-allied) - not for expanding an existing "
                    "business. Composite loan (term loan + working capital) of Rs. 10 lakh to Rs. 1 crore, "
                    "at least 51% shareholding/stake held by the eligible applicant. Rate is set per bank, "
                    "capped at MCLR + 3% + tenor premium (typically ~9-12% p.a. in practice); margin "
                    "money up to 25% of project cost, which can be reduced via convergence with other "
                    "government schemes. Backed by the Credit Guarantee Fund Scheme for Stand-Up India "
                    "(CGFSIL), reducing collateral requirements."
                ),
                source="Department of Financial Services, Ministry of Finance (standupmitra.in)",
                source_url="https://www.standupmitra.in/",
                last_verified_date=_scheme_verified,
                data_status="ESTIMATED",
            )
        )
        db.add(
            LoanScheme(
                scheme_name="NABARD Rural Enterprise Loan (refinance-backed)",
                provider="NABARD, via cooperative banks / RRBs / commercial banks",
                minimum_project_cost=500_000,
                maximum_project_cost=5_000_000,
                loan_percentage=0.85,
                beneficiary_contribution=0.15,
                maximum_loan=4_250_000,
                interest_rate=9.0,
                tenure_years=10,
                moratorium_months=12,
                repayment_frequency="QUARTERLY",
                eligibility=(
                    "For rural agri and allied (agro-processing, dairy, poultry, warehousing) micro and "
                    "small enterprises. NABARD refinances the lending bank rather than lending directly "
                    "to the entrepreneur, so the exact rate, margin, and moratorium are set by the "
                    "originating bank within NABARD's refinance guidelines - figures shown are "
                    "representative and should be confirmed with the local bank/DIC before applying."
                ),
                source="NABARD refinance guidelines for rural non-farm enterprises",
                source_url="https://www.nabard.org/",
                last_verified_date=_scheme_verified,
                data_status="ESTIMATED",
            )
        )

        print("Seeding default scoring weight + financial assumption configs ...")
        db.add(ScoringWeightConfig(config_name="default", active=True))
        db.add(FinancialAssumptionConfig(config_name="default", active=True))

        print("Seeding demo admin + demo user accounts ...")
        admin = User(
            full_name="Solapur Rural Admin",
            email="admin@solapur-rural-demo.com",
            hashed_password=hash_password("ChangeMe123!"),
            role="ADMIN",
        )
        db.add(admin)
        db.flush()
        db.add(UserProfile(user_id=admin.id))

        demo_user = User(
            full_name="Demo Entrepreneur",
            email="demo@solapur-rural-demo.com",
            hashed_password=hash_password("ChangeMe123!"),
            role="USER",
        )
        db.add(demo_user)
        db.flush()
        db.add(UserProfile(user_id=demo_user.id, village_id=village_objs[0].id if village_objs else None))

        db.commit()
        print(f"Done. Seeded {len(village_objs)} DEMO villages across {len(taluka_objs)} talukas.")
        print("Login: admin@solapur-rural-demo.com / demo@solapur-rural-demo.com, password: ChangeMe123!")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run()
