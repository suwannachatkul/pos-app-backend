import traceback

from sqlalchemy import select
from sqlalchemy.orm import Session

from api.models import PaymentMethod
from shared.logging import logger

from ..database import db_scope
from ..settings import settings
from .default_payment_method import DEFAULT_PAYMENT_METHODS


class InitializeTask:
    """Class to handle application initialization"""

    def __init__(self):
        self.logger = logger
        self.settings = settings

    def start(self):
        """Run initialization tasks"""
        self.logger.info("Starting application initialization")
        try:
            with db_scope() as db:
                self.create_default_payment_methods(db)
                # Add more initialization here

            self.logger.info("Application initialization completed successfully")
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            self.logger.debug(traceback.format_exc())
            raise

    # TODO: do seed script instead of initializer
    # For now this is just for ease of starting app without extra commands
    def create_default_payment_methods(self, db: Session):
        """Create default payment methods in the database"""
        self.logger.info("Creating default payment methods")
        try:
            names = [m["name"] for m in DEFAULT_PAYMENT_METHODS]
            if not names:
                self.logger.info("No default payment methods configured")
                return

            # Check existing payment methods
            stmt = select(PaymentMethod.name).where(PaymentMethod.name.in_(names))
            existing = set(db.execute(stmt).scalars().all())

            # Determine which payment methods need to be added
            missing = [m for m in DEFAULT_PAYMENT_METHODS if m["name"] not in existing]
            if not missing:
                self.logger.info("No new payment methods to add")
                return

            objs = [PaymentMethod(**m) for m in missing]
            db.add_all(objs)
            db.commit()

            for m in missing:
                self.logger.debug(
                    f"Added payment method '{m['name']}' to the database."
                )
            self.logger.info("Default payment methods created successfully")

        except Exception as e:
            self.logger.error(f"Failed to create payment methods: {e}")
            self.logger.debug(traceback.format_exc())
            raise


initialize_task = InitializeTask()
