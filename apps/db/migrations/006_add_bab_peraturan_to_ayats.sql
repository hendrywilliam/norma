-- Migration: Add bab_id and peraturan_id to ayats table
-- This denormalizes the data for faster queries

-- Add bab_id column to ayats
ALTER TABLE ayats ADD COLUMN IF NOT EXISTS bab_id INTEGER;

-- Add peraturan_id column to ayats
ALTER TABLE ayats ADD COLUMN IF NOT EXISTS peraturan_id VARCHAR(255);

-- Add foreign key constraint for bab_id
ALTER TABLE ayats ADD CONSTRAINT fk_ayat_bab
    FOREIGN KEY (bab_id) REFERENCES bab(id) ON DELETE SET NULL;

-- Add foreign key constraint for peraturan_id
ALTER TABLE ayats ADD CONSTRAINT fk_ayat_peraturan
    FOREIGN KEY (peraturan_id) REFERENCES peraturan(id) ON DELETE CASCADE;

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_ayat_bab_id ON ayats(bab_id);
CREATE INDEX IF NOT EXISTS idx_ayat_peraturan_id ON ayats(peraturan_id);

-- Update existing ayats with bab_id and peraturan_id from their pasal
UPDATE ayats a
SET 
    bab_id = p.bab_id,
    peraturan_id = p.peraturan_id
FROM pasals p
WHERE a.pasal_id = p.id;

-- Comments for new columns
COMMENT ON COLUMN ayats.bab_id IS 'Foreign key ke tabel bab (denormalized for faster queries)';
COMMENT ON COLUMN ayats.peraturan_id IS 'Foreign key ke tabel peraturan (denormalized for faster queries)';