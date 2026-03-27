-- Create storage buckets for audio files
INSERT INTO storage.buckets (id, name, public) VALUES ('audio-inputs', 'audio-inputs', true);
INSERT INTO storage.buckets (id, name, public) VALUES ('audio-dubs', 'audio-dubs', true);

-- Allow all operations on audio-inputs bucket
CREATE POLICY "Allow all on audio-inputs" ON storage.objects FOR ALL USING (bucket_id = 'audio-inputs') WITH CHECK (bucket_id = 'audio-inputs');

-- Allow all operations on audio-dubs bucket
CREATE POLICY "Allow all on audio-dubs" ON storage.objects FOR ALL USING (bucket_id = 'audio-dubs') WITH CHECK (bucket_id = 'audio-dubs');
