from seed_raw import get_conn_params
from core.config import settings
import pg8000

def main():
    url = str(settings.DATABASE_URL)
    if not url:
        raise RuntimeError('DATABASE_URL not set')
    params = get_conn_params(url)
    conn = pg8000.connect(**params)
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM brands')
    print('brands_count:', cur.fetchone()[0])
    cur.execute('SELECT COUNT(*) FROM menu_items')
    print('menu_items_count:', cur.fetchone()[0])
    cur.execute("SELECT COUNT(DISTINCT category) FROM menu_items")
    print('distinct_categories:', cur.fetchone()[0])
    cur.execute("SELECT b.name, COUNT(m.id) FROM brands b LEFT JOIN menu_items m ON b.id = m.brand_id GROUP BY b.name ORDER BY b.name")
    for r in cur.fetchall():
        print(f"{r[0]}: {r[1]}")
    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
