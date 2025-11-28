"""Create the reports table when missing and ensure supporting indexes exist."""

from app import app, db
from models import Report
from sqlalchemy import inspect, text


def upgrade() -> None:
    """Create the reports table and indexes in a backwards-compatible way."""
    with app.app_context():
        inspector = inspect(db.engine)
        if not inspector.has_table("reports"):
            Report.__table__.create(bind=db.engine, checkfirst=True)
            app.logger.info("reports table created via migration")

        # Ensure indexes exist even if the table was created manually before.
        index_statements = (
            "CREATE INDEX IF NOT EXISTS idx_reports_reporter_id ON reports(reporter_id)",
            "CREATE INDEX IF NOT EXISTS idx_reports_reported_user_id ON reports(reported_user_id)",
            "CREATE INDEX IF NOT EXISTS idx_reports_reported_post_id ON reports(reported_post_id)",
            "CREATE INDEX IF NOT EXISTS idx_reports_reported_message_id ON reports(reported_message_id)",
            "CREATE INDEX IF NOT EXISTS idx_reports_status ON reports(status)",
        )

        for statement in index_statements:
            db.session.execute(text(statement))

        db.session.commit()


if __name__ == "__main__":
    upgrade()
