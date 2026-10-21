"""
Run once after setup to create a default admin user:
    python seed_admin.py

Admin credentials (change immediately in a real deployment):
    email: admin@amazon.local
    password: Admin@123
"""
from app.database import SessionLocal, Base, engine
from app.models.user import User
from app.auth.hashing import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

existing = db.query(User).filter(User.email == "admin@amazon.local").first()
if existing:
    print("Admin already exists.")
else:
    admin = User(
        name="Admin",
        email="admin@amazon.local",
        hashed_password=hash_password("Admin@123"),
        is_admin=True,
    )
    db.add(admin)
    db.commit()
    print("Admin created: admin@amazon.local / Admin@123")

db.close()
