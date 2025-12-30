from orm import ActiveRecord
from database import Database


class Hero(ActiveRecord):
    table = "heroes"


class Item(ActiveRecord):
    table = "items"


class GuildManager:
    @staticmethod
    def create_hero_with_starter_pack(name, class_id, level, gold):
        conn = Database.get_connection()

        # fix stuck transactions just in case
        try:
            conn.rollback()
        except:
            pass

        conn.start_transaction()
        try:
            cursor = conn.cursor()

            # 1. make the hero
            sql = "INSERT INTO heroes (name, class_id, gold_balance, level) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (name, class_id, float(gold), int(level)))
            hero_id = cursor.lastrowid

            # 2. grab a starter item
            cursor.execute("SELECT id FROM items LIMIT 1")
            item = cursor.fetchone()

            if item:
                # 3. give it to the hero
                cursor.execute("INSERT INTO inventory (hero_id, item_id, quantity) VALUES (%s, %s, 1)",
                               (hero_id, item[0]))

            conn.commit()
            cursor.close()
            return hero_id
        except Exception as e:
            conn.rollback()
            raise e

    @staticmethod
    def update_hero_stats(hero_id, new_level, new_gold):
        # update level and gold
        sql = "UPDATE heroes SET level = %s, gold_balance = %s WHERE id = %s"
        Database.execute_query(sql, (int(new_level), float(new_gold), hero_id))

    @staticmethod
    def delete_hero(hero_id):
        # bye bye hero
        sql = "DELETE FROM heroes WHERE id = %s"
        Database.execute_query(sql, (hero_id,))

    @staticmethod
    def get_report():
        # get big list for the report table
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
        # get the total numbers for the bottom of the report
        sql = """
            SELECT
                (SELECT IFNULL(SUM(i.value), 0) FROM inventory inv JOIN items i ON inv.item_id = i.id) as guild_item_value,
                (SELECT IFNULL(AVG(level), 0) FROM heroes) as avg_level,
                (SELECT IFNULL(AVG(gold_balance), 0) FROM heroes) as avg_gold
        """
        result = Database.execute_query(sql)
        return result[0] if result else {'guild_item_value': 0, 'avg_level': 0, 'avg_gold': 0}

    # --- NEW STUFF ---

    @staticmethod
    def get_hero_inventory(hero_id):
        # finds what items a specific hero has
        sql = """
            SELECT i.name, i.rarity, i.value 
            FROM inventory inv 
            JOIN items i ON inv.item_id = i.id 
            WHERE inv.hero_id = %s
        """
        return Database.execute_query(sql, (hero_id,))

    @staticmethod
    def import_items_from_json(json_data):
        # loads new items from a file
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
        # loads new heroes from a file (Import #2)
        import json
        heroes_list = json.loads(json_data)
        count = 0
        for h_data in heroes_list:
            # simple insert, assumes class_id 1 (Warrior) for simplicity
            hero = Hero(name=h_data['name'], level=h_data.get('level', 1), gold_balance=h_data.get('gold', 0),
                        class_id=1)
            hero.save()
            count += 1
        return count