"""Add default users, devices, and measurements.

Revision ID: c4ae41cecbed
Revises: 43a05c5917d6
Create Date: 2026-10-07 19:14:05.985465

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c4ae41cecbed"
down_revision: str | None = "43a05c5917d6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    connection = op.get_bind()

    connection.execute(
        sa.text(
            """
            INSERT INTO users (id, name)
            VALUES
                ('00000000-0000-0000-0000-000000000001', 'dev_user'),
                ('00000000-0000-0000-0000-000000000002', 'test_user')
            ON CONFLICT DO NOTHING
            """
        )
    )
    connection.execute(
        sa.text(
            """
            INSERT INTO devices (id, serial_number)
            VALUES
                ('10000000-0000-0000-0000-000000000001', 'DEV-001'),
                ('10000000-0000-0000-0000-000000000002', 'DEV-002'),
                ('10000000-0000-0000-0000-000000000003', 'TEST-001')
            ON CONFLICT DO NOTHING
            """
        )
    )
    connection.execute(
        sa.text(
            """
            INSERT INTO user_device_association (user_id, device_id)
            VALUES
                (
                    '00000000-0000-0000-0000-000000000001',
                    '10000000-0000-0000-0000-000000000001'
                ),
                (
                    '00000000-0000-0000-0000-000000000001',
                    '10000000-0000-0000-0000-000000000002'
                ),
                (
                    '00000000-0000-0000-0000-000000000002',
                    '10000000-0000-0000-0000-000000000003'
                )
            ON CONFLICT DO NOTHING
            """
        )
    )
    connection.execute(
        sa.text(
            """
            INSERT INTO measurements (id, device_id, timestamp, x, y, z)
            VALUES
                (
                    '20000000-0000-0000-0000-000000000001',
                    '10000000-0000-0000-0000-000000000001',
                    '2026-10-01 09:00:00', 10.2, 20.1, 30.3
                ),
                (
                    '20000000-0000-0000-0000-000000000002',
                    '10000000-0000-0000-0000-000000000001',
                    '2026-10-02 09:00:00', 10.5, 20.4, 30.6
                ),
                (
                    '20000000-0000-0000-0000-000000000003',
                    '10000000-0000-0000-0000-000000000002',
                    '2026-10-01 09:00:00', 11.0, 21.2, 31.4
                ),
                (
                    '20000000-0000-0000-0000-000000000004',
                    '10000000-0000-0000-0000-000000000002',
                    '2026-10-02 09:00:00', 11.3, 21.5, 31.7
                ),
                (
                    '20000000-0000-0000-0000-000000000005',
                    '10000000-0000-0000-0000-000000000003',
                    '2026-10-01 09:00:00', 12.1, 22.2, 32.3
                ),
                (
                    '20000000-0000-0000-0000-000000000006',
                    '10000000-0000-0000-0000-000000000003',
                    '2026-10-02 09:00:00', 12.4, 22.5, 32.6
                )
            ON CONFLICT DO NOTHING
            """
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    connection = op.get_bind()

    connection.execute(
        sa.text(
            """
            DELETE FROM measurements
            WHERE id IN (
                '20000000-0000-0000-0000-000000000001',
                '20000000-0000-0000-0000-000000000002',
                '20000000-0000-0000-0000-000000000003',
                '20000000-0000-0000-0000-000000000004',
                '20000000-0000-0000-0000-000000000005',
                '20000000-0000-0000-0000-000000000006'
            )
            """
        )
    )
    connection.execute(
        sa.text(
            """
            DELETE FROM user_device_association
            WHERE user_id IN (
                '00000000-0000-0000-0000-000000000001',
                '00000000-0000-0000-0000-000000000002'
            )
            AND device_id IN (
                '10000000-0000-0000-0000-000000000001',
                '10000000-0000-0000-0000-000000000002',
                '10000000-0000-0000-0000-000000000003'
            )
            """
        )
    )
    connection.execute(
        sa.text(
            """
            DELETE FROM devices
            WHERE id IN (
                '10000000-0000-0000-0000-000000000001',
                '10000000-0000-0000-0000-000000000002',
                '10000000-0000-0000-0000-000000000003'
            )
            """
        )
    )
    connection.execute(
        sa.text(
            """
            DELETE FROM users
            WHERE id IN (
                '00000000-0000-0000-0000-000000000001',
                '00000000-0000-0000-0000-000000000002'
            )
            """
        )
    )
