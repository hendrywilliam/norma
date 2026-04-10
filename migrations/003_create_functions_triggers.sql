-- Migration 003: Create Functions and Triggers
-- File ini untuk membuat functions dan triggers untuk otomatisasi di semua tabel

-- ========================================
-- 1. FUNCTIONS
-- ========================================

-- Function untuk otomatis update kolom updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function untuk generate ID peraturan dari kategori, nomor, dan tahun
-- Format: {kategori}-{nomor}-{tahun}
CREATE OR REPLACE FUNCTION generate_peraturan_id()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.id IS NULL OR NEW.id = '' THEN
        NEW.id := lower(NEW.kategori) || '-' || NEW.nomor || '-' || NEW.tahun;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function untuk increment reparse_count
CREATE OR REPLACE FUNCTION increment_reparse_count()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.reparse_count IS NULL THEN
        NEW.reparse_count := 0;
    END IF;
    NEW.reparse_count := NEW.reparse_count + 1;
    NEW.last_reparse_at := CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function untuk log parsing operation ke tabel parsing_logs
CREATE OR REPLACE FUNCTION log_parsing_operation(
    p_peraturan_id VARCHAR(255),
    p_action VARCHAR(50),
    p_status VARCHAR(20),
    p_error_message TEXT DEFAULT NULL,
    p_metadata JSONB DEFAULT '{}'
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO parsing_logs (peraturan_id, action, status, error_message, metadata)
    VALUES (p_peraturan_id, p_action, p_status, p_error_message, p_metadata);
END;
$$ LANGUAGE plpgsql;

-- Function untuk cleanup old parsing logs (hapus log lebih dari 90 hari)
CREATE OR REPLACE FUNCTION cleanup_old_parsing_logs(days_to_keep INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM parsing_logs
    WHERE parsed_at < CURRENT_TIMESTAMP - (days_to_keep || ' days')::INTERVAL;

    GET DIAGNOSTICS deleted_count = ROW_COUNT;

    RAISE NOTICE 'Deleted % old parsing logs (older than % days)', deleted_count, days_to_keep;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function untuk mendapatkan statistik parsing
CREATE OR REPLACE FUNCTION get_parsing_stats(
    start_date TIMESTAMP DEFAULT NULL,
    end_date TIMESTAMP DEFAULT NULL
)
RETURNS TABLE (
    action VARCHAR(50),
    status VARCHAR(20),
    count BIGINT,
    success_rate NUMERIC,
    avg_time_minutes NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        action,
        status,
        COUNT(*) as count,
        ROUND(
            (COUNT(*) FILTER (WHERE status = 'success')::NUMERIC / COUNT(*)) * 100,
            2
        ) as success_rate,
        ROUND(
            AVG(
                EXTRACT(EPOCH FROM (
                    COALESCE(parsed_at, CURRENT_TIMESTAMP) - LAG(parsed_at) OVER (PARTITION BY action ORDER BY parsed_at)
                )) / 60
            ),
            2
        ) as avg_time_minutes
    FROM parsing_logs
    WHERE
        (start_date IS NULL OR parsed_at >= start_date)
        AND (end_date IS NULL OR parsed_at <= end_date)
    GROUP BY action, status
    ORDER BY action, status;
END;
$$ LANGUAGE plpgsql;

-- Function untuk log saat pasal diupdate (konten_pasal berubah)
CREATE OR REPLACE FUNCTION log_pasal_update()
RETURNS TRIGGER AS $$
BEGIN
    -- Log jika konten pasal berubah
    IF OLD.konten_pasal IS DISTINCT FROM NEW.konten_pasal THEN
        PERFORM log_parsing_operation(
            NEW.peraturan_id,
            'update_pasal',
            'success',
            NULL,
            jsonb_build_object(
                'pasal_id', NEW.id,
                'nomor_pasal', NEW.nomor_pasal,
                'old_length', length(OLD.konten_pasal),
                'new_length', length(NEW.konten_pasal)
            )
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function untuk count pasal di peraturan (untuk update metadata)
CREATE OR REPLACE FUNCTION update_peraturan_pasal_count()
RETURNS TRIGGER AS $$
DECLARE
    pasal_count INTEGER;
BEGIN
    IF TG_OP = 'INSERT' THEN
        -- Update count saat insert pasal baru
        UPDATE peraturan
        SET metadata = jsonb_set(
            COALESCE(metadata, '{}'),
            '{pasal_count}',
            to_jsonb((SELECT COUNT(*) FROM pasals WHERE peraturan_id = NEW.peraturan_id))
        )
        WHERE id = NEW.peraturan_id;
    ELSIF TG_OP = 'DELETE' THEN
        -- Update count saat delete pasal
        UPDATE peraturan
        SET metadata = jsonb_set(
            COALESCE(metadata, '{}'),
            '{pasal_count}',
            to_jsonb((SELECT COUNT(*) FROM pasals WHERE peraturan_id = OLD.peraturan_id))
        )
        WHERE id = OLD.peraturan_id;
    END IF;

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function untuk count ayat di pasal (untuk update metadata pasal)
CREATE OR REPLACE FUNCTION update_pasal_ayat_count()
RETURNS TRIGGER AS $$
DECLARE
    ayat_count INTEGER;
    pasal_id INTEGER;
BEGIN
    IF TG_OP = 'INSERT' THEN
        pasal_id := NEW.pasal_id;
    ELSE
        pasal_id := NEW.pasal_id;
    END IF;

    -- Update count saat insert ayat baru
    UPDATE pasals
    SET metadata = jsonb_set(
        COALESCE(metadata, '{}'),
        '{ayat_count}',
        to_jsonb((SELECT COUNT(*) FROM ayats WHERE pasal_id = pasal_id))
    )
    WHERE id = pasal_id;

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- 2. TRIGGERS untuk tabel peraturan
-- ========================================

-- Trigger untuk otomatis update updated_at pada tabel peraturan
DROP TRIGGER IF EXISTS update_peraturan_updated_at ON peraturan;
CREATE TRIGGER update_peraturan_updated_at
    BEFORE UPDATE ON peraturan
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger untuk generate ID peraturan secara otomatis (opsional)
-- Uncomment jika ingin otomatis generate ID
-- DROP TRIGGER IF EXISTS generate_peraturan_id ON peraturan;
-- CREATE TRIGGER generate_peraturan_id
--     BEFORE INSERT ON peraturan
--     FOR EACH ROW
--     EXECUTE FUNCTION generate_peraturan_id();

-- ========================================
-- 3. TRIGGERS untuk tabel bab
-- ========================================

-- Trigger untuk otomatis update updated_at pada tabel bab
DROP TRIGGER IF EXISTS update_bab_updated_at ON bab;
CREATE TRIGGER update_bab_updated_at
    BEFORE UPDATE ON bab
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- 4. TRIGGERS untuk tabel pasals
-- ========================================

-- Trigger untuk otomatis update updated_at pada tabel pasals
DROP TRIGGER IF EXISTS update_pasal_updated_at ON pasals;
CREATE TRIGGER update_pasal_updated_at
    BEFORE UPDATE ON pasals
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger untuk log update pasal (opsional)
-- Uncomment jika ingin otomatis log perubahan
-- DROP TRIGGER IF EXISTS log_pasal_changes ON pasals;
-- CREATE TRIGGER log_pasal_changes
--     AFTER UPDATE ON pasals
--     FOR EACH ROW
--     WHEN (OLD.konten_pasal IS DISTINCT FROM NEW.konten_pasal)
--     EXECUTE FUNCTION log_pasal_update();

-- Trigger untuk update peraturan metadata saat pasal diinsert/delete
-- DROP TRIGGER IF EXISTS update_peraturan_pasal_count_insert ON pasals;
-- CREATE TRIGGER update_peraturan_pasal_count_insert
--     AFTER INSERT OR DELETE ON pasals
--     FOR EACH ROW
--     EXECUTE FUNCTION update_peraturan_pasal_count();

-- ========================================
-- 5. TRIGGERS untuk tabel ayats
-- ========================================

-- Trigger untuk otomatis update updated_at pada tabel ayats
DROP TRIGGER IF EXISTS update_ayat_updated_at ON ayats;
CREATE TRIGGER update_ayat_updated_at
    BEFORE UPDATE ON ayats
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger untuk update pasal metadata saat ayat diinsert/delete
-- DROP TRIGGER IF EXISTS update_pasal_ayat_count_insert ON ayats;
-- CREATE TRIGGER update_pasal_ayat_count_insert
--     AFTER INSERT OR DELETE ON ayats
--     FOR EACH ROW
--     EXECUTE FUNCTION update_pasal_ayat_count();

-- ========================================
-- Log completion
-- ========================================

DO $$
BEGIN
    RAISE NOTICE 'Migration 003: Functions and triggers created successfully!';
    RAISE NOTICE '- Created functions for parsing operations';
    RAISE NOTICE '- Created triggers for peraturan table';
    RAISE NOTICE '- Created triggers for bab table';
    RAISE NOTICE '- Created triggers for pasals table';
    RAISE NOTICE '- Created triggers for ayats table';
END $$;
