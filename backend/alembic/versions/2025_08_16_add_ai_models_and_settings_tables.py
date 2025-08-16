from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2025_08_16_add_ai_models_and_settings_tables'
down_revision = '2025_08_16_fix_enum_types_and_timestamps'
branch_labels = None
depends_on = None

def upgrade() -> None:
	# Create knowledge_settings table
	op.create_table(
		'knowledge_settings',
		sa.Column('id', sa.String(length=36), primary_key=True),
		sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
		sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
		sa.Column('chunk_size', sa.Integer(), nullable=False, server_default=sa.text('500')),
		sa.Column('chunk_overlap', sa.Integer(), nullable=False, server_default=sa.text('50')),
		sa.Column('embedding_model', sa.String(length=200), nullable=False, server_default='text-embedding-ada-002'),
		sa.Column('index_type', sa.String(length=50), nullable=False, server_default='hybrid'),
		sa.Column('metadata_extraction', sa.Boolean(), nullable=False, server_default=sa.text('1')),
		sa.Column('auto_tagging', sa.Boolean(), nullable=False, server_default=sa.text('1')),
		sa.Column('search_algorithm', sa.String(length=50), nullable=False, server_default='hybrid'),
		sa.Column('max_file_size', sa.Integer(), nullable=False, server_default=sa.text(str(10 * 1024 * 1024))),
		sa.Column('supported_file_types', sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
		sa.Column('processing_timeout', sa.Integer(), nullable=False, server_default=sa.text('300')),
		sa.Column('batch_size', sa.Integer(), nullable=False, server_default=sa.text('10')),
		sa.Column('enable_cache', sa.Boolean(), nullable=False, server_default=sa.text('1')),
		sa.Column('cache_expiry', sa.Integer(), nullable=False, server_default=sa.text('3600')),
	)

	# Create ai_models table
	op.create_table(
		'ai_models',
		sa.Column('id', sa.String(length=36), primary_key=True),
		sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
		sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
		sa.Column('name', sa.String(length=200), nullable=False),
		sa.Column('provider', sa.String(length=100), nullable=False),
		sa.Column('model_key', sa.String(length=200), nullable=False),
		sa.Column('display_name', sa.String(length=200), nullable=False),
		sa.Column('description', sa.String(length=500), nullable=True),
		sa.Column('max_tokens', sa.Integer(), nullable=True),
		sa.Column('cost_per_1k_tokens', sa.Float(), nullable=True),
		sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
		sa.Column('is_default', sa.Boolean(), nullable=False, server_default=sa.text('0')),
		sa.Column('is_favorite', sa.Boolean(), nullable=False, server_default=sa.text('0')),
		sa.Column('capabilities', sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
		sa.Column('performance', sa.JSON(), nullable=True),
	)

	# Optional: add indexes
	op.create_index('ix_ai_models_provider', 'ai_models', ['provider'])
	op.create_index('ix_ai_models_model_key', 'ai_models', ['model_key'])


def downgrade() -> None:
	op.drop_index('ix_ai_models_model_key', table_name='ai_models')
	op.drop_index('ix_ai_models_provider', table_name='ai_models')
	op.drop_table('ai_models')
	op.drop_table('knowledge_settings')