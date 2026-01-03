-- 1. Create the sessions table (if it doesn't exist)
CREATE TABLE IF NOT EXISTS public.sessions (
    id TEXT PRIMARY KEY,
    response TEXT,
    timestamp TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Enable Row Level Security (RLS)
ALTER TABLE public.sessions ENABLE ROW LEVEL SECURITY;

-- 3. Create a policy to allow anonymous access (Drop existing to avoid error)
DROP POLICY IF EXISTS "Allow Anonymous Access" ON public.sessions;
CREATE POLICY "Allow Anonymous Access" ON public.sessions
FOR ALL 
USING (true) 
WITH CHECK (true);

-- 4. Enable Realtime Replication
-- We use a DO block to check if it's already added, to avoid the error you saw.
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_publication_tables 
    WHERE pubname = 'supabase_realtime' AND tablename = 'sessions'
  ) THEN
    ALTER PUBLICATION supabase_realtime ADD TABLE public.sessions;
  END IF;
END
$$;
