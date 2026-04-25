"""Debug: dump PDF candidate list from podatki.gov.pl."""
from fetch_l2_podatki import collect_pdf_links, SEED_URLS, link_score
from common import session_factory
from topics import assign_topics

sess = session_factory()
pdfs = collect_pdf_links(SEED_URLS, sess)
print(f"Total: {len(pdfs)}\n")
for url, meta in pdfs.items():
    s = link_score(meta["anchor"], url)
    t = assign_topics(meta["anchor"], url)
    print(f"{s:>3}  {len(t)} topics  {url[:90]:90}  | {meta['anchor'][:60]}")
