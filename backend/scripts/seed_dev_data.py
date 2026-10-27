"""Creates a demo org/user/location/camera for the Phase 1 clone-to-demo
smoke test. Run with: python -m scripts.seed_dev_data
"""

from cip.core.security import hash_password
from cip.db.session import SessionLocal
from cip.models.camera import Camera, SourceType
from cip.models.location import Location
from cip.models.organization import Organization
from cip.models.user import User

DEMO_EMAIL = "demo@democip.com"  # ".local"/".test" etc. are rejected as reserved TLDs by EmailStr
DEMO_PASSWORD = "demo1234"


def main() -> None:
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == DEMO_EMAIL).first():
            print("Demo data already exists, skipping.")
            return

        org = Organization(name="Demo Org")
        db.add(org)
        db.flush()

        user = User(
            organization_id=org.id,
            email=DEMO_EMAIL,
            hashed_password=hash_password(DEMO_PASSWORD),
            full_name="Demo User",
            role="org_admin",
        )
        db.add(user)

        location = Location(organization_id=org.id, name="Demo Location")
        db.add(location)
        db.flush()

        camera = Camera(
            location_id=location.id,
            name="Demo Upload Camera",
            source_type=SourceType.UPLOAD,
        )
        db.add(camera)

        db.commit()
        print(f"Seeded demo org. Login with {DEMO_EMAIL} / {DEMO_PASSWORD}")
        print(f"Demo camera id: {camera.id}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
