from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from pkg.extension import db


# -------------------------
# USERS
# -------------------------
class User(db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)

    user_fname = db.Column(db.String(200), nullable=False)
    users_lname = db.Column(db.String(200), nullable=False)

    email = db.Column(db.String(100), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=False)

    suspended = db.Column(db.Boolean, default=False, nullable=False)
    is_verified = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)

    user_password = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(200), nullable=False, index=True)

    def set_password(self, password):
        self.user_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.user_password, password)

    # relationships
    admin_profile = db.relationship("Admin", back_populates="user", uselist=False)
    agent_profile = db.relationship("PropertyAgent", back_populates="user", uselist=False)
    identity_verifications = db.relationship("IdentityVerification", back_populates="user")
    properties_owned = db.relationship("Property", back_populates="owner")
    interests = db.relationship("ClientInterest", back_populates="client")
    user_types = db.relationship("UserType", back_populates="user")


# -------------------------
# ADMIN
# -------------------------
class Admin(db.Model):
    __tablename__ = "admin"

    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_date = db.Column(db.Date, nullable=True)
    admin_email=db.Column(db.String(100),nullable=False,unique=True)
    admin_password=db.Column(db.String(255),nullable=False)

    # FK -> users.user_id (you said it's FK)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=True, index=True)

    user = db.relationship("User", back_populates="admin_profile")


# -------------------------
# PROPERTY AGENTS
# -------------------------
class PropertyAgent(db.Model):
    __tablename__ = "property_agents"

    agent_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False, index=True)
   

    license_number = db.Column(db.String(100), nullable=False)
    agency_name = db.Column(db.String(150), nullable=True)

    agency_status = db.Column(
        db.Enum("active", "suspended", "pending"),
        nullable=True,
        default="pending"
    )

    user = db.relationship("User", back_populates="agent_profile")
    properties = db.relationship("Property", back_populates="agent")

# -------------------------
# PROPERTIES
# -------------------------
class Property(db.Model):
    __tablename__ = "properties"

    property_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    owner_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False, index=True)

    property_title = db.Column(db.String(300), nullable=True)

    property_type = db.Column(
        db.Enum("land", "house", "apartment", "commercial"),
        nullable=True
    )

    adress = db.Column(db.Text, nullable=False)

    price = db.Column(db.Numeric(12, 2), nullable=True)

    property_status = db.Column(
        db.Enum("available", "under_verification", "sold", "rented", "rejected"),
        nullable=True,
        default="under_verification"
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    property_listing = db.Column(
        db.Enum("SALE"),
        nullable=False
    )

    agent_id = db.Column(db.Integer, db.ForeignKey("property_agents.agent_id"), nullable=True, index=True)

    state_id = db.Column(
        db.Integer,
        db.ForeignKey("state.state_id"),
        nullable=True
    )
    owner = db.relationship("User", back_populates="properties_owned")
    agent = db.relationship("PropertyAgent", back_populates="properties")

    images = db.relationship("PropertyImage", back_populates="property")
    documents = db.relationship("PropertyDocument", back_populates="property")
    requests = db.relationship("ClientInterest", back_populates="property")


# -------------------------
# PROPERTY IMAGES
# -------------------------
class PropertyImage(db.Model):
    __tablename__ = "property_image"

    image_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # FK -> properties.property_id
    property_id = db.Column(db.Integer, db.ForeignKey("properties.property_id"), nullable=False, index=True)

    image_url = db.Column(db.String(100), nullable=True)

    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    property = db.relationship("Property", back_populates="images")


# -------------------------
# PROPERTY DOCUMENTS
# -------------------------
class PropertyDocument(db.Model):
    __tablename__ = "property_documents"

    document_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # FK -> properties.property_id
    property_id = db.Column(db.Integer, db.ForeignKey("properties.property_id"), nullable=False, index=True)

    document_type = db.Column(
        db.Enum("c_of_o", "deed", "survey_plan"),
        nullable=True
    )

    document_reference = db.Column(db.String(200), nullable=True)

    verified_at = db.Column(
    db.DateTime,
    server_default=db.func.current_timestamp(),
    onupdate=db.func.current_timestamp(),
    nullable=False
    )

    # DB says CURRENT_TIMESTAMP and ON UPDATE CURRENT_TIMESTAMP
   

    property = db.relationship("Property", back_populates="documents")


# -------------------------
# CLIENT INTEREST
# -------------------------
class ClientInterest(db.Model):
    __tablename__ = "client_interest"

    interest_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    client_user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False, index=True)
    property_id = db.Column(db.Integer, db.ForeignKey("properties.property_id"), nullable=False, index=True)

    interest_status = db.Column(
        db.Enum("requested", "approved", "declined"),
        nullable=False,
        default="requested"
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    client = db.relationship("User", back_populates="interests")
    property = db.relationship("Property", back_populates="requests")

# -------------------------
# IDENTITY VERIFICATION
# NOTE: keep your exact column names (verificaticon_status, verifid_at)
# -------------------------
class IdentityVerification(db.Model):
    __tablename__ = "identity_verification"

    verification_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # FK -> users.user_id
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False, index=True)

    id_type = db.Column(
        db.Enum("nin", "passport", "drivers_license"),
        nullable=False
    )

    id_number = db.Column(db.String(100), nullable=False)

    # spelling in your DB: "verificaticon_status" (must match)
    verification_status = db.Column(
        db.Enum("pending", "approved", "rejected"),
        nullable=False,
        default="pending"
    )

    # DB says CURRENT_TIMESTAMP and ON UPDATE CURRENT_TIMESTAMP
    verified_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="identity_verifications")


# -------------------------
# STATE
# -------------------------
class State(db.Model):
    __tablename__ = "state"

    state_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    state_name = db.Column(db.String(50), nullable=True)

    properties=db.relationship('Property', backref='states')


# -------------------------
# USER TYPE
# WARNING: your DB enum is enum('buyer,seller,agent') (one single option).
# If you intended 3 options, fix DB to enum('buyer','seller','agent') later.
# For now, we match your DB exactly to avoid errors.
# -------------------------
class UserType(db.Model):
    __tablename__ = "user_type"

    user_typeid = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_type = db.Column(
        db.Enum("buyer","seller","agent"),
        nullable=True
    )

    # FK -> users.user_id
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=True, index=True)

    user = db.relationship("User", back_populates="user_types")