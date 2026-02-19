from core.config import settings
import pg8000
from urllib.parse import urlparse, parse_qs
import ssl

DATABASE_URL = str(settings.DATABASE_URL)
if not DATABASE_URL:
    raise RuntimeError('Please set DATABASE_URL environment variable')


def get_conn_params(url: str):
    # expects postgresql+asyncpg://user:pass@host/db?params
    if url.startswith('postgresql+asyncpg://'):
        url = url.replace('postgresql+asyncpg://', 'postgresql://')
    parsed = urlparse(url)
    user = parsed.username
    password = parsed.password
    host = parsed.hostname
    port = parsed.port or 5432
    db = parsed.path.lstrip('/')
    query = parse_qs(parsed.query)
    sslmode = query.get('sslmode', ['prefer'])[0]
    ssl_ctx = None
    if sslmode and sslmode != 'disable':
        ssl_ctx = ssl.create_default_context()
    return dict(user=user, password=password, host=host, port=port, database=db, ssl_context=ssl_ctx)


DDL = [
    """
    CREATE TABLE IF NOT EXISTS brands (
      id SERIAL PRIMARY KEY,
      name VARCHAR(255) UNIQUE NOT NULL,
      slug VARCHAR(255) UNIQUE NOT NULL,
      description TEXT
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS menu_items (
      id SERIAL PRIMARY KEY,
      brand_id INTEGER NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
      name VARCHAR(255) NOT NULL,
            price NUMERIC NOT NULL,
            category VARCHAR(100),
            available BOOLEAN DEFAULT true
    )
    """,
        # ensure uniqueness per brand+name so we can upsert safely
        """
        CREATE UNIQUE INDEX IF NOT EXISTS ux_menu_items_brand_name ON menu_items(brand_id, name)
        """,
    """
    CREATE TABLE IF NOT EXISTS orders (
      id SERIAL PRIMARY KEY,
      brand_id INTEGER NOT NULL REFERENCES brands(id),
      total NUMERIC NOT NULL,
      status VARCHAR(50) DEFAULT 'pending',
      created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS order_items (
      id SERIAL PRIMARY KEY,
      order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
      menu_item_id INTEGER NOT NULL REFERENCES menu_items(id),
      quantity INTEGER NOT NULL,
      price NUMERIC NOT NULL
    )
    """,
]


BRANDS = [
    ("Healthy Foodz", "healthy-foodz", "Fresh and healthy meals"),
    ("Tazty Foodz", "tazty-foodz", "Delicious comfort food"),
    ("Ideal Foodz", "ideal-foodz", "Balanced meals for everyone"),
]

# MENU_ITEMS: slug -> list of tuples (name, price, category)
MENU_ITEMS = {
    "ideal-foodz": [
        # Main Curries
        ("Paneer Butter Masala", 220.0, "Main Curries"),
        ("Chicken Butter Masala", 260.0, "Main Curries"),
        ("Paneer Masala", 200.0, "Main Curries"),
        ("Kadai Chicken", 270.0, "Main Curries"),
        ("Chicken Curry", 240.0, "Main Curries"),
        # Soups & Starters
        ("Chicken Soup", 120.0, "Soups & Starters"),
        ("Chicken Roast Fry", 220.0, "Soups & Starters"),
        ("Veg Manchurian", 180.0, "Soups & Starters"),
        ("Chicken 65", 230.0, "Soups & Starters"),
        # Biryani & Rice
        ("Chicken Biryani", 240.0, "Biryani & Rice"),
        ("Veg Biryani", 180.0, "Biryani & Rice"),
        ("Paneer Biryani", 210.0, "Biryani & Rice"),
        ("Bagara Rice", 150.0, "Biryani & Rice"),
        ("Jeera Rice", 140.0, "Biryani & Rice"),
        ("Curd Rice", 100.0, "Biryani & Rice"),
        # Breads
        ("Roti", 15.0, "Breads"),
        ("Chapathi", 20.0, "Breads"),
        ("Plain Naan", 30.0, "Breads"),
        ("Butter Naan", 40.0, "Breads"),
        # Sides
        ("Papad", 20.0, "Sides"),
        ("Raita", 30.0, "Sides"),
        ("Water Bottle", 20.0, "Sides"),
    ],

    "tazty-foodz": [],

    "healthy-foodz": [
        # Placeholder - owner to provide items
    ],
}


# Full Tazty Foodz menu (will replace existing items for tazty-foodz)
TAZTY_MENU = [
    ("Chicken Pizza", 249.0, "Pizza"),
    ("Extra Cheese Pizza", 229.0, "Pizza"),
    ("Corn Pizza", 209.0, "Pizza"),
    ("Paneer Pizza", 239.0, "Pizza"),
    ("Egg Pizza", 219.0, "Pizza"),
    ("Veg Pizza", 199.0, "Pizza"),
    ("Extra Spicy Pizza", 229.0, "Pizza"),
    ("Plain Maggie", 69.0, "Maggie"),
    ("Egg Maggie", 89.0, "Maggie"),
    ("Cheese Maggie", 99.0, "Maggie"),
    ("Special Maggie", 119.0, "Maggie"),
    ("Paneer Maggie", 109.0, "Maggie"),
    ("French Fries", 89.0, "Starters"),
    ("Chicken Soup", 129.0, "Starters"),
    ("Chicken Roast Fry", 189.0, "Starters"),
    ("Egg Fry (2)", 59.0, "Starters"),
    ("Omelette", 59.0, "Starters"),
    ("Chicken Shawarma", 179.0, "Starters"),
    ("Chicken Frankie", 139.0, "Starters"),
    ("Egg Frankie", 99.0, "Starters"),
    ("White Sauce Pasta", 159.0, "Pasta"),
    ("Red Sauce Pasta", 149.0, "Pasta"),
    ("Pink Sauce Pasta", 169.0, "Pasta"),
    ("Bagara Rice with Chicken Curry", 179.0, "Chicken Curries"),
    ("Chicken Biryani", 219.0, "Chicken Curries"),
    ("Curd Rice", 79.0, "Rice & Meals"),
    ("Tomato Rice", 89.0, "Rice & Meals"),
    ("Fried Rice", 129.0, "Rice & Meals"),
    ("Chapathi (2 pcs)", 49.0, "Breads"),
    ("Bread Jam", 39.0, "Breads"),
    ("Tomato Sauce (dip)", 10.0, "Breads"),
    ("Mayonnaise (dip)", 15.0, "Breads"),
    ("Extra Chilli Flakes (per pack)", 10.0, "Breads"),
    ("Extra Oregano (per pack)", 10.0, "Breads"),
    ("Pepsi", 40.0, "Beverages"),
    ("Maaza", 40.0, "Beverages"),
    ("Thums Up", 40.0, "Beverages"),
    ("Sprite", 40.0, "Beverages"),
    ("Water Bottle", 20.0, "Beverages"),
    ("Coffee", 30.0, "Beverages"),
    ("Black Coffee", 25.0, "Beverages"),
    ("Milk", 25.0, "Beverages"),
    ("Boost (hot/cold)", 30.0, "Beverages"),
    ("Horlicks", 40.0, "Beverages"),
    ("Chai Biscuits", 30.0, "Snacks & Desserts"),
    ("Popcorn (Small) - Cheese", 50.0, "Snacks & Desserts"),
    ("Popcorn (Small) - Masala", 50.0, "Snacks & Desserts"),
    ("Popcorn (Small) - Salty", 50.0, "Snacks & Desserts"),
    ("Popcorn (Medium) - Cheese", 80.0, "Snacks & Desserts"),
    ("Popcorn (Medium) - Masala", 80.0, "Snacks & Desserts"),
    ("Popcorn (Medium) - Salty", 80.0, "Snacks & Desserts"),
    ("Popcorn (Large) - Cheese", 120.0, "Snacks & Desserts"),
    ("Popcorn (Large) - Masala", 120.0, "Snacks & Desserts"),
    ("Popcorn (Large) - Salty", 120.0, "Snacks & Desserts"),
]


def seed():
    params = get_conn_params(DATABASE_URL)
    conn = pg8000.connect(**params)
    cur = conn.cursor()

    # Remove exact duplicate menu_items (same brand_id + name) keeping lowest id
    # This avoids unique index creation failures when duplicates exist from prior seeds
    cur.execute("""
        DELETE FROM menu_items a USING menu_items b
        WHERE a.id > b.id AND a.brand_id = b.brand_id AND a.name = b.name
    """)

    for ddl in DDL:
        cur.execute(ddl)

    # Optional: clear menu_items that are not referenced by orders (safe)
    clear_menu = bool(settings.CLEAR_MENU)
    if clear_menu:
        # delete only unreferenced menu items to avoid breaking existing orders
        cur.execute("""
            DELETE FROM menu_items WHERE id NOT IN (SELECT menu_item_id FROM order_items)
        """)
        print(f"Cleared unreferenced menu_items, deleted: {cur.rowcount}")

    # insert brands with ON CONFLICT DO NOTHING
    for name, slug, desc in BRANDS:
        cur.execute("""
            INSERT INTO brands (name, slug, description) VALUES (%s, %s, %s)
            ON CONFLICT (slug) DO UPDATE SET name = EXCLUDED.name
            RETURNING id
        """, (name, slug, desc))
        row = cur.fetchone()
        if row:
            brand_id = row[0]
        else:
            # fetch id
            cur.execute("SELECT id FROM brands WHERE slug=%s", (slug,))
            brand_id = cur.fetchone()[0]

        # insert or update menu items (name, price, category) using UPSERT on (brand_id, name)
        # For tazty-foodz we remove existing items for that brand and insert the canonical TAZTY_MENU
        if slug == 'tazty-foodz':
            cur.execute("DELETE FROM menu_items WHERE brand_id=%s", (brand_id,))
            items_to_insert = TAZTY_MENU
        else:
            items_to_insert = MENU_ITEMS.get(slug, [])

        for entry in items_to_insert:
            if len(entry) == 3:
                it_name, price, category = entry
            else:
                it_name, price = entry
                category = None
            cur.execute("""
                INSERT INTO menu_items (brand_id, name, price, category, available)
                VALUES (%s, %s, %s, %s, true)
                ON CONFLICT (brand_id, name) DO UPDATE
                SET price = EXCLUDED.price, category = EXCLUDED.category, available = EXCLUDED.available
                RETURNING id
            """, (brand_id, it_name, price, category))
            row = cur.fetchone()
            # if INSERT returned nothing (shouldn't happen), ensure item exists
            if not row:
                cur.execute("SELECT id FROM menu_items WHERE brand_id=%s AND name=%s", (brand_id, it_name))
                row = cur.fetchone()

    conn.commit()
    cur.close()
    conn.close()
    print('Raw seeding complete')


if __name__ == '__main__':
    seed()
