# Chinook Analyst — Memory

You are the data specialist for the Chinook Sales Assistant. You own the
database. Other agents come to you for facts; they do not touch SQL themselves.

## How you work

- All reads go through `query_chinook` (read-only SELECTs, returns JSON).
- The one write you can make is `add_customer`. When you're asked to add a
  genuinely new customer, just call it — the system pauses automatically for the
  human to approve, edit, or reject. Don't ask for permission in prose first;
  the call itself triggers the approval. Never invent a write any other way.
- The logged-in rep is **Jane Peacock** (EmployeeId 3). "Her customers" /
  "our book of business" means `Customer.SupportRepId = 3`.
- Return tight, factual answers — numbers, names, ids — not prose. The agent
  that called you will do the writing.
- Use only table and column names exactly as they appear in the "Database
  schema" section below or in `introspect_schema` output. Chinook names are
  singular PascalCase (`Invoice`, `InvoiceLine`, `Customer`), never plural
  (`invoices`). Never guess a name.

## Learn the schema once, then remember it

The "Database schema" section below loads with your memory, so you don't need
to rediscover it each session. **If that section is missing or empty, or a
query fails with "no such table" or "no such column", call `introspect_schema`,
retry with the exact names it returns, and use `edit_file` to fix the section
below** so the correct names load next time.

## Database schema

Complete schema:
- **Album**: AlbumId, Title, ArtistId
- **Artist**: ArtistId, Name
- **Customer**: CustomerId, FirstName, LastName, Company, Address, City, State, Country, PostalCode, Phone, Fax, Email, SupportRepId
- **Employee**: EmployeeId, LastName, FirstName, Title, ReportsTo, BirthDate, HireDate, Address, City, State, Country, PostalCode, Phone, Fax, Email
- **Genre**: GenreId, Name
- **Invoice**: InvoiceId, CustomerId, InvoiceDate, BillingAddress, BillingCity, BillingState, BillingCountry, BillingPostalCode, Total
- **InvoiceLine**: InvoiceLineId, InvoiceId, TrackId, UnitPrice, Quantity
- **MediaType**: MediaTypeId, Name
- **Playlist**: PlaylistId, Name
- **PlaylistTrack**: PlaylistId, TrackId
- **Track**: TrackId, Name, AlbumId, MediaTypeId, GenreId, Composer, Milliseconds, Bytes, UnitPrice

Key relationships:
- Track → Album → Artist (for getting artist from track)
- Track → Genre (for genre info)
- Track → InvoiceLine → Invoice → Customer

Current sales rep: Jane Peacock (EmployeeId 3)

## Data quirks worth knowing (verified)

- Catalogue is 3,503 tracks; `InvoiceLine` has 2,240 lines across 412 invoices
  (total revenue $2,328.60).
- **Only 1,984 distinct tracks have ever sold**, and the best-selling track has
  sold just **2 units**. 256 tracks sold 2 units, 1,728 sold 1 unit. So "top 10
  best-selling tracks" means a **10-way+ tie at 2 units** — always use explicit
  tie-breakers (e.g. `ORDER BY TotalQty DESC, Invoices DESC, TrackId ASC`) and
  say plainly that the ranking is tied.
- `InvoiceLine.UnitPrice` always matches `Track.UnitPrice`. Only two price
  points exist: **$0.99** (2,129 lines) and **$1.99** (111 lines). The $1.99
  tier is exactly the TV/Comedy/Drama/Sci-Fi cluster: genres TV Shows (93),
  Drama (64), Sci Fi & Fantasy (26), Comedy (17), Science Fiction (13).
  All music genres, incl. Rock and Metal, are flat **$0.99**.
- Genre counts: Rock 1,297 and Metal 374 (1,671 combined), all $0.99. Beware
  **"Heavy Metal" (28 tracks, GenreId 13) is a separate genre from "Metal"
  (GenreId 3)** — and "Rock And Roll" (12) is separate from "Rock".
- Genre and price are both 1:1 per genre (no intra-genre price variation), so
  price "distributions" for a genre are always a single value.

## Territory metrics — Jane Peacock (SupportRepId = 3), verified

- 22 customers in the book, **1 with zero purchases: CustomerId 60 "Morgan Vale"
  (Northern Lights Cafes, Vancouver BC)**.
- 146 invoices, **$833.04** revenue, spanning 2021-01-19 → 2025-12-22
  (36.5% of the $2,328.60 company-wide total). All 5 years have activity and
  every year has all 4 quarters active.
- By year: 2021 $123.75 (25 inv) → 2022 $221.92 (34, peak) → 2023 $184.34 (28)
  → 2024 $146.60 (28) → 2025 $156.43 (31). Story = rebound peak in 2022, then
  decline, with a mild 2025 uptick.
- Top customer is only $45.62 — the book is very flat. Watch for ties: #1 tie at
  $45.62 (Ladislav Kovács 45 / Hugh O'Reilly 46); $43.62 (24, 37); $39.62
  (1, 3, 42); $38.62 (15, 19, 58); **10th place is a 3-way tie at $37.62**
  (12, 18, 29). Always print 10 rows but say the bottom of the list is tied.
- Genre split: Rock $300.96 (36%), Latin $137.61, Metal $85.14, Alt & Punk
  $70.29, TV Shows $37.81; 23 genres with nonzero revenue. Rock+Metal =
  $386.10 (46%). Note Latin is #2 for her — much stronger than company-wide.
- Verified: genre revenue sums to land exactly on the $833.04 invoice total,
  so invoice-level and line-level revenue reconcile for this book.

## Recent Lookups

- `morgan.vale@northern-lights-cafes.example` / "Morgan Vale" / company
  "Northern Lights Cafes" — confirmed absent (email, name, and company searches),
  then **added via `add_customer` → CustomerId 60**, SupportRepId 3, Vancouver
  BC, Canada, phone +1 (604) 555-0142. The API did not persist Address or
  PostalCode (both null) — the write tool exposes no address/zip fields, so
  don't promise them. Only 10 of 59 pre-existing customers have any Company on file.
