import os, random, time
import barnum, psycopg2
from psycopg2 import Error

# CONFIG (identique à votre script)
users_seed_count = 10000
item_seed_count  = 1000
item_inventory_min, item_inventory_max = 1000, 5000
item_price_min,    item_price_max      = 5,    500
purchase_gen_count   = 100
purchase_gen_every_ms = 100

channels   = ["organic search", "paid search", "referral", "social", "display"]
categories = ["widgets", "gadgets", "doodads", "clearance"]
campaigns  = ["BOGO23", "FLASH2025"]

POSTGRES = dict(
    host=os.getenv("POSTGRES_HOST", "postgres"),
    port=os.getenv("POSTGRES_PORT", "5432"),
    user=os.getenv("POSTGRES_USER", "postgresuser"),
    password=os.getenv("POSTGRES_PASSWORD", "postgrespw"),
    dbname=os.getenv("POSTGRES_DB", "oneshop"),
)

item_insert     = "INSERT INTO items (name, category, price, inventory) VALUES (%s, %s, %s, %s)"
user_insert     = "INSERT INTO users (first_name, last_name, email, is_vip) VALUES (%s, %s, %s, %s)"
purchase_insert = "INSERT INTO purchases (user_id, item_id, campaign_id, quantity, purchase_price, created_at) VALUES (%s, %s, %s, %s, %s, %s)"


def seed_if_empty(cursor):
    cursor.execute("SELECT COUNT(*) FROM items")
    if cursor.fetchone()[0] == 0:
        print(f"Seeding {item_seed_count} items...")
        cursor.executemany(item_insert, [
            (
                barnum.create_nouns(),
                random.choice(categories),
                random.randint(item_price_min * 100, item_price_max * 100) / 100,
                random.randint(item_inventory_min, item_inventory_max),
            ) for _ in range(item_seed_count)
        ])

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        print(f"Seeding {users_seed_count} users...")
        cursor.executemany(user_insert, [
            (*barnum.create_name(), barnum.create_email(), random.randint(0, 10) > 8)
            for _ in range(users_seed_count)
        ])


def main():
    while True:  # reconnects on failure
        try:
            with psycopg2.connect(**POSTGRES) as conn:
                with conn.cursor() as cur:
                    seed_if_empty(cur)
                    conn.commit()

                    cur.execute("SELECT id, price FROM items")
                    item_prices = cur.fetchall()

                    cur.execute("SELECT id FROM users")
                    user_ids = [row[0] for row in cur.fetchall()]

                    print(f"→ Streaming purchases every {purchase_gen_every_ms}ms "
                          f"(items={len(item_prices)}, users={len(user_ids)})")

                    while True:
                        rows = []
                        for _ in range(purchase_gen_count):
                            item_id, price = random.choice(item_prices)
                            user_id  = random.choice(user_ids)  # vraie FK
                            qty      = random.randint(1, 5)
                            camp     = random.choice(campaigns)
                            ts       = time.strftime(
                                '%Y-%m-%d %H:%M:%S',
                                time.localtime(time.time() - random.randint(0, 86400))
                            )
                            rows.append((user_id, item_id, camp, qty, price * qty, ts))
                            time.sleep(purchase_gen_every_ms / 1000)
                        cur.executemany(purchase_insert, rows)
                        conn.commit()
                        print(f"✓ Inserted {len(rows)} purchases")
        except Error as e:
            print(f"DB error, retrying in 5s: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()