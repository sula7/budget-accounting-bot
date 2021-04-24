import psycopg2
from loader import logger

con = psycopg2.connect(
    database='budget_bot',
    user='postgres',
    password='password',
    host='127.0.0.1',
    port='5432'
)


def add_outcome_category(name, chat_id):
    cur = con.cursor()
    try:
        cur.execute('INSERT INTO outcome_category (name, chat_id) VALUES (%s, %s);', (name, chat_id,))
        con.commit()
        return True

    except Exception as e:
        logger.error(e)
        return False

    finally:
        cur.close()


def delete_outcome_category(outcome_id):
    cur = con.cursor()
    try:
        cur.execute('UPDATE outcome_category SET is_deleted = TRUE WHERE id = %s AND is_default = FALSE RETURNING id;',
                    (outcome_id,))
        con.commit()
        category_id = cur.fetchall()
        return category_id

    except Exception as e:
        logger.error(e)
        return False

    finally:
        cur.close()


def select_outcome_category(chat_id):
    cur = con.cursor()
    try:
        cur.execute(
            'SELECT name, id, is_default from outcome_category WHERE chat_id = %s AND is_deleted IS FALSE OR is_default = TRUE',
            (chat_id,))
        categories_name = cur.fetchall()
        con.commit()
        return categories_name

    except Exception as e:
        logger.error(e)
        return False

    finally:
        cur.close()


def add_income(amount, chat_id, username):
    cur = con.cursor()
    try:
        cur.execute('INSERT INTO income (amount, chat_id, username) VALUES (%s, %s, %s);', (amount, chat_id, username,))
        con.commit()
        return True

    except Exception as e:
        logger.error(e)
        return False

    finally:
        cur.close()


def add_outcome(chat_id, category_id, amount):
    cur = con.cursor()
    try:
        cur.execute('INSERT INTO outcome (chat_id, category_id, amount) VALUES (%s, %s, %s);',
                    (chat_id, category_id, amount,))
        con.commit()
        return True

    except Exception as e:
        logger.error(e)
        return False

    finally:
        cur.close()


def get_report_json(created_at_from, created_at_to, chat_id):
    cur = con.cursor()
    try:
        cur.execute("""
            SELECT json_build_object('incomes', income, 'incomes_total_amount', incomes_total_amount, 'outcome', outcome,
                                 'outcome_total_amount', outcome_total_amount)
        FROM (
                 SELECT (
                            SELECT json_agg(base)
                            FROM (
                                     SELECT sum(inc.amount)               user_amount,
                                            inc.username                  username,
                                            concat(
                                                    round(
                                                                100 * sum(inc.amount) /
                                                                (
                                                                    SELECT sum(amount)
                                                                    FROM income
                                                                    WHERE chat_id IN (%s)
                                                                      AND created_at >= %s
                                                                      AND created_at <= %s
                                                                )), '%%') percentage
                                     FROM income inc
                                     WHERE inc.chat_id = %s
                                       AND inc.created_at >= %s
                                       AND inc.created_at <= %s
                                     GROUP BY inc.username
                                 ) base
                        )
                            income,
                        (
                            SELECT sum(amount)
                            FROM income
                            WHERE chat_id IN (%s)
                              AND created_at >= %s
                              AND created_at <= %s
                        )   incomes_total_amount,
                        (
                            SELECT json_agg(base)
                            FROM (
                                     SELECT sum(o.amount)                 category_amount,
                                            oc.name                       category_name,
                                            concat(
                                                    round(
                                                                100 * sum(o.amount) /
                                                                (
                                                                    SELECT sum(amount)
                                                                    FROM outcome
                                                                    WHERE chat_id IN (%s)
                                                                      AND created_at >= %s
                                                                      AND created_at <= %s
                                                                )), '%%') percentage
                                     FROM outcome o
                                              LEFT JOIN outcome_category oc on o.category_id = oc.id
                                     WHERE o.chat_id = %s
                                       AND o.created_at >= %s
                                       AND o.created_at <= %s
                                     GROUP BY oc.name
                                 ) base
                        )   outcome,
                        (
                            SELECT sum(amount)
                            FROM outcome
                            WHERE chat_id IN (%s)
                              AND created_at >= %s
                              AND created_at <= %s
                        )   outcome_total_amount
             ) a
            """, (
            chat_id, created_at_from, created_at_to, chat_id, created_at_from, created_at_to, chat_id, created_at_from,
            created_at_to, chat_id, created_at_from, created_at_to, chat_id, created_at_from, created_at_to, chat_id,
            created_at_from,
            created_at_to,))
        argument = cur.fetchall()
        con.commit()
        return argument[0][0]

    except Exception as e:
        logger.error(e)
        return False

    finally:
        cur.close()
