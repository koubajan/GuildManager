from orm import ActiveRecord
from database import Database


class Hero(ActiveRecord):
    table = "heroes"


class Item(ActiveRecord):
    table = "items"


class GuildManager:
    @staticmethod
    def create_hero_with_starter_pack(name, class_id, level, gold, starter_item_id):
        conn = Database.get_connection()

        try:
            conn.rollback()
        except:
            pass

        conn.start_transaction()
        try:
            cursor = conn.cursor()

            # 1. create hero
            sql = "INSERT INTO heroes (name, class_id, gold_balance, level) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (name, class_id, float(gold), int(level)))
            hero_id = cursor.lastrowid

            # 2. give selected starter item (if one was picked)
            if starter_item_id:
                cursor.execute("INSERT INTO inventory (hero_id, item_id, quantity) VALUES (%s, %s, 1)",
                               (hero_id, starter_item_id))

            conn.commit()
            cursor.close()
            return hero_id
        except Exception as e:
            conn.rollback()
            raise e

    # --- HERO MANAGEMENT ---
    @staticmethod
    def update_hero_stats(hero_id, new_level, new_gold):
        sql = "UPDATE heroes SET level = %s, gold_balance = %s WHERE id = %s"
        Database.execute_query(sql, (int(new_level), float(new_gold), hero_id))

    @staticmethod
    def delete_hero(hero_id):
        sql = "DELETE FROM heroes WHERE id = %s"
        Database.execute_query(sql, (hero_id,))

    # --- ITEM MANAGEMENT (CRUD) ---
    @staticmethod
    def create_item(name, rarity, value):
        sql = "INSERT INTO items (name, rarity, value) VALUES (%s, %s, %s)"
        Database.execute_query(sql, (name, rarity, float(value)))

    @staticmethod
    def update_item(item_id, name, rarity, value):
        sql = "UPDATE items SET name=%s, rarity=%s, value=%s WHERE id=%s"
        Database.execute_query(sql, (name, rarity, float(value), item_id))

    @staticmethod
    def delete_item(item_id):
        # delete item from global DB (will fail if used in inventory unless we cascade, usually handled by DB constraints)
        # but for safety let's just try delete
        sql = "DELETE FROM items WHERE id=%s"
        Database.execute_query(sql, (item_id,))

    # --- INVENTORY MANAGEMENT ---
    @staticmethod
    def get_hero_inventory(hero_id):
        # Now returns the INVENTORY ID too (inv.id) so we can delete the link
        sql = """
            SELECT inv.id as inv_id, i.name, i.rarity, i.value 
            FROM inventory inv 
            JOIN items i ON inv.item_id = i.id 
            WHERE inv.hero_id = %s
        """
        return Database.execute_query(sql, (hero_id,))

    @staticmethod
    def add_item_to_inventory(hero_id, item_id):
        sql = "INSERT INTO inventory (hero_id, item_id, quantity) VALUES (%s, %s, 1)"
        Database.execute_query(sql, (hero_id, item_id))

    @staticmethod
    def remove_item_from_inventory(inventory_id):
        # deletes the specific row from inventory table
        sql = "DELETE FROM inventory WHERE id = %s"
        Database.execute_query(sql, (inventory_id,))

    # --- REPORTING & IMPORT ---
    @staticmethod
    def get_report():
        sql = """
            SELECT h.name, h.level, h.gold_balance, COUNT(inv.id) as item_count, SUM(i.value) as items_value
            FROM heroes h
            LEFT JOIN inventory inv ON h.id = inv.hero_id
            LEFT JOIN items i ON inv.item_id = i.id
            GROUP BY h.id
        """
        return Database.execute_query(sql)

    @staticmethod
    def get_guild_stats():
        sql = """
            SELECT
                (SELECT IFNULL(SUM(i.value), 0) FROM inventory inv JOIN items i ON inv.item_id = i.id) as guild_item_value,
                (SELECT IFNULL(AVG(level), 0) FROM heroes) as avg_level,
                (SELECT IFNULL(AVG(gold_balance), 0) FROM heroes) as avg_gold
        """
        result = Database.execute_query(sql)
        return result[0] if result else {'guild_item_value': 0, 'avg_level': 0, 'avg_gold': 0}

    @staticmethod
    def import_items_from_json(json_data):
        import json
        items_list = json.loads(json_data)
        count = 0
        for i_data in items_list:
            item = Item(name=i_data['name'], rarity=i_data['rarity'], value=i_data['value'])
            item.save()
            count += 1
        return count

    @staticmethod
    def import_heroes_from_json(json_data):
        import json
        heroes_list = json.loads(json_data)
        count = 0
        for h_data in heroes_list:
            hero = Hero(name=h_data['name'], level=h_data.get('level', 1), gold_balance=h_data.get('gold', 0),
                        class_id=1)
            hero.save()
            count += 1
        return count