"""Enhance knowledge base with tags and structured metadata

Revision ID: 2024_01_01_enhance_knowledge_base
Revises: c02ce5c4f07b
Create Date: 2024-01-01 12:00:00.000000

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "2024_01_01_enhance_knowledge_base"
down_revision: str | Sequence[str] | None = "c02ce5c4f07b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('is_system', sa.Boolean(), nullable=False, default=False),
        sa.Column('usage_count', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_tags_name'), 'tags', ['name'], unique=False)
    
    # Create document_tag_association table
    op.create_table(
        'document_tag_association',
        sa.Column('document_id', sa.UUID(), nullable=False),
        sa.Column('tag_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
        sa.PrimaryKeyConstraint('document_id', 'tag_id')
    )
    
    # Create document_processing_jobs table
    op.create_table(
        'document_processing_jobs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('document_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('job_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, default='pending'),
        sa.Column('priority', sa.Integer(), nullable=False, default=0),
        sa.Column('processing_engine', sa.String(length=100), nullable=True),
        sa.Column('processing_options', sa.JSON(), nullable=True),
        sa.Column('progress', sa.Float(), nullable=False, default=0.0),
        sa.Column('current_step', sa.String(length=100), nullable=True),
        sa.Column('total_steps', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, default=0),
        sa.Column('max_retries', sa.Integer(), nullable=False, default=3),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add new columns to documents table
    op.add_column('documents', sa.Column('author', sa.String(length=255), nullable=True))
    op.add_column('documents', sa.Column('source', sa.String(length=500), nullable=True))
    op.add_column('documents', sa.Column('language', sa.String(length=10), nullable=True))
    op.add_column('documents', sa.Column('year', sa.Integer(), nullable=True))
    op.add_column('documents', sa.Column('version', sa.String(length=50), nullable=True))
    op.add_column('documents', sa.Column('keywords', sa.JSON(), nullable=True))
    op.add_column('documents', sa.Column('document_type', sa.String(length=50), nullable=True))
    op.add_column('documents', sa.Column('processing_engine', sa.String(length=100), nullable=True))
    op.add_column('documents', sa.Column('processing_options', sa.JSON(), nullable=True))
    op.add_column('documents', sa.Column('page_count', sa.Integer(), nullable=True))
    op.add_column('documents', sa.Column('word_count', sa.Integer(), nullable=True))
    op.add_column('documents', sa.Column('character_count', sa.Integer(), nullable=True))
    
    # Add new columns to document_chunks table
    op.add_column('document_chunks', sa.Column('chunk_type', sa.String(length=50), nullable=True))
    op.add_column('document_chunks', sa.Column('page_number', sa.Integer(), nullable=True))
    op.add_column('document_chunks', sa.Column('section_title', sa.String(length=255), nullable=True))
    op.add_column('document_chunks', sa.Column('table_id', sa.String(length=100), nullable=True))
    op.add_column('document_chunks', sa.Column('figure_id', sa.String(length=100), nullable=True))
    
    # Create indexes for better performance
    op.create_index(op.f('ix_documents_title'), 'documents', ['title'], unique=False)
    op.create_index(op.f('ix_documents_author'), 'documents', ['author'], unique=False)
    op.create_index(op.f('ix_documents_language'), 'documents', ['language'], unique=False)
    op.create_index(op.f('ix_documents_year'), 'documents', ['year'], unique=False)
    op.create_index(op.f('ix_documents_document_type'), 'documents', ['document_type'], unique=False)
    op.create_index('idx_documents_user_status', 'documents', ['user_id', 'status'], unique=False)
    op.create_index('idx_documents_type_year', 'documents', ['document_type', 'year'], unique=False)
    op.create_index('idx_documents_author_year', 'documents', ['author', 'year'], unique=False)
    
    op.create_index('idx_chunks_document_index', 'document_chunks', ['document_id', 'chunk_index'], unique=False)
    op.create_index(op.f('ix_document_chunks_chunk_type'), 'document_chunks', ['chunk_type'], unique=False)
    op.create_index(op.f('ix_document_chunks_page_number'), 'document_chunks', ['page_number'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('idx_documents_author_year', table_name='documents')
    op.drop_index('idx_documents_type_year', table_name='documents')
    op.drop_index('idx_documents_user_status', table_name='documents')
    op.drop_index(op.f('ix_documents_document_type'), table_name='documents')
    op.drop_index(op.f('ix_documents_year'), table_name='documents')
    op.drop_index(op.f('ix_documents_language'), table_name='documents')
    op.drop_index(op.f('ix_documents_author'), table_name='documents')
    op.drop_index(op.f('ix_documents_title'), table_name='documents')
    
    op.drop_index(op.f('ix_document_chunks_page_number'), table_name='document_chunks')
    op.drop_index(op.f('ix_document_chunks_chunk_type'), table_name='document_chunks')
    op.drop_index('idx_chunks_document_index', table_name='document_chunks')
    
    # Drop columns from document_chunks
    op.drop_column('document_chunks', 'figure_id')
    op.drop_column('document_chunks', 'table_id')
    op.drop_column('document_chunks', 'section_title')
    op.drop_column('document_chunks', 'page_number')
    op.drop_column('document_chunks', 'chunk_type')
    
    # Drop columns from documents
    op.drop_column('documents', 'character_count')
    op.drop_column('documents', 'word_count')
    op.drop_column('documents', 'page_count')
    op.drop_column('documents', 'processing_options')
    op.drop_column('documents', 'processing_engine')
    op.drop_column('documents', 'document_type')
    op.drop_column('documents', 'keywords')
    op.drop_column('documents', 'version')
    op.drop_column('documents', 'year')
    op.drop_column('documents', 'language')
    op.drop_column('documents', 'source')
    op.drop_column('documents', 'author')
    
    # Drop tables
    op.drop_table('document_processing_jobs')
    op.drop_table('document_tag_association')
    op.drop_index(op.f('ix_tags_name'), table_name='tags')
    op.drop_table('tags')